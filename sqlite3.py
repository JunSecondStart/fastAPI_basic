import sqlite3
import json

# データベースに接続（データベースが存在しない場合は新規作成）
conn = sqlite3.connect('fruits.db')
cursor = conn.cursor()

# テーブルの作成
cursor.execute('''
CREATE TABLE IF NOT EXISTS fruits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fruit_list TEXT
)
''')

# 配列データ
fruits = ["momo", "budou", "mikan"]

# 配列をJSON形式に変換して保存
fruit_list_json = json.dumps(fruits)

# データを挿入
cursor.execute('''
INSERT INTO fruits (fruit_list) VALUES (?)
''', (fruit_list_json,))

# 変更を保存
conn.commit()

# データの取得
cursor.execute('SELECT * FROM fruits')
rows = cursor.fetchall()
for row in rows:
    print(row)

# 接続を閉じる
conn.close()

