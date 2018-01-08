import logging
import asyncio
import sqlite3
import sys
import time
import copy

import aiohttp

from .consts import HH_API
from .errors import HHApiError, ShutdownClient
from .http import Route
from .post import Post

from .HydrusTagArchive import HydrusTagArchive, HASH_TYPE_MD5

log = logging.getLogger(__name__)


class SuccMain:
    """succ main class.
    
    manages all operation of succ,
    from event loop, to download jobs,
    to shutdown, to everything.
    """
    def __init__(self):
        log.info('connecting to db')
        self._running = False
        self.db = sqlite3.connect('succ.db')
        self.cache = {}

        # create hydrus tag archive very early
        self.hta = HydrusTagArchive('succ-archive.db')
        self.hta.SetHashType(HASH_TYPE_MD5)

        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.async_init())

    def is_running(self) -> bool:
        """Check if the client is in a runnable state."""
        return self._running

    async def async_init(self):
        """Initialize things that need async."""
        self.session = aiohttp.ClientSession()

    async def hh_req(self, route, payload=None):
        """Call an HH route."""
        log.info(f'Calling {route!r}')
        async with self.session.request(route.method,
                                        f'{HH_API}{route.path}',
                                        json=payload) as res:
            if res.status != 200:
                raise HHApiError('Error contacting the api')

            return await res.json()

    def init(self):
        """Start the main stuff.
        
        Creating tables, etc
        """
        log.info('initializing')

        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS uploaders (
            author text,
            tag text,
        );
        """)

        self._running = True

    def shutdown(self, code):
        if not self._running:
            log.warning('trying to shutdown twice.')
            return

        # shutdown jobs here.
        self.db.commit()
        self.session.close()

        log.info(f'exiting with code {code}')
        self._running = False
        sys.exit(code)

    def c_exit(self, args):
        """Exit the client."""
        try:
            status = int(args[1])
        except:
            status = 0

        raise ShutdownClient(status)

    def c_quit(self, args):
        """Alias to exit."""
        self.c_exit(args)

    def c_commit(self, args):
        """Force a db commit"""
        log.info('forcing commit')
        self.db.commit()

    async def fetch_page(self, page: int) -> list:
        res = await self.hh_req(Route('GET', '/post/index.json?page'
                                             f'={page}&limit=200'))

        posts = []
        cur = self.db.cursor()
        for rawpost in res:
            post = Post(rawpost)

            # process namespaces
            post.tags.append(f'md5:{post.hash}')
            post.tags.append(f'id:{post.id}')

            for tag in copy.copy(post.tags):
                if '_(manipper)' in tag:
                    log.debug('got manipper [from hard manipper]')
                    post.tags.append(f'creator:{tag}')
                    post.tags.append(f'manipper:{tag}')
                elif '_(artist)' in tag:
                    log.debug('got artist [from hard artist]')
                    post.tags.append(f'creator:{tag}')
                elif post.author.lower() in tag:
                    log.debug('got artist [match]')
                    post.tags.append(f'creator:{tag}')

            # second pass, this time we checkin for any creator:
            # if none is found, we try to search
            # something using post.author, then slapping creator: on top
            good = False
            for tag in post.tags:
                if 'creator:' in tag:
                    good = True
                    break

            if not good:
                author = post.author.lower()
                cur.execute("SELECT tag FROM uploaders WHERE author=?",
                            (author,))

                tag = cur.fetchone()
                try:
                    tag = tag[0]
                except TypeError:
                    tag = 'none'

                if not tag:
                    log.debug(f'ignoring {author!r} as it wouldnt work')
                elif tag != 'none':
                    log.debug(f'got {author!r} from db = {tag!r}')
                    post.tags.append(tag)
                else:
                    # query hh to know about that uploader
                    r = Route('GET', '/tag/index.json?name='
                                     f'{author}&limit=1')

                    tags = await self.hh_req(r)
                    try:
                        artist_tag = tags[0]["name"]
                        tag = f'creator:{artist_tag}'
                        log.debug(f'found {author!r} = {tag!r}')
                        cur.execute('INSERT INTO uploaders (author, tag)'
                                    'VALUES (?, ?)',
                                    (author, tag))
                        post.tags.append(tag)
                    except IndexError:
                        log.debug(f'not found {author!r}')
                        cur.execute('INSERT INTO uploaders (author, tag) '
                                    'VALUES (?, NULL)',
                                    (author,))

                    log.debug('commiting')
                    self.db.commit()

            posts.append(post)

        log.info(f'got page {page}, {len(posts)} posts')
        return posts

    def fetch_pages(self, start: int, end: int) -> list:
        """Fetch a handful of pages."""
        posts = []
        coros = []

        log.info(f'fetching from page {start} to {end}')

        for page in range(start, end + 1):
            coro = self.fetch_page(page)
            coros.append(coro)

        done, pending = self.loop.run_until_complete(asyncio.wait(coros))
        for pagetask in done:
            data = pagetask.result()
            posts.extend(data)

        return posts

    def process_hta(self, posts, listid):
        """Process a list of hypnohub posts
        into the hydrus tag archive.
        """
        tstart = time.monotonic()
        self.hta.BeginBigJob()

        for post in posts:
            self.hta.AddMappings(post.bhash, post.tags)

        self.hta.CommitBigJob()

        tend = time.monotonic()
        delta = round((tend - tstart) * 1000, 3)
        log.info(f'took {delta}ms processing {len(posts)} posts [{listid}]')

    def c_fetch_latest(self, args):
        """fetch latest stuff from hypnohub"""
        posts = self.loop.run_until_complete(self.fetch_page(0))
        self.process_hta(posts, 'index')

    def c_fetch_pages(self, args):
        start, end = int(args[1]), int(args[2])
        data = self.fetch_pages(start, end)
        self.process_hta(data, f'pages: {start} - {end}')

    def c_fetch_all(self, args):
        """fetch all from hypnohub. ALL."""
        i = 0
        page_continue = 4
        while True:
            try:
                data = self.fetch_pages(i, i + page_continue)
            except HHApiError as err:
                print(f'api error! retrying. {err!r}')
                data = self.fetch_pages(i, i + page_continue)

            if not data:
                print('we received an empty page, assuming it finished!')
                break

            self.process_hta(data, f'pages: {i} - {i + page_continue}')
            i += page_continue + 1
            time.sleep(2)

    def process_line(self, line):
        """Process a line as a command"""
        args = line.split(' ')
        command = args[0]
        try:
            handler = getattr(self, f'c_{command}')
        except AttributeError:
            log.warning(f'command {command!r} not found')

        try:
            handler(args)
        except ShutdownClient as err:
            self.shutdown(err.args[0])
        except:
            log.exception('error executing command')
