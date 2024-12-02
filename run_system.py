# %%
import configparser
from dotenv import load_dotenv
import traceback
import multiprocessing
import logging
from src.server.watchdog_receiver import watchdog_run
import json
load_dotenv()


class LINEBotProcess:
    def __init__(self):
        pass

    def dump_and_splitte(self,data):
        # タグを確認してif条件分岐
        data["contents"] = json.loads(data["contents"])
        if data["tag"] == "LINE":
            # 辞書をリストに置き換え
            data["contents"] = [event for event in data["contents"]["events"]]
        elif data["tag"] == "GoogleForm":
            pass
        else:
            pass
        return data

    def notification(self,data_list):
        # queueを受け取った分だけ処理を回す
        for data in data_list:
            data = json.loads(data)
            data = self.dump_and_splitte(data)
            # タグを確認してif条件分岐
            if data["tag"] == "LINE":
                # typeを確認して処理をif分岐
                # LINE応答部分の処理は専用のクラスを作成して処理したい
                pass
            elif data["tag"] == "GoogleForm":
                pass
            else:
                pass


        pass

if __name__ == "__main__":
    lp = LINEBotProcess()
    config = configparser.ConfigParser()
    config.read('config.txt')
    path = config.get('CONFIG', 'receiver_path', fallback="G:/マイドライブ/interview_system/receiver")
    queue = multiprocessing.Queue()
    wg = watchdog_run(path,queue)
    # ここで並列処理システムを管理→動的に変化させる部分はそれぞれで管理する
    p = multiprocessing.Process(target=watchdog_run,args=(path,queue))
    # 常時起動するシステム部分はここで開始
    p.start()
    while True:
        try:
            data_list = queue.get()
            data = data_list if data_list else None
            lp.notification(data)
        except Exception as e:
            print("エラーが発生しました。システム管理者に問い合わせてください")
            print(traceback.format_exc())
            print(e)
            exit(200)


# 並列システム、メインシステム
# ・通知の受信→一つのサブプロセスで管理する
# ・LINEボット関係→最低でも2つくらいは必要？
# ・面接AIシステム→これだけで3つくらい並列させている？これ自体がメイン
# →多分最小構成でも6つくらいは並列処理させる必要がある
# →必要に応じて立ち上げたり削除したりして、動的に変化させるシステムにしたい

# 初期設定
#   リッチメニューを作成
#   DBの読み込み
#   タイムスケジュールの読み込み
# 1秒おきに通知の確認
#   ファイルが更新されているか
#   タイムスケジュールからの指示があるか
# 通知がある場合の処理
#   ファイルを読み込み、通知の内容を確認する
#   通知の種類
#       LINEの登録・応答
#       事前設定したプッシュトークの時間
#       Googleフォームの入力完了
#       面接予定日（時間）
#       通話面接の終了
#       など
#   LINE通知の場合の処理
#       登録の場合、ユーザーIDをDBに保存する
#       ユーザーの何らかのアクションの場合、ステータスと進行度を参照して、特定の応答を行う
#           ユーザーIDと紐づいたDBデータ、フォルダの内容を更新する
#   プッシュトークの時間の場合
#       ユーザーごとのステータスと進行度、登録してからの経過時間に応じて、特定のプッシュトークを送る
#   Googleフォームの入力完了の場合
#       Googleフォームの内容を構造化データに変換してユーザーIDと紐づけて保存
#       ユーザーのステータスを進める
#   面接予定日（時間）
#       ユーザーIDを参照してステータスを更新する
#       ビデオ通話URLを作成し、プッシュ通知
#       ビデオ通話URLでWebブラウザの起動、面接、閉じるまでの自動化
#   通話面接の終了
#       ユーザーIDを参照してステータスを更新する
#       ビデオ通話の結果を受取り、プッシュ通知とステータスの更新を行う
#       結果により、半年間後に再度面接を受けられるようにタイムスケジュールを設定する
# %%
