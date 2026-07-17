from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), nullable=False)

    category = db.Column(db.String(50), nullable=False)

    description = db.Column(db.String(300))

    filename = db.Column(db.String(200), nullable=False)

    downloads = db.Column(db.Integer, default=0)