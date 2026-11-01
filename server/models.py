from marshmallow import Schema, fields

from config import db

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String)
    description = db.Column(db.String)

    def __repr__(self):
        return f'<Book {self.id}: {self.title}>'

class BookSchema(Schema):
    id = fields.Int()
    title = fields.String()
    author = fields.String()
    description = fields.String()
