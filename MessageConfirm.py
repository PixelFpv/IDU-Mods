#!/bin/python3 
import discord
import asyncio
import requests
import markdownify
import re
import os
from dotenv import load_dotenv

load_dotenv()

# Retrieve username and password from environment variables
user = os.getenv('USER_NAME')
passw = os.getenv('PASSWORD')

# Function to send messages
def Message():
    # URL for logging in
    url = 'https://s35.idu.edu.pl/users/sign_in'

    # Start a session
    session = requests.Session()

    # Make a GET request to obtain login page content
    r = requests.get(url, allow_redirects=False)
    txt = r.content.decode('utf-8')

    # Extract authenticity token for login
    m = list(re.finditer('''<input name="authenticity_token" type="hidden" value="''', txt))[-1]
    m2 = re.search('''"''', txt[m.end()+1:])
    auth_token = txt[m.end(): m.end()+m2.end()]

    # Prepare login credentials
    values = {'user[login]': user,
            'user[password]': passw,
            'authenticity_token': auth_token,
            'remember_me': 1}

    # Log in using provided credentials
    rp = session.post(url,data=values)

    # Access the internal messages page
    html = session.get("https://s35.idu.edu.pl/internal_messages")
    html_string = html.content.decode('utf-8')

    # Pattern to match the number of pages of internal messages
    pattern = r'>(\d+)</a> <a class="next_page"'
    match = re.search(pattern, html_string)

    # Function to scrape information from HTML
    def scrape(html_in):
        pattern = r'><img alt="(\w+)\s+(\w+)"\s+src="'
        match = re.search(pattern, html_in)
        if match:
            name = match.group(1)
            surname = match.group(2)
            header = name + " " + surname
        else:
            header = ""
        text = html_in.find('''<div id="message-body">''')
        if text != -1:
            text = html_in[text:]
        else:
            text = html_in 
        part = text.split('''<form accept-charset="UTF-8" action="/internal_messages/create_for_thread" class="no-border no-bg"''', 1)
        title = "### Od: " + header
        return [title, part[0]]

    # Extract the number of pages of internal messages
    number_of_pages = int(match.group(1))

    # Iterate through each page to extract and send messages
    for i in range(1, number_of_pages + 1, 1):
        print(i)
        information_url = "https://s35.idu.edu.pl/internal_messages?page=" + str(i)
        info_get = session.get(information_url)
        info_string = info_get.content.decode('utf-8')
        info_part = info_string.split('''<table class="message-table">''')
        text = str(info_part[1]).find('''<td class="unread">''')
        if text != -1:
            info_split = info_part[1].split('''<td class="unread">''')
        else:
            exit(666)
        # Iterate through each message to extract and send
        for i in range(len(info_split), 1, -1):
            new_page = info_split[i-1]
            pattern = r'<a\s+href="(/internal_messages/\d+/watek)"\s+title="'            
            match = re.search(pattern, new_page)
            if match:
                link = match.group(1)
            else:
                continue
            # Access each message thread
            html = session.get("https://s35.idu.edu.pl" + link)
            html_string = html.content.decode('utf-8')
            # Scrape message information
            h = scrape(html_string)
            h = "\n".join(h)
            h = markdownify.markdownify(h, heading_style="ATX") 
            h = h.replace("####", "#")
            print(h)

            # Send the message asynchronously
            asyncio.run(send_message(h))

# Retrieve Discord token and channel ID from environment variables
TOKEN = os.getenv('TOKEN')
CHANNEL_ID = int(os.getenv('MESSAGE_CHANEL_ID'))
MAX_MESSAGE_LENGTH = 2000

# Asynchronously send message to Discord channel
async def send_message(content):
    intents = discord.Intents.default()
    intents.messages = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'We have logged in as {client.user}')
        # Find the designated channel
        channel = client.get_channel(CHANNEL_ID)
        if channel is None:
            print(f'Failed to find channel with ID {CHANNEL_ID}')
            await client.close()
            return
        # Send the message in chunks if it exceeds maximum length
        if len(content) > MAX_MESSAGE_LENGTH:
            chunks = [content[i:i+MAX_MESSAGE_LENGTH] for i in range(0, len(content), MAX_MESSAGE_LENGTH)]
            for chunk in chunks:
                await channel.send(chunk)
        else:
            await channel.send(content)
        await client.close()
    await client.start(TOKEN)

# Call the function to send messages
Message()
