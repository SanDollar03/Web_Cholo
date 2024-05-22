import logging
import os
import csv
import atexit
import tracemalloc
import time
from flask import Flask, render_template, Response, jsonify, request
import cv2
import torch
from ultralytics import YOLO
from datetime import datetime
import json
import webbrowser
from threading import Timer

# メモリプロファイリングを開始
tracemalloc.start()

# ログ設定
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

logging.debug('App initialized')

# デバイスの設定
device = torch.device('cpu')
logging.debug('Device set to CPU')

# YOLOv8n (Nano) モデルをロード
model = YOLO('yolov8s.pt')
model.to(device)  # モデルをCPUに移動
logging.debug('Model loaded and moved to CPU')

# カメラを初期化
camera_id = 0
flip_camera = False
cap = cv2.VideoCapture(camera_id)
logging.debug(f'Camera initialized with ID {camera_id}')

# 保存先ディレクトリ
save_directory = os.path.dirname(os.path.abspath(__file__))

# 保存先ディレクトリを読み込む関数
def load_save_directory():
    global save_directory
    try:
        with open('save_directory.csv', 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                save_directory = row[0]
    except FileNotFoundError:
        pass

# 保存先ディレクトリを保存する関数
def save_save_directory():
    global save_directory
    with open('save_directory.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([save_directory])

load_save_directory()

def generate_frames():
    global flip_camera
    frame_count = 0
    while True:
        success, frame = cap.read()
        if not success:
            logging.error('Failed to read frame from camera')
            break
        else:
            frame_count += 1
            if frame_count % 30 == 0:  # 1秒ごとに1フレーム処理
                if flip_camera:
                    frame = cv2.flip(frame, 1)
                # YOLOv8で推論を実行
                results = model(frame)
                logging.debug('Inference executed')

                # 結果をフレームに描画
                annotated_frame = results[0].plot()

                # フレームをJPEG形式にエンコード
                ret, buffer = cv2.imencode('.jpg', annotated_frame)
                frame = buffer.tobytes()

                # フレームをジェネレータとして返す
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

                # 明示的にテンソルを解放
                del results
                torch.cuda.empty_cache()

def generate_logs():
    while True:
        success, frame = cap.read()
        if not success:
            logging.error('Failed to read frame from camera')
            break
        else:
            now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            # YOLOv8で推論を実行
            results = model(frame)
            logging.debug('Inference executed for logging')

            # ログの生成
            for result in results[0].boxes:
                class_id = int(result.cls)
                class_name = model.names[class_id]
                center_x = result.xywh[0][0].item()
                center_y = result.xywh[0][1].item()
                width = result.xywh[0][2].item()
                height = result.xywh[0][3].item()
                
                log_data = {
                    "class_id": class_id,
                    "class_name": class_name,
                    "timestamp": now,
                    "center_x": center_x,
                    "center_y": center_y,
                    "width": width,
                    "height": height
                }
                yield f"data: {json.dumps(log_data)}\n\n"
                time.sleep(1)
            
            # 明示的にテンソルを解放
            del results
            torch.cuda.empty_cache()

@app.route('/')
def index():
    logging.debug('Rendering index.html')
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    logging.debug('Starting video feed')
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/log_feed')
def log_feed():
    logging.debug('Starting log feed')
    return Response(generate_logs(), mimetype='text/event-stream')

@app.route('/change_camera/<int:camera_id>', methods=['GET'])
def change_camera(camera_id):
    global cap
    cap.release()
    cap = cv2.VideoCapture(camera_id)
    logging.debug(f'Camera changed to ID {camera_id}')
    return jsonify(success=True)

@app.route('/flip_camera', methods=['GET'])
def flip_camera():
    global flip_camera
    flip_camera = not flip_camera
    logging.debug(f'Camera flip set to {flip_camera}')
    return jsonify(success=True)

@app.route('/current_camera', methods=['GET'])
def current_camera():
    global camera_id
    logging.debug(f'Current camera ID is {camera_id}')
    return jsonify(camera_id=camera_id)

@app.route('/default_save_directory', methods=['GET'])
def default_save_directory():
    global save_directory
    return jsonify(path=save_directory)

@app.route('/set_save_directory', methods=['POST'])
def set_save_directory():
    global save_directory
    data = request.json
    save_directory = data['path']
    save_save_directory()
    return jsonify(success=True)

@app.route('/save_csv', methods=['POST'])
def save_csv():
    global save_directory
    data = request.json
    file_path = os.path.join(save_directory, "log_data.csv")

    # CSVファイルにデータを書き込む
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['class_id', 'class_name', 'timestamp', 'center_x', 'center_y', 'width', 'height']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for row in data:
                writer.writerow(row)
        return jsonify(success=True)
    except Exception as e:
        logging.error(f"Failed to save CSV: {e}")
        return jsonify(success=False, error=str(e))

def open_browser():
    logging.debug('Opening browser to http://127.0.0.1:5000')
    webbrowser.open_new("http://127.0.0.1:5000")

def release_resources():
    # カメラを解放
    global cap
    if cap.isOpened():
        cap.release()
        logging.debug('Camera released')

    # メモリプロファイリングの結果を表示
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    logging.debug("[ Top 10 memory usage ]")
    for stat in top_stats[:10]:
        logging.debug(stat)

if __name__ == "__main__":
    # サーバー起動後にブラウザを開く
    Timer(1, open_browser).start()
    logging.debug('Starting Flask app')
    atexit.register(release_resources)
    app.run(debug=False)
