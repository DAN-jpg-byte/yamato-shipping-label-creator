import os
from dotenv import load_dotenv
import traceback
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl


# =====================================
# 1. 変数・定数の初期設定
# =====================================         

# 以下にGmailの設定を書き込む★ --- (*1)
load_dotenv()


gmail_account = os.getenv("GMAIL_ACCOUNT")
gmail_password = os.getenv("GMAIL_PASSWORD")
# メールの送信先★ --- (*2)
mail_to = os.getenv("MAIL_TO")

# Gmail SMTPサーバーの設定
# なぜ？: Gmailのメール送信に必要な接続情報
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587  # TLSポート

# TODO: 必要に応じてCCやBCCの設定を追加する

# =====================================
# 2. 関数定義
# =====================================

def send_mail(subject, body):
    """
    Gmailを使ってメールを送信する関数
    
    Args:
        subject (str): メールの件名
        body (str): メールの本文
    
    Returns:
        bool: 送信成功ならTrue、失敗ならFalse
    """
    try:
        # -- メールメッセージの作成 --
        # なぜ？: MIME形式でメールを作成し、件名や本文を正しくエンコードするため
        msg = MIMEMultipart()
        msg['From'] = gmail_account
        msg['To'] = mail_to
        msg['Subject'] = subject
        
        # メール本文を追加（HTMLではなくテキスト形式）
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # -- SMTPサーバーへの接続と送信 --
        # なぜ？: GmailのSMTPサーバーに安全に接続してメールを送信するため
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # TLS暗号化を開始
        
        # ログイン（アプリパスワードを使用）
        server.login(gmail_account, gmail_password)
        
        # メール送信
        server.send_message(msg)
        server.quit()
        
        print(f"✅ メール送信成功: {subject}")
        return True
        
    except Exception as e:
        print("❌ メール送信エラー！詳細はこちら ↓")
        traceback.print_exc()
        return False








access_token = os.getenv("LINE_ACCESS_TOKEN")

user_id = os.getenv("LINE_USER_ID")
# ヘッダー情報
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}"
}
# LINE Messaging APIのURL
endpoint_url = "https://api.line.me/v2/bot/message/broadcast"


import requests
def send_line_message(message_text):
    # メッセージデータの作成
    data = {
        "to": user_id,
        "messages": [
            {
                "type": "text", 
                "text": message_text
            }
        ]
    }

    # メッセージの送信リクエスト
    response = requests.post(endpoint_url, headers=headers, json=data)

    # レスポンスの確認
    if response.status_code == 200:
        print("メッセージが送信されました")
    else:
        print(f"エラーが発生しました: {response.status_code} - {response.text}")














# =====================================
# 3. テスト実行（このファイルを直接実行した場合）
# =====================================

if __name__ == "__main__":
    # テスト用のメール送信
    test_subject = "テストメール"
    test_body = "これはGmail送信プログラムのテストです。\n\n送信時刻: " + str(datetime.datetime.now())
    
    success = send_mail(test_subject, test_body)
    if success:
        print("🎉 テストメール送信完了")
    else:
        print("💥 テストメール送信失敗")


    send_line_message("テストのラインメッセージです")








