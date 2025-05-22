import os
import base64
import hashlib
import requests
import secrets
import urllib.parse

from pathlib import Path
from flask import Flask, redirect, request, session, url_for, render_template_string, abort
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
from urllib.parse import urlencode

load_dotenv()

# Allow OAuth over HTTP for development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 300  # 5 minutes

# Make sessions permanent by default
@app.before_request
def make_session_permanent():
    session.permanent = True

CLIENT_KEY = os.environ.get("TIKTOK_CLIENT_ID")
CLIENT_SECRET = os.environ.get("TIKTOK_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("TIKTOK_REDIRECT_URI")
AUTHORIZATION_URL = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"


def generate_code_verifier():
    token = secrets.token_urlsafe(64)
    return token[:128] if len(token) > 128 else token


def generate_code_challenge(verifier):
    return hashlib.sha256(verifier.encode('utf-8')).hexdigest()


def read_static_file(filename):
    static_path = Path(app.static_folder) / filename
    return static_path.read_text(encoding='utf-8')


@app.route("/")
def home():
    access_token = session.get("access_token")
    refresh_token = session.get("refresh_token")
    expires_in = session.get("expires_in")
    html_content = read_static_file("index.html")
    
    if access_token:
        html_content = html_content.replace(
            "<h1>Welcome to AI TikTok Video Uploader</h1>",
            f"<h1>Welcome to AI TikTok Video Uploader</h1><p>You are logged in!</p><p><a href='/logout'>Logout</a></p>"
        )
    else:
        html_content = html_content.replace(
            "<ul>",
            "<ul><li><a href='/login'>Login with TikTok</a></li>"
        )
    
    token_info = "<div class='token-info' style='margin: 20px; padding: 10px; border: 1px solid #ccc;'>"
    if access_token:
        token_info += f"<p><strong>Access Token:</strong> {access_token}</p>"
        if refresh_token:
            token_info += f"<p><strong>Refresh Token:</strong> {refresh_token}</p>"
        if expires_in:
            token_info += f"<p><strong>Expires In:</strong> {expires_in} seconds</p>"
    else:
        token_info += "<p><strong>No token information available</strong> - please log in with TikTok to get access</p>"
    token_info += "</div>"
    
    html_content = html_content.replace("</body>", f"{token_info}</body>")
    return html_content


@app.route("/login")
def login():
    # Generate PKCE parameters
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    session["code_verifier"] = code_verifier
    session.modified = True # Ensure session is saved immediately

    state = base64.urlsafe_b64encode(os.urandom(30)).rstrip(b"=").decode("utf-8")
    session["oauth_state"] = state
    session.modified = True

    params = {
        'response_type': 'code',
        'client_key': CLIENT_KEY,
        'redirect_uri': REDIRECT_URI,
        'scope': 'user.info.basic,video.publish,video.upload',
        'state': state,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }
    
    authorization_url = f"{AUTHORIZATION_URL}?{urlencode(params)}"

    return redirect(authorization_url)


@app.route("/callback")
def callback():

    code = request.args.get('code')        
    code_verifier = session.get("code_verifier")
    if not code_verifier:
        raise Exception("No code_verifier found in session. Session may have been lost.")
        
    decoded_code = urllib.parse.unquote(code)
    print(f"URL decoded code: {decoded_code}")
        
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache'
    }
    data = {
        'client_key': CLIENT_KEY,
        'client_secret': CLIENT_SECRET,
        'code': decoded_code,
        'grant_type': 'authorization_code',
        'code_verifier': code_verifier,
        'redirect_uri': REDIRECT_URI
    }
    
    response = requests.post(TOKEN_URL, headers=headers, data=data, timeout=5)
    
    if response.ok:
        token = response.json()
        print(token)
        session["access_token"] = token.get("access_token")
        session["refresh_token"] = token.get("refresh_token")
        session["expires_in"] = token.get("expires_in")
        session.modified = True
        return redirect(url_for("home"))
    else:
        print("Token request failed:", response.status_code, response.text)
        return f"Failed to get token: {response.text}", 500

@app.route("/refresh")
def refresh():
    """Manually refresh the access token using the refresh token."""
    refresh_token = session.get("refresh_token")
    if not refresh_token:
        return "No refresh token found. Please login again.", 400

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache'
    }
    data = {
        'client_key': CLIENT_KEY,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data, timeout=5)

    if response.ok:
        token = response.json()
        print("Refreshed token:", token)
        session["access_token"] = token.get("access_token")
        session["refresh_token"] = token.get("refresh_token", refresh_token)
        session["expires_in"] = token.get("expires_in")
        session.modified = True
        return redirect(url_for("home"))
    else:
        print("Refresh token request failed:", response.status_code, response.text)
        return f"Failed to refresh token: {response.text}", 500

@app.route("/tos")
def tos():
    return read_static_file("tos.html")


@app.route("/privacy")
def privacy():
    return read_static_file("privacy.html")


@app.route("/demo")
def demo():
    return read_static_file("demo.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
