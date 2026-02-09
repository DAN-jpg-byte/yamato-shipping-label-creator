# logging_config.py
# ログの設定をまとめて管理するファイルです
# アプリ全体のログ出力の形式・出力先などをここで一括設定します

import logging
import logging.config  # ログ設定用の機能を使うためにインポート

# ログ設定を行う関数
# log_filename にはログを書き出すファイルのパスを指定します
# デフォルトでは logs/my_app.log に出力されます
def setup_logging(log_filename='logs/my_app.log'):
    # ログ設定を辞書（dict）形式で定義
    config = {
        # ログ設定のバージョン。必ず "1" にする決まりです（変更不可）
        "version": 1,

        # すでに作られている他のロガー（例えばライブラリ内部のロガー）を無効化しない
        # これを True にすると、外部ライブラリのログが出なくなるので通常は False にしておきます
        "disable_existing_loggers": False,

        # フォーマッタ（ログの見た目）を定義
        "formatters": {
            "simple": {
                # ログの出力形式を指定
                # %(asctime)s: 日時, %(name)s: ロガー名（モジュール名）
                # %(lineno)s: 行番号, %(funcName)s: 関数名
                # %(levelname)s: ログレベル（INFOなど）, %(message)s: メッセージ本文
                "format": "%(asctime)s %(name)s:%(lineno)s %(funcName)s [%(levelname)s]: %(message)s"
            }
        },

        # ハンドラ（ログの出力先）を定義　画面に出力したり、ファイルに出力したりするための設定
        "handlers": {
            # コンソール（画面）出力用のハンドラ(画面に出すか出さないかの設定)
            "consoleHandler": {
                "class": "logging.StreamHandler",  # 標準出力（printと同じ）に出す
                "level": "DEBUG",                   # このハンドラが出す最小レベル（INFO以上）
                "formatter": "simple",             # 上で定義したフォーマッタを使う
                "stream": "ext://sys.stdout"       # 標準出力（ターミナル）に出力
            },


            # ファイル出力用のハンドラ(ファイルに出すか出さないかの設定)
            "fileHandler": {
                # ファイルサイズに応じて自動的にログを分割してくれるハンドラ
                "class": "logging.handlers.RotatingFileHandler",

                # このハンドラで出力するログレベル
                "level": "INFO",

                # フォーマットの設定（いつ・どこで・どんな内容かがわかるように）
                "formatter": "simple",

                # ログファイルの保存先（ログがここに追記されていく）
                "filename": log_filename,

                # ファイルの最大サイズ（バイト数）
                # 例：25MB = 25 * 1024 * 1024
                # "maxBytes": 25 * 1024 * 1024,  # 約25MBでファイルをローテーション約5MB。1MB = 1024×1024バイト
                "maxBytes": 50 * 1024 ,  # 約25MBでファイルをローテーション約5MB。1MB = 1024×1024バイト


                # 古いログファイルを何個まで保存するか
                # backupCount=3なら、最大4個のファイルが存在（現行 + 3世代）
                # "backupCount": 3,
                "backupCount": 1,                

                # ファイルの文字コード（日本語ログでも文字化けしないように）
                "encoding": "utf-8"
            }

        },












        # 特定のロガー（ここでは __main__）の設定
        "loggers": {
            # 実行ファイルが __main__（メインスクリプト）の場合の設定
            "__main__": {
                "level": "DEBUG",                         # DEBUGレベルから出力（開発中向け）
                "handlers": ["consoleHandler", "fileHandler"],  # 2つのハンドラで出力
                "propagate": False                        # 親（ルート）ロガーにログを流さない
            }
        },

        # ルートロガー（明示的にgetLogger()しなかったときに使われるロガー）
        # これも一応設定しておきます（予備）
        "root": {
            "level": "INFO",                         # INFO以上のログを出す
            "handlers": ["consoleHandler"]           # 画面に出力（ファイルには出さない）
        }
    }

    # 上で定義した辞書を使ってログ設定を反映させる
    logging.config.dictConfig(config)
