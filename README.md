﻿つかいかた:

ホスト
  部屋建て --yyk empty or "room name"
  爆破する --bakuha "room number"

参加者
  参加する --no "room number"
  ぬける   --nuke "room number"

その他
  部屋一覧 --rooms
  つかいかたを出す --help


デプロイしてくれる人向け:
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
