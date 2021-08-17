'''
Runnable python script which launches the telegram bot.
Run with --help flag to see all options.
'''

import os
import sys
import argparse
from loguru import logger

parser = argparse.ArgumentParser(
    description='''
 ██████╗██╗  ██╗ █████╗ ████████╗██████╗  ██████╗ ████████╗
██╔════╝██║  ██║██╔══██╗╚══██╔══╝██╔══██╗██╔═══██╗╚══██╔══╝
██║     ███████║███████║   ██║   ██████╔╝██║   ██║   ██║
██║     ██╔══██║██╔══██║   ██║   ██╔══██╗██║   ██║   ██║
╚██████╗██║  ██║██║  ██║   ██║   ██████╔╝╚██████╔╝   ██║
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═════╝  ╚═════╝    ╚═╝

Author:
   github.com/antibagr
''',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    prog='chatbot',
    )
parser.add_argument(
    '-p',
    '--production',
    dest='production',
    default=False,
    action='store_true',
    help='Run chatbot in the production mode.'
)
cmd_args = vars(parser.parse_args())

if cmd_args.get('production'):
    os.environ['DEBUG'] = 'False'
