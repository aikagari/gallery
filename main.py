from flask import Flask, render_template
import config

from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

from views.picture import picture_bp
from views.video import video_bp

auth = HTTPBasicAuth()
users = {"test_user": generate_password_hash("test")}


@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False


url_static = "//{}/get_{}/{}"
full_host = "{}:{}".format(config.HOST, config.PORT)

app = Flask(__name__)
app.register_blueprint(picture_bp)
app.register_blueprint(video_bp)


@app.route("/")
@auth.login_required
def index():
    return render_template("base.html")

# @app.route("/video")
# def video():
#     return render_template("video.html")

if __name__ == "__main__":
    app.run(debug=True)
