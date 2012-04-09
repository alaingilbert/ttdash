from settings import *
from Bot import Bot
from ids import FALSE_IDS
import logging, time, json, random
logging.basicConfig()

i = 0
for (u,a) in FALSE_IDS:
   i += 1
   bot = Bot('Bot MAIN', a, u, None)
   bot.room_now()
   bot.ws.recv()
   bot.user_authenticate()
   bot.ws.recv()
   bot.user_modify_name('ttdashboard_%s' % i)
   print bot.ws.recv()
   del bot
