import os
import sys

from pathlib import Path

BASE_DIR = Path(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.join(BASE_DIR.resolve(), ''))
sys.path.append(os.path.join(BASE_DIR.resolve().parent, 'locbot', ''))
# sys.path.append(os.path.join(BASE_DIR.resolve().parent,'locbot',  'admin'))


from chatbot.load.setup_django import setup_django
print('setting up django')
setup_django()
