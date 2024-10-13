from flask import Flask, request, jsonify, render_template
# from gevent.pywsgi import WSGIServer

app = Flask(__name__)

# Main page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # http_server = WSGIServer(("127.0.0.1", 8000), app)
    # http_server.serve_forever()
    app.run(host='0.0.0.0', port=80)