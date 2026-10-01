from flask import Flask, render_template, request, redirect, session, url_for, send_file
import os
import requests
BASE_URL = "https://itunes.apple.com/search"


app = Flask(__name__)
app.secret_key = "spotify_secret_key_123"

UPLOAD_FOLDER = "static/profile_pics"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/')
def home():
    return render_template('login.html')

from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

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

conn.execute("""
CREATE TABLE IF NOT EXISTS playlist_songs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    playlist_name TEXT,
    song_name TEXT,
    artist TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    song_name TEXT,
    artist TEXT
)
""")

# Profile Pictures
conn.execute("""
CREATE TABLE IF NOT EXISTS profile_pictures(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    image TEXT
)
""")

# Recently Played
conn.execute("""
CREATE TABLE IF NOT EXISTS recently_played(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    song_name TEXT,
    artist TEXT
)
""")

# Ratings
conn.execute("""
CREATE TABLE IF NOT EXISTS ratings(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    song_name TEXT,
    rating INTEGER
)
""")

# Reviews
conn.execute("""
CREATE TABLE IF NOT EXISTS reviews(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    song_name TEXT,
    review TEXT
)
""")

conn.commit()
conn.close()


print("Users table created successfully")

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect('spotify.db')
        cur = conn.cursor()

        cur.execute(
    "INSERT INTO users(username,email,password) VALUES(?,?,?)",
    (username, email, hashed_password)
)

        
     
        




      

        
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():

    email = request.form['email']
    password = request.form['password']

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    )

    user = cur.fetchone()

    conn.close()

    if user and check_password_hash(user[3], password):
        session['user'] = user[1]
        return redirect('/dashboard')

    return "Invalid Email or Password"

@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM favorites WHERE username=?",
        (session['user'],)
    )
    favorite_count = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM playlists WHERE username=?",
        (session['user'],)
    )
    playlist_count = cur.fetchone()[0]

    conn.close()

    return render_template(
        'dashboard.html',
        favorite_count=favorite_count,
        playlist_count=playlist_count,
        username=session['user']
    )

@app.route('/search', methods=['GET', 'POST'])
def search():

    if 'user' not in session:
        return redirect('/')

    songs = []

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    # User ki playlists fetch karo
    cur.execute(
        "SELECT playlist_name FROM playlists WHERE username=?",
        (session['user'],)
    )

    playlists = cur.fetchall()

    if request.method == 'POST':

        query = request.form['song']

        # Save Search History
        cur.execute("""
            INSERT INTO history(username,song_name,artist)
            VALUES(?,?,?)
        """, (session['user'], query, "Search"))

        conn.commit()

        # Search Songs
        response = requests.get(
            BASE_URL,
            params={
                "term": query,
                "media": "music",
                "limit": 20
            }
        )

        songs = response.json().get("results", [])

        for song in songs:
            print("SONG :", song.get("trackName"))
            print("URL  :", song.get("previewUrl"))
            print("-------------------")

        

    conn.close()

    return render_template(
        "search.html",
        songs=songs,
        playlists=playlists
    )

@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/')

@app.route('/add_favorite')
def add_favorite():

    if 'user' not in session:
        return redirect('/')

    song = request.args.get('song')
    artist = request.args.get('artist')

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO favorites(username,song_name,artist) VALUES(?,?,?)",
        (session['user'], song, artist)
    )

    conn.commit()
    conn.close()

    return redirect('/search')

@app.route('/favorites')
def favorites():

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute(
        "SELECT song_name,artist FROM favorites WHERE username=?",
        (session['user'],)
    )

    songs = cur.fetchall()

    conn.close()

    return render_template('favorites.html', songs=songs)

@app.route('/create_playlist', methods=['GET', 'POST'])
def create_playlist():

    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':

        playlist_name = request.form['playlist_name']

        conn = sqlite3.connect('spotify.db')
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO playlists(username,playlist_name) VALUES(?,?)",
            (session['user'], playlist_name)
        )

        conn.commit()
        conn.close()

        return redirect('/playlists')

    return render_template('create_playlist.html')

@app.route('/playlists')
def playlists():

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute(
        "SELECT playlist_name FROM playlists WHERE username=?",
        (session['user'],)
    )

    playlists = cur.fetchall()

    conn.close()

    return render_template(
        'playlists.html',
        playlists=playlists
    )

@app.route('/add_to_playlist', methods=['POST'])
def add_to_playlist():

    if 'user' not in session:
        return redirect('/')

    playlist_name = request.form['playlist_name']
    song_name = request.form['song_name']
    artist = request.form['artist']

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO playlist_songs
        (playlist_name,song_name,artist)
        VALUES(?,?,?)
    """, (playlist_name,song_name,artist))

    conn.commit()
    conn.close()

    return redirect('/search')

@app.route('/playlist/<playlist_name>')
def view_playlist(playlist_name):

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute("""
        SELECT song_name,artist
        FROM playlist_songs
        WHERE playlist_name=?
    """, (playlist_name,))

    songs = cur.fetchall()

    conn.close()

    return render_template(
        'playlist_songs.html',
        songs=songs,
        playlist_name=playlist_name
    )


@app.route('/profile')
def profile():

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute(
        "SELECT username,email FROM users WHERE username=?",
        (session['user'],)
    )
    user = cur.fetchone()

    cur.execute(
        "SELECT COUNT(*) FROM favorites WHERE username=?",
        (session['user'],)
    )
    favorite_count = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM playlists WHERE username=?",
        (session['user'],)
    )
    playlist_count = cur.fetchone()[0]

    cur.execute("""
        SELECT image
        FROM profile_pictures
        WHERE username=?
    """, (session['user'],))

    profile_pic = cur.fetchone()

    conn.close()

    return render_template(
        "profile.html",
        user=user,
        favorite_count=favorite_count,
        playlist_count=playlist_count,
        profile_pic=profile_pic
    )

@app.route('/remove_favorite/<song_name>')
def remove_favorite(song_name):

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM favorites
        WHERE username=? AND song_name=?
    """, (session['user'], song_name))

    conn.commit()
    conn.close()

    return redirect('/favorites')

@app.route('/trending')
def trending():

    response = requests.get(
        BASE_URL,
        params={
            "term":"top songs",
            "media":"music",
            "limit":20
        }
    )

    songs = response.json().get("results", [])

    return render_template(
        "trending.html",
        songs=songs
    )


@app.route('/remove_song/<playlist_name>/<song_name>')
def remove_song(playlist_name, song_name):

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM playlist_songs
        WHERE playlist_name=? AND song_name=?
    """, (playlist_name, song_name))

    conn.commit()
    conn.close()

    return redirect(f'/playlist/{playlist_name}')

@app.route('/play_song', methods=['POST'])
def play_song():

    if 'user' not in session:
        return redirect('/')

    song_name = request.form['song_name']
    artist = request.form['artist']

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO recently_played
        (username,song_name,artist)
        VALUES(?,?,?)
    """, (session['user'], song_name, artist))

    conn.commit()
    conn.close()

    return "Success"

@app.route('/recently_played')
def recently_played():

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute("""
        SELECT song_name,artist
        FROM recently_played
        WHERE username=?
        ORDER BY id DESC
        LIMIT 20
    """, (session['user'],))

    songs = cur.fetchall()

    conn.close()

    return render_template(
        'recently_played.html',
        songs=songs
    )

@app.route('/admin')
def admin():

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM favorites")
    total_favorites = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM playlists")
    total_playlists = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM history")
    total_searches = cur.fetchone()[0]

    conn.close()

    return render_template(
        'admin.html',
        total_users=total_users,
        total_favorites=total_favorites,
        total_playlists=total_playlists,
        total_searches=total_searches
    )

@app.route('/rate_song', methods=['POST'])
def rate_song():

    if 'user' not in session:
        return redirect('/')

    song_name = request.form['song_name']
    rating = request.form['rating']

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO ratings(username,song_name,rating)
        VALUES(?,?,?)
    """, (session['user'], song_name, rating))

    conn.commit()
    conn.close()

    return redirect('/search')

@app.route('/ratings')
def ratings():

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute("""
        SELECT song_name,rating
        FROM ratings
        WHERE username=?
    """, (session['user'],))

    songs = cur.fetchall()

    conn.close()

    return render_template(
        'ratings.html',
        songs=songs
    )

@app.route('/add_review', methods=['POST'])
def add_review():

    if 'user' not in session:
        return redirect('/')

    song_name = request.form['song_name']
    review = request.form['review']

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO reviews(username,song_name,review)
        VALUES(?,?,?)
    """, (session['user'], song_name, review))

    conn.commit()
    conn.close()

    return redirect('/search')

@app.route('/reviews')
def reviews():

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute("""
        SELECT song_name,review
        FROM reviews
        WHERE username=?
    """, (session['user'],))

    reviews = cur.fetchall()

    conn.close()

    return render_template(
        'reviews.html',
        reviews=reviews
    )

@app.route('/lyrics')
def lyrics():

    song = request.args.get('song')
    artist = request.args.get('artist')

    url = f"https://api.lyrics.ovh/v1/{artist}/{song}"

    try:
        response = requests.get(url)
        data = response.json()
        lyrics = data.get("lyrics", "Lyrics not found")
    except:
        lyrics = "Lyrics not available"

    return render_template(
        "lyrics.html",
        song=song,
        artist=artist,
        lyrics=lyrics
    )


from werkzeug.utils import secure_filename

@app.route('/upload_profile', methods=['POST'])
def upload_profile():

    if 'user' not in session:
        return redirect('/')

    file = request.files['profile_pic']

    if file:

        filename = secure_filename(file.filename)

        filepath = os.path.join(
            app.config['UPLOAD_FOLDER'],
            filename
        )

        file.save(filepath)

        conn = sqlite3.connect('spotify.db')
        cur = conn.cursor()

        cur.execute("""
            DELETE FROM profile_pictures
            WHERE username=?
        """, (session['user'],))

        cur.execute("""
            INSERT INTO profile_pictures
            (username,image)
            VALUES(?,?)
        """, (session['user'], filename))

        conn.commit()
        conn.close()

    return redirect('/profile')

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    if request.method == 'POST':

        new_email = request.form['email']

        cur.execute("""
            UPDATE users
            SET email=?
            WHERE username=?
        """, (new_email, session['user']))

        conn.commit()

        conn.close()

        return redirect('/profile')

    cur.execute("""
        SELECT username,email
        FROM users
        WHERE username=?
    """, (session['user'],))

    user = cur.fetchone()

    conn.close()

    return render_template(
        'edit_profile.html',
        user=user
    )

from reportlab.pdfgen import canvas
from flask import send_file
import io


from reportlab.pdfgen import canvas
from flask import send_file
import io

@app.route('/download_playlist/<playlist_name>')
def download_playlist(playlist_name):

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute("""
        SELECT song_name, artist
        FROM playlist_songs
        WHERE playlist_name=?
    """, (playlist_name,))

    songs = cur.fetchall()

    conn.close()

    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer)

    pdf.setTitle(playlist_name)

    pdf.drawString(100, 800,
                   f"Playlist: {playlist_name}")

    y = 760

    for song in songs:

        pdf.drawString(
            100,
            y,
            f"{song[0]} - {song[1]}"
        )

        y -= 25

    pdf.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{playlist_name}.pdf",
        mimetype='application/pdf'
    )

from reportlab.pdfgen import canvas
from flask import send_file
import io

@app.route('/download_report')
def download_report():

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    username = session['user']

    cur.execute(
        "SELECT COUNT(*) FROM favorites WHERE username=?",
        (username,)
    )
    favorites = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM playlists WHERE username=?",
        (username,)
    )
    playlists = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM history WHERE username=?",
        (username,)
    )
    searches = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM recently_played WHERE username=?",
        (username,)
    )
    played = cur.fetchone()[0]

    conn.close()

    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer)

    pdf.setTitle("Spotify Analytics Report")

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(150, 800, "Spotify Analytics Report")

    pdf.setFont("Helvetica", 12)

    pdf.drawString(100, 740, f"Username : {username}")
    pdf.drawString(100, 700, f"Favorites : {favorites}")
    pdf.drawString(100, 670, f"Playlists : {playlists}")
    pdf.drawString(100, 640, f"Searches : {searches}")
    pdf.drawString(100, 610, f"Recently Played : {played}")

    pdf.drawString(100, 550, "Generated By Spotify Clone")

    pdf.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="analytics_report.pdf",
        mimetype="application/pdf"
    )
@app.route('/recommendations')
def recommendations():

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute("""
        SELECT song_name
        FROM favorites
        WHERE username=?
        ORDER BY id DESC
        LIMIT 1
    """, (session['user'],))

    fav_song = cur.fetchone()

    conn.close()

    songs = []

    if fav_song:

        response = requests.get(
            BASE_URL,
            params={
                "term": fav_song[0],
                "media": "music",
                "limit": 10
            }
        )

        songs = response.json().get("results", [])

    return render_template(
        "recommendations.html",
        songs=songs
    )

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == 'POST':

        username = request.form['username']
        new_password = request.form['new_password']

        conn = sqlite3.connect('spotify.db')
        cur = conn.cursor()

        cur.execute("""
            UPDATE users
            SET password=?
            WHERE username=?
        """, (new_password, username))

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('forgot_password.html')

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import os

@app.route('/analytics')
def analytics():

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute("""
        SELECT artist, COUNT(*)
        FROM favorites
        WHERE username=?
        GROUP BY artist
    """, (session['user'],))

    data = cur.fetchall()

    conn.close()

    if data:

        artists = [row[0] for row in data]
        counts = [row[1] for row in data]

        plt.figure(figsize=(8,5))
        plt.bar(artists, counts)
        plt.title("Favorite Artists")
        plt.xticks(rotation=45)

        chart_path = "static/chart.png"

        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()

    return render_template(
        "analytics.html"
    )

@app.route('/artist_search', methods=['GET', 'POST'])
def artist_search():

    if 'user' not in session:
        return redirect('/')

    artists = []

    if request.method == 'POST':

        artist_name = request.form['artist']

        response = requests.get(
            BASE_URL,
            params={
                "term": artist_name,
                "entity": "musicArtist",
                "limit": 20
            }
        )

        artists = response.json().get("results", [])

    return render_template(
        "artist_search.html",
        artists=artists
    )

@app.route('/artist/<artist_name>')
def artist_songs(artist_name):

    if 'user' not in session:
        return redirect('/')

    response = requests.get(
        BASE_URL,
        params={
            "term": artist_name,
            "media": "music",
            "limit": 20
        }
    )

    songs = response.json().get("results", [])

    return render_template(
        "artist_songs.html",
        songs=songs,
        artist_name=artist_name
    )

@app.route('/history')
def history():

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute("""
        SELECT song_name
        FROM history
        WHERE username=?
        ORDER BY id DESC
    """, (session['user'],))

    searches = cur.fetchall()

    conn.close()

    return render_template(
        'history.html',
        searches=searches
    )

@app.route('/like_song', methods=['POST'])
def like_song():

    if 'user' not in session:
        return redirect('/')

    song_name = request.form['song_name']

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO song_likes(username,song_name)
        VALUES(?,?)
    """, (session['user'], song_name))

    conn.commit()
    conn.close()

    return redirect('/search')

@app.route('/liked_songs')
def liked_songs():

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute("""
        SELECT song_name
        FROM song_likes
        WHERE username=?
    """, (session['user'],))

    songs = cur.fetchall()

    conn.close()

    return render_template(
        'liked_songs.html',
        songs=songs
    )

def add_notification(username, message):

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO notifications(username,message)
        VALUES(?,?)
    """, (username, message))

    conn.commit()
    conn.close()


@app.route('/notifications')
def notifications():

    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('spotify.db')
    cur = conn.cursor()

    cur.execute("""
        SELECT message
        FROM notifications
        WHERE username=?
        ORDER BY id DESC
    """, (session['user'],))

    notifications = cur.fetchall()

    conn.close()

    return render_template(
        'notifications.html',
        notifications=notifications
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)