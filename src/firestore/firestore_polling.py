# %%
import time
import datetime
import configparser
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from dotenv import load_dotenv

def initialize_firestore():
    load_dotenv()
    config = configparser.ConfigParser()
    config.read('config.txt')
    credentials_path = config.get('CONFIG', 'credentials_path', fallback='./gcp/secret-key/credentials_file.json')
    cred = credentials.Certificate(credentials_path)
    firebase_admin.initialize_app(cred)
    return firestore.client()

def get_user_data(db, user_id):
    user_doc_ref = db.collection('userDatas').document(user_id)
    user_doc = user_doc_ref.get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        return user_data.get('datas', {}).get('google_form_datas', {})
    return {}

def poll_firestore(db, queue):
    while True:
        # 次の時間の00分まで待機
        now = datetime.datetime.now()
        next_hour = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
        wait_time = (next_hour - now).total_seconds()
        time.sleep(wait_time)

        # 1時間後の時刻を取得
        one_hour_later = (next_hour + datetime.timedelta(hours=1)).strftime("%Y%m%d%H")
        
        # Firestoreからデータを取得
        doc_ref = db.collection('reserveDocs').document(one_hour_later)
        doc = doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            user_ids = data.get('user_id', [])
            meeting_urls = data.get('meeting_url', [])
            
            print(f"Data found for time: {one_hour_later}")
            print(f"User IDs: {user_ids}")
            print(f"Meeting URLs: {meeting_urls}")
            
            # 各ユーザーのGoogle Form dataを取得
            user_form_data = {}
            for user_id in user_ids:
                user_form_data[user_id] = get_user_data(db, user_id)
            
            # データをメインプロセスに送信
            queue.put({
                'time': one_hour_later,
                'user_ids': user_ids,
                'meeting_urls': meeting_urls,
                'user_form_data': user_form_data
            })
        else:
            print(f"No data found for time: {one_hour_later}")

def start_polling_subprocess(queue):
    db = initialize_firestore()
    poll_firestore(db, queue)