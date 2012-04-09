# -*- coding: utf-8 -*-

import MySQLdb as mdb
from datetime import datetime
import inspect

class Database():
   def __init__(self, host='localhost', user='root', pasw='', db=''):
      self.host = host
      self.user = user
      self.pasw = pasw
      self.db = db
      self.cnx = mdb.connect(self.host, self.user, self.pasw, self.db)
      self.cnx.set_character_set('utf8')


   def __del__(self):
      self.cnx.close()


   def register_chat(self, userid, name, text, created, roomid):
      cursor = self.cnx.cursor(mdb.cursors.DictCursor)
      cursor.execute('SET NAMES utf8;')
      cursor.execute('SET CHARACTER SET utf8;')
      cursor.execute('SET character_set_connection=utf8;')

      cursor.execute("INSERT INTO chatlog (userid, roomid, name, text, created) \
                      VALUES ('%s', '%s', '%s', '%s', '%s')" % \
                      (
                        int(userid),
                        int(roomid),
                        mdb.escape_string(name.encode('utf-8')),
                        mdb.escape_string(text.encode('utf-8')),
                        created,
                      )
                    )
      self.cnx.commit()
      cursor.close()


   def register_room_stat(self, room_id, listeners, djcount, current_dj, created):
      cursor = self.cnx.cursor(mdb.cursors.DictCursor)
      cursor.execute('SET NAMES utf8;')
      cursor.execute('SET CHARACTER SET utf8;')
      cursor.execute('SET character_set_connection=utf8;')

      cursor.execute("INSERT INTO room_stats (roomid, listeners, djcount, current_dj, created) \
                      VALUES ('%s', '%s', '%s', '%s', '%s')" % \
                      (
                        int(room_id),
                        int(listeners),
                        int(djcount),
                        int(current_dj),
                        created,
                      )
                    )
      self.cnx.commit()
      cursor.close()


   def register_song_log(self, room_id, song_id, starttime, downvotes, upvotes, current_dj=None, override=True):
      try:
         cursor = self.cnx.cursor(mdb.cursors.DictCursor)
         cursor.execute('SET NAMES utf8;')
         cursor.execute('SET CHARACTER SET utf8;')
         cursor.execute('SET character_set_connection=utf8;')

         cursor.execute("SELECT * FROM songlog \
                        WHERE roomid='%s' AND songid='%s' AND starttime='%s'" % \
                         (
                           int(room_id),
                           int(song_id),
                           starttime,
                         )
                       )
         songlog_exists = int(cursor.rowcount)
         if not songlog_exists > 0:
            cursor.execute("INSERT INTO songlog (roomid, songid, starttime, downvotes, upvotes, current_dj) \
                            VALUES ('%s', '%s', '%s', '%s', '%s', %s)" % \
                            (
                              int(room_id),
                              int(song_id),
                              starttime,
                              int(downvotes),
                              int(upvotes),
                              "%s" % ("'%s'" % (int(current_dj)) if current_dj != None else "NULL"),
                            )
                          )
            cursor.execute("UPDATE songs SET nb_play=nb_play+1 WHERE id='%s'" % int(song_id))
            self.cnx.commit()
         else:
            if override:
               cursor.execute("UPDATE songlog SET downvotes='%s', upvotes='%s' \
                               WHERE roomid='%s' AND songid='%s' AND starttime='%s'" %
                               (
                                 int(downvotes),
                                 int(upvotes),
                                 int(room_id),
                                 int(song_id),
                                 starttime,
                               )
                             )
            self.cnx.commit()
         cursor.close()
      except Exception, e:
         f, file, line, fn_name, lines, n = inspect.trace()[-1]
         log(sender, e, {'log':True, 'file':file, 'line':line, 'command':'DB REGISTER_SONG_LOG'})


   def register_song(self, songid, album, artist, coverart, song, length, mnid, genre, filepath, bitrate, nb_play):
      cursor = self.cnx.cursor(mdb.cursors.DictCursor)
      cursor.execute('SET NAMES utf8;')
      cursor.execute('SET CHARACTER SET utf8;')
      cursor.execute('SET character_set_connection=utf8;')

      cursor.execute("SELECT * FROM songs WHERE songid = '%s'" % \
         mdb.escape_string(songid.encode('utf-8')))
      song_exists = int(cursor.rowcount)
      if not song_exists > 0:
         cursor.execute("INSERT INTO songs (songid, album, artist, coverart, song, length, mnid, genre, filepath, bitrate, nb_play) \
                         VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
                         (
                           mdb.escape_string(songid.encode('utf-8')),
                           mdb.escape_string(album.encode('utf-8')),
                           mdb.escape_string(artist.encode('utf-8')),
                           mdb.escape_string(coverart.encode('utf-8')),
                           mdb.escape_string(song.encode('utf-8')),
                           int(length),
                           int(mnid),
                           mdb.escape_string(genre.encode('utf-8')),
                           mdb.escape_string(filepath.encode('utf-8')),
                           int(bitrate),
                           int(nb_play),
                         )
                       )
         self.cnx.commit()
         db_song_id = cursor.lastrowid
      else:
         db_song_id = cursor.fetchone()['id']

      cursor.close()
      return db_song_id


   def register_user(self, userid, fbid, name, laptop, acl, fans, points, avatarid):
      cursor = self.cnx.cursor(mdb.cursors.DictCursor)
      cursor.execute('SET NAMES utf8;')
      cursor.execute('SET CHARACTER SET utf8;')
      cursor.execute('SET character_set_connection=utf8;')


      if fans == None: fans = 0
      if points == None: points = 0
      fans = int(fans)
      points = int(points)
      if fans < 0: fans = 0
      if points < 0: points = 0


      cursor.execute("SELECT * FROM users WHERE userid = '%s'" % mdb.escape_string(userid.encode('utf-8')))
      user_exists = int(cursor.rowcount)
      if not user_exists > 0:
         if userid != None:
            cursor.execute("INSERT INTO users (userid, fbid, name, laptop, acl, fans, points, avatarid) \
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)" % \
                            (
                              "%s" % ("'%s'" % (mdb.escape_string(userid.encode('utf-8'))) if userid != None else "NULL"),
                              "%s" % ("'%s'" % (mdb.escape_string(fbid.encode('utf-8'))) if fbid != None else "NULL"),
                              "%s" % ("'%s'" % (mdb.escape_string(name.encode('utf-8'))) if name != None else "NULL"),
                              "%s" % ("'%s'" % (mdb.escape_string(laptop.encode('utf-8'))) if laptop != None else "NULL"),
                              "%s" % ("'%s'" % (int(acl)) if acl != None else "NULL"),
                              "%s" % ("'%s'" % (int(fans)) if fans != None else "NULL"),
                              "%s" % ("'%s'" % (int(points)) if points != None else "NULL"),
                              "%s" % ("'%s'" % (int(avatarid)) if avatarid != None else "NULL"),
                            )
                          )
            self.cnx.commit()
            db_user_id = cursor.lastrowid
      
      else:
         user = cursor.fetchone()
         cursor.execute("UPDATE users SET name=%s, laptop=%s, acl=%s, \
                           fans=%s, points=%s, avatarid=%s \
                         WHERE userid='%s'" % \
                         (
                           "%s" % ("'%s'" % (mdb.escape_string(name.encode('utf-8'))) if name != None else "NULL"),
                           "%s" % ("'%s'" % (mdb.escape_string(laptop.encode('utf-8'))) if laptop != None else "NULL"),
                           "%s" % ("'%s'" % (int(acl)) if acl != None else "NULL"),
                           "%s" % ("'%s'" % (int(fans)) if fans != None else "NULL"),
                           "%s" % ("'%s'" % (int(points)) if points != None else "NULL"),
                           "%s" % ("'%s'" % (int(avatarid)) if avatarid != None else "NULL"),
                           mdb.escape_string(user['userid']),
                         )
                       )
         self.cnx.commit()
         db_user_id = user['id']
      
      cursor.close()
      return db_user_id


   def get_song_id(self, songid):
      cursor = self.cnx.cursor(mdb.cursors.DictCursor)
      cursor.execute('SET NAMES utf8;')
      cursor.execute('SET CHARACTER SET utf8;')
      cursor.execute('SET character_set_connection=utf8;')

      cursor.execute("SELECT * FROM songs WHERE songid='%s'" % \
         mdb.escape_string(songid.encode('utf-8')))
      song_exists = int(cursor.rowcount)
      if song_exists > 0:
         db_song_id = cursor.fetchone()['id']
      else:
         cursor.close()
         raise Exception('song id does not exists.')
      cursor.close()
      return db_song_id


   def get_room_id(self, roomid):
      cursor = self.cnx.cursor(mdb.cursors.DictCursor)
      cursor.execute('SET NAMES utf8;')
      cursor.execute('SET CHARACTER SET utf8;')
      cursor.execute('SET character_set_connection=utf8;')

      cursor.execute("SELECT * FROM rooms WHERE roomid='%s' LIMIT 1" % \
         mdb.escape_string(roomid.encode('utf-8')))
      room_exists = int(cursor.rowcount)
      if room_exists > 0:
         db_room_id = cursor.fetchone()['id']
      else:
         cursor.close()
         raise Exception('Room id does not exists. %s' % roomid)
      cursor.close()
      return db_room_id
   
   
   def get_user_id(self, userid):
      if userid == None:
         raise Exception('User id does not exists 1. %s' % userid)
      cursor = self.cnx.cursor(mdb.cursors.DictCursor)
      cursor.execute('SET NAMES utf8;')
      cursor.execute('SET CHARACTER SET utf8;')
      cursor.execute('SET character_set_connection=utf8;')

      cursor.execute("SELECT * FROM users WHERE userid='%s' LIMIT 1" % \
         mdb.escape_string(userid.encode('utf-8')))
      user_exists = int(cursor.rowcount)
      if user_exists > 0:
         db_user_id = cursor.fetchone()['id']
      else:
         cursor.close()
         raise Exception('User id does not exists 2. %s' % userid)
      cursor.close()
      return db_user_id


   def update_room(self, roomid, listeners, upvotes, downvotes):
      try:
         cursor = self.cnx.cursor(mdb.cursors.DictCursor)
         cursor.execute('SET NAMES utf8;')
         cursor.execute('SET CHARACTER SET utf8;')
         cursor.execute('SET character_set_connection=utf8;')

         cursor.execute("SELECT * FROM rooms WHERE roomid = '%s' LIMIT 1" % \
                         mdb.escape_string(roomid.encode('utf-8')))
         room_exists = int(cursor.rowcount)
         if room_exists > 0:
            db_room_id = cursor.fetchone()['id']
            cursor.execute("UPDATE rooms SET \
                                             listeners=%s, \
                                             downvotes=%s, \
                                             upvotes=%s \
                            WHERE id='%s'" %
                            (
                              "%s" % ("'%s'" % (int(listeners)) if listeners != None else "NULL"),
                              "%s" % ("'%s'" % (int(downvotes)) if downvotes != None else "0"),
                              "%s" % ("'%s'" % (int(upvotes)) if upvotes != None else "0"),
                              int(db_room_id),
                            ))
         else:
            cursor.close()
            raise Exception('Room id does not exists. (update_room)')
         cursor.close()
         return db_room_id
      except Exception, e:
         f, file, line, fn_name, lines, n = inspect.trace()[-1]
         log(sender, e, {'log':True, 'file':file, 'line':line, 'command':'DB UPDATE_ROOM'})


   def register_room(self, roomid, name, created, description, shortcut, \
                     current_dj=None, listeners=None, downvotes=0, upvotes=0, song_starttime=None, song_id=None):
      cursor = self.cnx.cursor(mdb.cursors.DictCursor)
      cursor.execute('SET NAMES utf8;')
      cursor.execute('SET CHARACTER SET utf8;')
      cursor.execute('SET character_set_connection=utf8;')

      cursor.execute("SELECT * FROM rooms WHERE roomid = '%s' LIMIT 1" % \
                      mdb.escape_string(roomid.encode('utf-8')))
      room_exists = int(cursor.rowcount)
      if not room_exists > 0:
         cursor.execute("INSERT INTO rooms (roomid, name, created, description, shortcut, \
                           current_dj, listeners, downvotes, upvotes, song_starttime, current_song, modified) \
                         VALUES ('%s', '%s', '%s', '%s', '%s', %s, %s, %s, %s, %s, %s, '%s')" % \
                         (
                           mdb.escape_string(roomid.encode('utf-8')),
                           mdb.escape_string(name.encode('utf-8')),
                           created,
                           mdb.escape_string(description.encode('utf-8')),
                           mdb.escape_string(shortcut.encode('utf-8')),
                           "%s" % ("'%s'" % (int(current_dj)) if current_dj != None else "NULL"),
                           "%s" % ("'%s'" % (int(listeners)) if listeners != None else "NULL"),
                           "%s" % ("'%s'" % (int(downvotes)) if downvotes != None else "0"),
                           "%s" % ("'%s'" % (int(upvotes)) if upvotes != None else "0"),
                           "%s" % ("'%s'" % song_starttime if song_starttime != None else "NULL"),
                           "%s" % ("'%s'" % song_id if song_id != None else "NULL"),
                           datetime.now(),
                         )
                       )
         self.cnx.commit()
         db_room_id = cursor.lastrowid
      else:
         db_room_id = cursor.fetchone()['id']
         cursor.execute("UPDATE rooms SET current_dj=%s, \
                                          listeners=%s, \
                                          downvotes=%s, \
                                          upvotes=%s, \
                                          song_starttime=%s, \
                                          current_song=%s, \
                                          modified='%s' \
                         WHERE id='%s'" %
                         (
                           "%s" % ("'%s'" % (int(current_dj)) if current_dj != None else "NULL"),
                           "%s" % ("'%s'" % (int(listeners)) if listeners != None else "NULL"),
                           "%s" % ("'%s'" % (int(downvotes)) if downvotes != None else "0"),
                           "%s" % ("'%s'" % (int(upvotes)) if upvotes != None else "0"),
                           "%s" % ("'%s'" % song_starttime if song_starttime != None else "NULL"),
                           "%s" % ("'%s'" % song_id if song_id != None else "NULL"),
                           datetime.now(),
                           int(db_room_id),
                         ))
      
      cursor.close()
      return db_room_id


   def register_vote(self, user_id, song_id, starttime, room_id, created, appreciate):
      try:
         cursor = self.cnx.cursor(mdb.cursors.DictCursor)
         cursor.execute('SET NAMES utf8;')
         cursor.execute('SET CHARACTER SET utf8;')
         cursor.execute('SET character_set_connection=utf8;')



         if appreciate == 'up':
            cursor.execute("INSERT INTO users_songs_liked (user_id, song_id, nb_awesomes, nb_lames, modified) \
                            VALUES ('%s', '%s', '1', '0', NOW()) ON DUPLICATE KEY UPDATE nb_awesomes=nb_awesomes+1, modified='%s'" % \
                            ( int(user_id),
                              int(song_id),
                              datetime.now(),
                            )
                          )
            self.cnx.commit()
         elif appreciate == 'down':
            cursor.execute("INSERT INTO users_songs_liked (user_id, song_id, nb_awesomes, nb_lames, modified) \
                            VALUES ('%s', '%s', '0', '1', NOW()) ON DUPLICATE KEY UPDATE nb_lames=nb_lames+1, modified='%s'" % \
                            ( int(user_id),
                              int(song_id),
                              datetime.now(),
                            )
                          )
            self.cnx.commit()




         cursor.execute("SELECT * FROM votes \
                        WHERE userid='%s' AND songid='%s' AND starttime='%s'" % \
                         (
                           int(user_id),
                           int(song_id),
                           starttime,
                         )
                       )
         songlog_exists = int(cursor.rowcount)
         if not songlog_exists > 0:
            cursor.execute("INSERT INTO votes (userid, songid, starttime, roomid, created, appreciate) \
                            VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % \
                            (
                              int(user_id),
                              int(song_id),
                              starttime,
                              int(room_id),
                              created,
                              mdb.escape_string(appreciate.encode('utf-8')),
                            )
                          )
            self.cnx.commit()
         else:
            cursor.execute("UPDATE votes SET appreciate='%s', created='%s' \
                            WHERE userid='%s' AND songid='%s' AND starttime='%s'" %
                            (
                              mdb.escape_string(appreciate.encode('utf-8')),
                              created,
                              int(user_id),
                              int(song_id),
                              starttime,
                            )
                          )
            self.cnx.commit()
         cursor.close()
      except Exception, e:
         f, file, line, fn_name, lines, n = inspect.trace()[-1]
         log(sender, e, {'log':True, 'file':file, 'line':line, 'command':'DB REGISTER_VOTE'})
