import config
import traceback
from logging_config import setup_logging
from logging import getLogger
import os
from pathlib import Path
from dotenv import load_dotenv
import time
import datetime
import tkinter as tk
from tkinter import messagebox

# Selenium関連
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select 

from g_mail_send import send_mail  # LINE送信は使わないので削除しても良いですが、残しておいても問題ありません
from LineYamatoParser import analyze_yamato_line_url


# =====================================
# ログと環境設定
# =====================================
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
setup_logging()
logger = getLogger(__name__)

load_dotenv()

USER = config.USER
PASS = config.PASS
WELCOME_MESSAGE = config.WELCOME_MESSAGE
URL = "https://sp-send.kuronekoyamato.co.jp/smpTaqWeb/"


# =====================================
# Chrome設定
# =====================================
chrome_options = Options()

# モバイルエミュレーション（iPhone指定）
mobile_emulation = {"deviceName": "iPhone 12 Pro"}
chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

# ダウンロード設定
prefs = {
    "download.default_directory": os.path.join(os.getcwd(), "downloads"),
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True
}
chrome_options.add_experimental_option("prefs", prefs)

# 自動操作の検知回避設定
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

# =====================================
# 処理ロジック
# =====================================

def login(driver):
    """ログイン操作"""
    wait = WebDriverWait(driver, 15)
    
    # ログインボタン表示待ち
    login_btn = wait.until(EC.element_to_be_clickable((By.ID, 'portalEntrance')))
    login_btn.click()
    
    # ID/PASS入力
    user_field = wait.until(EC.presence_of_element_located((By.ID, 'login-form-id')))
    user_field.clear()
    user_field.send_keys(USER)

    pass_field = driver.find_element(By.ID, 'login-form-password')
    pass_field.clear()
    pass_field.send_keys(PASS)

    driver.find_element(By.ID, 'login-form-submit').click()
    time.sleep(2)

def send_package(driver, word, is_compact):
    """
    配送処理を行い、生成されたメッセージテキストを返す関数
    """
    wait = WebDriverWait(driver, 15)
    try:
        print(f"--- 処理開始: {word} ---")
        
        # 通常の荷物を送る
        el = wait.until(EC.element_to_be_clickable((By.ID, "normal")))
        driver.execute_script("arguments[0].click();", el)

        # 発払い
        el = wait.until(EC.element_to_be_clickable((By.ID, "nextLeavePay")))
        driver.execute_script("arguments[0].click();", el)

        # 個数（1個）
        el = wait.until(EC.element_to_be_clickable((By.ID, "one")))
        driver.execute_script("arguments[0].click();", el)

        # サイズ選択
        size_val = "C" if is_compact else "S"
        radio = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, f'input[name="viwb2050ActionBean.size"][value="{size_val}"]')))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", radio)
        driver.execute_script("arguments[0].click();", radio)

        # 品名入力
        input_box = driver.find_element(By.ID, "form_viwb2050ActionBean_itemName")
        input_box.clear()
        input_box.send_keys(word)

        # 荷物扱いチェック
        for val in ["02", "03"]:
            cb = driver.find_element(By.CSS_SELECTOR, f'input[name="handling"][value="{val}"]')
            driver.execute_script("arguments[0].click();", cb)
        
        # 非制限品確認チェック
        not_prohibited = driver.find_element(By.CSS_SELECTOR, 'input.js-notProhibitedItem')
        driver.execute_script("arguments[0].click();", not_prohibited)
        
        # 次へ
        next_btn = driver.find_element(By.CSS_SELECTOR, 'a.js-nextBtn.js-doTransition')
        driver.execute_script("arguments[0].click();", next_btn)
        
        # LINEでリクエスト
        wait.until(EC.element_to_be_clickable((By.ID, 'nextLine'))).click()
        
        # --- 日付選択の処理 ---
        try:
            date_el = wait.until(EC.presence_of_element_located((By.ID, "dateToShip")))
            date_select = Select(date_el)
            #ここで発送予定日を選択
            date_select.select_by_index(7) #0=今日、1=明日、2=明後日、3=3日後...
        except Exception as e:
            print(f"日付の選択に失敗しました: {e}")

        # 決定
        wait.until(EC.element_to_be_clickable((By.ID, 'next'))).click()
        
        # メッセージ入力
        msg_area = wait.until(EC.presence_of_element_located((By.ID, "form_viwb3050ActionBean_lineMessage")))
        msg_area.clear()
        msg_area.send_keys(word)
        
        # ニックネーム
        nick_field = driver.find_element(By.ID, "form_viwb3050ActionBean_nickName")
        nick_field.clear()
        nick_field.send_keys(word)
        
        # LINE友だちを選ぶボタン
        driver.find_element(By.ID, 'next').click()

        # モーダルOK
        try:
            time.sleep(2) 
            ok_btn = driver.find_element(By.XPATH, "//div[@id='modal_caution']//a[text()='OK']")
            driver.execute_script("arguments[0].click();", ok_btn)
        except Exception as e:
            print(f"OKボタンのクリックでエラーが発生しました: {e}")

        # ウィンドウ切り替え
        handles = driver.window_handles
        driver.switch_to.window(handles[-1])

        # QRコードログインボタン待機
        wait.until(EC.element_to_be_clickable((
            By.XPATH, "//a[contains(@class, 'MdBtn02') and .//span[text()='QRコードログイン']]"
        )))
        time.sleep(3) 

        # 新しいタブのURLを取得
        new_tab_url = driver.current_url
        logger.info(f"新しいタブのURL: {new_tab_url}")

        # LINEメッセージを解析
        line_message = analyze_yamato_line_url(new_tab_url)
        logger.info(f"LINEメッセージ変換完了: {word}")

        # 新しいタブを閉じる
        driver.close() 
        
        # 元のタブに戻る
        driver.switch_to.window(handles[0])

        # 最初に戻る
        driver.get(URL) 
        time.sleep(1) 
        login_btn = wait.until(EC.element_to_be_clickable((By.ID, 'portalEntrance')))
        login_btn.click()
        time.sleep(1) 

        # ★変更点：生成したメッセージを返す
        return line_message

    except Exception as e:
        logger.error(f"送信中にエラーが発生しました ({word}): {e}")
        raise e

def on_submit():
    # Chromeの起動
    driver = webdriver.Chrome(options=chrome_options)
    
    # ★変更点：メッセージを溜めるリストを作成
    all_messages = []

    try:
        driver.get(URL)
        login(driver)

        # フォームの数だけループ
        for i in range(10):
            # i番目の入力欄から値を取得
            entry = entries[i]
            checkbox = checkboxes[i]
            
            name = entry.get().strip()
            if not name:
                continue # 空欄ならスキップ

            # サニタイズ
            name = ''.join(c for c in name if ord(c) < 0x110000 and not (0xD800 <= ord(c) <= 0xDFFF))
            is_compact = checkbox.get()
            
            logger.info(f"処理開始: {name} (コンパクト: {is_compact})")
            
            # ★変更点：send_packageの結果（メッセージ）を受け取ってリストに追加
            result_msg = send_package(driver, name, is_compact)
            result_msg=result_msg+"\n\n"+"--------------------------------"+"\n\n"+"--------------------------------"+"\n\n"+"--------------------------------"+"\n\n"


            all_messages.append(result_msg)

        # ★変更点：ループ終了後、メッセージがあればまとめてGmail送信
        if all_messages:
            # メッセージを区切り線で繋げる
            full_body = "\n\n" + ("="*30) + "\n\n" + "\n\n".join(all_messages) + "\n\n" + ("="*30)
            
            # 件名を作成（件数を入れると分かりやすい）
            subject = f"【ヤマト配送自動入力】伝票作成完了通知 ({len(all_messages)}件)"
            
            # Gmail送信実行
            print("Gmail送信を開始します...")
            if send_mail(subject, full_body):
                logger.info("まとめメール送信成功")
            else:
                logger.error("まとめメール送信失敗")
            
            messagebox.showinfo("完了", f"すべての処理が完了しました。\nGmailを送信しました（計{len(all_messages)}件）。")
        else:
            messagebox.showinfo("完了", "処理対象がありませんでした。")

    except Exception as e:
        logger.error(traceback.format_exc())
        messagebox.showerror("エラー", f"予期せぬエラーが発生しました:\n{e}")
    finally:
        driver.quit()

# =====================================
# GUI構築
# =====================================
print(WELCOME_MESSAGE)
root = tk.Tk()
root.title("ヤマト配送自動入力 (Chrome版)")

frame = tk.Frame(root)
frame.pack(pady=20, padx=20)

entries = []
checkboxes = []

for i in range(10):
    tk.Label(frame, text=f"配送名 {i+1} :").grid(row=i, column=0, padx=5, pady=5)
    
    entry = tk.Entry(frame, width=30)
    entry.grid(row=i, column=1, padx=5, pady=5)
    entries.append(entry)

    var = tk.BooleanVar()
    cb = tk.Checkbutton(frame, variable=var, text="コンパクト")
    cb.grid(row=i, column=2, padx=5, pady=5)
    checkboxes.append(var)

submit_button = tk.Button(root, text="入力を開始する", command=on_submit, bg="#f39c12", fg="white", font=("MS Gothic", 12, "bold"))
submit_button.pack(pady=10)

root.mainloop()