from pathlib import Path
from dotenv import load_dotenv
import os
from requests_oauthlib import OAuth1


# .envファイルを読み込み
load_dotenv()




# =====================================
# 定数定義
# =====================================
# 環境変数を取得



USER = os.getenv("USER")


PASS = os.getenv("PASS")
WELCOME_MESSAGE = os.getenv("WELCOME_MESSAGE")
print(WELCOME_MESSAGE)

