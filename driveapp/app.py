import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

# main.pyから必要な関数をインポート
from main import get_accounts_info, upload_logic_for_web

app = Flask(__name__)
# 一時保存フォルダのパスを設定
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    """トップページ"""
    accounts = get_accounts_info()
    return render_template('index.html', accounts=accounts)


# '/upload' というURLに、POSTメソッドでリクエストが来たときに実行
@app.route('/upload', methods=['POST'])
def upload_file_route():
    # フォームから 'file' という名前のファイルを取得
    if 'file' not in request.files:
        return redirect(url_for('index')) # ファイルがなければトップに戻る

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index')) # ファイル名がなければトップに戻る

    if file:
        # 安全なファイル名に変換 (例: ../../passwords.txt のような攻撃を防ぐ)
        filename = secure_filename(file.filename)
        # 一時ファイルの保存パスを生成
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # ファイルを一時保存
        file.save(temp_path)

        # main.pyのアップロードロジックを呼び出す
        success = upload_logic_for_web(temp_path)

        # 一時ファイルを削除 (任意ですが、推奨)
        if os.path.exists(temp_path):
            os.remove(temp_path)

        # 処理が終わったらトップページにリダイレクト (戻る)
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)