from Bot import Bot
import sys, logging, json
logging.basicConfig()


def main():
   auth = sys.argv[1]
   ttuid = sys.argv[2]

   bot = Bot('Bot Export', auth, ttuid, None)
   bot.playlist_all()
   data = bot.ws.recv()
   data = json.loads(data[data.index('{'):])

   # Remove all songs in my current playlist.
   playlist = data['list']
   for s in playlist:
      bot.playlist_remove('default', 0)
      bot.ws.recv()

   for song in sys.argv[3:]:
      bot.playlist_add('default', song)
      bot.ws.recv()

   print 'true'

if __name__ == '__main__':
   main()

