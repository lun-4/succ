#!/usr/bin/env python3.6

import logging
from succ import SuccMain

__doc__ = """
a hypnohub api scraper

this calls the api a lot of times
in a sane matter, saving anything it can
to a SQLite database.

It also exports itself to a Hydrus
tag archive, so you can have your tagged porn

    ⣠⣦⣤⣀
⠀⠀⠀⠀⢡⣤⣿⣿
⠀⠀⠀⠀⠠⠜⢾⡟
⠀⠀⠀⠀⠀⠹⠿⠃⠄
⠀⠀⠈⠀⠉⠉⠑⠀⠀⠠⢈⣆
⠀⠀⣄⠀⠀⠀⠀⠀⢶⣷⠃⢵
⠐⠰⣷⠀⠀⠀⠀⢀⢟⣽⣆⠀⢃
⠰⣾⣶⣤⡼⢳⣦⣤⣴⣾⣿⣿⠞
⠀⠈⠉⠉⠛⠛⠉⠉⠉⠙⠁
⠀⠀⡐⠘⣿⣿⣯⠿⠛⣿⡄
⠀⠀⠁⢀⣄⣄⣠⡥⠔⣻⡇
⠀⠀⠀⠘⣛⣿⣟⣖⢭⣿⡇
⠀⠀⢀⣿⣿⣿⣿⣷⣿⣽⡇
⠀⠀⢸⣿⣿⣿⡇⣿⣿⣿⣇
⠀⠀⠀⢹⣿⣿⡀⠸⣿⣿⡏
⠀⠀⠀⢸⣿⣿⠇⠀⣿⣿⣿
⠀⠀⠀⠈⣿⣿⠀⠀⢸⣿⡿
⠀⠀⠀⠀⣿⣿⠀⠀⢀⣿⡇
⠀⣠⣴⣿⡿⠟⠀⠀⢸⣿⣷
⠀⠉⠉⠁⠀⠀⠀⠀⢸⣿⣿⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈
"""

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def main():
    log.debug('initializing succ')
    succ = SuccMain()
    succ.init()

    while True:
        try:
            line = input('> ')
        except EOFError:
            log.info('leaving')
            succ.shutdown(0)
            break

        try:
            succ.process_line(line)
        except:
            log.exception('error while processing command')

    succ.shutdown(0)

if __name__ == '__main__':
    main()
    """
    hta = HydrusTagArchive.HydrusTagArchive('succ.db')
    hta.SetHashType(HydrusTagArchive.HASH_TYPE_MD5)
    print(hta)
    del hta
    """

