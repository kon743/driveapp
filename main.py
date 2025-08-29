import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

    # アクセス権限の範囲を指定 (読み取り専用)
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def main():
        creds = None
        # token.jsonファイルは、ユーザーのアクセストークンとリフレッシュトークンを保存します。
        # 認証フローが初めて完了したときに自動的に作成されます。
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        # 有効な認証情報がない場合は、ユーザーにログインしてもらいます。
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # ★★★ ここが一番重要です！★★★
                # '...' の部分を、あなたがダウンロードしたJSONファイルの名前に書き換えてください。
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secret_94798413997-dqkm5gilq8duvcelfn63944m4tmilp1f.apps.googleusercontent.com.json', SCOPES) # ← このファイル名を書き換える！
                creds = flow.run_local_server(port=0)

            # 次回のために認証情報を保存します
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('drive', 'v3', credentials=creds)

            # Drive APIを呼び出します
            print('ファイル一覧を取得中...')
            results = service.files().list(
                pageSize=10, fields="nextPageToken, files(id, name)").execute()
            items = results.get('files', [])

            if not items:
                print('ファイルが見つかりませんでした。')
                return

            print('--- あなたのGoogle Driveのファイル一覧 (最大10件) ---')
            for item in items:
                print(f'ファイル名: {item["name"]}')
            print('----------------------------------------------------')

        except HttpError as error:
            print(f'エラーが発生しました: {error}')

if __name__ == '__main__':
        main()