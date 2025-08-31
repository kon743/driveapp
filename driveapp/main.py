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


def get_drive_space(service):
    """Google Driveのストレージ情報を取得し、空き容量を返す"""
    try:
        about = service.about().get(fields='storageQuota').execute()
        quota = about['storageQuota']

        limit = int(quota['limit'])      # 全容量
        usage = int(quota['usage'])      # 使用量
        free_space = limit - usage       # 空き容量

        # ギガバイト(GB)に変換して返す
        return free_space / (1024**3)

    except HttpError as error:
        print(f"ストレージ情報の取得中にAPIエラーが発生しました: {error}")
        return 0 # エラー時は0を返す


def list_accounts():
    """登録されている全アカウントの情報を一覧表示する"""
    print("\n--- 登録済みアカウント一覧 ---")
    token_files = glob.glob('token_*.json')
    if not token_files:
        print("アカウントが登録されていません。")
        return

    for token_file in token_files:
        account_name = token_file.replace('token_', '').replace('.json', '')
        try:
            creds = authenticate(account_name)
            service = build('drive', 'v3', credentials=creds)
            free_space_gb = get_drive_space(service)
            print(f" - アカウント名: {account_name}, 空き容量: {free_space_gb:.2f} GB")
        except Exception as e:
            print(f" - アカウント名: {account_name}, 情報取得エラー: {e}")
    print("--------------------------")


def upload_to_best_drive():
    """空き容量が最大のドライブにファイルをアップロードする"""
    file_to_upload = input("アップロードするファイルのパスを入力してください: ")
    if not os.path.exists(file_to_upload):
        print(f"エラー: ファイル '{file_to_upload}' が見つかりません。")
        return

    token_files = glob.glob('token_*.json')
    if not token_files:
        print("アップロード先のアカウントが登録されていません。")
        return

    print("\n各アカウントの空き容量をチェックしています...")
    best_account = None
    max_free_space = -1

    for token_file in token_files:
        account_name = token_file.replace('token_', '').replace('.json', '')
        try:
            creds = authenticate(account_name)
            service = build('drive', 'v3', credentials=creds)
            free_space_gb = get_drive_space(service)
            print(f" - [{account_name}] 空き容量: {free_space_gb:.2f} GB")
            if free_space_gb > max_free_space:
                max_free_space = free_space_gb
                best_account = account_name
        except Exception as e:
            print(f" - [{account_name}] 情報取得エラー: {e}")

    if best_account:
        print(f"\n空き容量が最も多いアカウント [{best_account}] にアップロードします。")
        creds = authenticate(best_account)
        service = build('drive', 'v3', credentials=creds)
        upload_file(service, file_to_upload, best_account)
    else:
        print("\nアップロードに適したアカウントが見つかりませんでした。")



def main():
    """メインの処理。メニューを表示してユーザーの入力を待つ"""
    while True:
        print("\n==============================")
        print("  Google Drive Manager Menu")
        print("==============================")
        print("1: 登録アカウント一覧を表示")
        print("2: ファイルを自動選択でアップロード")
        print("3: 新しいアカウントを登録")
        print("0: プログラムを終了")

        choice = input("操作を選んで番号を入力してください: ")

        if choice == '1':
            list_accounts()
        elif choice == '2':
            upload_to_best_drive()
        elif choice == '3':
            # 新しいアカウント登録の処理
            new_account_name = input("登録する新しいアカウント名を入力してください (例: user3, private など): ")
            if new_account_name:
                authenticate(new_account_name)
                print(f"アカウント '{new_account_name}' の認証が完了しました。")
            else:
                print("アカウント名が入力されなかったのでキャンセルしました。")
        elif choice == '0':
            print("プログラムを終了します。")
            break # 無限ループを抜ける
        else:
            print("無効な選択です。0から3の番号を入力してください。")

if __name__ == '__main__':
    main()