import pynput.keyboard,sqlite3,psutil,time,os
from datetime import datetime
conn=sqlite3.connect('data/activity.db')
conn.execute('CREATE TABLE IF NOT EXISTS logs (timestamp TEXT,process TEXT, keys TEXT)')
def log_activity():
    proc=psutil.Process().name()
    while True:
        time.sleep(30)
        conn.execute('INSERT INTO logs VALUES (?,?,?)',(datetime.now().isoformat(),proc,''))
        conn.commit()