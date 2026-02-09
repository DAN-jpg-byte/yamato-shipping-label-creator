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
    wait = WebDriverWait(driver, 15)
    try:
        print(f"--- 処理開始: {word} ---")
        
        # 通常の荷物を送る
        el = wait.until(EC.element_to_be_clickable((By.ID, "normal")))
        driver.execute_script("arguments[0].click();", el)
        print("1. 通常ボタンOK")

        # 発払い
        el = wait.until(EC.element_to_be_clickable((By.ID, "nextLeavePay")))
        driver.execute_script("arguments[0].click();", el)
        print("2. 発払いOK")

        # 個数（1個）
        el = wait.until(EC.element_to_be_clickable((By.ID, "one")))
        driver.execute_script("arguments[0].click();", el)
        print("3. 個数OK")

        # サイズ選択 (ここが怪しい場合が多い)
        size_val = "C" if is_compact else "S"
        radio = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, f'input[name="viwb2050ActionBean.size"][value="{size_val}"]')))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", radio) # 中央にスクロール
        driver.execute_script("arguments[0].click();", radio)
        print(f"4. サイズ({size_val})選択OK")

        # 品名入力
        input_box = driver.find_element(By.ID, "form_viwb2050ActionBean_itemName")
        input_box.clear()
        input_box.send_keys(word)
        print("5. 品名入力OK")

        # 荷物扱いチェック (精密機器/ワレモノ)
        for val in ["02", "03"]:
            cb = driver.find_element(By.CSS_SELECTOR, f'input[name="handling"][value="{val}"]')
            driver.execute_script("arguments[0].click();", cb)
            print(f"6. 荷物扱いチェック({val})OK")
        # 非制限品確認チェック
        not_prohibited = driver.find_element(By.CSS_SELECTOR, 'input.js-notProhibitedItem')
        driver.execute_script("arguments[0].click();", not_prohibited)
        print("7. 非制限品確認チェックOK")
        # 次へ
        next_btn = driver.find_element(By.CSS_SELECTOR, 'a.js-nextBtn.js-doTransition')
        driver.execute_script("arguments[0].click();", next_btn)
        print("8. 次へOK")
        # LINEでリクエスト
        wait.until(EC.element_to_be_clickable((By.ID, 'nextLine'))).click()
        
        # 決定
        wait.until(EC.element_to_be_clickable((By.ID, 'next'))).click()
        print("9. 決定OK")
        # メッセージ入力
        msg_area = wait.until(EC.presence_of_element_located((By.ID, "form_viwb3050ActionBean_lineMessage")))
        msg_area.clear()
        msg_area.send_keys(word)
        print("10. メッセージ入力OK")
        # ニックネーム
        nick_field = driver.find_element(By.ID, "form_viwb3050ActionBean_nickName")
        nick_field.clear()
        nick_field.send_keys(word)
        print("11. ニックネーム入力OK")
        # LINE友だちを選ぶボタン
        driver.find_element(By.ID, 'next').click()
        print("12. LINE友だちを選ぶボタンOK")


        # 画面遷移の完了を待つためのバッファ
        time.sleep(1) 

        # --- 最初に戻るための処理（ここを強化） ---
        # 1. 確実にURLを指定してトップへ戻る（refreshより確実）
        driver.get(URL) 
        print("13-1. トップURLへ再アクセスOK")
        
        print("14. 最初に戻るOK")
        time.sleep(1) 

        # ログインボタン表示待ち
        login_btn = wait.until(EC.element_to_be_clickable((By.ID, 'portalEntrance')))
        login_btn.click()
        time.sleep(1) 

    except Exception as e:
        logger.error(f"送信中にエラーが発生しました ({word}): {e}")
        raise e

def on_submit():
    # Chromeの起動（Selenium 4.6+ の自動管理機能を利用）
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(URL)
        login(driver)

        for i in range(10):
            name = entries[i].get().strip()
            if not name:
                continue

            # サニタイズ
            name = ''.join(c for c in name if ord(c) < 0x110000 and not (0xD800 <= ord(c) <= 0xDFFF))
            is_compact = checkboxes[i].get()
            
            logger.info(f"処理開始: {name} (コンパクト: {is_compact})")
            send_package(driver, name, is_compact)

        messagebox.showinfo("完了", "すべての入力が完了しました。")
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