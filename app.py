import os
import pytz
from datetime import datetime
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session
from flask import Flask, redirect, url_for, session, request, render_template

# Allow insecure HTTP for OAuth (dev only)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# OAuth Config
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://localhost:5000/callback"
AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://accounts.google.com/o/oauth2/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v1/userinfo"
SCOPE = ['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email']

# Static folders
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp')
VIDEO_FOLDER = os.path.join('static', 'videos')
os.makedirs(VIDEO_FOLDER, exist_ok=True)


@app.route('/')
def home():
    if 'profile' in session:
        profile = session['profile']
        ist = datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")
        return render_template('welcome.html', profile=profile, ist=ist)
    return render_template('home.html')


@app.route('/login')
def login():
    google = OAuth2Session(CLIENT_ID, scope=SCOPE, redirect_uri=REDIRECT_URI)
    authorization_url, state = google.authorization_url(
        AUTHORIZATION_BASE_URL,
        access_type='offline', prompt='select_account'
    )
    session['oauth_state'] = state
    return redirect(authorization_url)


@app.route('/callback')
def callback():
    if 'oauth_state' not in session:
        return redirect(url_for('home'))

    google = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, state=session['oauth_state'])
    token = google.fetch_token(
        TOKEN_URL,
        client_secret=CLIENT_SECRET,
        authorization_response=request.url
    )
    resp = google.get(USER_INFO_URL)
    session['profile'] = resp.json()
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)