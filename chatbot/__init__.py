import os
import sys

from pathlib import Path

BASE_DIR = Path(os.path.abspath(os.path.dirname(__file__)))


# root
sys.path.append(os.path.join(BASE_DIR.resolve().parent.parent, ''))
# locbot
sys.path.append(os.path.join(BASE_DIR.resolve().parent, ''))
# chatbot
sys.path.append(os.path.join(BASE_DIR.resolve(), ''))
