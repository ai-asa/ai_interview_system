# %%
from ai_interview_system import InterviewSystem
import traceback
import multiprocessing
from src.voice.play_sound import subprocess_play
from src.firestore.firestore_polling import start_polling_subprocess

if __name__ == "__main__":
    queue1 = multiprocessing.Queue()
    queue2 = multiprocessing.Queue()
    queue_polling = multiprocessing.Queue()
    q_flag1 = multiprocessing.Queue()
    q_flag2 = multiprocessing.Queue()
    iv = InterviewSystem(queue1,queue2,q_flag1,q_flag2)
    p1 = multiprocessing.Process(target=subprocess_play,args=(queue1,q_flag1))
    p2 = multiprocessing.Process(target=iv.subprocess_streaming,args=(queue2,q_flag2))
    polling_subprocess = multiprocessing.Process(target=start_polling_subprocess, args=(queue_polling,))
    p1.start()
    p2.start()
    polling_subprocess.start()
    result = True
    while result == True:
        # ポーリングにてデータ取得した場合進む
        polling_data = queue_polling.get()
        try:
            result = iv.interview_system()
        except Exception as e:
            print("エラーが発生しました")
            print(traceback.format_exc())
            print(e)
            break

# %%
