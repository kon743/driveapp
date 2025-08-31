from flask import Flask, render_template

# main.pyから、アカウント情報を取得する関数をインポート(読み込み)
from main import get_accounts_info

app = Flask(__name__)

@app.route('/')
def index():
    """トップページ"""
    # 1. main.pyの関数を呼び出して、アカウント情報のリストを取得
    accounts = get_accounts_info()

    # 2. 取得したデータをHTMLテンプレートに渡して、Webページを生成
    # 'accounts=accounts' の左側はHTMLで使う変数名、右側はPythonの変数
    return render_template('index.html', accounts=accounts)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)