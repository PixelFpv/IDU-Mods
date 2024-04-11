#!/bin/python3 

# from parse import is_busy
import pandas as pd
import time
from datetime import datetime, timedelta
from bisect import bisect_left
from datetime import datetime
from IDUAutoConfirm import *

import os
from dotenv import load_dotenv

load_dotenv()

user = os.getenv('USER_NAME')
passw = os.getenv('PASSWORD')   

week = {0: "Poniedziałek", 1: "Wtorek", 2: "Środa", 3: "Czwartek", 4: "Piątek"}
h = 3600
m = 60
start_times = [
    7 * h + 55 * m,
    8 * h + 45 * m,
    9 * h + 35 * m,
    10 * h + 30 * m,
    11 * h + 25 * m,
    12 * h + 15 * m,
    13 * h + 30 * m,
    14 * h + 25 * m,
    15 * h + 15 * m,
    16 * h + 5 * m,
    17 * h,
    17 * h + 45 * m,
]


def is_busy(page):

    nw = datetime.now()
    hrs = nw.hour
    mins = nw.minute
    secs = nw.second
    zero = timedelta(seconds=secs + mins * 60 + hrs * 3600)
    st = nw - zero  #

    lesson = bisect_left(start_times, secs + mins * 60 + hrs * 3600) - 1

    today = (datetime.today().toordinal() - 1) % 7

    df = pd.read_html(page)[1]

    lesson_now = lesson

    free_count = 0

    while lesson_now <= 10 and lesson_now >= 0 and str(df[week[today]][lesson_now]) == "nan":

        lesson_now = lesson_now + 1
        free_count = free_count + 1

        if lesson_now == 10 and free_count != 1:
            free_count = "Wolna do końca"
            break


    if lesson <= 10 and lesson >= 0 and str(df[week[today]][lesson]) != "nan":
             return True, 0

    return False, free_count

rooms_1 ={
    "Warsztat": 921,
    "Jaskinia": 1134,

}
rooms_2 ={
    "Parter": 916,
    "Tv": 920,
    "Akwarium": 953,
    "Techniczna": 952,
}
rooms_3 ={
    "Przyrodnicza": 891,
    "Niemiecka": 890,
    "Hiszpańska": 894,
    "Inf mała": 917,
    "Kanapowa": 956,
    "Angielska": 892,
    "Świetlica" : 889,
    "Północna": 955,
    "Przedsionek": 954,
    "Inf duża": 895,
}
import requests
import re
def get_empty_rooms():
    url = 'https://s35.idu.edu.pl/users/sign_in'


    session = requests.Session()
    r = requests.get(url, allow_redirects=False)
    txt = r.content.decode('utf-8')
    m = list(re.finditer('''<input name="authenticity_token" type="hidden" value="''', txt))[-1]
    m2 = re.search('''"''', txt[m.end()+1:])

    values = {'user[login]': user,
            'user[password]': passw,
            'authenticity_token': txt[m.end(): m.end()+m2.end()]}

    rp = session.post(url,values)

    request = session.get("https://s35.idu.edu.pl/")
    while (request.url.find("announcements") != -1) or (request.url.find("informations") != -1):
        asyncio.run(send_message())
        request = session.get("https://s35.idu.edu.pl/")

    free_1 = []
    for name, id in rooms_1.items():
        busy, count = is_busy(session.get(f"https://s35.idu.edu.pl/rooms/{id}").content)
        if not busy:
            
            free_1.append(name)
            if count == 0:
                free_1.append("")
            else:
               free_1.append(count)

    free_2 = []
    for name, id in rooms_2.items():
        busy, count = is_busy(session.get(f"https://s35.idu.edu.pl/rooms/{id}").content)
        if not busy:
            
            free_2.append(name)
            if count == 0:
                free_2.append("")
            else:
                free_2.append(count)

    free_3 = []
    for name, id in rooms_3.items():
        busy, count = is_busy(session.get(f"https://s35.idu.edu.pl/rooms/{id}").content)
        if not busy:
            
            free_3.append(name)
            if count == 0:
                free_3.append("")    
            else:
                free_3.append(count)


    website = open(r'../IDUwww/index.html',"r+")

    website.truncate(0)
    website.write('''
    <!DOCTYPE html>
    <html lang="en">
<head>

    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wolne Sale</title>
    <link rel="stylesheet" href="styles.css">
    <link rel="icon" type="image/png" href="icon.png">
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-RNGNB8P004"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'G-RNGNB8P004');
    </script>

    <script>
        var manifest = {
            "name": "Wolne Sale",
            "short_name": "Sale",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#ffffff",
            "icons": [
                {
                    "src": "icon.png",
                    "sizes": "192x192",
                    "type": "image/png"
                }
            ]
        };
        // Optionally, you can use the manifest object in your JavaScript code
        // For example, you can use it to set the theme color dynamically:
        document.querySelector('meta[name="theme-color"]').setAttribute('content', manifest.theme_color);
    </script>
                  
</head>
<body>
    <div class="container">
        <h1>Obecnie wolne sale w BSR</h1>
    ''')
    

    
    time = datetime.now()
    website.write("<h2>" + time.strftime("%Y-%m-%d %H:%M") + "</h2>" + '''<div class="rooms"><p>Sala&nbsp;&nbsp;|&nbsp;&nbsp;Wolne godziny</p><h3 style="font-size:35px">Piwnica:</h3>''')

    for i in range(0,len(free_1),2): 
        print (free_1[i], free_1[i+1])
        website.write("<p>&nbsp;&nbsp;&nbsp;" +free_1[i] + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + str(free_1[i+1]) + "</p>")
    if len(free_1) == 0:
        website.write("<p>&nbsp;&nbsp;&nbsp;Wszystkie sale zajęte</p>")
        
    website.write('''<h3 style="font-size:35px">Parter:</h3>''')
    for i in range(0,len(free_2),2):
        print (free_2[i], free_2[i+1])
        website.write("<p>&nbsp;&nbsp;&nbsp;" + free_2[i] + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + str(free_2[i+1]) + "</p>") 
    if len(free_2) == 0:
        website.write("<p>&nbsp;&nbsp;&nbsp;Wszystkie sale zajęte</p>")

    website.write('''<h3 style="font-size:35px">Piętro:</h3>''')
    for i in range(0,len(free_3),2):
        print (free_3[i], free_3[i+1])
        website.write("<p>&nbsp;&nbsp;&nbsp;" +free_3[i] + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + str(free_3[i+1]) +"</p>")
    if len(free_3) == 0:
        website.write("<p>&nbsp;&nbsp;&nbsp;Wszystkie sale zajęte</p>")
    website.write('''
            </div>
    </div>
</body>
</html>
            ''')

    return free_1+free_2+free_3

get_empty_rooms()
