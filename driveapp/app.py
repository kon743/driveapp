import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

# main.pyから必要な関数をインポート (重複をなくし、一行にまとめました)
from main import get_accounts_info, upload_logic_for_web, get_all_files_from_all_accounts, download_file_logic

# 現在のファイル(app.py)の絶対パスを取得
basedir = os.path.abspath(os.path.dirname(__file__))

# Flaskアプリケーションのインスタンスを作成
# template_folder に templates フォルダの絶対パスを指定
app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'))

# フラッシュメッセージ機能には、セッションを暗号化するための秘密鍵が必要
app.secret_key = '987654321'

# 一時保存フォルダのパスを設定
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    """トップページ"""
    accounts = get_accounts_info()
    return render_template('index.html', accounts=accounts)

@app.route('/upload', methods=['POST'])
def upload_file_route():
    if 'file' not in request.files:
        flash('ファイルが選択されていません。')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('ファイル名が空です。')
        return redirect(url_for('index'))

    if file:
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)

        success = upload_logic_for_web(temp_path)

        if success:
            flash(f"ファイル '{filename}' のアップロードに成功しました！", 'success')
        else:
            flash(f"ファイル '{filename}' のアップロードに失敗しました。", 'error')

        if os.path.exists(temp_path):
            os.remove(temp_path)

        return redirect(url_for('index'))

# ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
# ★  ここに /files ルートを配置するのが正しい場所です  ★
# ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
@app.route('/files')
def files_list_page():
    """全ファイル一覧ページ"""
    files = get_all_files_from_all_accounts()
    return render_template('files.html', files=files)

@app.route('/download/<account_name>/<file_id>')
def download_file_route(account_name, file_id):
    """ファイルをダウンロードさせる"""
    # main.pyの新しい関数 (これから作る) を呼び出す
    file_content, file_name = download_file_logic(account_name, file_id)

    if file_content is None:
        flash(f"ファイルのダウンロードに失敗しました。ファイルが見つからないか、アクセス権限に問題がある可能性があります。", 'error')
        return redirect(url_for('files_list_page'))

    # ブラウザに「これはダウンロードするファイルですよ」と伝えるためのヘッダー
    headers = {
        'Content-Disposition': f'attachment; filename="{file_name}"'
    }

    # ファイルのコンテンツを、ヘッダー情報と共にブラウザに返す
    return (file_content, 200, headers)



# この if ブロックの中には、サーバーを起動する app.run() だけを置きます
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)