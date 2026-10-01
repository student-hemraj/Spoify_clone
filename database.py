import sqlite3

def create_tables():
    conn = sqlite3.connect("spotify.db")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS favorites(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        song_name TEXT,
        artist TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS playlists(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        playlist_name TEXT
    )
    """)

    conn.commit()
    conn.close()

create_tables()