import tkinter as tk
import customtkinter as ctk
import webbrowser
import pyautogui
import time
import threading
import os
import pandas as pd
import sys
import psutil

# タブ切り替えアプリケーションクラス
class TabSwitcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tab Switcher")
        self.root.geometry("880x520")  # ウィンドウサイズを設定
        self.root.resizable(False, False)  # ウィンドウサイズを固定

        # フレームを使用してUIを整理
        self.frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.url_entries = []  # URL入力フィールドのリスト
        self.time_entries = []  # タイマー入力フィールドのリスト
        self.user_entries = []  # ユーザー名入力フィールドのリスト
        self.pass_entries = []  # パスワード入力フィールドのリスト

        # ヘッダラベルを追加
        headers = ["URL", "Username", "Password", "Time (seconds)"]
        for j, header in enumerate(headers):
            label = ctk.CTkLabel(self.frame, text=header)
            label.grid(row=0, column=j, padx=5, pady=5, sticky="ew")

        # URL、ユーザー名、パスワード、タイマー入力フィールドを最大10行作成
        for i in range(10):
            url_entry = ctk.CTkEntry(self.frame, width=400, state='readonly')  # URL入力フィールド
            url_entry.grid(row=i+1, column=0, padx=5, pady=5)
            self.url_entries.append(url_entry)  # リストに追加

            user_entry = ctk.CTkEntry(self.frame, width=150, state='readonly')  # ユーザー名入力フィールド
            user_entry.grid(row=i+1, column=1, padx=5, pady=5)
            self.user_entries.append(user_entry)  # リストに追加

            pass_entry = ctk.CTkEntry(self.frame, show="*", width=150, state='readonly')  # パスワード入力フィールド
            pass_entry.grid(row=i+1, column=2, padx=5, pady=5)
            self.pass_entries.append(pass_entry)  # リストに追加

            time_entry = ctk.CTkEntry(self.frame, width=100, state='readonly')  # タイマー入力フィールド
            time_entry.grid(row=i+1, column=3, padx=5, pady=5)
            self.time_entries.append(time_entry)  # リストに追加

        # ボタンのフレームを追加
        self.button_frame = ctk.CTkFrame(self.frame, corner_radius=10)
        self.button_frame.grid(row=11, column=0, columnspan=4, pady=10, sticky="ew")

        self.start_button = ctk.CTkButton(self.button_frame, text="Start", command=self.start, state="normal")  # 開始ボタン
        self.start_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.save_button = ctk.CTkButton(self.button_frame, text="Save", command=self.save_data, state="normal")  # 保存ボタン
        self.save_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.edit_button = ctk.CTkButton(self.button_frame, text="Edit", command=self.enable_editing, fg_color="blue")  # 編集ボタン
        self.edit_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.confirm_button = ctk.CTkButton(self.button_frame, text="Confirm", command=self.disable_editing, state="disabled", fg_color="gray")  # 確定ボタン
        self.confirm_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.load_data()  # アプリケーション起動時にデータを読み込む

    def load_data(self):
        # CSVファイルからデータを読み込み、入力フィールドにセットする
        if os.path.exists('data.csv'):
            data = pd.read_csv('data.csv')
            for i in range(min(10, len(data))):
                if pd.isna(data.loc[i, 'URL']):
                    data.loc[i, 'URL'] = ''
                if pd.isna(data.loc[i, 'Username']):
                    data.loc[i, 'Username'] = ''
                if pd.isna(data.loc[i, 'Password']):
                    data.loc[i, 'Password'] = ''
                if pd.isna(data.loc[i, 'Time']):
                    data.loc[i, 'Time'] = ''
                self.url_entries[i].configure(state='normal')
                self.url_entries[i].insert(0, data.loc[i, 'URL'])
                self.url_entries[i].configure(state='readonly')
                self.user_entries[i].configure(state='normal')
                self.user_entries[i].insert(0, data.loc[i, 'Username'])
                self.user_entries[i].configure(state='readonly')
                self.pass_entries[i].configure(state='normal')
                self.pass_entries[i].insert(0, data.loc[i, 'Password'])
                self.pass_entries[i].configure(state='readonly')
                self.time_entries[i].configure(state='normal')
                self.time_entries[i].insert(0, str(data.loc[i, 'Time']))
                self.time_entries[i].configure(state='readonly')

    def save_data(self):
        # 入力フィールドからデータを取得し、CSVファイルに保存する
        data = []
        for i in range(10):
            url = self.url_entries[i].get()
            username = self.user_entries[i].get()
            password = self.pass_entries[i].get()
            time = self.time_entries[i].get()
            if url and time:
                data.append({
                    'URL': url,
                    'Username': username,
                    'Password': password,
                    'Time': int(time) if time.isdigit() else None
                })
        df = pd.DataFrame(data)
        df.to_csv('data.csv', index=False)

    def enable_editing(self):
        for i in range(10):
            self.url_entries[i].configure(state='normal')
            self.user_entries[i].configure(state='normal')
            self.pass_entries[i].configure(state='normal')
            self.time_entries[i].configure(state='normal')
        self.edit_button.configure(fg_color="red")
        self.start_button.configure(state="disabled", fg_color="gray")
        self.save_button.configure(state="disabled", fg_color="gray")
        self.confirm_button.configure(state="normal", fg_color="blue")

    def disable_editing(self):
        for i in range(10):
            self.url_entries[i].configure(state='readonly')
            self.user_entries[i].configure(state='readonly')
            self.pass_entries[i].configure(state='readonly')
            self.time_entries[i].configure(state='readonly')
        self.edit_button.configure(fg_color="blue")
        self.start_button.configure(state="normal", fg_color="blue")
        self.save_button.configure(state="normal", fg_color="blue")
        self.confirm_button.configure(state="disabled", fg_color="gray")

    def open_urls(self, urls):
        for url in urls:
            webbrowser.open_new_tab(url)
            time.sleep(5)  # 各URLが開かれるまで待機

    def close_app(self):
        self.root.quit()
        self.root.destroy()
        sys.exit()

    def start(self):
        # 入力されたURL、ユーザー名、パスワード、タイマー秒数を取得
        urls = [entry.get() for entry in self.url_entries if entry.get()]
        users = [entry.get() for entry in self.user_entries]
        passwords = [entry.get() for entry in self.pass_entries]
        times = [int(entry.get()) for entry in self.time_entries if entry.get()]

        # URLとタイマーの数が一致しない場合のチェック
        if len(urls) != len(times):
            print("URLと時間の入力数は同じでなければなりません")
            return

        # URLとタイマーが空でないことのチェック
        if not urls or not times:
            print("少なくとも1つのURLと時間を入力してください")
            return

        # フォームを非表示にする
        self.frame.pack_forget()

        # 各URLを新しいタブで順に開く
        threading.Thread(target=self.open_urls, args=(urls,)).start()

        # タブを切り替える関数
        def switch_tabs():
            current_index = 0
            while True:
                pyautogui.hotkey('ctrl', str(current_index + 1))  # タブを切り替え
                pyautogui.hotkey('ctrl', 'r')  # タブをリフレッシュ

                # ユーザー名とパスワードの入力が必要かチェックして自動入力
                user = users[current_index]
                password = passwords[current_index]
                if user and password:
                    pyautogui.write(user)
                    pyautogui.press('tab')
                    pyautogui.write(password)
                    pyautogui.press('enter')

                time.sleep(times[current_index])  # 指定された時間待機
                current_index = (current_index + 1) % len(urls)  # 次のタブに切り替え

        threading.Thread(target=switch_tabs).start()  # 別スレッドでタブ切り替えを実行

        # ブラウザが閉じられたかを確認する関数
        def monitor_browser():
            while True:
                if not any(["msedge.exe" in p.name() or "chrome.exe" in p.name() for p in psutil.process_iter()]):
                    self.close_app()
                time.sleep(1)

        threading.Thread(target=monitor_browser).start()  # 別スレッドでブラウザの監視を実行

if __name__ == "__main__":
    ctk.set_appearance_mode("System")  # 見た目のモードをシステム設定に合わせる
    ctk.set_default_color_theme("blue")  # カラーテーマを青に設定

    root = ctk.CTk()  # CustomTkinterのルートウィンドウを作成
    app = TabSwitcherApp(root)  # アプリケーションのインスタンスを作成
    root.mainloop()  # メインループを開始
