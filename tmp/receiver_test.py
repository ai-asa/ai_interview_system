# %%
import multiprocessing
import configparser
from src.server.watchdog_receiver import watchdog_run

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.txt')
    path = config.get('CONFIG', 'receiver_path', fallback="G:/マイドライブ/interview_system/receiver")
    queue = multiprocessing.Queue()
    wg = watchdog_run(path,queue)
    p = multiprocessing.Process(target=watchdog_run,args=(path,queue))
    print(queue.get())

# %%
