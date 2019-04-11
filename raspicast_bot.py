#!.venv/bin/python3

import telebot
from telebot import types
from telebot.types import Message, Update
import random, logging, sys, os, time, logging
# from tinydb import TinyDB, Query
import pexpect
import youtube_dl

logging.basicConfig(
    filename='RaspiCast.log',
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt='%m-%d %H:%M:%S',
    level=logging.DEBUG
)
logger = logging.getLogger("RaspberryCast")

URL = 't.me/raspicast_bot'
BOT_NAME = 'RaspicastBot'
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
keyfile = open(os.path.join(__location__, 'apiKey.txt'), "r")
TOKEN = keyfile.read().replace('\n', '')
STICKERS_APPROVED = [
    'CAADBAADQAADyIsGAAE7MpzFPFQX5QI',
    'CAADBAADGQADyIsGAAFl6KYZBflVyQI',
    'CAADBQADbgMAAukKyAN8NA8_2uwEbQI',
    'CAADBQADiQMAAukKyAPZH7wCI2BwFwI',
    'CAADBQADbwMAAukKyAOvzr7ZArpddAI',
    'CAADBQADrAMAAukKyAOwtKgu24enOwI',
    'CAADBQADpgMAAukKyAN5s5AIa4Wx9AI',
    'CAADBAAEAgAC4nLZAAE7R15Jpzl7cAI'
]
STICKERS_DONTKNOW = [
    'CAADBQADqgMAAukKyAOMMrddotAFYQI',
    'CAADBQADwwMAAukKyAPFFlt0dg1c3wI',
    'CAADBQADhAMAAukKyAPQ5EQgpjzLMwI',
    'CAADBQADnAMAAukKyAPo8e_mkstdpQI',
    'CAADBQADfgMAAukKyAMythx0wTDJDAI'
]

BOT_USERS_DB = 'bot_user_list.json' 
ADMIN_USER = ['maxtacu']
CURRENT_UNIX_DATE = int(time.time())

process = None
bot = telebot.TeleBot(TOKEN)
# db = TinyDB(BOT_USERS_DB)
# query = Query()

# telebot.logger.setLevel(logging.DEBUG)

@bot.message_handler(commands=['start'])
def handle_start(message: Message):
    if message.date <= CURRENT_UNIX_DATE:
        pass
    else:
        bot.reply_to(message, """Hi %s, what video would you like me to play?
        Use /help to check all my potential""" % message.from_user.first_name)
        markup = types.ReplyKeyboardMarkup(row_width=3)
        itembtn1 = types.KeyboardButton('/help')
        itembtn2 = types.KeyboardButton('video controls')
        itembtn3 = types.KeyboardButton('create a playlist')
        markup.add(itembtn1, itembtn2, itembtn3)
        bot.send_message(message.chat.id, "Choose the option:", reply_markup=markup)

@bot.message_handler(commands=['shutdown'])
def send_poweroff(message: Message):
    bot.reply_to(message, f"""{BOT_NAME} is going down for power-off. 
    To start it back please plug the power cable again""")
    shutdown()

@bot.message_handler(commands=['admin'])
def admin(message: Message):
    bot.reply_to(message, f"""{BOT_NAME} admin menu.""")
    admin_pannel(message)


@bot.message_handler(content_types=['text'])
def message(message: Message):
    user = message.from_user
    global process
    if message.date <= CURRENT_UNIX_DATE:
        pass
    else:
        if 'create a playlist' in message.text:
            bot.send_message(message.chat.id, "Sorry. This feature is under development and is not available now")
            return
        url = message.text
        if url.startswith('http'):
            bot.send_sticker(message.chat.id, random.choice(STICKERS_APPROVED))
            controls(message)
            launchvideo(url)
            return
        if 'video controls' in message.text:
            controls(message)
            return
        if '+ vol' in message.text:
            if process:
                process.send('+')
            else:
                bot.send_message(message.chat.id, f"""{BOT_NAME} is not playing anything now. 
                    Please send me a link to play something""")
                bot.send_sticker(message.chat.id, random.choice(STICKERS_DONTKNOW))
            return
        if '- vol' in message.text:
            if process:
                process.send('-')
            else:
                bot.send_message(message.chat.id, f"""{BOT_NAME} is not playing anything now. 
                    Please send me a link to play something""")
                bot.send_sticker(message.chat.id, random.choice(STICKERS_DONTKNOW))
            return
        if 'pause/resume' in message.text:
            if process:
                process.send('p')
            else:
                bot.send_message(message.chat.id, f"""{BOT_NAME} is not playing anything now. 
                    Please send me a link to play something""")
                bot.send_sticker(message.chat.id, random.choice(STICKERS_DONTKNOW))
            return
        if 'stop' in message.text:
            if process:
                process.send('q')
            else:
                bot.send_message(message.chat.id, f"""{BOT_NAME} is not playing anything now. 
                    Please send me a link to play something""")
                bot.send_sticker(message.chat.id, random.choice(STICKERS_DONTKNOW))
            return
        if '-30 seconds' in message.text:
            if process:
                process.send('\x1b[D')
            else:
                bot.send_message(message.chat.id, f"""{BOT_NAME} is not playing anything now. 
                    Please send me a link to play something""")
                bot.send_sticker(message.chat.id, random.choice(STICKERS_DONTKNOW))
            return
        if '+30 seconds' in message.text:
            if process:
                process.send('\x1b[C')
            else:
                bot.send_message(message.chat.id, f"""{BOT_NAME} is not playing anything now. 
                    Please send me a link to play something""")
                bot.send_sticker(message.chat.id, random.choice(STICKERS_DONTKNOW))
            return
        if 'fast forward' in message.text:
            if process:
                process.send('>')
            else:
                bot.send_message(message.chat.id, f"""{BOT_NAME} is not playing anything now. 
                    Please send me a link to play something""")
                bot.send_sticker(message.chat.id, random.choice(STICKERS_DONTKNOW))
            return
        if 'decrease speed' in message.text:
            if process:
                process.send('1')
            else:
                bot.send_message(message.chat.id, f"""{BOT_NAME} is not playing anything now. 
                    Please send me a link to play something""")
                bot.send_sticker(message.chat.id, random.choice(STICKERS_DONTKNOW))
            return
        if 'increase speed' in message.text:
            if process:
                process.send('2')
            else:
                bot.send_message(message.chat.id, f"""{BOT_NAME} is not playing anything now. 
                    Please send me a link to play something""")
                bot.send_sticker(message.chat.id, random.choice(STICKERS_DONTKNOW))
            return
        # Admin Commands
        if user.username in ADMIN_USER:
            if 'Add User' in message.text:
                    bot.send_message(message.chat.id, """Give me a username to add user""")
                    return
            if 'Delete User' in message.text:
                    bot.send_message(message.chat.id, """Give me a username to delete from users list""")
                    return
            if 'List Users' in message.text:
                    bot.send_message(message.chat.id, """Here is the list of users""")
                    return

def start_process(videourl):
    global process
    playcmd = f"/usr/bin/omxplayer -b -o hdmi --vol -600 {videourl}"
    process = pexpect.spawn(playcmd)
    

def controls(message: Message):
    markup = types.ReplyKeyboardMarkup(row_width=3)
    itembtn1 = types.KeyboardButton('+ vol')
    itembtn2 = types.KeyboardButton('stop')
    itembtn3 = types.KeyboardButton('pause/resume')
    itembtn4 = types.KeyboardButton('- vol')
    itembtn5 = types.KeyboardButton('-30 seconds')
    itembtn6 = types.KeyboardButton('+30 seconds')
    itembtn7 = types.KeyboardButton('fast forward')
    itembtn8 = types.KeyboardButton('decrease speed')
    itembtn9 = types.KeyboardButton('increase speed')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6, itembtn7, itembtn8, itembtn9)
    bot.send_message(message.chat.id, "Video controls:", reply_markup=markup)

def shutdown():
    os.system('sudo shutdown -h now')

def admin_pannel(message: Message):
    markup = types.ReplyKeyboardMarkup(row_width=3)
    itembtn1 = types.KeyboardButton('Add User')
    itembtn2 = types.KeyboardButton('Delete User')
    itembtn3 = types.KeyboardButton('List Users')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.chat.id,"Here are available Admin Controls", reply_markup=markup)

def launchvideo(url):

    logger.info('Extracting source video URL...')

    out = return_full_url(url)

    logger.debug("Full video URL fetched.")

    start_process(out)

def return_full_url(url):
    logger.debug(f"Parsing source url for {url}")

    if ((url[-4:] in (".avi", ".mkv", ".mp4", ".mp3")) or (".googlevideo.com/" in url)):
        logger.debug('Direct video URL, no need to use youtube-dl.')
        return url

    ydl = youtube_dl.YoutubeDL(
        {
            'logger': logger,
            'noplaylist': True,
            'ignoreerrors': True,
        })  # Ignore errors in case of error in long playlists
    with ydl:  # Downloading youtub-dl infos. We just want to extract the info
        result = ydl.extract_info(url, download=False)

    if result is None:
        logger.error(
            "Result is none, returning none. Cancelling following function.")
        return None

    if 'entries' in result:  # Can be a playlist or a list of videos
        video = result['entries'][0]
    else:
        video = result  # Just a video

    if "youtu" in url:
        logger.debug('''CASTING: Youtube link detected.
            Extracting url in maximal quality.''')
        for fid in ('22', '18', '36'): # also 137,136, but these are only videos
            for i in video['formats']:
                if i['format_id'] == fid:
                    logger.debug(
                        'CASTING: Playing highest video quality ' +
                        i['format_note'] + '(' + fid + ').'
                    )
                    return i['url']
    elif "vimeo" in url:
        logger.debug(
            'Vimeo link detected, extracting url in maximal quality.')
        return video['url']
    else:
        logger.debug('''Video not from Youtube or Vimeo.
            Extracting url in maximal quality.''')
        return video['url']

bot.polling(timeout=60)

## About
# Send your video link to the Raspicast device from anywhere and from multiple users without sharing the ssh connection.
## Description
# This is a Telegram bot that runs on top of a configured Raspicast device(https://pimylifeup.com/raspberry-pi-chromecast/) and listens for video links and commands to control it.