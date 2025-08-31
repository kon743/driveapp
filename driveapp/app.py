import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

# main.pyから必要な関数をインポート
from main import get_accounts_info, upload_logic_for_web, get_all_files_from_all_accounts, download_file_logic, search_files_in_all_accounts

# 現在のファイル(app.py)の絶対パスを取得
basedir = os.path.abspath(os.path.dirname(__file__))

# Flaskアプリケーションのインスタンスを作成
app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'))

# フラッシュメッセージ機能には、セッションを暗号化するための秘密鍵が必要
app.secret_key = '987654321'

# 一時保存フォルダのパスを設定
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    """トップページ"""
    # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
    # ★  この行が欠けていました！ accounts変数を定義します ★
    # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
    accounts = get_accounts_info()
    return render_template('index.html', accounts=accounts, query='', mime_type='')


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


@app.route('/files')
def files_list_page():
    """全ファイル一覧ページ"""
    # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
    # ★ この行も欠けていました！ files変数を定義します ★
    # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
    files = get_all_files_from_all_accounts()
    return render_template('files.html', files=files, query='', mime_type='')


@app.route('/download/<account_name>/<file_id>')
def download_file_route(account_name, file_id):
    """ファイルをダウンロードさせる"""
    file_content, file_name = download_file_logic(account_name, file_id)

    if file_content is None:
        flash(f"ファイルのダウンロードに失敗しました。ファイルが見つからないか、アクセス権限に問題がある可能性があります。", 'error')
        # ★★★ ここも修正: 'files_list_page' が正しい関数名 ★★★
        return redirect(url_for('files_list_page'))

    headers = {
        'Content-Disposition': f'attachment; filename="{file_name}"'
    }
    
    return (file_content, 200, headers)


@app.route('/search')
def search_page():
    """検索結果ページ"""
    query = request.args.get('query', '')
    mime_type = request.args.get('mimeType', '')

    files = []
    if query or mime_type:
        files = search_files_in_all_accounts(query, mime_type)

    mime_type_map = {
        "application/pdf": "PDF",
        "application/vnd.google-apps.document": "Google ドキュメント",
        "application/msword": "Word",
        "application/vnd.google-apps.spreadsheet": "Google スプレッドシート",
        "application/vnd.ms-excel": "Excel",
        "image/jpeg": "JPEG 画像",
        "image/png": "PNG 画像",
        "application/vnd.google-apps.folder": "フォルダ",
    }
    mime_type_display = mime_type_map.get(mime_type)

    return render_template(
        'search_results.html',
        files=files,
        query=query,
        mime_type=mime_type,
        mime_type_display=mime_type_display
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)