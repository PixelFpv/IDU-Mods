# IDU-Mods
This is a list of mods for IDU - Internetowy Dziennik Ucznia

## Usage:
   Create .env file:
      '''
      
         USER_NAME = "YOUR IDU LOGIN NAME"
         PASSWORD = "YOUR IDU LOGIN PASSWORD"
         TOKEN = "YOUR DISCORD BOT TOKEN"
         
         #LEAVE BLANK IF YOU DONT WANT TO USE
         
         AKTUALNOSCI_CHANEL_ID = CHANEL TO SEND AKTUALNOŚCI
         
         OGLOSZENIE_CHANEL_ID = CHANEL TO SEND OGŁOSZENIA
         
         MESSAGE_CHANEL_ID = CHANEL TO SEND MESSAGES
         
         MARKS_CHANEL_ID = CHANEL TO SEND MARKS   
   '''

## As for now:
 - IduFreeRooms.py <-- is uset to generate website with available rooms
 - IDUAutoConfirm.py <-- confirms anouncements (is called by IduFreeRooms when needed)
 - MessageConfirm.py <-- sends unread messages
 - OgloszenieConfirm.py <-- sends unread informations

## To-do:
 - [ ] send mark and revievs
 - [ ] send subject announcements
