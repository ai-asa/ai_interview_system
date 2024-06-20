# %%
from dotenv import load_dotenv
import configparser
import json
import os
import re
import soundfile
from src.openai.openai_adapter import OpenaiAdapter
from src.prompt.get_prompt import GetPrompt
from src.openai.whisper_adapter import WhisperApiAdapter
from src.voice.stylebertvits2_adapter import StyleBertVITS2_Adapter
from src.obs.obs_websocket_adapter import OBSAdapter
load_dotenv()

class InterviewSystem:
    LINE_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN')
    config = configparser.ConfigParser()
    config.read('config.txt')
    gpt_35 = config.get('CONFIG', 'gpt_35', fallback='gpt-4-preview')
    gpt_40 = config.get('CONFIG', 'gpt_40', fallback='gpt-3.5-turbo-0125')
    templete_json_path = config.get('CONFIG', 'templete_json_path', fallback='./docs/interview_templete/templete.json')
    templete_audiofile_path = config.get('CONFIG', 'templete_audiofile_path', fallback='./data/templete_audio/')
    with open(templete_json_path,'r',encoding='utf-8') as f:
        templete_json = json.load(f)
    
    oa = OpenaiAdapter()
    gp = GetPrompt()
    wa = WhisperApiAdapter()
    sa = StyleBertVITS2_Adapter()
    ob = OBSAdapter()

    def __init__(self,queue1,queue2,q_flag1,q_flag2):
        self.status = 0
        self.conversations = []
        self.conversations_sub = []
        self.timer = 0
        self.queue1 = queue1
        self.queue2 = queue2
        self.q_flag1 = q_flag1
        self.q_flag2 = q_flag2
        self._get_templete_audio()
        pass

    def _get_templete_audio(self):
        for templete in self.templete_json:
            text_list = templete["ai_text"]
            audio_list = []
            for text in text_list:
                file_path = os.path.join(self.templete_audiofile_path, f"{text}.wav")
                if os.path.exists(file_path):
                    data, rate = soundfile.read(file_path)
                else:
                    data, rate = self.sa.get_voice_data(text)
                    soundfile.write(file_path, data, rate)
                audio_list.append((data,rate))
            templete["audio_data_list"] = audio_list
            if templete["status"] == "one_more_time":
                self.common_audio = (data,rate)
            elif templete["status"] == "filler":
                self.filler_audio = (data,rate)
        pass

    def _status_hundler(self):
        response = self._openai_response(flag=1,temperature=1)
        if response:
            print(f"==== 話題遷移: True/False ====")
            print(response)
            if re.search(r'\bTrue\b|\btrue\b', response):
                return True
            elif re.search(r'\bFalse\b|\bfalse\b', response):
                return False
            else:
                print("値がブール値で返されませんでした。")
        pass

    def _get_templete_text_and_audio(self) -> list:
        for templete in self.templete_json:
            if templete["status"] == self.status:
                text_list = templete["ai_text"]
                audio_list = templete["audio_data_list"]
                break
        return text_list, audio_list

    def _read_text(self,text,flag):
        if flag == 0:
            print("面接官: ",text)
            data,rate = self.sa.get_voice_data(text)
            self.queue1.put((data,rate))
            self.ob.set_subtitle_ai(text)
        else:
            print("求職者: ",text)
        pass

    def _openai_response(self,flag,temperature):
        prompt = self.gp.get_prompt(self.conversations,flag,self.status)
        return self.oa.openai_chat(self.gpt_40, prompt, temperature)
    
    def _openai_response_judg(self):
        flag = 0
        temperature = 0.5
        prompt = self.gp.get_prompt(self.conversations_sub,flag,self.status)
        response = self.oa.openai_chat(self.gpt_40, prompt, temperature)
        if re.search(r'\b採用\b|\b採用\b', response):
            result = "採用"
        elif re.search(r'\bF不採用\b|\b不採用\b', response):
            result = "不採用"
        else:
            print("値が指定したフォーマットで返されませんでした。")
            pass
        return result
    
    def _judg_by_gpt(self,text):
        if self.status == "test_audio" or self.status == "test_microphone":
            prompt = self.gp.get_judg_prompt(text,self.status)
        else:
            prompt = self.gp.get_judg_conversation(text,self.conversations_sub)
        print(prompt)
        response = self.oa.openai_chat(self.gpt_40, prompt, temperature=0.8)
        print(response)
        if re.search(r'\bTrue\b|\btrue\b', response):
            return True
        elif re.search(r'\bFalse\b|\bfalse\b', response):
            return False
        else:
            return False

    def _correct_response(self,text):
        pattern_to_remove = r'[\[\]"\{\}:;]|面接官'
        # テキスト中に指定したパターンが含まれているかチェック
        if re.search(pattern_to_remove, text):
            print("Specified symbols or words found in text. Removing...")
            # 指定したパターンを含む部分を空文字に置換して削除
            text = re.sub(pattern_to_remove, '', text)
        else:
            print("No specified symbols or words found in text.")
        return text

    def interview_system_text(self) -> bool:
        if self.status == 0:
            ai_text = self._templete_text()
            self._read_text(ai_text,flag=0)
            self.status = 1
            self.conversations.append("{面接官: " + ai_text + "}")
            self.conversations_sub.append("{面接官: " + ai_text + "}")
        else:
            user_text = input("キーボードで入力：")
            self.conversations.append("{求職者: " + user_text + "}")
            self.conversations_sub.append("{求職者: " + user_text + "}")
            self._read_text(user_text,flag=1)
            status_now = self.status
            self._status_hundler()
            if self.status == status_now and self.timer == 3:
                self.status += 1
            self.timer += 1
            if self.status == 8:
                ai_text = self._templete_text()
                self._read_text(ai_text,flag=0)
                ai_text = self._openai_response_judg()
                print("=== 採用判定 ===")
                print(ai_text)
                return False
            elif self.status != status_now:
                self.conversations.append("=== 次の話題へ変わりました ===")
                ai_text = self._templete_text()
                self._read_text(ai_text,flag=0)
                self.timer = 0
            ai_text = self._openai_response(flag=0,temperature=0.5)
            self._read_text(ai_text,flag=0)
            self.conversations.append("{面接官: " + ai_text + "}")
            self.conversations_sub.append("{面接官: " + ai_text + "}")
        return True
    
    def _update_conversaitions(self,text:str):
        self.conversations.append(text)
        self.conversations_sub.append(text)
        pass

    def subprocess_streaming(self,queue,q_flag2):
        text = ""
        full_text = ""
        while True:
            char = queue.get()
            if char in [':','{','}']:
                pass
            elif char in [',','.','、','。','?','？','!','！']:
                text += char
                full_text += text
                data,rate = self.sa.get_voice_data(text)
                self.queue1.put((data,rate))
                self.ob.set_subtitle_ai(full_text)
                text = ""
            elif char == 'END':
                self.queue1.put("END")
                q_flag2.put(0)
                text = ""
                full_text = ""
            else:
                text += char

    def _run_interview_ai(self,flag):
        prompt = self.gp.get_prompt(self.conversations,flag,self.status)
        ai_text = ""
        for text_chunk in self.oa.openai_chat_streaming(self.gpt_40, prompt, temperature=0.5):
            self.queue2.put(text_chunk)
            ai_text += text_chunk
        # ENDマーカー
        self.queue2.put("END")
        print("面接官: ",ai_text)
        self._update_conversaitions("{面接官: " + ai_text + "}")
        ai_text = ""
        pass

    def _blocking(self):
        self.q_flag1.get()
        self.q_flag2.get()
        pass

    def _visualize_queue(self,q):
        temp_list = []
        while not q.empty():
            item = q.get()
            temp_list.append(item)
        
        # キューの内容をリストにコピーした後、元に戻す
        for item in temp_list:
            q.put(item)
        
        return temp_list  # 可視化のため、リストを返す

    def test_phase(self) -> bool:
        if self.status in ["test_audio" ,"test_microphone"]:
            self.ob.set_subtitle_explain2("音声が認識されない場合は、マイク設定、周辺環境をご確認ください。また、解決しない場合はLINEメニューの問い合わせフォームをご確認ください")
            ai_text_list, audio_list = self._get_templete_text_and_audio()
            for i in range(len(ai_text_list)):
                self.queue1.put(audio_list[i])
                self.queue1.put("END")
                self.ob.set_subtitle_ai(ai_text_list[i])
                self.q_flag1.get()
            judg = False
            while judg == False:
                judg = self._judg_by_gpt(self.wa.detect_audio(option=2))
        elif self.status in ["interview_qualification","interview_it_skill", "interview_work_experience", "interview_motivation", "interview_objective"]:
            self._run_interview_ai(flag=0)
            self._blocking()
            judg = False
            while judg == False:
                user_text = self.wa.detect_audio(option=2)
                judg = self._judg_by_gpt(user_text)
                if judg == False:
                    self.queue1.put(self.common_audio)
                    self.queue1.put("END")
                    self.q_flag1.get()
            self._update_conversaitions("{求職者: " + user_text + "}")
            print("求職者: ",user_text)
            if self._status_hundler():
                return True
            # filler
            self.queue1.put(self.filler_audio)
            return False
        elif self.status == "judg":
            self.ob.set_subtitle_explain1("面接が終了いたしました。通話画面から退出してください。")
            self.ob.set_subtitle_explain2("")
            return True
    
    def interview_system(self) -> bool:
        test_status_list = ["test_audio","test_microphone"]
        interview_status_list = ["interview_qualification","interview_it_skill", "interview_work_experience", "interview_motivation", "interview_objective","judg"]
        self.ob.set_subtitle_explain1("通話画面に表示される字幕に従って面接を進行してください。問題が発生した場合はLINEからサポートに問い合わせください")
        for status in test_status_list:
            self.status = status
            self.test_phase()
        for status in interview_status_list:
            self.status = status
            self.conversations.append("=== 次の話題へ変わりました ===")
            ai_text_list, audio_list = self._get_templete_text_and_audio()
            for i in range(len(ai_text_list)):
                self.queue1.put(audio_list[i])
                self.queue1.put("END")
                self.ob.set_subtitle_ai(ai_text_list[i])
                self._update_conversaitions("{面接官: " + ai_text_list[i] + "}")
                self.q_flag1.get()
            value = False
            timer = 0
            while value == False and timer < 5:
                value = self.test_phase()
                timer += 1
        return True

    def interview_system_audio(self) -> bool:
        if self.status == 0:
            # 音声認識のテストフェーズ
            # LINE画面にて、「通話画面に表示される字幕に従って、面接を開始してください。字幕が表示されない場合は、サポートに問い合わせください」
            # 音声認識の確認
            #   常設字幕「音声が認識されない場合は、マイク設定、周辺環境をご確認ください。また、解決しない場合はLINEメニューの問い合わせフォームをご確認ください」
            ai_text = self._templete_text()
            self._read_text(ai_text,flag=0)
            judg = False
            while judg == False:
                user_text = self.wa.detect_audio(option=2)
                judg = self._judg_by_gpt(user_text)
            self.status += 1
            # 音声再生の確認
            # マイクテストを完了した旨を通知
            ai_text = self._templete_text()
            judg = False
            self._read_text(ai_text,flag=0)
            while judg == False:
                user_text = self.wa.detect_audio(option=2)
                judg = self._judg_by_gpt(user_text)
            #   常設字幕「音声が聞こえない場合は、スピーカー設定をご確認ください。また、解決しない場合はLINEメニューの問い合わせフォームをご確認ください」
            #   → はいの場合は、面接フェーズへ進行
            self.status += 1
            ai_text = self._templete_text()
            self._read_text(ai_text,flag=0)
            self.conversations.append("{面接官: " + ai_text + "}")
            self.conversations_sub.append("{面接官: " + ai_text + "}")
            self.status += 1
            ai_text = self._templete_text()
            self._read_text(ai_text,flag=0)
            self.conversations.append("{面接官: " + ai_text + "}")
            self.conversations_sub.append("{面接官: " + ai_text + "}")
            ai_text = self._openai_response(flag=0,temperature=0.5)
            ai_text = self.correct_response(ai_text)
            self._read_text(ai_text,flag=0)
            self.conversations.append("{面接官: " + ai_text + "}")
            self.conversations_sub.append("{面接官: " + ai_text + "}")
        else:
            judg = False
            while judg == False:
                user_text = self.wa.detect_audio(option=2)
                judg = self._judg_by_gpt(user_text)
                #ここで、質問に答えられているかをジャッジする
                if judg == False:
                    ai_text = "すみません、うまく聞き取れませんでした。初めからもう一度お願いします。"
                    self._read_text(ai_text,flag=0)
            self.conversations.append("{求職者: " + user_text + "}")
            self.conversations_sub.append("{求職者: " + user_text + "}")
            self._read_text(user_text,flag=1)
            status_now = self.status
            self._status_hundler()
            if self.status == status_now and self.timer == 3:
                self.status += 1
            self.timer += 1
            if self.status == 8:
                ai_text = self._templete_text()
                self._read_text(ai_text,flag=0)
                ai_text = self._openai_response_judg()
                print("=== 採用判定 ===")
                print(ai_text)
                return False
            elif self.status != status_now:
                self.conversations.append("=== 次の話題へ変わりました ===")
                ai_text = self._templete_text()
                self._read_text(ai_text,flag=0)
                self.timer = 0
            ai_text = self._openai_response(flag=0,temperature=0.5)
            ai_text = self.correct_response(ai_text)
            self._read_text(ai_text,flag=0)
            self.conversations.append("{面接官: " + ai_text + "}")
            self.conversations_sub.append("{面接官: " + ai_text + "}")
        return True
# 追加機能
#   AI音声再生中には音声認識を行わない
#   gptのストリーミング実行
#   単語ごとの音声合成
#   適切な並列処理化
# %%
