#!/usr/bin/env python3
"""Replace the book catalog with 500 sample books when run as a script."""

import os

from faker import Faker

from config import create_app, db
from models import Book


def seed_books():
    fake = Faker()
    app = create_app(os.getenv('FLASK_ENV', 'dev'))

    with app.app_context():
        print('Deleting all books...')
        Book.query.delete()

        print('Creating books...')
        db.session.add_all([
            Book(
                title=fake.sentence(nb_words=4),
                author=fake.name(),
                description=fake.paragraph(nb_sentences=5),
            )
            for _ in range(500)
        ])
        db.session.commit()
        print('Complete.')


if __name__ == '__main__':
    seed_books()
