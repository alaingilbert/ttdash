from Bot import Bot
import sys, logging, json
logging.basicConfig()


def main():
   auth = sys.argv[1]
   ttuid = sys.argv[2]

   bot = Bot('Bot Import', auth, ttuid, None)
   bot.playlist_all()
   data = bot.ws.recv()
   data = json.loads(data[data.index('{'):])

   print json.dumps(data)


if __name__ == '__main__':
   main()
