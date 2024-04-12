#!/bin/python3 

import discord
import asyncio
import requests
import markdownify
import re

import os
from dotenv import load_dotenv

load_dotenv()

user = os.getenv('USER_NAME')
passw = os.getenv('PASSWORD')   
    

def IDU():
    url = 'https://s35.idu.edu.pl/users/sign_in'

    session = requests.Session()

    r = requests.get(url, allow_redirects=False)
    txt = r.content.decode('utf-8')
    m = list(re.finditer('''<input name="authenticity_token" type="hidden" value="''', txt))[-1]
    m2 = re.search('''"''', txt[m.end()+1:])
    auth_token = txt[m.end(): m.end()+m2.end()]

    values = {'user[login]': user,
            'user[password]': passw,
            'authenticity_token': auth_token,
            'remember_me': 1}

    rp = session.post(url,data=values)
    html = session.get("https://s35.idu.edu.pl")
    html_string = html.content.decode('utf-8')
    # new_url = rp.url
    pattern = r'<a href="/students/(\d+)'
    match = re.search(pattern, html_string)

    if match:
        student_id = match.group(1)
    else:
        student_id = 1

    html = session.get("https://s35.idu.edu.pl/students/" + student_id + "/subject_announcements")
    html_string = html.content.decode('utf-8')

    pattern = r'>(\d+)</a> <a class="next_page"'

    match = re.search(pattern, html_string)


    def scrape(html_in):
        text = html_in.find('''<div class="double-column">''')
        
        if text != -1:
            text = html_in[text:]
        else:
            text = html_in 

        part = text.split('''data-method="post" rel="nofollow''', 1)
        return part[0]


    number_of_pages = int(match.group(1))
    # print(number_of_pages)
    for i in range(number_of_pages, 0, -1):
        information_url = "https://s35.idu.edu.pl/students/" + student_id + "/subject_announcements?page=" + str(i)
        # print(information_url)
        info_get = session.get(information_url)
        # print(info_get)
        info_string = info_get.content.decode('utf-8')
        info_split = info_string.split("profile-event announcement new")
        for i in range(len(info_split), 1, -1):
            new_page = info_split[i-1]
            pattern = r'<a\s+href="(/subject_announcements/\d+/confirm)">'                
            match = re.search(pattern, new_page)
            link = match.group(1)
            # print(link)
            html = session.get("https://s35.idu.edu.pl" + link)
            html_string = html.content.decode('utf-8')

            h = scrape(html_string)
            h = "\n".join(h.splitlines()[2:-4])
            
            h = markdownify.markdownify(h, heading_style="ATX") 
            # print(h)

            
            # r = session.get(new_url, allow_redirects=True)
            # txt = r.content.decode('utf-8')
            m = list(re.finditer('''<input name="authenticity_token" type="hidden" value="''', html_string))[-1]
            m2 = re.search('''"''', html_string[m.end()+1:])
            auth_token = html_string[m.end(): m.end()+m2.end()]

                
            data = {
                '_method': 'post',
                'authenticity_token': auth_token
            }
            response = session.post(html.url, data=data)

            
            print (h)
            asyncio.run(send_message(h))


TOKEN = os.getenv('TOKEN')
CHANNEL_ID = int(os.getenv('PRZEDMIOTOWE_CHANEL_ID'))
MAX_MESSAGE_LENGTH = 2000

async def send_message(content):
    # Intents needed for certain events (like reading message content)
    intents = discord.Intents.default()
    intents.messages = True

    # Create a Discord client
    client = discord.Client(intents=intents)

    # Event that triggers when the bot is ready
    @client.event
    async def on_ready():
        print(f'We have logged in as {client.user}')

        # Fetch the channel where you want to send the message
        channel = client.get_channel(CHANNEL_ID)
        if channel is None:
            print(f'Failed to find channel with ID {CHANNEL_ID}')
            await client.close()
            return

        # Construct your message with a bolded heading
        if len(content) > MAX_MESSAGE_LENGTH:
            # Split the message into chunks
            chunks = [content[i:i+MAX_MESSAGE_LENGTH] for i in range(0, len(content), MAX_MESSAGE_LENGTH)]
            for chunk in chunks:
                await channel.send(chunk)
        else:
            await channel.send(content)

        
        await client.close()
    await client.start(TOKEN)

IDU()