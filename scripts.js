const eventSource = new EventSource("/log_feed");
const maxRows = 50;
let logDataArray = []; // ログデータを保存する配列
let saveDirectory = ""; // 保存先ディレクトリ

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

fetch('/default_save_directory')
    .then(response => response.json())
    .then(data => {
        saveDirectory = data.path;
        document.getElementById('save-directory').value = saveDirectory;
    });

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

    // テーブルの行数が50を超えた場合、古い行を削除する
    if (tableBody.rows.length > maxRows) {
        tableBody.deleteRow(maxRows);
    }

    // ログデータを配列に保存
    logDataArray.push(data);

    // 定期的にCSVとして保存
    if (logDataArray.length % 10 === 0) { // 例えば10行ごとに保存
        saveLogDataToCSV(logDataArray);
    }
};

// CSVファイルとして保存する関数
function saveLogDataToCSV(logData) {
    fetch('/save_csv', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(logData),
    })
    .then(response => {
        if (response.ok) {
            console.log('CSVファイルが保存されました');
        } else {
            alert('CSVファイルの保存に失敗しました');
        }
    });
}

// 保存先フォルダのパスを保存する関数
document.getElementById('save-directory-btn').addEventListener('click', function() {
    saveDirectory = document.getElementById('save-directory').value;
    fetch('/set_save_directory', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ path: saveDirectory }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`保存先ディレクトリが ${saveDirectory} に設定されました`);
        } else {
            alert('保存先ディレクトリの設定に失敗しました');
        }
    });
});
