import os

from dotenv import load_dotenv


def runserver():
    load_dotenv()
    os.system("python3 manage.py runserver")
