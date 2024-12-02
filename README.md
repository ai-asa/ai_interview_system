# ai interview system




https://github.com/user-attachments/assets/2afae341-8e25-4d21-b619-e725f2776d8e




Live2D AIアバターによる自動面接システムです。LINEボットを通じて面接予約から実施までを自動化し、音声対話による面接を実現します。

## 機能

- LINE経由での面接予約・管理(google calender)
- 音声認識による面接対話
- AIによる面接官のシミュレーション
- 面接結果の自動判定

## 必要要件

- Python 3.8以上
- OpenAI API Key
- LINE Messaging API
- OBS Studio (28.0.0以上)
- VB-Audio Virtual Cable

## インストール

1. リポジトリをクローン:

    git clone https://github.com/ai-asa/ai_interview_system.git

2. 依存パッケージをインストール:

    pip install -r requirements.txt

3. 環境変数の設定:
`.env`ファイルを作成し、以下の項目を設定:

    [APIKEY]
    OPENAI_API_KEY=your_openai_api_key

    [OBS]
    OBS_WS_HOST=localhost
    OBS_WS_PORT=4455
    OBS_WS_PASSWORD=your_obs_password

## 使用方法

1. OBS Studioを起動し、WebSocket設定を有効化

2. システムを起動:

    python main.py

3. LINEボットから面接予約を行い、指示に従って面接を実施

## システム構成

- `main.py`: メインシステム起動スクリプト
- `run_system.py`: LINE通知受信・管理システム
- `ai_interview_process.py`: 面接処理メインロジック
- `src/`: 各種機能モジュール
  - `firestore/`: Firestore連携モジュール
  - `line/`: LINE Bot連携モジュール
  - `obs/`: OBS連携モジュール
  - `openai/`: OpenAI API連携モジュール
  - `voice/`: 音声処理モジュール
  - その他

## 注意事項

- 本システムは通常公開されません。第三者のクローンやコピーは禁止しています。
- 面接データは適切に管理し、個人情報の取り扱いには十分注意してください
