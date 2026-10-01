import sqlite3
import os

print("Database Path:", os.path.abspath("spotify.db"))

conn = sqlite3.connect("spotify.db")
cur = conn.cursor()

# Users Table
cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    password TEXT
)
""")

# Favorites Table
cur.execute("""
CREATE TABLE IF NOT EXISTS favorites(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    song_name TEXT,
    artist TEXT
)
""")

# History Table
cur.execute("""
CREATE TABLE IF NOT EXISTS history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    song_name TEXT,
    artist TEXT
)
""")

# Playlists Table
cur.execute("""
CREATE TABLE IF NOT EXISTS playlists(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    playlist_name TEXT
)
""")

# Playlist Songs Table
cur.execute("""
CREATE TABLE IF NOT EXISTS playlist_songs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    playlist_id INTEGER,
    song_name TEXT,
    artist TEXT
)
""")

conn.commit()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", cur.fetchall())

conn.close()

print("Database Created Successfully!")