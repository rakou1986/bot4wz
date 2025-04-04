#coding: utf-8
#!/path/to/Python_3.6.3 bot4wz.py

"""
[requirements]

python -V
Python 3.6.3 :: Anaconda, Inc.

pip show discord
Version: 1.7.3

[discord developer setting]
Bot:
  MESSAGE CONTENT INTENT: enable
  TOKEN: Press "Reset Token". Token appear once. Copy token and s/YOUR_DISCORD_APP_TOKEN_HERE/copied_token/ and save.

OAuth2:
  SCOPES:
    bot
  BOT PERMISIOONS:
    Send Messages
    Manage Messages
    Read Message History
    Mention Everyone

  Copy and paste to warzone "GENERATED URL" at "OAuth2"

[run]
$ python bot4wz.py

[quit]
Ctrl + C
"""

import asyncio
from datetime import datetime, timedelta
import os
import pickle
from pprint import pprint
import time
import win32gui
import win32con

import discord
from discord.ext import commands

from app_token import TOKEN

#TOKEN = "YOUR_DISCORD_APP_TOKEN_HERE"

lock = asyncio.Lock()

intents = discord.Intents.default()
intents.messages = True
allowed_mentions = discord.AllowedMentions(users=True)
bot = commands.Bot(command_prefix="!", intents=intents)

commands = ["--yyk", "--bakuha", "--no", "--nuke", "--rooms", "--force-bakuha-tekumakumayakonn-tekumakumayakonn", "--help"]
room_number_pool = list(range(1, 100))
room_number_pool_file = "room_number_pool.bot4wz.pickle"
rooms = []
rooms_file = "rooms.bot4wz.pickle"
temp_message_ids = []
temp_message_ids_file = "temp_message_ids.bot4wz.pickle"
last_process_message_timestamp = datetime.utcnow()

guild_id = 390895191659118594 # warzone-aoe サーバーID
#guild_id = 414119071408193536 # テストサーバー

usage = """\
つかいかた:

ホスト
  部屋建て --yyk 部屋名（デフォルト無制限）
  1～6人を募集 --yyk1～6 部屋名
  爆破する --bakuha 部屋番号（1つしか立ててないときは省略可能）

参加者
  参加する --no 部屋番号（1つしか部屋がないときは省略可能）
  ぬける   --nuke 部屋番号（1つの部屋にしか入ってないときは省略可能）

その他
  部屋一覧 --rooms
  無理矢理部屋を消す（干しっぱなし用、管理者使用推奨） --force-bakuha-tekumakumayakonn-tekumakumayakonn 部屋番号
  つかいかたを出す --help
"""

class RoomPicklable(object):

    def __init__(self, room):
        self.number = room.number
        self.name = room.name
        self.owner_id = room.owner.id
        self.member_ids = [user.id for user in room.members]
        self.capacity = room.capacity
        self.garbage_queue = room.garbage_queue

    async def to_room(self, bot):
        guild = bot.get_guild(guild_id)
        if not guild:
            raise ValueError("Guild not found")

        try:
            owner = await guild.fetch_member(self.owner_id)
        except discord.NotFound:
            owner = None

        members = []
        for user_id in self.member_ids:
            try:
                member = await guild.fetch_member(user_id)
                members.append(member)
            except discord.NotFound:
                continue

        #owner = await bot.fetch_user(self.owner_id)
        #members = [await bot.fetch_user(user_id) for user_id in self.member_ids]
        room = Room(author=owner, name=self.name, capacity=self.capacity)
        room.number = self.number
        room.members = members
        return room


class Room(object):

    def __init__(self, author , name, capacity):
        self.number = room_number_pool.pop(0)
        self.name = name
        self.owner = author
        self.members = [author]
        self.capacity = capacity
        self.garbage_queue = []


async def save():
    rooms_picklable = [RoomPicklable(room) for room in rooms]
    with open(rooms_file, "wb") as f:
        pickle.dump(rooms_picklable, f)
    with open(room_number_pool_file, "wb") as f:
        pickle.dump(room_number_pool, f)
    with open(temp_message_ids_file, "wb") as f:
        pickle.dump(temp_message_ids, f)

async def load(bot):
    global rooms
    if os.path.exists(rooms_file):
        with open(rooms_file, "rb") as f:
            try:
                rooms_picklable = pickle.load(f)
                rooms = await asyncio.gather(*(picklable.to_room(bot) for picklable in rooms_picklable))
            except Exception as e:
                print(f"Error loading rooms: {e}")
    global room_number_pool
    if os.path.exists(room_number_pool_file):
        with open(room_number_pool_file, "rb") as f:
            try:
                room_number_pool = pickle.load(f)
            except Exception as e:
                pass
    global temp_message_ids
    if os.path.exists(temp_message_ids_file):
        with open(temp_message_ids_file, "rb") as f:
            try:
                temp_message_ids = pickle.load(f)
            except Exception as e:
                pass

def to_int(string):
    try:
        return int(string)
    except ValueError:
        return None

def get_name(user):
    # サーバーニックネーム、表示名、ユーザー名（グローバル）の順に名前を探す
    for name in [user.nick, user.display_name, user.name]:
        if name is not None:
            return name
    return "名前を取得できませんでした"

def delete_room(room):
    rooms.pop(rooms.index(room))
    room_number_pool.append(room.number)
    room_number_pool.sort()

async def process_message(message):
    async with lock:
        reply = "初期値。問題が起きているのでrakouに連絡"
        room_to_clean = None
        temp_message = False
        if message.content.startswith("--yyk"):
            capacity = 8
            name = message.content.split("--yyk")[1]
            if name:
                if name[0] in ["1", "2", "3", "4", "5", "6", "１", "２", "３", "４", "５", "６"]:
                    capacity = to_int(name[0]) + 1
                    name = name.replace(name[0], "")
            name = "無制限" if not name else name.strip()
            room = Room(author=message.author, name=name, capacity=capacity)
            rooms.append(room)
            reply = f"[{room.number}] {room.name} ＠{room.capacity - len(room.members)}\n" + ", ".join(f"{get_name(member)}" for member in room.members)
            room_to_clean = room
            rooms.sort(key=lambda room: room.number)

        if message.content.startswith("--bakuha"):
            room_number = message.content.split("--bakuha")[1]
            if room_number == "":
                owned_rooms = []
                for room in rooms:
                    if message.author.id == room.owner.id:
                        owned_rooms.append(room)
                if len(owned_rooms) == 1:
                    room = owned_rooms[0]
                    delete_room(room)
                    reply = f"爆破: [{room.number}] {room.name} ＠{room.capacity - len(room.members)}\n" + " ".join(f"{member.mention}" for member in room.members)
                    room_to_clean = room
                else:
                    reply = "複数の部屋を建てたときは部屋番号を指定してね"
                    temp_message = True
            else:
                room_number = to_int(room_number)
                if room_number is None:
                    reply = "部屋番号をアラビア数字で指定してね"
                    temp_message = True
                else:
                    room = None
                    for room_ in rooms:
                        if room_number == room_.number:
                            if message.author.id == room_.owner.id:
                                room = room_
                                break
                    if room is None:
                        reply = "その番号の部屋がないか、ホストではないため爆破できません"
                        temp_message = True
                    else:
                        delete_room(room)
                        reply = f"爆破: [{room.number}] {room.name} ＠{room.capacity - len(room.members)}\n" + " ".join(f"{member.mention}" for member in room.members)
                        room_to_clean = room

        if message.content.startswith("--no"):
            room_number = message.content.split("--no")[1]
            room = None
            if room_number == "":
                if len(rooms) == 1:
                    room = rooms[0]
                    if not message.author in room.members:
                        room.members.append(message.author)
                        reply = f"[{room.number}] {room.name} ＠{room.capacity - len(room.members)}\n" + ", ".join(f"{get_name(member)}" for member in room.members) + f"\n[IN] {get_name(message.author)}"
                        room_to_clean = room
                    else:
                        reply = "もう入ってるよ"
                        temp_message = True
                elif len(rooms) == 0:
                    reply = "現在、部屋はありません"
                    temp_message = True
                else:
                    reply = "複数の部屋があるときは部屋番号を指定してね"
                    temp_message = True
            else:
                room_number = to_int(room_number)
                if room_number is None:
                    reply = "部屋番号をアラビア数字で指定してね"
                    temp_message = True
                else:
                    room = None
                    for room_ in rooms:
                        if room_number == room_.number:
                            room = room_
                            break
                    if room is None:
                        reply = "その番号の部屋はありません"
                        temp_message = True
                    else:
                        if not message.author in room.members:
                            room.members.append(message.author)
                            reply = f"[{room.number}] {room.name} ＠{room.capacity - len(room.members)}\n" + ", ".join(f"{get_name(member)}" for member in room.members) + f"\n[IN] {get_name(message.author)}"
                            room_to_clean = room
                        else:
                            reply = "もう入ってるよ"
                            temp_message = True
            if room is not None:
                if len(room.members) == room.capacity:
                    reply = f"[IN] {get_name(message.author)}\n" + f"埋まり: [{room.number}] {room.name} ＠{room.capacity - len(room.members)}\n" + ", ".join(f"{get_name(member)}" for member in room.members) + "\n" + " ".join(f"{member.mention}" for member in room.members)
                    delete_room(room)
                    room_to_clean = room

        if message.content.startswith("--nuke"):
            room_number = message.content.split("--nuke")[1]
            if room_number == "":
                entered_rooms = []
                for room in rooms:
                    for member in room.members:
                        if message.author.id == member.id:
                            entered_rooms.append(room)
                            break
                if len(entered_rooms) == 1:
                    room = entered_rooms[0]
                    if room.owner == message.author:
                        reply = "ホストが抜けるときは--bakuhaを使ってね"
                        temp_message = True
                    else:
                        room.members.pop(room.members.index(message.author))
                        reply = f"[{room.number}] {room.name} ＠{room.capacity - len(room.members)}\n" + ", ".join(f"{get_name(member)}" for member in room.members) + f"\n[OUT] {get_name(message.author)}"
                        room_to_clean = room
                elif len(entered_rooms) == 0:
                    reply = "どこにも入ってないよ"
                    temp_message = True
                else:
                    reply = "複数の部屋に入っているときは部屋番号を指定してね"
                    temp_message = True
            else:
                room_number = to_int(room_number)
                if room_number is None:
                    reply = "部屋番号をアラビア数字で指定してね"
                    temp_message = True
                else:
                    room = None
                    for room_ in rooms:
                        if room_number == room_.number:
                            for member in room_.members:
                                if message.author.id == member.id:
                                    room = room_
                                    break
                            break
                    if room is None:
                        reply = "その番号の部屋がないか、入っていないので抜けれません"
                        temp_message = True
                    else:
                        if room.owner == message.author:
                            reply = "ホストが抜けるときは--bakuhaを使ってね"
                            temp_message = True
                        else:
                            room.members.pop(room.members.index(message.author))
                            reply = f"[{room.number}] {room.name} ＠{room.capacity - len(room.members)}\n" + ", ".join(f"{get_name(member)}" for member in room.members) + f"\n[OUT] {get_name(message.author)}"
                            room_to_clean = room

        if message.content.startswith("--rooms"):
            lines = []
            for room in rooms:
                lines.append(f"[{room.number}] {room.name} ＠{room.capacity - len(room.members)}\n" + ", ".join(f"{get_name(member)}" for member in room.members) + "\n")
            if lines:
                reply = "\n".join(lines)
            else:
                reply = "現在、部屋はありません"
            temp_message = True

        if message.content.startswith("--force-bakuha-tekumakumayakonn-tekumakumayakonn"):
            room_number = to_int(message.content.split("--force-bakuha-tekumakumayakonn-tekumakumayakonn")[1])
            if room_number is None:
                reply = "部屋番号をアラビア数字で指定してね"
                temp_message = True
            else:
                room = None
                for room_ in rooms:
                    if room_number == room_.number:
                        room = room_
                        break
                if room is None:
                    reply = "その番号の部屋はありません"
                    temp_message = True
                else:
                    delete_room(room)
                    reply = f"爆破: [{room.number}] {room.name} ＠{room.capacity - len(room.members)}\n" + ", ".join(f"{get_name(member)}" for member in room.members)
                    room_to_clean = room

        if message.content.startswith("--help"):
            reply = usage
            temp_message = True

        global last_process_message_timestamp
        last_process_message_timestamp = datetime.utcnow()

        return reply, room_to_clean, temp_message

async def room_cleaner(room, received_message, sent_message):
    room.garbage_queue.append(sent_message.id)
    while True:
        if 1 < len(room.garbage_queue):
            message_id = room.garbage_queue.pop(0)
            try:
                msg = await received_message.channel.fetch_message(message_id)
                await msg.delete()
            except discord.NotFound:
                pass
        else:
            break

async def temp_message_cleaner():
    global last_process_message_timestamp
    await bot.wait_until_ready()
    await asyncio.sleep(120)
    while True:
        await asyncio.sleep(3)
        if timedelta(minutes=2) <= datetime.utcnow() - last_process_message_timestamp:
            for channel_id, message_id in temp_message_ids:
                channel = bot.get_channel(channel_id)
                if channel:
                    try:
                        msg = await channel.fetch_message(message_id)
                        await msg.delete()
                    except discord.NotFound:
                        pass
            temp_message_ids.clear()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    print("Loading")
    await load(bot)
    print("Loaded, now starting other tasks")

@bot.event
async def on_message(message):
    # bot自身の発言を拾わない
    if message.author.bot:
        return
    if message.channel.name == "general（de）":
        for command in commands:
            if message.content.startswith(command):
                print(f"INPUT:\n{message.content}\n")
                reply, room_to_clean, temp_message = await process_message(message)
                sent_message = await message.channel.send(reply, allowed_mentions=allowed_mentions)
                if room_to_clean:
                    await room_cleaner(room_to_clean, message, sent_message)
                if temp_message:
                    temp_message_ids.append( (message.channel.id, sent_message.id) )
                print(f"OUTPUT:\n{reply}\n")
                print(rooms)
                await save()
    await bot.process_commands(message)

def disable_close_button():
    # うっかり閉じるボタンで終了しないように、閉じるボタンを無効化する
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        menu = win32gui.GetSystemMenu(hwnd, False)
        win32gui.RemoveMenu(menu, win32con.SC_CLOSE, win32con.MF_BYCOMMAND)
        win32gui.DrawMenuBar(hwnd)

def main():
    disable_close_button()
    loop = asyncio.get_event_loop()
    temp_message_cleaner_task = loop.create_task(temp_message_cleaner())
    try:
        loop.run_until_complete(bot.start(TOKEN))
    except KeyboardInterrupt:
        print("shutting down...")
        temp_message_cleaner_task.cancel()
        try:
            loop.run_until_complete(temp_message_cleaner_task)
        except asyncio.CancelledError:
            pass
        loop.run_until_complete(bot.close())
    finally:
        loop.close()
        print("bye")
        print("閉じるにはタスクバーで右クリック > ウインドウを閉じる")
        time.sleep(5)

if __name__ == "__main__":
    main()
