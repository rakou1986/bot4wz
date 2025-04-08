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


実行してくれる人向け:

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

手順を実行したらbot4wz.exeをダブルクリックすればbotが起動します。

botを起動後、botが1回応答すると、3つの.pickleファイルが作られます。これらを触らないようにしてください。

既知の不具合:

Discordとの接続が不安定？なときにexceptできないssl.SSLErrorが送出されてbotが落ちる。
またはbotの終了時にexceptできなかったssl.SSLErrorが遅れて送出されて異常終了する。
再現困難なため、不要メッセージの定期削除、ステータスチャンネルへの生存報告、この2つの非同期タスクからの例外送出を保留してbotが落ちにくくするようにパッチワークしてある。
対応：botを再起動
```
