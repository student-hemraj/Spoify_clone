import sqlite3

conn = sqlite3.connect("spotify.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS playlists(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    playlist_name TEXT
)
""")

conn.commit()
conn.close()

print("Playlists table created successfully!")