from flask import Flask, render_template, Response, jsonify
import cv2
import torch
from ultralytics import YOLO
from datetime import datetime
import json
import time
import webbrowser
from threading import Timer

app = Flask(__name__)

# デバイスの設定
device = torch.device('cpu')

# YOLOv8n (Nano) モデルをロード
model = YOLO('yolov8n.pt')
model.to(device)  # モデルをCPUに移動

# カメラを初期化
camera_id = 0
flip_camera = False
cap = cv2.VideoCapture(camera_id)

def generate_frames():
    global flip_camera
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            if flip_camera:
                frame = cv2.flip(frame, 1)
            # YOLOv8で推論を実行
            results = model(frame)

            # 結果をフレームに描画
            annotated_frame = results[0].plot()

            # フレームをJPEG形式にエンコード
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            frame = buffer.tobytes()

            # フレームをジェネレータとして返す
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def generate_logs():
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            # YOLOv8で推論を実行
            results = model(frame)

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
                    "timestamp": now,  # タイムスタンプを追加
                    "center_x": center_x,
                    "center_y": center_y,
                    "width": width,
                    "height": height
                }
                yield f"data: {json.dumps(log_data)}\n\n"
                time.sleep(1)  # 更新頻度を調整

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/log_feed')
def log_feed():
    return Response(generate_logs(), mimetype='text/event-stream')

@app.route('/change_camera/<int:camera_id>', methods=['GET'])
def change_camera(camera_id):
    global cap
    cap.release()
    cap = cv2.VideoCapture(camera_id)
    return jsonify(success=True)

@app.route('/flip_camera', methods=['GET'])
def flip_camera():
    global flip_camera
    flip_camera = not flip_camera
    return jsonify(success=True)

@app.route('/current_camera', methods=['GET'])
def current_camera():
    global camera_id
    return jsonify(camera_id=camera_id)

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    # サーバー起動後にブラウザを開く
    Timer(1, open_browser).start()
    app.run(debug=True)
