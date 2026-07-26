from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from models import db, Material
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = "your_secret_key_here"
UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# Home Page
@app.route("/")
def home():
    materials = Material.query.all()
    return render_template("index.html", materials=materials)

# Admin Login
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

# Dashboard
@app.route("/dashboard")
def dashboard():

    if not session.get("admin"):
        return redirect(url_for("login"))

    return render_template("dashboard.html")

# Logout
@app.route("/logout")
def logout():

    session.pop("admin", None)

    return redirect(url_for("home"))
@app.route("/upload", methods=["GET", "POST"])
def upload():

    if not session.get("admin"):
        return redirect(url_for("login"))

    if request.method == "POST":

        title = request.form["title"]
        category = request.form["category"]
        description = request.form["description"]

        file = request.files["file"]

        if file:

            filename = secure_filename(file.filename)

            file.save(
                os.path.join(app.config["UPLOAD_FOLDER"], filename)
            )

            material = Material(
                title=title,
                category=category,
                description=description,
                filename=filename
            )

            db.session.add(material)
            db.session.commit()

            return redirect("/")

    return render_template("upload.html")
@app.route("/download/<int:id>")
def download(id):

    material = Material.query.get_or_404(id)

    material.downloads += 1
    db.session.commit()

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        material.filename,
        as_attachment=True
    )
@app.route("/bulk-upload", methods=["GET", "POST"])
def bulk_upload():

    if not session.get("admin"):
        return redirect(url_for("login"))

    if request.method == "POST":

        category = request.form["category"].strip()
        description = request.form["description"].strip()
        files = request.files.getlist("files")

        uploaded_count = 0

        for file in files:
            if file and file.filename:

                original_name = secure_filename(file.filename)
                filename = f"{uuid.uuid4().hex}_{original_name}"

                file.save(
                    os.path.join(app.config["UPLOAD_FOLDER"], filename)
                )

                title = os.path.splitext(original_name)[0].replace("_", " ")

                material = Material(
                    title=title,
                    category=category,
                    description=description,
                    filename=filename
                )

                db.session.add(material)
                uploaded_count += 1

        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("bulk_upload.html")
if __name__ == "__main__":
    app.run(debug=True)
