# -*- coding: utf-8 -*-

from settings import *
from Bot import Bot
from threading import Thread, Lock
from datetime import datetime
from callbacks import recv_list_rooms
from ids import FALSE_IDS
from utils import log
import logging, time, json, random
logging.basicConfig()


def main():

   threads = []
   bot_id = 0
   tracked_rooms = {}
   used_ids = set()

   def kill_thread(roomid):
      room_infos = tracked_rooms[roomid]
      bot_userid = room_infos['userid']
      room_bot = room_infos['bot']
      # Kill bot and remove used_ids, tracked_rooms
      room_bot.kill()
      threads.remove(room_bot)
      used_ids.remove(bot_userid)
      del tracked_rooms[roomid]

   # Keep the main thread alive.
   try:
      while True:
         try:

            bot = Bot('Bot MAIN', AUTH, USERID, None)
            bot.room_now()
            bot.ws.recv()
            bot.user_authenticate()
            bot.ws.recv()


            ok = False
            skip = 0
            data = {'rooms':[]}
            ids = []
            while not ok:
               bot.room_list_rooms(skip)
               d = bot.ws.recv()
               d = json.loads(d[d.index('{'):])

               if not d.get('rooms', False):
                  time.sleep(1)
                  continue

               for r in d['rooms']:
                  ids.append(r[0].get('roomid', None))
                  data['rooms'].append(r)

               ll = d['rooms'][len(d['rooms'])-1]
               lll = ll[0]['metadata']['listeners']
               if lll >= MIN_USERS:
                  skip += len(d['rooms'])-1
               else:
                  ok = True
            
            bot.ws.close()

            rooms = data['rooms'][:15]

            for rid in ROOM_EXCEPT:
               if rid not in ids:
                  rooms.append([{'roomid':rid, 'name':'ROOM PRIVILEGE!', 'metadata': {'listeners':-1}}])


            # Ici on check tous les rooms connu du serveur (limit 50)
            # TODO: Check threads that already exists... They may be not in that list.
            tmp_rooms = []
            for room in rooms:
               
               roomid = room[0]['roomid']
               room_name = room[0].get('name', None)
               listeners = room[0]['metadata'].get('listeners', 0)

               # We track only rooms with 10 listeners and more
               if listeners >= MIN_USERS or roomid in ROOM_EXCEPT:
                  tmp_rooms.append(roomid)

               # Is the room already tracked ?
               if roomid in tracked_rooms:
                  if listeners < MIN_USERS and roomid not in ROOM_EXCEPT:
                     # Get infos for the room.
                     room_infos = tracked_rooms[roomid]
                     bot_userid = room_infos['userid']
                     room_bot = room_infos['bot']
                     # Kill bot and remove used_ids, tracked_rooms
                     room_bot.kill()
                     threads.remove(room_bot)
                     used_ids.remove(bot_userid)
                     del tracked_rooms[roomid]


               # The room isn't tracked
               else:

                  if listeners >= MIN_USERS or roomid in ROOM_EXCEPT:

                     # Find a userid/auth for the new bot.
                     find = False
                     while not find:
                        userid, auth = random.choice(FALSE_IDS)
                        if userid not in used_ids:
                           find = True

                     print "Thread %s Start" % bot_id
                     bot = Bot('Bot %s' % bot_id, auth, userid, roomid)
                     bot.room_name = room_name
                     bot.deamon = True
                     
                     threads.append(bot)
                     used_ids.add(userid)
                     tracked_rooms[roomid] = {'userid':userid, 'bot':bot}

                     bot.start()
                     bot_id += 1
               



            # Ensure that all threads receive activities.
            for thread in threads:

               print "THREAD [%s] GETTIME" % thread.__str__().encode('utf-8')
               thread.room_now()

               # Verifie that all threads are on the previous room list.
               if thread.roomid not in tmp_rooms:
                  room_infos = tracked_rooms[thread.roomid]
                  bot_userid = room_infos['userid']
                  room_bot = room_infos['bot']
                  # Kill bot and remove used_ids, tracked_rooms
                  room_bot.kill()
                  threads.remove(room_bot)
                  used_ids.remove(bot_userid)
                  del tracked_rooms[thread.roomid]


               delta_activity = datetime.now() - thread.last_activity
               delta_heartbeat = datetime.now() - thread.last_heartbeat

               # If there is no activity and heartbeat since 10min.
               if delta_activity.seconds > 60 * 10 and delta_heartbeat.seconds > 60 * 10:
                  log(thread, 'No activity (%ss) and no heartbeat (%ss)' % (delta_activity.seconds, delta_heartbeat.seconds), {'log':True})

                  # Procedure to kill the thread.
                  room_infos = tracked_rooms[thread.roomid]
                  bot_userid = room_infos['userid']
                  room_bot = room_infos['bot']
                  # Kill bot and remove used_ids, tracked_rooms
                  room_bot.kill()
                  threads.remove(room_bot)
                  used_ids.remove(bot_userid)
                  del tracked_rooms[thread.roomid]

            # Sleep for another minute
            time.sleep(SLEEP_TIME)

         except Exception, e:
            with open('%s/fatal.log' % LOG_PATH, 'a') as f:
               f.write("EXCEPTION: [%s] %s\n" % (datetime.now(), e))

            print e
            continue

   except Exception, e:
      print e
      

   # Kill all threads
   for thread in threads:
      thread.kill()

   # Wait threads to join
   for thread in threads:
      thread.join()


if __name__ == '__main__':
   main()
