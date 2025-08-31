from flask import Flask

# Flaskアプリケーションのインスタンスを作成
app = Flask(__name__)

# '/' というURLにアクセスが来たときに実行される関数を定義
@app.route('/')
def index():
    """トップページ"""
    return '<h1>こんにちは！ Google Drive Manager Webへようこそ！</h1>'

# このスクリプトが直接実行された場合にのみ、Webサーバーを起動
if __name__ == '__main__':
    # デバッグモードでサーバーを起動
    # host='0.0.0.0' は外部からのアクセスを許可するため(Replitなどでも動くように)
    # port=8080 は使用するポート番号
    app.run(host='0.0.0.0', port=8080, debug=True)