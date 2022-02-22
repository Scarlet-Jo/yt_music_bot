from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton,InlineKeyboardMarkup

#from download import Descargar
import time, ffmpeg
from youtube_search import YoutubeSearch
import requests
import yt_dlp
from yt_dlp import YoutubeDL
from text import Text
from yt_dlp.postprocessor.common import PostProcessor
#from pytube import YouTube
import asyncio
import random

import os
from Config import Config

bot = Client(
    'song_bot',
    bot_token = Config.BOT_TOKEN,
    api_id = Config.API_ID,
    api_hash = Config.API_HASH
)
PICS = "https://telegra.ph/file/9bf7cc8100a7b64c67650.jpg, https://telegra.ph/file/270303beef51ec94f746e.jpg"

def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(':'))))

##descargar = Descargar('downloads/')

@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    Ytdl_Bot = f"👋 Hello {message.from_user.username}\n\nI'm an advanced Song Finder Bot exclusively made for All Music Group\nCheck my buttons below to know more..\n"
    await client.send_photo(message.chat.id,
        photo=random.choice(PICS),
        caption=Text.START_TXT.format(message.from_user.mention),  
        parse_mode='html',
        reply_markup=InlineKeyboardMarkup(
            [[
            InlineKeyboardButton("Help", callback_data="help"),
            InlineKeyboardButton("About", callback_data="about")
            ],[
            InlineKeyboardButton("Group", url="https://t.me/All_music_grp"),
            InlineKeyboardButton("Close", callback_data="close_data")
            ]]
        )
    )

@bot.on_message(filters.command("song") & filters.group)
def a(client, message):
    
    query = ''
    for i in message.command[1:]:
        query += ' ' + str(i)
    print(query)
    m =  message.reply("Searching..🥤")
   
    try:
        results = []
        count = 0
        while len(results) == 0 and count < 6:
            if count>0:
                time.sleep(1)
            results = YoutubeSearch(query, max_results=1).to_dict()
            count += 1
        # results = YoutubeSearch(query, max_results=1).to_dict()
        try:
            link = f"https://youtube.com{results[0]['url_suffix']}"
            # print(results)

            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            duration = results[0]["duration"]
            katy = "[Music Bot](https://t.me/all_music_helpbot)"
            ids = "message.from_user.username"

            #UNCOMMENT THIS IF YOU WANT A LIMIT ON DURATION. CHANGE 1800 TO YOUR OWN PREFFERED DURATION AND EDIT THE MESSAGE (30 minutes cap) LIMIT IN SECONDS
            if time_to_seconds(duration) >= 1800:  # duration limit
                m.edit("Exceeded 30mins cap")
                return

            views = results[0]["views"]
            thumb_name = f'thumb{message.message_id}.jpg'
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, 'wb').write(thumb.content)
            link = f"https://youtube.com{results[0]['url_suffix']}"           
            info_dict = yt_dlp.YoutubeDL().extract_info(link, download=False)
            filename = f"{info_dict['title']}.mp3"
            out_folder = f"https://t.me/file_incoming"
            
            """ ydl_opts = {
                'format': 'bestaudio/best',
                'audio-quality':0,
  	        'outtmpl': filename,
            }"""
            ydl_opts = {
             'format': 'bestaudio/best',
             'postprocessors': [{
             'key': 'FFmpegExtractAudio',
                  'preferredcodec': 'mp3',
                  'preferredquality': '320',
                  }],
             'outtmpl': filename,
            }
           
        except Exception as e:
            print(e)
            m.edit('Name incorrect or empty try with correct spelling')
            return
    except Exception as e:
        m.edit(
            "✖️ Check spelling bro try again\n\n"
        )
        print(str(e))
        return
    m.edit("Processing 📥")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(str(link), download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
     
    
        #audio_file = f'downloads/{ytinfo.title.replace("/","|")}-{ytinfo.video_id}.mp3'
        rep =f"⎆ Title : {title[:45]}\n⎆ Duration : {duration} \n⎆ Upload By : {katy}\n⎆ Reqstd by : {message.from_user.username}"
        secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(float(dur_arr[i])) * secmul
            secmul *= 60
        m.edit("Uploading..📤")
        message.reply_audio(
            audio_file,
            caption=rep,
            thumb=thumb_name,
            parse_mode="markdown",
            title=title,
            duration=dur,
            #reply_markup=InlineKeyboardMarkup(
            #    [[
            #      InlineKeyboardButton("Send PM", callback_data="send_pm")
            #    ]]
            #)
        )
        m.delete()
    except Exception as e:
        m.edit("❌ Error Contact Admin") 
        print(e)

    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)

@bot.on_callback_query()
async def cb_handler(client, query):
    
    if query.data == "close_data":
        await query.message.delete()

    elif query.data == "start":
        button = [[
            InlineKeyboardButton("Help", callback_data="help"),
            InlineKeyboardButton("About", callback_data="about")
        ],[
            InlineKeyboardButton("Channel", url="https://t.me/malayalam_music"),
            InlineKeyboardButton("Close", callback_data="close_data")
        ]]
        await query.message.edit_text(Text.START_TXT.format(query.from_user.mention), reply_markup=InlineKeyboardMarkup(button))
    
    elif query.data == "help":
        button = [[
            InlineKeyboardButton("Home", callback_data="start"),
            InlineKeyboardButton("About", callback_data="about")
            ],[
            InlineKeyboardButton("Examples", callback_data="eg")
        ]]
        await query.message.edit_text(Text.HELP_TXT.format(query.from_user.mention), reply_markup=InlineKeyboardMarkup(button))

    elif query.data == "about":
        button = [[
            InlineKeyboardButton("Home", callback_data="start"),
            InlineKeyboardButton("Back", callback_data="help")
        ]]
        await query.message.edit_text(Text.ABOUT_TXT.format(query.from_user.mention), reply_markup=InlineKeyboardMarkup(button))

    elif query.data == "eg":
        await query.answer(text=Text.EG_TXT, show_alert=True)
    """elif query.data == "send_pm":             
       await query.answer(url=f"https://t.me/All_Music_Helpbot?start={file_id}")
       await query.answer(text= "send pm successfully", show_alert=True)
    """
bot.run()
