# ターミナル（コマンドプロンプト）で以下のコマンドを実行してください
# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

import os.path
import glob
from googleapiclient.http import MediaFileUpload 
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

#アクセス権限の範囲を指定 (読み取り専用から、読み書き可能に変更)
SCOPES = ['https://www.googleapis.com/auth/drive']

# 認証情報ファイル (client_secret....json) の名前をここに指定
# ★★★ あなたのファイル名に書き換えてください ★★★
CLIENT_SECRET_FILE = 'client_secret_94798413997-23kqbvko2vu14bh2nohubspb2ktsejla.apps.googleusercontent.com.json'

def authenticate(account_name):
    """指定されたアカウント名で認証を行い、有効な認証情報を返す"""
    creds = None
    # アカウントごとにtokenファイルを分ける (例: token_user1.json)
    token_file = f'token_{account_name}.json'

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    # 有効な認証情報がない、または期限切れの場合は、ログイン・更新を行う
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print(f'{account_name} のアクセストークンを更新します...')
            creds.refresh(Request())
        else:
            print(f'{account_name} の認証が必要です。ブラウザを起動します...')
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # 次回のために、新しい認証情報をファイルに保存
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
        print(f'{account_name} の認証情報を {token_file} に保存しました。')

    return creds

def upload_file(service, file_path, account_name):
    """指定されたファイルをGoogle Driveにアップロードする"""
    if not os.path.exists(file_path):
        print(f"エラー: アップロードするファイル '{file_path}' が見つかりません。")
        return

    file_name = os.path.basename(file_path)
    print(f"[{account_name}] へ '{file_name}' のアップロードを開始します...")

    try:
        # アップロードするためのメディアオブジェクトを作成
        media = MediaFileUpload(file_path, resumable=True)

        # アップロードするファイルの情報 (メタデータ) を設定
        file_metadata = {'name': file_name}

        # Drive APIを呼び出してアップロードを実行
        request = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        )

        # 進捗を表示するためのループ (resumable upload)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"進捗: {int(status.progress() * 100)}%")

        print(f"[{account_name}] へのアップロードが完了しました！ ファイルID: {response.get('id')}")

    except HttpError as error:
        print(f"アップロード中にAPIエラーが発生しました: {error}")
    except Exception as e:
        print(f"アップロード中に予期せぬエラーが発生しました: {e}")

# ... def main(): はこの下に続く ...

def main():
    # 1. アップロードするファイルの準備
    # このプログラムと同じフォルダに 'upload_test.txt' という名前で
    # テキストファイルを作成し、中に何か文字を書いておいてください。
    file_to_upload = 'upload_test.txt'

    # 2. どのアカウントにアップロードするか指定
    # 'user1', 'user2' など、あなたが登録したアカウント名を指定してください。
    upload_target_account = 'user1'

    print(f"'{upload_target_account}' アカウントを使って '{file_to_upload}' をアップロードします。")

    try:
        # 指定されたアカウントで認証
        creds = authenticate(upload_target_account)
        # Google Drive API サービスを構築
        service = build('drive', 'v3', credentials=creds)
        # アップロード関数を呼び出し
        upload_file(service, file_to_upload, upload_target_account)

    except Exception as e:
        print(f"処理全体でエラーが発生しました: {e}")


if __name__ == '__main__':
    main()