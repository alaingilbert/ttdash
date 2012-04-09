# -*- coding: utf-8 -*-

# TODO: Really need to do something like transaction for the new votes.
# See why my bots are killed after 20min.

from datetime import datetime
from utils import log
from types import *
import inspect

def on_message(sender, data):
   command = data.get('command', '')
   if command == 'registered':
      for user in data['user']:
         try:
            userid   = user['userid']
            fbid     = user.get('fbid', None)
            name     = user['name']
            laptop   = user['laptop']
            acl      = user['acl']
            fans     = user['fans']
            points   = user['points']
            avatarid = user['avatarid']
            sender.db.register_user(userid, fbid, name, laptop, acl, fans, points, \
                             avatarid)
         except Exception, e:
            f, file, line, fn_name, lines, n = inspect.trace()[-1]
            log(sender, e, {'log':True, 'file':file, 'line':line, 'data':user, 'command':command})

   elif command == 'speak':
      pass
      #try:
      #   userid   = data['userid']
      #   name     = data['name']
      #   text     = data['text']
      #   date     = datetime.now()
      #   roomid   = sender.roomid
      #   db_room_id = sender.db.get_room_id(roomid)
      #   db_user_id = sender.db.get_user_id(userid)

      #   sender.db.register_chat(db_user_id, name, text, date, db_room_id)
      #except Exception, e:
      #   f, file, line, fn_name, lines, n = inspect.trace()[-1]
      #   log(sender, e, {'log':True, 'file':file, 'line':line, 'command':command})

   elif command == 'deregistered':
      for user in data['user']:
         try:
            userid   = user['userid']
            fbid     = user.get('fbid', None)
            name     = user['name']
            laptop   = user['laptop']
            acl      = user['acl']
            fans     = user['fans']
            points   = user['points']
            avatarid = user['avatarid']
            sender.db.register_user(userid, fbid, name, laptop, acl, fans, points, \
                             avatarid)
         except Exception, e:
            f, file, line, fn_name, lines, n = inspect.trace()[-1]
            log(sender, e, {'log':True, 'file':file, 'line':line, 'data':user, 'command':command})

   elif command == 'newsong':
      log(sender, 'NEW SONG')
      try:
         song = data['room']['metadata']['current_song']
         songid      = song['_id']
         album       = song['metadata'].get('album', '')
         artist      = song['metadata'].get('artist', '')
         coverart    = song['metadata'].get('coverart', '')
         song_name   = song['metadata'].get('song', '')
         length      = song['metadata'].get('length', 0)
         mnid        = song['metadata'].get('mnid', 0)
         genre       = song['metadata'].get('genre', '')
         filepath    = song['metadata'].get('filepath', '')
         bitrate     = song['metadata'].get('bitrate', 0)
         current_dj  = data['room']['metadata']['current_dj']
         db_current_dj = sender.db.get_user_id(current_dj)
         listeners   = data['room']['metadata']['listeners']
         djcount     = data['room']['metadata']['djcount']
         starttime   = datetime.fromtimestamp(song['starttime'])

         roomid         = data['room']['roomid']
         name           = data['room']['name']
         created        = datetime.fromtimestamp(data['room']['created'])
         description    = data['room'].get('description', '')
         shortcut       = data['room']['shortcut']
         current_dj     = data['room']['metadata'].get('current_dj', None)
         db_current_dj  = sender.db.get_user_id(current_dj)
         listeners      = data['room']['metadata'].get('listeners', None)
         downvotes      = data['room']['metadata'].get('downvotes', 0)
         upvotes        = data['room']['metadata'].get('upvotes', 0)
         starttime      = data['room']['metadata']['current_song'].get('starttime', None)
         if starttime != None : starttime = datetime.fromtimestamp(starttime)

         sender.current_song['id'] = songid
         sender.current_song['starttime'] = starttime
         sender.current_song['current_dj'] = current_dj

         # Create/update song
         db_song_id = sender.db.register_song(songid, album, artist, coverart, \
                                       song_name, length, mnid, genre, \
                                       filepath, bitrate, 0)
         db_room_id = sender.db.get_room_id(roomid)

         # Create song log
         sender.db.register_song_log(db_room_id, db_song_id, starttime, 0, 0, db_current_dj)

         # Create room stat
         sender.db.register_room_stat(db_room_id, listeners, djcount, db_current_dj, starttime)

         # Create/update Room
         db_room_id = sender.db.register_room(roomid, name, created, description, shortcut, \
                                              db_current_dj, listeners, downvotes, upvotes, starttime, db_song_id)
      except Exception, e:
         f, file, line, fn_name, lines, n = inspect.trace()[-1]
         log(sender, e, {'log':True, 'file':file, 'line':line, 'command':command})


   elif command == 'update_votes':
      log(sender, 'UPDATES VOTES')
      try:
         listeners            = data['room']['metadata'].get('listeners', 0)
         downvotes            = data['room']['metadata'].get('downvotes', 0)
         upvotes              = data['room']['metadata'].get('upvotes', 0)
         db_song_id           = sender.db.get_song_id(sender.current_song['id'])
         db_current_dj_id     = sender.db.get_user_id(sender.current_song['current_dj'])
         db_room_id           = sender.db.get_room_id(sender.roomid)

         # Update room infos.
         db_room_id = sender.db.update_room(sender.roomid, listeners, upvotes, downvotes)

         # Create/Update song log.
         sender.db.register_song_log(db_room_id, db_song_id, sender.current_song['starttime'], downvotes, upvotes, db_current_dj_id)

         # Create/Update Votes
         votelog = data['room']['metadata'].get('votelog', None)
         if votelog != None:
            for vote in votelog:
               try:
                  db_user_id = sender.db.get_user_id(vote[0])
               except Exception, e:
                  db_user_id = sender.db.register_user(vote[0], fbid=None, name=None, laptop=None, acl=None, fans=None, points=None, avatarid=None)
               appreciate = vote[1]
               sender.db.register_vote(db_user_id, db_song_id, sender.current_song['starttime'], db_room_id, datetime.now(), appreciate)
      except Exception, e:
         f, file, line, fn_name, lines, n = inspect.trace()[-1]
         log(sender, e, {'log':True, 'file':file, 'line':line, 'command':command})


   elif command == 'booted_user':
      # If the bot get booted. Reconect to the room.
      if data['userid'] == sender.userid:
         sender.room_register(sender.roomid)
         log(sender, data, {'log':True, 'comamnd':command})


   else:
      if data.get('command', False):
         log(sender, 'Command: %s' % command)
      elif type(data.get('msgid', False)) == IntType:
         if not data.get('success', False):
            if data.get('err', '') == 'user not in room':
               sender.room_register(sender.roomid)
            else:
               log(sender, 'Msgid: %s' % data)
      else:
         log(sender, data)


def recv_room_info(sender, data):
   try:
      log(sender, 'RECV ROOM INFO')

      roomid         = data['room']['roomid']
      name           = data['room']['name']
      created        = datetime.fromtimestamp(data['room']['created'])
      description    = data['room'].get('description', '')
      shortcut       = data['room']['shortcut']
      current_dj     = data['room']['metadata'].get('current_dj', None)
      try:
         db_current_dj  = sender.db.get_user_id(current_dj)
      except Exception, e:
         db_current_dj = None
      listeners      = data['room']['metadata'].get('listeners', None)
      downvotes      = data['room']['metadata'].get('downvotes', 0)
      upvotes        = data['room']['metadata'].get('upvotes', 0)
      current_song   = data['room']['metadata'].get('current_song', None)
      starttime      = None
      if current_song != None:
         starttime   = current_song.get('starttime', None)
      if starttime != None : starttime = datetime.fromtimestamp(starttime)

      sender.current_song['id'] = current_song.get('_id', None)
      sender.current_song['starttime'] = starttime
      sender.current_song['current_dj'] = current_dj

      db_room_id = sender.db.register_room(roomid, name, created, description, shortcut, \
                                           db_current_dj, listeners, downvotes, upvotes, starttime, song_id=None)

      for user in data['users']:
         try:
            userid   = user['userid']
            fbid     = user.get('fbid', None)
            name     = user['name']
            laptop   = user['laptop']
            acl      = user['acl']
            fans     = user['fans']
            points   = user['points']
            avatarid = user['avatarid']
            sender.db.register_user(userid, fbid, name, laptop, acl, fans, points, \
                             avatarid)
         except Exception, e:
            f, file, line, fn_name, lines, n = inspect.trace()[-1]
            log(sender, e, {'log':True, 'file':file, 'line':line, 'command':'RECV_ROOM_INFO 1'})

      for song in data['room']['metadata']['songlog']:
         try:
            songid      = song['_id']
            album       = song['metadata'].get('album', '')
            artist      = song['metadata'].get('artist', '')
            coverart    = song['metadata'].get('coverart', '')
            song_name   = song['metadata'].get('song', '')
            length      = song['metadata'].get('length', 0)
            mnid        = song['metadata'].get('mnid', 0)
            genre       = song['metadata'].get('genre', '')
            filepath    = song['metadata'].get('filepath', '')
            bitrate     = song['metadata'].get('bitrate', 0)
            db_song_id = sender.db.register_song(songid, album, artist, coverart, \
                                          song_name, length, mnid, genre, \
                                          filepath, bitrate, 0)

            starttime   = datetime.fromtimestamp(song['starttime'])
            sender.db.register_song_log(db_room_id, db_song_id, starttime, 0, 0, None, False)
         except Exception, e:
            f, file, line, fn_name, lines, n = inspect.trace()[-1]
            log(sender, e, {'log':True, 'file':file, 'line':line, 'command':'RECV_ROOM_INFO 2'})

      if current_song != None:
         db_song_id     = sender.db.get_song_id(current_song.get('_id', None))
      else:
         db_song_id = None
      sender.db.register_room(roomid, name, created, description, shortcut, \
                              db_current_dj, listeners, downvotes, upvotes, starttime, db_song_id)
   except Exception, e:
      f, file, line, fn_name, lines, n = inspect.trace()[-1]
      log(sender, e, {'log':True, 'file':file, 'line':line, 'command':'RECV_ROOM_INFO 3'})


def recv_list_rooms(sender, data):
   i = 0 
   for room in data['rooms']:
      if room[0]['metadata']['listeners'] > 10: 
         i += 1
         print room[0]['roomid']
   print i
