import discord  
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
    new_url = rp.url


    request = session.get("https://s35.idu.edu.pl/")
    if (request.url.find("announcements") == -1) and (request.url.find("informations") == -1):
        exit(2137)

    html = session.get(new_url)
    html_string = html.content.decode('utf-8')
 
    def scrape(html_in):
        text = html_in.find('''double-column''')
        
        if text != -1:
            text = html_in[text:]
        else:
            text = html_in 

        part = text.split('''data-method="post" rel="nofollow"''', 1)
        return part[0]

    h = scrape(html_string)

    h = "\n".join(h.splitlines()[2:-4])

    h = markdownify.markdownify(h, heading_style="ATX") 
 







    r = session.get(new_url, allow_redirects=True)
    txt = r.content.decode('utf-8')
    m = list(re.finditer('''<input name="authenticity_token" type="hidden" value="''', txt))[-1]
    m2 = re.search('''"''', txt[m.end()+1:])
    auth_token = txt[m.end(): m.end()+m2.end()]

    new_url_new = new_url.split("/")
    if (new_url_new[-1] != "confirm"):
        new_url += "/confirm"

        
    data = {
        '_method': 'post',
        'authenticity_token': auth_token
    }
    response = session.post(new_url, data=data)


    return h


TOKEN = os.getenv('TOKEN')
CHANNEL_ID = int(os.getenv('AKTUALNOSCI_CHANEL_ID'))
MAX_MESSAGE_LENGTH = 2000

async def send_message():
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
        content = IDU()
        if len(content) > MAX_MESSAGE_LENGTH:
            # Split the message into chunks
            chunks = [content[i:i+MAX_MESSAGE_LENGTH] for i in range(0, len(content), MAX_MESSAGE_LENGTH)]
            for chunk in chunks:
                await channel.send(chunk)
        else:
            await channel.send(content)

        
        # await channel.send(message_content)
        await client.close()
    await client.start(TOKEN)