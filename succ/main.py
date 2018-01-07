import logging
import sqlite3

log = logging.getLogger(__name__)

class SuccMain:
    """succ main class.
    
    manages all operation of succ,
    from event loop, to download jobs,
    to shutdown, to everything.
    """
    def __init__(self):
        log.info('connecting to db')
        self.db = sqlite3.connect('succ.db')

    def init(self):
        log.info('initializing')

    def c_test(self, args):
        print('things are working!')

    def process_line(self, line):
        args = line.split(' ')
        command = args[0]
        try:
            handler = getattr(self, f'c_{command}')
            handler(args)
        except:
            log.warning(f'command {command} not found')
