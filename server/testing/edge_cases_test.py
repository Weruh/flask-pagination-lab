import importlib

import pytest

from config import create_app, db
from models import Book


@pytest.fixture
def client():
    app = create_app('test')
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_empty_catalog(client):
    response = client.get('/books')
    assert response.status_code == 200
    assert response.get_json() == {
        'page': 1, 'per_page': 5, 'total': 0, 'total_pages': 0, 'items': []
    }


@pytest.mark.parametrize('query,page,per_page', [
    ('page=abc&per_page=abc', 1, 5),
    ('page=&per_page=', 1, 5),
    ('page=0&per_page=0', 1, 5),
    ('page=-2&per_page=-3', 1, 5),
    ('page=1.5&per_page=2.5', 1, 5),
    ('per_page=1000', 1, 100),
    ('page=2&per_page=invalid', 2, 5),
])
def test_invalid_parameters(client, query, page, per_page):
    response = client.get(f'/books?{query}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['page'] == page
    assert data['per_page'] == per_page


def test_pages_are_ordered_and_do_not_overlap(client):
    db.session.add_all([
        Book(id=9, title='Last', author='Author', description='Description'),
        Book(id=2, title='First'),
        Book(id=5, title='Middle'),
    ])
    db.session.commit()

    first = client.get('/books?per_page=2').get_json()
    second = client.get('/books?page=2&per_page=2').get_json()
    assert [book['id'] for book in first['items']] == [2, 5]
    assert second['items'] == [{
        'id': 9, 'title': 'Last', 'author': 'Author', 'description': 'Description'
    }]
    assert first['total'] == second['total'] == 3
    assert first['total_pages'] == second['total_pages'] == 2


def test_page_size_is_capped(client):
    db.session.add_all([Book(title=f'Book {i}') for i in range(105)])
    db.session.commit()
    data = client.get('/books?per_page=1000').get_json()
    assert data['per_page'] == 100
    assert len(data['items']) == 100
    assert data['total'] == 105
    assert data['total_pages'] == 2


def test_factory_registers_routes_on_independent_apps(client):
    db.session.add(Book(title='Only in the first app'))
    db.session.commit()
    second_app = create_app('test')
    with second_app.app_context():
        db.create_all()
        response = second_app.test_client().get('/books')
        assert response.status_code == 200
        assert response.get_json()['total'] == 0
        db.drop_all()
    assert client.get('/books').get_json()['total'] == 1


def test_init_db_is_repeatable_and_preserves_books():
    app = create_app('test')
    runner = app.test_cli_runner()
    assert runner.invoke(args=['init-db']).exit_code == 0
    with app.app_context():
        db.session.add(Book(title='Keep me'))
        db.session.commit()
    assert runner.invoke(args=['init-db']).exit_code == 0
    with app.app_context():
        assert Book.query.one().title == 'Keep me'
        db.drop_all()


def test_importing_seed_does_not_modify_catalog(client):
    db.session.add(Book(title='Keep me'))
    db.session.commit()
    import seed

    importlib.reload(seed)
    assert Book.query.one().title == 'Keep me'


def test_seeder_replaces_catalog_with_sample_books(client, monkeypatch):
    from flask import current_app
    import seed

    app = current_app._get_current_object()
    monkeypatch.setattr(seed, 'create_app', lambda env: app)
    db.session.add(Book(title='Old book'))
    db.session.commit()
    seed.seed_books()
    assert Book.query.count() == 500
    assert Book.query.filter_by(title='Old book').count() == 0
    assert all(book.title and book.author and book.description for book in Book.query.all())
