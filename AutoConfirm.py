#!/bin/python3


from IDUAutoConfirm import *
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

user = os.getenv('USER_NAME')
passw = os.getenv('PASSWORD') 
   
asyncio.run(send_message()) 