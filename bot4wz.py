#coding: utf-8
#!/path/to/Python_3.6.3 bot4wz.py

_debug = True

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
import psutil
import random
import socket
import sys
import time
import win32gui
import win32con

import discord
from discord.ext import commands

TOKEN = None

if _debug:
    token_file = "canary_token.txt"
    from key_store import canary_bot_status_channel_id as status_channel_id
    from key_store import canary_bot_server_id as guild_id
else:
    token_file = "token.txt"
    from key_store import available_bot_status_channel_id as status_channel_id
    from key_store import available_bot_server_id as guild_id

if os.path.exists(token_file):
    with open(token_file) as f:
        TOKEN = f.read().strip()
        print(f"{token_file}を読み取りました。")

if TOKEN is None:
    print("""\
botの実行にはトークンが必要です。
warzone-aoeで認証済みのbotのトークンはrakouが発行しますが、rakouがいない場合はDiscord Developer Portalでアプリケーションを作成し、warzone-aoeで認証し、有効なトークンをセットしなければなりません。

2025/04現在の手順
  ブラウザ版Discordにログイン
  https://discord.com/developers/docs/intro を開く
  Applications > New Application > rakou_botなどと入力 > Create

  SETTINGS > OAuth2 > OAuth2 URL Generator > bot をチェック
  下に出てくる BOT PERMISSIONSで以下をチェック
    - Send Messages
    - Manage Messages
    - Read Message History
    - Mention Everyone

  一番下に出てくるGENERATED URLをCopyしてwarzone-aoeのテキストに貼り付け

  @rate_counseler（名前が黄色い人）を呼んで、貼り付けたURLを押してもらって、botを認証してもらう。

  【注意】botを使用するテキストチャンネル名は general（de） でなければなりません！（カッコは全角）

  Dicord Developerの画面に戻り、 SETTINGS > Bot を開く
  TOKEN > Reset Token を押すたびに1度だけ出てくる Token をコピーして、token.txt という名前で bot4wz.exe と同じフォルダに保存する。
  ファイル名は token.txt でなければなりません。

  【注意】さらにReset Tokenを押すと、過去のトークンが無効になります。トークンは常に最新の1つだけが有効です。
  もしReset Tokenを押してしまったら、token.txt を削除して、新しいトークンを token.txt に保存してください。

手順を実行したらこのウインドウを閉じて、再度bot4wz.exeをダブルクリックすればbotが起動します。

botが起動すると、# bot_statusチャンネルに、botを起動したPCのホスト名が出ます。
恥ずかしいホスト名とか、人に見られたくないホスト名は、事前に変更をおすすめします。
できれば誰のPCか分かる名前だとよいでしょう。
Windows 10では、設定 > システム > バージョン情報 > デバイス名
これがホスト名です。「このPCの名前を変更」で変更します。

botを起動後、botが1回応答すると、3つの.pickleファイルが作られます。これらを触らないようにしてください。
ただしbotがなにか動作不良を起こした場合はこれらを削除すると初期化できます。

""")
    input("Enterを押して終了: ")
    sys.exit(0)

lock = asyncio.Lock()
on_ready_complete = asyncio.Event()

intents = discord.Intents.default()
intents.messages = True
allowed_mentions = discord.AllowedMentions(users=True)
bot = commands.Bot(command_prefix="!", intents=intents)

bot_commands = [
    "--yyk", "--call", "--create", "--reserve", "--heybros",
    "--bakuha", "--del", "--cancel", "--destroy", "--hakai", "--explosion",
    "--no", "--in", "--join",
    "--nuke", "--out", "--leave", "--dismiss",
    "--rooms",
    "--force-bakuha-tekumakumayakonn-tekumakumayakonn",
    "--remember-takaomikawahashi",
    "--help"
    ]
room_number_pool = list(range(1, 100))
room_number_pool_file = "room_number_pool.bot4wz.pickle"
rooms = []
rooms_file = "rooms.bot4wz.pickle"
temp_message_ids = []
temp_message_ids_file = "temp_message_ids.bot4wz.pickle"
last_process_message_timestamp = datetime.utcnow()
last_running = None

usage = """\
```
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

How to use:
  Send a [--commands] below on #general（de）.

Host
  Create room: --yyk [room name]（無制限 is default）
  無制限 means all welcome.
    --yyk is the same as these:
      --call, --create, --reserve, --heybros

  Call 1 to 6 brothers: --yyk1to6 [room name]（無制限 is default）
    --yyk1to6 is the same as these:
      --call1to6, --create1to6, --reserve1to6, --heybros1to6

    Example: Call 3 brothers for ranked match.
      --call3 [room name]

  Cencel: --bakuha [room number] (The room number can be omitted if there is only one room)
    --bakuha is the same as these:
      --destroy, --explosion, --del, --cancel, --hakai
    --hakai is Japanese 破壊 it means destroy.

Guest
  Join: --no [room number] (The room number can be omitted if there is only one room)
    --no is the same as these:
      --in, --join

  Dismiss: --nuke [room number] (The room number can be omitted if you are in only one room)
    --nuke is the same as these:
      --out, --leave, --dismiss

Others
  See room list: --rooms
  DANGER (DO NOT USE): --force-bakuha-tekumakumayakonn-tekumakumayakonn
    tekumaku mayakonn is the magical words in Japan.
  See this help: --help
```
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
                pass
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
        yyk_complete = False

        for command in ["--yyk", "--call", "--create", "--reserve", "--heybros"]:
            if message.content.startswith(command):
                capacity = 8
                name = message.content.split(command)[1]
                if name:
                    if name[0] in ["1", "2", "3", "4", "5", "6", "１", "２", "３", "４", "５", "６"]:
                        capacity = to_int(name[0]) + 1
                        name = name.replace(name[0], "")
                name = "無制限" if not name else name.strip()
                room = Room(author=message.author, name=name, capacity=capacity)
                rooms.append(room)
                yyk_complete = True
                reply = f"[{room.number}] {room.name} ＠{room.capacity - len(room.members)}\n" + ", ".join(f"{get_name(member)}" for member in room.members)
                room_to_clean = room
                rooms.sort(key=lambda room: room.number)

        for command in ["--bakuha", "--del", "--cancel", "--destroy", "--hakai", "--explosion"]:
            if message.content.startswith(command):
                room_number = message.content.split(command)[1]
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

        for command in ["--no", "--in", "--join"]:
            if message.content.startswith(command):
                room_number = message.content.split(command)[1]
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

        for command in ["--nuke", "--out", "--leave", "--dismiss"]:
            if message.content.startswith(command):
                room_number = message.content.split(command)[1]
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

        if message.content.startswith("--remember-takaomikawahashi"):
            reply = random.choice([
                "学びっすね",
                "マジ破壊されたわ",
                "これがインプルーブ",
                "ソーリー、マイバ、あぁ。",
                "GG! BOYZ!!",
                "えっガラさん1v1するんすか？見ものっすね",
                "まどうさん偏差値なんぼっすか？",
                ])
            temp_message = True

        global last_process_message_timestamp
        last_process_message_timestamp = datetime.utcnow()

        return reply, room_to_clean, temp_message, yyk_complete

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
    if not on_ready_complete.is_set():
        on_ready_complete.wait()
    await asyncio.sleep(5)
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

async def report_survive():
    global last_running
    if not on_ready_complete.is_set():
        on_ready_complete.wait()
    await asyncio.sleep(5)
    channel = bot.get_channel(status_channel_id)
    hostname = socket.gethostname()
    if channel:
        await channel.send(f"{bot.user.id} launch on {hostname}")
    while True:
        if channel:
            sent_message = await channel.send(f"{bot.user.id} running on {hostname}")
            if last_running is not None:
                await last_running.delete()
            last_running = sent_message
        await asyncio.sleep(300)

@bot.event
async def on_ready():
    # already_running()がPC上での重複起動を防ぐのに対して、botの生存実績を見て、他の人がbotを実行中に重複実行を防ぐ
    channel = bot.get_channel(status_channel_id)
    messages = await channel.history(limit=1).flatten()
    if messages:
        message = messages[0]
        if message.content.startswith(f"{bot.user.id} running"):
            delta = datetime.utcnow() - message.created_at.replace(tzinfo=None)
            if delta.total_seconds() < 900:
                print("botが実行中であることをbot自身がステータスチャンネル # bot_status に報告してから間もないため他のPCでbotが実行されている可能性があります。多重実行を防ぐためbotを実行せずに終了します。")
                await asyncio.sleep(10)
                await bot.close()
                return

    print("前回の状態を読み取り中。")
    await load(bot)
    print(f"""\
読み取り完了。botを実行します。
{bot.user}でDicordにログインしました。

終了するには必ずこのウインドウでCtrl+Cを押してください。
ほとんどの場合、Ctrl+Cを押してからbotが反応するまでに時間がかかります。お待ちください。
実行中にWindowsを終了したり、閉じるボタンを押したり、タスクバーからウインドウを閉じたり、タスクマネージャから終了しないでください。

Windows10では閉じるボタンは無効になります。

Windows11では既定のターミナルアプリケーションがWindowsコンソールホストなら閉じるボタンが無効になります。
うっかり閉じてしまわないためには以下の手順を実行してください。
  1. Windows Terminalを開く
  2. タブバーの空白部分を右クリックし、設定を開く
  3. 既定のターミナルアプリケーションをWindowsコンソールホストに設定し、保存
  4. Ctrl+Cでこのbotを終了し、botを再度起動

部屋の状態などを保存するための.pickleファイルが3つ作られますが、触らないでください。
""")

    on_ready_complete.set()

@bot.event
async def on_message(message):
    if not on_ready_complete.is_set():
        await on_ready_complete.wait()
    # bot自身の発言を拾わない
    if message.author.bot:
        return
    if message.channel.name == "general（de）":
        for command in bot_commands:
            if message.content.startswith(command):
                jst = datetime.utcnow() + timedelta(hours=9)
                print(f"INPUT:\n{message.content}\n{jst}\n")
                reply, room_to_clean, temp_message, yyk_complete = await process_message(message)
                sent_message = await message.channel.send(reply, allowed_mentions=allowed_mentions)
                if room_to_clean:
                    await room_cleaner(room_to_clean, message, sent_message)
                if temp_message:
                    temp_message_ids.append( (message.channel.id, sent_message.id) )
                if yyk_complete:
                    lines = ["=========== 部屋一覧 ===========\n"]
                    for room in rooms:
                        lines.append(f"[{room.number}] {room.name} ＠{room.capacity - len(room.members)}\n" + ", ".join(f"{get_name(member)}" for member in room.members) + "\n")
                    line = "\n".join(lines)
                    sent_message = await message.channel.send(line, allowed_mentions=allowed_mentions)
                    temp_message_ids.append( (message.channel.id, sent_message.id) )
                jst = datetime.utcnow() + timedelta(hours=9)
                print(f"OUTPUT:\n{reply}\n{jst}\n")
                await save()
    await bot.process_commands(message)

def disable_close_button():
    # うっかり閉じるボタンで終了しないように、閉じるボタンを無効化する
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        menu = win32gui.GetSystemMenu(hwnd, False)
        try:
            win32gui.RemoveMenu(menu, win32con.SC_CLOSE, win32con.MF_BYCOMMAND)
        except Exception:
            # シェルで2回目に実行するとボタンがないので例外が出る
            pass
        win32gui.DrawMenuBar(hwnd)

def already_running():
    # うっかりbotを重複起動しちゃうのを防止
    current = psutil.Process()
    current_pid = current.pid
    parent_pid = current.ppid()
    for proc in psutil.process_iter(attrs=["pid", "cmdline"]):
        try:
            cmdline = " ".join(proc.info["cmdline"])
            if "bot4wz.py" in cmdline and proc.info["pid"] != current_pid and not "cmd" in proc.info["cmdline"]:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except TypeError:
            pass
    for proc in psutil.process_iter(attrs=["pid", "exe"]):
        try:
            if proc.pid in (current_pid, parent_pid):
                continue
            proc_exe = proc.info["exe"]
            if not proc_exe:
                continue
            if "bot4wz.exe" == os.path.basename(proc_exe):
                return True
            if "bot4wz.exe" == proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def main():
    disable_close_button()
    loop = asyncio.get_event_loop()
    tasks = []
    tasks.append(loop.create_task(temp_message_cleaner()))
    tasks.append(loop.create_task(report_survive()))
    asyncio.gather(*tasks, return_exceptions=True) # ssl.SSLErrorの出所を探るため、例外がタスクから来た場合に Ctrl+C を押すまで保留する
    try:
        loop.run_until_complete(bot.start(TOKEN))
    except KeyboardInterrupt:
        print("終了命令Ctrl+Cを受け付けました。非同期タスクの終了を待っています…")
    except discord.errors.LoginFailure:
        print("botがDiscordにログインできませんでした。有効なトークンをtoken.txtに保存してください。")
        print("トークンが有効ならば、Discordに問題が起きているかもしれません。")
        time.sleep(10)
    finally:
        for task in tasks:
            task.cancel()
            try:
                loop.run_until_complete(task)
            except asyncio.CancelledError:
                pass
        if not bot.is_closed():
            loop.run_until_complete(bot.close())
        loop.close()
        print("10秒後に終了します。")
        time.sleep(10)

if __name__ == "__main__":
    if already_running():
        print("すでに実行中のbot4wz.pyまたはbot4wz.exeがあるのでbotを開始せず10秒後に終了します")
        time.sleep(10)
        sys.exit(0)
    main()
