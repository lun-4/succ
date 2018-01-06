#!/usr/bin/env python3
MAIN_DESC = """
succ - a hypnohub api scraper

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
import logging
import argparse

import HydrusTagArchive

logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser(description=MAIN_DESC)
parser.add_argument('mode', type=str,
                    help='which mode to act as')
parser.add_argument('--db', default='mainsucc.db',
                    help='which db file to use to store main succ data')

def main():
    args = parser.parse_args()
    print(args.mode)
    print(args.db)

if __name__ == '__main__':
    main()
    """
    hta = HydrusTagArchive.HydrusTagArchive('succ.db')
    hta.SetHashType(HydrusTagArchive.HASH_TYPE_MD5)
    print(hta)
    del hta
    """

