# -*- coding: utf-8 -*-

from settings import LOG_PATH
from datetime import datetime

def log(sender, message, params={}):
   log = params.get('log', False)
   filename = params.get('filename', None)
   line = params.get('line', None)
   command = params.get('command', None)

   if command:
      print "(Command: %s)\n" % command

   if filename and line:
      print "[%s] [%s] %s:%s %s" % (datetime.now(), sender.__str__().encode('utf-8'), filename, line, message)
   else:
      print "[%s] [%s] %s" % (datetime.now(), sender.__str__().encode('utf-8'), message)

   if log:
       with open('%s/error.log' % LOG_PATH, 'a') as f:
          f.write("%s\n" % datetime.now())
          if filename and line:
             f.write("%s:%s" % (filename, line))
          if command:
             f.write(" [command: %s] " % command)
          f.write("EXCEPTION: [%s] %s\n" % (sender.__str__().encode('utf-8'), message))
