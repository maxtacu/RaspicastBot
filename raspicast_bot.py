#!.venv/bin/python3

import telebot
from telebot import types
from telebot.types import Message, Update
import random, logging, sys, os, time, logging
from tinydb import TinyDB, Query
import pexpect
import youtube_dl

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

BOT_USERS_DB = os.path.join(__location__, 'bot_userlist.json')
ADMIN_USER = ['maxtacu']
CURRENT_UNIX_DATE = int(time.time())

logging.basicConfig(
    filename=os.path.join(__location__, 'raspicast.log'),
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt='%m-%d %H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger("RaspberryCast")

process = None
bot = telebot.TeleBot(TOKEN)
db = TinyDB(BOT_USERS_DB)
query = Query()

HELP_MESSAGE = """To play a video just send a link to me anytime without any commands
                
                This is a list of commands available.
                /controls - Show video controls
                /playlist - Create a video playlist(Not available yet)
                /admin - Show additional admin menu
                /shutdown - Power-off the Raspicast
                /reboot - Reboot the device
                
                Pick one bellow"""

@bot.message_handler(commands=['start'])
def handle_start(message: Message):
    if message.date <= CURRENT_UNIX_DATE:
        pass
    else:
        bot.reply_to(message, """Hi %s, what video would you like me to play?
        Use /help to check all my potential""" % message.from_user.first_name)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        itembtn1 = types.KeyboardButton('/help')
        itembtn2 = types.KeyboardButton('/controls')
        itembtn3 = types.KeyboardButton('/playlist')
        markup.add(itembtn1, itembtn2, itembtn3)
        bot.send_message(message.chat.id, "Choose the option:", reply_markup=markup)

@bot.message_handler(commands=['help'])
def send_poweroff(message: Message):
    if message.date <= CURRENT_UNIX_DATE:
        pass
    else:
        bot.send_message(message.chat.id, HELP_MESSAGE)
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        itembtn1 = types.KeyboardButton('/shutdown')
        itembtn2 = types.KeyboardButton('/reboot')
        itembtn3 = types.KeyboardButton('/playlist')
        itembtn4 = types.KeyboardButton('/admin')
        itembtn5 = types.KeyboardButton('/controls')
        markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5)
        bot.send_message(message.chat.id, "Choose the option:", reply_markup=markup)

@bot.message_handler(commands=['shutdown'])
def send_poweroff(message: Message):
    if message.date <= CURRENT_UNIX_DATE:
        pass
    elif not db.search(query.username == message.from_user.username):
        bot.reply_to(message, """Sorry. Permission denied""")
    else:
        bot.reply_to(message, f"""{BOT_NAME} is going down for POWER-OFF. 
        To start it back please plug the power cable again""")
        logger.info('Power-off signal received.')
        shutdown()

@bot.message_handler(commands=['reboot'])
def send_reboot(message: Message):
    if message.date <= CURRENT_UNIX_DATE:
        pass
    elif not db.search(query.username == message.from_user.username):
        bot.reply_to(message, """Sorry. Permission denied""")
    else:
        bot.reply_to(message, f"""{BOT_NAME} is going for REBOOT """)
        logger.info('Reboot signal received.')
        reboot()

@bot.message_handler(commands=['admin'])
def admin(message: Message):
    if message.date <= CURRENT_UNIX_DATE:
        pass
    else:
        logger.info('Admin menu signal received.')
        bot.reply_to(message, f"""{BOT_NAME} admin menu.""")
        admin_pannel(message)

@bot.message_handler(commands=['controls'])
def show_controls(message: Message):
    if message.date <= CURRENT_UNIX_DATE:
        pass
    else:
        controls(message)

@bot.message_handler(commands=['playlist'])
def playlist(message: Message):
    if message.date <= CURRENT_UNIX_DATE:
        pass
    else:
        bot.send_message(message.chat.id, "Sorry. This feature is under development and is not available now")
        return

@bot.message_handler(content_types=['text'])
def message(message: Message):
    global process
    if message.date <= CURRENT_UNIX_DATE:
        pass
    elif not db.search(query.username == message.from_user.username) and (message.from_user.username not in ADMIN_USER):
        bot.reply_to(message, """Sorry. Permission denied""")
        logger.info(f'Got permission denied for user {message.from_user.username}')
    else:
        url = message.text
        if url.startswith('http'):
            bot.send_sticker(message.chat.id, random.choice(STICKERS_APPROVED))
            controls(message)
            launchvideo(url)
        if '+ vol' in message.text:
            if process:
                logger.info('Volume increase signal received.')
                process.send('+')
            else:
                bot.send_message(message.chat.id, f"""{BOT_NAME} is not playing anything now. 
                    Please send me a link to play something""")
                bot.send_sticker(message.chat.id, random.choice(STICKERS_DONTKNOW))
        if '- vol' in message.text:
            if process:
                logger.info('Volume decrease signal received.')
                process.send('-')
            else:
                bot.send_message(message.chat.id, f"""{BOT_NAME} is not playing anything now. 
                    Please send me a link to play something""")
                bot.send_sticker(message.chat.id, random.choice(STICKERS_DONTKNOW))
        if 'pause/resume' in message.text:
            if process:
                logger.info('Pause/Resume signal received.')
                process.send('p')
            else:
                bot.send_message(message.chat.id, f"""{BOT_NAME} is not playing anything now. 
                    Please send me a link to play something""")
                bot.send_sticker(message.chat.id, random.choice(STICKERS_DONTKNOW))
        if 'stop' in message.text:
            if process:
                logger.info('Stop video signal received.')
                process.send('q')
            else:
                bot.send_message(message.chat.id, f"""{BOT_NAME} is not playing anything now. 
                    Please send me a link to play something""")
                bot.send_sticker(message.chat.id, random.choice(STICKERS_DONTKNOW))
        if '-30 seconds' in message.text:
            if process:
                logger.info('+30 seconds signal received.')
                process.send('\x1b[D')
            else:
                bot.send_message(message.chat.id, f"""{BOT_NAME} is not playing anything now. 
                    Please send me a link to play something""")
                bot.send_sticker(message.chat.id, random.choice(STICKERS_DONTKNOW))
        if '+30 seconds' in message.text:
            if process:
                logger.info('-30 seconds signal received.')
                process.send('\x1b[C')
            else:
                bot.send_message(message.chat.id, f"""{BOT_NAME} is not playing anything now. 
                    Please send me a link to play something""")
                bot.send_sticker(message.chat.id, random.choice(STICKERS_DONTKNOW))
        if 'fast forward' in message.text:
            if process:
                logger.info('Fast forward signal received.')
                process.send('>')
            else:
                bot.send_message(message.chat.id, f"""{BOT_NAME} is not playing anything now. 
                    Please send me a link to play something""")
                bot.send_sticker(message.chat.id, random.choice(STICKERS_DONTKNOW))
        if 'decrease speed' in message.text:
            if process:
                logger.info('Decrease video speed signal received.')
                process.send('1')
            else:
                bot.send_message(message.chat.id, f"""{BOT_NAME} is not playing anything now. 
                    Please send me a link to play something""")
                bot.send_sticker(message.chat.id, random.choice(STICKERS_DONTKNOW))
        if 'increase speed' in message.text:
            if process:
                logger.info('Increase video speed signal received.')
                process.send('2')
            else:
                bot.send_message(message.chat.id, f"""{BOT_NAME} is not playing anything now. 
                    Please send me a link to play something""")
                bot.send_sticker(message.chat.id, random.choice(STICKERS_DONTKNOW))
        # Admin Commands
        if 'Add User' in message.text: 
            if message.from_user.username not in ADMIN_USER:
                bot.reply_to(message, """Sorry. Permission denied""")
                logger.info(f'Got ADMIN permission denied for user {message.from_user.username}')
            else:
                bot.send_message(message.chat.id, """Give me a telegram username to add user""")
                bot.register_next_step_handler(message, add_username)
        if 'Delete User' in message.text:
            if message.from_user.username not in ADMIN_USER:
                bot.reply_to(message, """Sorry. Permission denied""")
                logger.info(f'Got ADMIN permission denied for user {message.from_user.username}')
            else:
                bot.send_message(message.chat.id, """Give me a telegram username to delete from users list""")
                bot.register_next_step_handler(message, delete_username)
        if 'List Users' in message.text:
            if message.from_user.username not in ADMIN_USER:
                bot.reply_to(message, """Sorry. Permission denied""")
                logger.info(f'Got ADMIN permission denied for user {message.from_user.username}')
            else:
                bot.send_message(message.chat.id, """Here is the list of users""")
                list_users(message)       

def add_username(message: Message):
    try:
        chat_id = message.chat.id
        username = message.text
        db.insert({'username': username })
        bot.reply_to(message, f'User {username} successfully added')
    except Exception as e:
        bot.reply_to(message, 'oooops')

def delete_username(message: Message):
    try:
        chat_id = message.chat.id
        username = message.text
        db.remove(query.username == username)
        bot.reply_to(message, f'User {username} successfully deleted')
    except Exception as e:
        bot.reply_to(message, 'oooops')

def list_users(message: Message):
    try:
        chat_id = message.chat.id
        all_users = db.all()
        bot.send_message(message.chat.id, str(all_users))
    except Exception as e:
        bot.reply_to(message, 'oooops')

def start_process(videourl):
    global process
    playcmd = f"/usr/bin/omxplayer -b -o hdmi --vol -600 {videourl}"
    logger.info('Starting the video')
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

def reboot():
    os.system('sudo reboot')

def admin_pannel(message: Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=1)
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
    logger.info(f"Parsing source url for {url}")

    if ((url[-4:] in (".avi", ".mkv", ".mp4", ".mp3")) or (".googlevideo.com/" in url)):
        logger.info('Direct video URL, no need to use youtube-dl.')
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
        logger.info('''CASTING: Youtube link detected.
            Extracting url in maximal quality.''')
        for fid in ('22', '18', '36'): # also 137,136, but these are only videos
            for i in video['formats']:
                if i['format_id'] == fid:
                    logger.info(
                        'CASTING: Playing highest video quality ' +
                        i['format_note'] + '(' + fid + ').'
                    )
                    return i['url']
    elif "vimeo" in url:
        logger.info(
            'Vimeo link detected, extracting url in maximal quality.')
        return video['url']
    else:
        logger.info('''Video not from Youtube or Vimeo.
            Extracting url in maximal quality.''')
        return video['url']

bot.polling(timeout=60)

'''
## About
Send your video link to the Raspicast device from anywhere and from multiple users without sharing the ssh connection.
## Description
This is a Telegram bot that runs on top of a configured Raspicast device(https://pimylifeup.com/raspberry-pi-chromecast/) and listens for video links and commands to control it.
## Commands to be set in BotFather
start - start the bot
controls - show video controls
admin - admin menu
playlist - create a playlist
shutdown - power-off the device
reboot - reboot the device
'''