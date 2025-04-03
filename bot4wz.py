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

import discord
from discord.ext import commands
import asyncio

from app_token import TOKEN

#TOKEN = "YOUR_DISCORD_APP_TOKEN_HERE"

intents = discord.Intents.default()
intents.messages = True
allowed_mentions = discord.AllowedMentions(users=True)

bot = commands.Bot(command_prefix="!", intents=intents)
commands = ["--yyk", "--bakuha", "--no", "--nuke", "--rooms", "--force-bakuha-tekumakumayakonn-tekumakumayakonn", "--help"]
room_number_pool = list(range(1, 10000))
rooms = []
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

class Room(object):
    def __init__(self, message, name, capacity):
        self.number = room_number_pool.pop(0)
        self.name = name
        self.owner = message.author
        self.members = [message.author]
        self.capacity = capacity

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

def process_message(message):
    reply = "初期値。問題が起きているのでrakouに連絡"
    if message.content.startswith("--yyk"):
        capacity = 8
        name = message.content.split("--yyk")[1]
        if name:
            if name[0] in ["1", "2", "3", "4", "5", "6", "１", "２", "３", "４", "５", "６"]:
                capacity = to_int(name[0]) + 1
                name = name.replace(name[0], "")
        name = "無制限" if not name else name.strip()
        room = Room(message=message, name=name, capacity=capacity)
        rooms.append(room)
        rooms.sort(key=lambda room: room.number)
        reply = f"[{room.number}] {room.name} ＠{room.capacity - len(room.members)}\n" + ", ".join(f"{get_name(member)}" for member in room.members)

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
            else:
                reply = "複数の部屋を建てたときは部屋番号を指定してね"
        else:
            room_number = to_int(room_number)
            if room_number is None:
                reply = "部屋番号をアラビア数字で指定してね"
            else:
                room = None
                for room_ in rooms:
                    if room_number == room_.number:
                        if message.author.id == room.owner.id:
                            room = room_
                            break
                if room is None:
                    reply = "その番号の部屋がないか、ホストではないため爆破できません"
                else:
                    delete_room(room)
                    reply = f"爆破: [{room.number}] {room.name} ＠{room.capacity - len(room.members)}\n" + " ".join(f"{member.mention}" for member in room.members)

    if message.content.startswith("--no"):
        room_number = message.content.split("--no")[1]
        room = None
        if room_number == "":
            if len(rooms) == 1:
                room = rooms[0]
                if not message.author in room.members:
                    room.members.append(message.author)
                    reply = f"[{room.number}] {room.name} ＠{room.capacity - len(room.members)}\n" + ", ".join(f"{get_name(member)}" for member in room.members) + f"\n[IN] {get_name(message.author)}"
                else:
                    reply = "もう入ってるよ"
            else:
                reply = "複数の部屋があるときは部屋番号を指定してね"
        else:
            room_number = to_int(room_number)
            if room_number is None:
                reply = "部屋番号をアラビア数字で指定してね"
            else:
                room = None
                for room_ in rooms:
                    if room_number == room_.number:
                        room = room_
                        break
                if room is None:
                    reply = "その番号の部屋はありません"
                else:
                    if not message.author in room.members:
                        room.members.append(message.author)
                        reply = f"[{room.number}] {room.name} ＠{room.capacity - len(room.members)}\n" + ", ".join(f"{get_name(member)}" for member in room.members) + f"\n[IN] {get_name(message.author)}"
                    else:
                        reply = "もう入ってるよ"
        if room is not None:
            if len(room.members) == room.capacity:
                reply = f"[IN] {get_name(message.author)}\n" + f"埋まり: [{room.number}] {room.name} ＠{room.capacity - len(room.members)}\n" + ", ".join(f"{get_name(member)}" for member in room.members) + "\n" + " ".join(f"{member.mention}" for member in room.members)
                delete_room(room)

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
                else:
                    room.members.pop(room.members.index(message.author))
                    reply = f"[{room.number}] {room.name} ＠{room.capacity - len(room.members)}\n" + ", ".join(f"{get_name(member)}" for member in room.members) + f"\n[OUT] {get_name(message.author)}"
            elif len(entered_rooms) == 0:
                reply = "どこにも入ってないよ"
            else:
                reply = "複数の部屋に入っているときは部屋番号を指定してね"
        else:
            room_number = to_int(room_number)
            if room_number is None:
                reply = "部屋番号をアラビア数字で指定してね"
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
                else:
                    if room.owner == message.author:
                        reply = "ホストが抜けるときは--bakuhaを使ってね"
                    else:
                        room.members.pop(room.members.index(message.author))
                        reply = f"[{room.number}] {room.name} ＠{room.capacity - len(room.members)}\n" + ", ".join(f"{get_name(member)}" for member in room.members) + f"\n[OUT] {get_name(message.author)}"

    if message.content.startswith("--rooms"):
        lines = []
        for room in rooms:
            lines.append(f"[{room.number}] {room.name} ＠{room.capacity - len(room.members)}\n" + ", ".join(f"{get_name(member)}" for member in room.members) + "\n")
        if lines:
            reply = "\n".join(lines)
        else:
            reply = "現在、部屋はありません"

    if message.content.startswith("--force-bakuha-tekumakumayakonn-tekumakumayakonn"):
        room_number = to_int(message.content.split("--force-bakuha-tekumakumayakonn-tekumakumayakonn")[1])
        if room_number is None:
            reply = "部屋番号をアラビア数字で指定してね"
        else:
            room = None
            for room_ in rooms:
                if room_number == room_.number:
                    room = room_
                    break
            if room is None:
                reply = "その番号の部屋はありません"
            else:
                delete_room(room)
                reply = f"爆破: [{room.number}] {room.name} ＠{room.capacity - len(room.members)}\n" + ", ".join(f"{get_name(member)}" for member in room.members)

    if message.content.startswith("--help"):
        reply = usage

    return reply

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    # bot自身の発言を拾わない
    if message.author.bot:
        return

    if message.channel.name == "general（de）":
        for command in commands:
            if command in message.content:
                print(f"INPUT:\n{message.content}\n")
                reply = process_message(message)
                await message.channel.send(reply, allowed_mentions=allowed_mentions)
                print(f"OUTPUT:\n{reply}\n")

    await bot.process_commands(message)

def main():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(bot.start(TOKEN))
    except KeyboardInterrupt:
        print("bye")
        loop.run_until_complete(bot.close())
    finally:
        loop.close()

if __name__ == "__main__":
    main()
