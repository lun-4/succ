import logging
import asyncio
import sqlite3
import sys

import aiohttp

from .consts import HH_API
from .errors import HHApiError, ShutdownClient
from .http import Route

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

        self.db.execute("""
        CREATE TABLE IF NOT EXISTS files (
            hash text PRIMARY KEY
        )
        """)
        
        self.db.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            hash text,
            tag text,
            PRIMARY KEY (hash, tag)
        )
        """)

        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.async_init())

    def is_running(self) -> bool:
        return self._running

    async def async_init(self):
        self.session = aiohttp.ClientSession()

    async def hh_req(self, route, payload=None):
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

    def c_test(self, args):
        """test command"""
        print('things are working!')

    def c_exit(self, args):
        """Exit the client."""
        try:
            status = int(args[1])
        except:
            status = 0

        raise ShutdownClient(status)

    def c_fetch_latest(self, args):
        """fetch latest stuff from hypnohub"""
        coro = self.hh_req(Route('GET', '/post/index.json'))
        res = self.loop.run_until_complete(coro)
        print(f'got {len(res)} posts from index!')
        print(res)

    def process_line(self, line):
        args = line.split(' ')
        command = args[0]
        try:
            handler = getattr(self, f'c_{command}')
            handler(args)
        except AttributeError:
            log.warning(f'command {command!r} not found')
        except ShutdownClient as e:
            self.shutdown(e.args[0])
        except:
            log.exception('error executing command')
