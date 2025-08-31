import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

# main.pyから必要な関数をインポート
from main import get_accounts_info, upload_logic_for_web

app = Flask(__name__)
# フラッシュメッセージ機能には、セッションを暗号化するための秘密鍵が必要
# これは好きな文字列で構いません
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

        # upload_logic_for_web からの True/False の結果を受け取る
        success = upload_logic_for_web(temp_path)

        # 結果に応じてフラッシュメッセージを設定
        if success:
            flash(f"ファイル '{filename}' のアップロードに成功しました！", 'success')
        else:
            flash(f"ファイル '{filename}' のアップロードに失敗しました。", 'error')

        if os.path.exists(temp_path):
            os.remove(temp_path)

        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)