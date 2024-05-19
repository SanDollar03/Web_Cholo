document.getElementById('change-camera-btn').addEventListener('click', function() {
    const selectedCamera = document.getElementById('camera-select').value;
    fetch(`/change_camera/${selectedCamera}`)
        .then(response => {
            if (response.ok) {
                // カメラ変更後にページをリロードして描画を更新
                window.location.reload();
            } else {
                alert('カメラの変更に失敗しました');
            }
        });
});

document.getElementById('flip-camera-btn').addEventListener('click', function() {
    fetch(`/flip_camera`)
        .then(response => {
            if (response.ok) {
                // カメラ変更後にページをリロードして描画を更新
                window.location.reload();
            } else {
                alert('カメラの反転に失敗しました');
            }
        });
});

fetch('/current_camera')
    .then(response => response.json())
    .then(data => {
        document.getElementById('camera-select').value = data.camera_id;
    });

const eventSource = new EventSource("/log_feed");
eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    const tableBody = document.getElementById("log-table-body");
    const row = document.createElement("tr");
    const classIdCell = document.createElement("td");
    const classNameCell = document.createElement("td");
    const timestampCell = document.createElement("td"); // タイムスタンプ列
    const centerXCell = document.createElement("td");
    const centerYCell = document.createElement("td");
    const widthCell = document.createElement("td");
    const heightCell = document.createElement("td");

    classIdCell.textContent = data.class_id;
    classNameCell.textContent = data.class_name;
    timestampCell.textContent = data.timestamp; // タイムスタンプの内容を追加
    centerXCell.textContent = data.center_x;
    centerYCell.textContent = data.center_y;
    widthCell.textContent = data.width;
    heightCell.textContent = data.height;

    row.appendChild(classIdCell);
    row.appendChild(classNameCell);
    row.appendChild(timestampCell); // タイムスタンプ列を行に追加
    row.appendChild(centerXCell);
    row.appendChild(centerYCell);
    row.appendChild(widthCell);
    row.appendChild(heightCell);

    // テーブルの先頭に新しい行を追加して降順にする
    tableBody.insertBefore(row, tableBody.firstChild);
};
