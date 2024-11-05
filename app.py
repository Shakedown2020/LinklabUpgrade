from flask import Flask, request, send_file, render_template,jsonify
import os
import json
import subprocess  # 用于运行系统命令

app = Flask(__name__)

SRC_DIR = 'src'
BOMBROOT_DIR = 'bombs'
UPLOAD_FOLDER = 'handin'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # 确保handin目录存在

scores = {}
score = {}

def process(bomb_id, src_dir, bomb_dir, bomb_datapack):
    if len(bomb_id.strip()) <= 0:
        return False

    command = f'python3 {os.path.join(src_dir, "makebomb.py")} {bomb_id} {src_dir} {bomb_dir} {bomb_datapack}'
    subprocess.run(command, shell=True)

    return os.path.isfile(bomb_datapack)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():

    student_id = request.form['student_id']

    if not student_id:
        return "Please provide student ID.", 400

    bomb_dir = os.path.join(BOMBROOT_DIR, student_id)
    bomb_datapack = os.path.join(BOMBROOT_DIR, f'{student_id}.tar')

    result = process(student_id, SRC_DIR, bomb_dir, bomb_datapack)
    if not result:
        return f'ERROR: Failed to generate lab data for ID: <{student_id}>!', 500

    return send_file(bomb_datapack, as_attachment=True)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return '没有文件上传'

        file = request.files['file']
        if file.filename == '':
            return '未选择文件'
        filename = os.path.splitext(file.filename)[0]
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        student_id = filename  # 学生ID
        bomb_dir = os.path.join(BOMBROOT_DIR, student_id)  # 炸弹目录
       
        try:
            command = ['python3', 'grade_linklab.py', student_id, filepath, bomb_dir, SRC_DIR]
            result = subprocess.run(command, capture_output=True, text=True)
            output = result.stdout

            return f'评分结果：<br>{output}'
        except Exception as e:
            return f'运行评分程序时出错：{e}'

    return render_template('upload.html')

@app.route('/scores')
def get_scores():
    with open('scores.json', 'r') as f:
        scores = json.load(f)
    return jsonify(scores)

@app.route('/scoreboard')
def scoreboard():
    return render_template('LinklabScoreboard.html')

if __name__ == '__main__':
    app.run(debug=True)
