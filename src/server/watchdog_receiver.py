# %%
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import json

class MyHandler(FileSystemEventHandler):
    def __init__(self, queue):
        self.queue = queue

    def on_created(self, event):
        print(f"作成を検知しました: {event.src_path}")
        try:
            # ファイルが完全に書き込まれるのを待つ
            #time.sleep(0.1)  # 0.1秒間待機
            # ファイル名でデータ種類を分けているので、ファイル名でif分岐する
            with open(event.src_path, 'r', encoding='utf-8') as f:
                contents = f.read()
                print(contents)
                # データ種類のタグとデータの辞書型をputする
                self.queue.put(contents)
        except PermissionError:
            print(f"アクセス権限エラー: {event.src_path}")
        except IOError as e:
            print(f"ファイルオープンエラー: {e}")
        except json.JSONDecodeError:
            print("エラー：読み込まれたファイルが有効なJSON形式ではありません。")
        except Exception as e:
            print(f"その他のエラー: {e}")

def watchdog_run(path, queue):
    event_handler = MyHandler(queue)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# %%

"""
LINEボットの通知を取得するプログラム
→GASでLINEの通知内容をmessage_data.jsonファイル形式で出力する
→watchdogで監視して、取得する→内容をqueueにいれる

queueを受け取る側のシステム
LINEの通知内容によって処理を分岐
→LINEボットの登録の場合
→登録されたユーザーのユーザーIDを取得し、データベースに保存。ステータスの初期化、リッチメニューを反映、ユーザーフォルダを作成

リッチメニューのボタンを押した際の通知を受け取ることは可能？
→受け取れたら、それをトリガーに次のステータス

面接時の録画をどうするか...
"""