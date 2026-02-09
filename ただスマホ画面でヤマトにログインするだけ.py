import config
from logging_config import setup_logging
from logging import getLogger
import os
from pathlib import Path
from dotenv import load_dotenv
import time
import tkinter as tk
from tkinter import messagebox

# Selenium関連
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# =====================================
# 環境設定
# =====================================
load_dotenv()
USER = config.USER
PASS = config.PASS
URL = "https://sp-send.kuronekoyamato.co.jp/smpTaqWeb/"

# Chrome設定
chrome_options = Options()
mobile_emulation = {"deviceName": "iPhone 12 Pro"}
chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

# 実行時にブラウザを閉じないようにする設定（念のため）
chrome_options.add_experimental_option("detach", True)

def login_only():
    """ログインのみ実行するメイン処理"""
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 15)
    
    try:
        driver.get(URL)
        print("ヤマト運輸サイトにアクセス中...")

        # ログインボタンをクリック
        login_btn = wait.until(EC.element_to_be_clickable((By.ID, 'portalEntrance')))
        login_btn.click()
        
        # ID/PASS入力
        user_field = wait.until(EC.presence_of_element_located((By.ID, 'login-form-id')))
        user_field.clear()
        user_field.send_keys(USER)

        pass_field = driver.find_element(By.ID, 'login-form-password')
        pass_field.clear()
        pass_field.send_keys(PASS)

        # ログインボタン押下
        driver.find_element(By.ID, 'login-form-submit').click()
        print("ログイン情報を送信しました。")

        # ログイン成功後の画面（トップ画面など）の要素が出るまで待機
        wait.until(EC.presence_of_element_located((By.ID, 'normal')))
        print("ログイン成功！そのままブラウザをお使いいただけます。")

        # 無限ループで維持（手動で閉じるまで待機）
        while True:
            time.sleep(10)
            # ブラウザが閉じられたかチェック（閉じられていたらループを抜ける）
            if not driver.window_handles:
                break

    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        print("プログラムを終了します。")
        driver.quit()

if __name__ == "__main__":
    login_only()