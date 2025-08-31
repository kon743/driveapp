# ターミナル（コマンドプロンプト）で以下のコマンドを実行してください
# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

import os.path
import glob
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# アクセス権限の範囲を指定 (今回は読み取り専用のまま)
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# 認証情報ファイル (client_secret....json) の名前をここに指定
# ★★★ あなたのファイル名に書き換えてください ★★★
CLIENT_SECRET_FILE = 'client_secret_94798413997-dqkm5gilq8duvcelfn63944m4tmilp1f.apps.googleusercontent.com.json'

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

def main():
    """メインの処理"""
    # "token_*.json" という名前の認証ファイルを全て探し出す
    token_files = glob.glob('token_*.json')

    if not token_files:
        print("認証済みのGoogleアカウントが見つかりません。")
        print("まずはアカウントを追加してください。")
        # 登録処理を呼び出す (あとで実装)
        # add_new_account()
        return

    print(f"{len(token_files)}個のアカウントが見つかりました。スキャンを開始します...\n")

    # 見つかったアカウント全てに対してループ処理を行う
    for token_file in token_files:
        # ファイル名からアカウント名を抽出 (例: "token_user1.json" -> "user1")
        account_name = token_file.replace('token_', '').replace('.json', '')

        try:
            # 指定されたアカウント名で認証処理を呼び出す
            creds = authenticate(account_name)

            # 認証情報を使ってGoogle Drive APIへの接続を確立
            service = build('drive', 'v3', credentials=creds)

            # Drive APIを呼び出してファイル一覧を取得
            print(f'--- [{account_name}] のファイル一覧 (最大10件) ---')
            results = service.files().list(
                pageSize=10, fields="nextPageToken, files(name)").execute()
            items = results.get('files', [])

            if not items:
                print('ファイルが見つかりませんでした。')
            else:
                for item in items:
                    print(f'  - {item["name"]}')

            print('-----------------------------------------------------\n')

        except HttpError as error:
            print(f'[{account_name}] でAPIエラーが発生しました: {error}')
        except Exception as e:
            print(f'[{account_name}] で予期せぬエラーが発生しました: {e}')


if __name__ == '__main__':
    main()