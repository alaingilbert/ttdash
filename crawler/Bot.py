# -*- coding: utf-8 -*-

from settings import *
from Http import Http
from websocket import create_connection
from hashlib import sha1
from threading import Thread
from database import Database
from callbacks import recv_room_info, recv_list_rooms, on_message
from utils import log
from datetime import datetime
import re, cookielib, time, json, inspect, random


class Bot(Thread):
   def __init__(self, name, auth, userid, roomid=None):

      Thread.__init__(self)

      self.name = name
      self.room_name = ''
      self.http = Http()
      self.db = Database(DB_HOST, DB_USER, DB_PASW, DB_DB)

      self.last_heartbeat = datetime.now()
      self.last_activity = datetime.now()

      self._killed = False

      # Create cookies.
      ck = cookielib.Cookie(version=0, name='turntableUserAuth', value=auth,
                            port=None, port_specified=False,
                            domain='turntable.fm', domain_specified=False,
                            domain_initial_dot=False, path='/',
                            path_specified=True, secure=False, expires=None,
                            discard=True, comment=None, comment_url=None,
                            rest={'HttpOnly': None}, rfc2109=False)
      self.http.cj.set_cookie(ck)
      ck = cookielib.Cookie(version=0, name='turntableUserId', value=userid,
                            port=None, port_specified=False,
                            domain='turntable.fm', domain_specified=False,
                            domain_initial_dot=False, path='/',
                            path_specified=True, secure=False, expires=None,
                            discard=True, comment=None, comment_url=None,
                            rest={'HttpOnly': None}, rfc2109=False)
      self.http.cj.set_cookie(ck)
      ck = cookielib.Cookie(version=0, name='turntableUserNamed', value='true',
                            port=None, port_specified=False,
                            domain='turntable.fm', domain_specified=False,
                            domain_initial_dot=False, path='/',
                            path_specified=True, secure=False, expires=None,
                            discard=True, comment=None, comment_url=None,
                            rest={'HttpOnly': None}, rfc2109=False)
      self.http.cj.set_cookie(ck)

      test = int( time.time()*1000 )
      self.clientid = "%s-0.26004539988934994" % test
      self.auth = auth
      self.userid = userid
      self._msgid = 0
      self.roomid = roomid
      self.current_song = {'id':None, 'starttime':None, 'current_dj':None}
      self.cmds = []

      CHATSERVER_ADDRS = [("chat2.turntable.fm", 80), ("chat3.turntable.fm", 80)]
      if self.roomid != None:
         HOST, PORT = CHATSERVER_ADDRS[self._hash_mod(self.roomid, len(CHATSERVER_ADDRS))]
      else:
         HOST, PORT = CHATSERVER_ADDRS[len(CHATSERVER_ADDRS)-1]

      self.ws = create_connection(HOST, PORT, '/socket.io/websocket', False)
      self.ws.recv()


   def __str__(self):
      return (self.name+" ("+self.room_name[:20]+")").ljust(35)


   def do_work(self):
      self.room_now()
      self.user_authenticate()
      try:
         self.room_register(self.roomid)
      except Exception as e:
         print e
      self.room_info(self.roomid, recv_room_info)


   def kill(self):
      log(self, "GOT KILL")
      self._killed = True


   def run(self):
      t = Thread(target=self.do_work)
      t.deamon = True
      t.start()
      self.serve(on_message)
      t.join()


   def serve(self, callback):
      try:
         while not self._killed:
            try:
               data = self.ws.recv()
               # Answer the heartbeat
               is_heartbeat = re.match('~m~[0-9]+~m~(~h~[0-9]+)', data)
               if is_heartbeat:
                  self._heartbeat(is_heartbeat.group(1))
                  log(self, 'HB: %s' % is_heartbeat.group(1))
                  self.last_heartbeat = datetime.now()
                  continue

               self.last_activity = datetime.now()

               data = json.loads(data[data.index('{'):])
               for i in range(0, len(self.cmds)):
                  id, clb = self.cmds[i]
                  if id == data.get('msgid', None):
                     if clb:
                        clb(self, data)
                     del self.cmds[i]
                     break

               if callback:
                  callback(self, data)
            except Exception, e:
               if str(e) == 'Bad file descriptor':
                  self.kill()

               time.sleep(1)
               f, file, line, fn_name, lines, n = inspect.trace()[-1]
               log(self, e, {'log':True, 'file':file, 'line':line, 'command':'BOT SERVE'})
         self.ws.close()
      except KeyboardInterrupt, e:
         print e

   def _hash_mod(self, roomid, port_range=20):
      d = sha1(roomid).hexdigest();
      c = 0;
      for a in range(0, len(d)):
         c += ord(d[a]);
      return c % port_range;

   def _heartbeat(self, d):
      self._send_message(d)

   def vote(self):
      if self.current_song['id']:
         self.room_vote(self.roomid, self.current_song['id'])

   def _send_message(self, msg, callback=None):
      #print "> %s" % msg
      self.ws.send('~m~%s~m~%s' % (len(msg), msg))
      self.cmds.append((self._msgid, callback))
      self._msgid += 1

   def room_now(self, callback=None):
      rq = '{"api":"room.now","msgid":%s,"clientid":"%s"}' % (self._msgid, self.clientid)
      self._send_message(rq, callback)

   def room_list_rooms(self, skip=0, callback=None):
      rq = '{"api":"room.list_rooms","skip":%s,"msgid":%s,"clientid":"%s","userid":"%s","userauth":"%s"}' % (skip, self._msgid, self.clientid, self.userid, self.auth)
      self._send_message(rq, callback)

   def room_register(self, roomid, callback=None):
      rq = '{"api":"room.register","roomid":"%s","msgid":%s,"clientid":"%s","userid":"%s","userauth":"%s"}' % (roomid, self._msgid, self.clientid, self.userid, self.auth)
      self._send_message(rq, callback)

   def room_deregister(self, roomid, callback=None):
      rq = '{"api":"room.deregister","roomid":"%s","msgid":%s,"clientid":"%s","userid":"%s","userauth":"%s"}' % (roomid, self._msgid, self.clientid, self.userid, self.auth)
      self._send_message(rq, callback)

   def room_info(self, roomid, callback=None):
      rq = '{"api":"room.info","roomid":"%s","msgid":%s,"clientid":"%s","userid":"%s","userauth":"%s"}' % (roomid, self._msgid, self.clientid, self.userid, self.auth)
      self._send_message(rq, callback)

   def room_speak(self, roomid, msg, callback=None):
      rq = '{"api":"room.speak","roomid":"%s","text":"%s","msgid":%s,"clientid":"%s","userid":"%s","userauth":"%s"}' % (roomid, msg, self._msgid, self.clientid, self.userid, self.auth)
      self._send_message(rq, callback)

   def room_boot_user(self, roomid, userid, callback=None):
      rq = '{"api":"room.boot_user","roomid":"%s","target_userid":"%s","msgid":%s,"clientid":"%s","userid":"%s","userauth":"%s"}' % (roomid, userid, self._msgid, self.clientid, self.userid, self.auth)
      self._send_message(rq, callback)
      
   def room_add_dj(self, roomid, callback=None):
      rq = '{"api":"room.add_dj","roomid":"%s","msgid":%s,"clientid":"%s","userid":"%s","userauth":"%s"}' % (roomid, self._msgid, self.clientid, self.userid, self.auth)
      self._send_message(rq, callback)

   def room_rem_dj(self, roomid, callback=None):
      rq = '{"api":"room.rem_dj","roomid":"%s","msgid":%s,"clientid":"%s","userid":"%s","userauth":"%s"}' % (roomid, self._msgid, self.clientid, self.userid, self.auth)
      self._send_message(rq, callback)

   def room_stop_song(self, roomid, callback=None):
      rq = '{"api":"room.stop_song","roomid":"%s","msgid":%s,"clientid":"%s","userid":"%s","userauth":"%s"}' % (roomid, self._msgid, self.clientid, self.userid, self.auth)
      self._send_message(rq, callback)

   def room_vote(self, roomid, currentsong_id, callback=None):
      vh = sha1(roomid+'up'+currentsong_id).hexdigest();
      th = sha1(str(random.random())+'').hexdigest()
      ph = sha1(str(random.random())+'').hexdigest()
      rq = '{"api":"room.vote","roomid":"%s","val":"up","vh":"%s","th":"%s","ph":"%s","msgid":"%s","clientid":"%s","userid":"%s","userauth":"%s"}' % (roomid, vh, th, ph, self._msgid, self.clientid, self.userid, self.auth)
      self._send_message(rq, callback)

   def user_authenticate(self, callback=None):
      rq = '{"api":"user.authenticate","msgid":%s,"clientid":"%s","userid":"%s","userauth":"%s"}' % (self._msgid, self.clientid, self.userid, self.auth)
      self._send_message(rq, callback)

   def user_info(self, callback=None):
      rq = '{"api":"user.info","msgid":%s,"clientid":"%s","userid":"%s","userauth":"%s"}' % (self._msgid, self.clientid, self.userid, self.auth)
      self._send_message(rq, callback)

   def user_modify(self, laptop="mac", callback=None):
      rq = '{"api":"user.modify","laptop":"%s","msgid":%s,"clientid":"%s","userid":"%s","userauth":"%s"}' % (laptop, self._msgid, self.clientid, self.userid, self.auth)
      self._send_message(rq, callback)

   def user_modify_name(self, name, callback=None):
      rq = '{"api":"user.modify","name":"%s","msgid":%s,"clientid":"%s","userid":"%s","userauth":"%s"}' % (name, self._msgid, self.clientid, self.userid, self.auth)
      self._send_message(rq, callback)

   def user_set_avatar(self, avatarid, callback=None):
      rq = '{"api":"user.set_avatar","avatarid":%s,"msgid":%s,"clientid":"%s","userid":"%s","userauth":"%s"}' % (avatarid, self._msgid, self.clientid, self.userid, self.auth)
      self._send_message(rq, callback)

   def playlist_all(self, playlist_name='default', callback=None):
      rq = '{"api":"playlist.all","playlist_name":"%s","msgid":%s,"clientid":"%s","userid":"%s","userauth":"%s"}' % (playlist_name, self._msgid, self.clientid, self.userid, self.auth)
      self._send_message(rq, callback)

   def playlist_add(self, playlist_name, songid, callback=None):
      rq = '{"api":"playlist.add","playlist_name":"%s","song_dict":{"fileid":"%s"},"index":0,"msgid":%s,"clientid":"%s","userid":"%s","userauth":"%s"}' % (playlist_name, songid, self._msgid, self.clientid, self.userid, self.auth)
      self._send_message(rq, callback)

   def playlist_remove(self, playlist_name, index, callback=None):
      rq = '{"api":"playlist.remove","playlist_name":"%s","index":%s,"msgid":%s,"clientid":"%s","userid":"%s","userauth":"%s"}' % (playlist_name, index, self._msgid, self.clientid, self.userid, self.auth)
      self._send_message(rq, callback)

   def __del__(self):
      self.ws.close()
