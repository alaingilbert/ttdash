# -*- coding: utf-8 -*-

import MySQLdb as mdb

cnx =  mdb.connect('localhost', 'root', '', 'ttbot');
cursor = cnx.cursor()
cursor.execute('SET NAMES utf8;')
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')

cursor.execute("SELECT id FROM users")
rows = cursor.fetchall()
for row in rows:
   cursor.execute(" \
   INSERT INTO users_songs_liked \
   (user_id, song_id, nb_awesomes, nb_lames) \
   select \
      v.userid AS user_id, \
      s.id AS song_id, \
      sum(v.appreciate = 'up') AS nb_awesomes, \
      sum(v.appreciate = 'down') AS nb_lames \
   FROM ttbot.votes AS v \
   LEFT JOIN ttbot.songs AS s \
      ON s.id = v.songid \
   WHERE v.userid = %s \
   GROUP BY v.songid \
                 " % row[0])
   cnx.commit()
cursor.close()
