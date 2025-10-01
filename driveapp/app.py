import os
# ▼▼▼ flask の import 文に flash を追加し忘れている可能性もあるので、フルで記載します ▼▼▼
from flask import Flask, render_template, request, redirect, url_for, flash

# ▼▼▼ この行に secure_filename を追加、またはこの行自体を追加 ▼▼▼
from werkzeug.utils import secure_filename

# main.pyから必要な関数をインポート
from main import (
    init_database, update_file_index, get_files_from_db, search_files_in_db,
    get_accounts_info, upload_logic_for_web, download_file_logic,
    delete_file_logic
)
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'))
app.secret_key = '987654321'
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# フォルダが存在しない場合は作成する
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# アプリケーション起動時に一度だけデータベースを初期化
init_database()

@app.route('/')
def index():
    accounts = get_accounts_info()
    return render_template('index.html', accounts=accounts, query='', mime_type='')

@app.route('/upload', methods=['POST'])
def upload_file_route():
    # 'file' という名前で送られてきたファイルのリストを取得
    uploaded_files = request.files.getlist("file")

    if not uploaded_files or uploaded_files[0].filename == '':
        flash('ファイルが選択されていません。', 'error')
        return redirect(url_for('index'))

    success_files = []
    error_files = []

    # 取得したファイルのリストをループ処理
    for file in uploaded_files:
        if file:
            filename = secure_filename(file.filename)
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            try:
                file.save(temp_path)
                # 既存の1ファイル用アップロードロジックを呼び出す
                success = upload_logic_for_web(temp_path)

                if success:
                    success_files.append(filename)
                else:
                    error_files.append(filename)

            except Exception as e:
                print(f"ファイル '{filename}' の処理中にエラー: {e}")
                error_files.append(filename)
            finally:
                # 処理が終わったら一時ファイルを必ず削除
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    # 処理結果をまとめてフラッシュメッセージで表示
    if success_files:
        flash(f"{len(success_files)}件のファイルアップロードに成功しました！<br>- " + "<br>- ".join(success_files), 'success')
    if error_files:
        flash(f"{len(error_files)}件のファイルアップロードに失敗しました。<br>- " + "<br>- ".join(error_files), 'error')

    # 完了後、インデックス更新を促すメッセージを追加
    if success_files:
        flash('ファイル一覧を最新にするには、インデックスを更新してください。', 'info') # infoカテゴリを追加

    return redirect(url_for('index'))

@app.route('/files')
def files_list_page():
    # APIではなくDBからファイルリストを取得
    files = get_files_from_db()
    return render_template('files.html', files=files, query='', mime_type='')

@app.route('/download/<account_name>/<file_id>')
def download_file_route(account_name, file_id):
    # (この関数は変更なし)
    file_content, file_name = download_file_logic(account_name, file_id)
    if file_content is None:
        flash(f"ダウンロードに失敗しました。", 'error')
        return redirect(url_for('files_list_page'))
    headers = {'Content-Disposition': f'attachment; filename="{file_name}"'}
    return (file_content, 200, headers)

@app.route('/search')
def search_page():
    query = request.args.get('query', '')
    mime_type = request.args.get('mimeType', '')
    # APIではなくDBを検索
    files = search_files_in_db(query, mime_type)
    mime_type_map = {
        "application/pdf": "PDF", "text/plain": "テキストファイル",
        "application/vnd.google-apps.document": "Google ドキュメント", "application/msword": "Word",
        "application/vnd.google-apps.spreadsheet": "Google スプレッドシート", "application/vnd.ms-excel": "Excel",
        "image/jpeg": "JPEG 画像", "image/png": "PNG 画像",
        "application/vnd.google-apps.folder": "フォルダ",
    }
    mime_type_display = mime_type_map.get(mime_type)
    return render_template(
        'search_results.html', files=files, query=query,
        mime_type=mime_type, mime_type_display=mime_type_display
    )

# インデックス更新用の新しいルート
@app.route('/update_index', methods=['POST'])
def update_index_route():
    success = update_file_index()
    if success:
        flash('ファイルインデックスを更新しました。', 'success')
    else:
        flash('インデックスの更新に失敗しました。', 'error')
    return redirect(url_for('index'))

@app.route('/delete/<account_name>/<file_id>', methods=['POST'])
def delete_file_route(account_name, file_id):
    """ファイルを削除する"""
    success = delete_file_logic(account_name, file_id)

    if success:
        flash('ファイルを削除しました。', 'success')
    else:
        flash('ファイルの削除に失敗しました。', 'error')

    # 削除操作後、直前にいたページに戻る (リファラを取得)
    # もしリファラがなければ、ファイル一覧ページにリダイレクト
    return redirect(request.referrer or url_for('files_list_page'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)