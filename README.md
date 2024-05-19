プロジェクトディレクトリ構造の更新

yolov8_flask_app/
├── app.py
├── templates/
│   └── index.html
└── static/
    ├── css/
    │   └── styles.css
    └── js/
        └── scripts.js

必要ライブラリ
pip install flask
pip install opencv-python
pip install ultralytics
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
