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
def MarkSend():
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
    html = session.get("https://s35.idu.edu.pl/")
    html_string = html.content.decode('utf-8')

    # Pattern to match the number of pages of internal messages

    # Function to scrape information from HTML
    def scrape(html_in):
        text = html_in.find('''<span class="subject">''')
        if text != -1:
            text = html_in[text:]
        else:
            text = html_in 
        part = text.split('''class="fancybox">''')

        return (part[0])
    
    def scrape_third(html_in):
        text = html_in.find('''<span class="subject">''')
        if text != -1:
            text = html_in[text:]
        else:
            text = html_in 
        part = text.split('''class="fancybox">''')

        text1 = html_in.find('''<span class="description">(''')
        if text1 != -1:
            text1 = html_in[text1:]
            text1 = text1.replace('''<span class="description">(''', "")
        else:
            text1 = html_in 
        part1 = text1.split(''')</span>''')
        # print(part[0])
        part = part[0].split("</span>")

        # print(part[0] + "\n" + part1[0])
        return (part[0] + "\n" + part1[0])
    
    def scrape_second(html_in, subject):
        text = html_in.find('''<div id="''' + subject)
        if text != -1:
            text = html_in[text:]
        else:
            text = html_in 
        part = text.split('''</div><div id="''')
        
        return part[0]

    # Extract the number of pages of internal messages


    # Iterate through each page to extract and send messages

    info_part = html_string.split('''<h3>Oceny<span class="toggle-switch"><a href="#" class="hide-me">zwiń</a></span></h3>''')
    # text = str(info_part[1]).find('''<div class="profile-event mark unseen">''')
    text = str(info_part[1]).find('''<div class="profile-event mark">''')

    if text != -1:
        # info_split = info_part[1].split('''<div class="profile-event mark unseen">''')
        info_split = info_part[1].split('''<div class="profile-event mark">''')
        # print("Found unread mark")

    else:
        print("No new marks")
        exit(666)
        # Iterate through each message to extract and send
    # print(len(info_split))
    for i in range(0, len(info_split), 1):
        # print(i)
        h = scrape(info_split[i])
        # print (h)
        ha = h
        h = scrape_third(info_split[i])
        splith = h.split('''<a href="#description_for_grade_''')
        h = str(splith[0])

        pattern = r'class="name"><a\s*href=["\']([^"\']+)["\']'
        # print("ha: ", ha)
# Search for the pattern in the string
        match = re.search(pattern, ha)

        if match:
            # Extract the content
            content = match.group(1)
            content = content.replace("#", "")
            # print("Content found:", content)
        else:
            content = -1
            # print("Content not found")
        
        if content != -1:
            second = scrape_second(str(info_split), content)
            # print("second: ", second)

        else:
            second = ""
            # print("no description")
        # print(h, second)
        
        
        
        h = h + "\n" + second
        # h = second


        # Scrape message information
        
        # h = "\n".join(h)
        # print(h)
        h = markdownify.markdownify(h, heading_style="ATX") 
        # h = h.replace("####", "#")
        # print(h)
        h = h.replace("[", "")
        h = h.replace("]", "    ")
        print(h)
            # Send the message asynchronously
        # asyncio.run(send_message(h))

# Retrieve Discord token and channel ID from environment variables
TOKEN = os.getenv('TOKEN')
CHANNEL_ID = int(os.getenv('MARKS_CHANEL_ID'))
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
MarkSend()
