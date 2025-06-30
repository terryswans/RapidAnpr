import os
import uuid
import subprocess
from flask import Flask, request, jsonify, render_template
from flask_httpauth import HTTPTokenAuth
from config import SECRET_TOKEN, COUNTRY

app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')

@auth.verify_token
def verify_token(token):
    return token == SECRET_TOKEN

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        token = request.form.get('token')
        if token != SECRET_TOKEN:
            result = {'error': 'Invalid token'}
        else:
            image = request.files.get('image')
            if image:
                filename = f"/tmp/{uuid.uuid4().hex}.jpg"
                image.save(filename)
                proc = subprocess.run([
                    'alpr', '-c', COUNTRY, '--json', filename
                ], capture_output=True, text=True)
                try:
                    result = proc.stdout
                except Exception as e:
                    result = {'error': str(e)}
    return render_template('index.html', token=SECRET_TOKEN, result=result)

@app.route('/alpr', methods=['POST'])
@auth.login_required
def alpr_api():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    image = request.files['image']
    filename = f"/tmp/{uuid.uuid4().hex}.jpg"
    image.save(filename)
    proc = subprocess.run([
        'alpr', '-c', COUNTRY, '--json', filename
    ], capture_output=True, text=True)
    return proc.stdout, 200, {'Content-Type': 'application/json'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
