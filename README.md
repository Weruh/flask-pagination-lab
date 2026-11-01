# Flask Pagination Lab

A Flask REST API that returns books in pages, with metadata clients can use to
navigate the catalog. Built with Flask-RESTful, Flask-SQLAlchemy, Marshmallow,
and SQLite. This project is an API; it does not include a frontend.

## Setup

The Pipfile targets Python 3.8.13. Install that version and Pipenv, then run
these commands from the repository root:

```bash
pipenv sync
pipenv run flask --app server/app.py init-db
pipenv run python server/seed.py
pipenv run python server/app.py
```

The API runs at http://localhost:5555. The development database is stored at
`server/instance/app.db` and is ignored by Git. `init-db` creates missing tables
and can be rerun without deleting books. The optional seed script **replaces
all existing books** with 500 sample records; run it only for sample data.

To use an already installed compatible Python version, create a virtual
environment and install the existing locked dependencies:

```bash
python3 -m venv .venv
pipenv requirements --hash > /tmp/flask-pagination-requirements.txt
.venv/bin/python -m pip install --require-hashes -r /tmp/flask-pagination-requirements.txt
.venv/bin/python -m flask --app server/app.py init-db
.venv/bin/python server/seed.py
.venv/bin/python server/app.py
```

The requirements export is temporary; `Pipfile.lock` remains the dependency source.

## Books API

```bash
curl 'http://localhost:5555/books?page=2&per_page=3'
```

`GET /books` returns HTTP 200 with this structure (example for 20 books):

```json
{
  "page": 2,
  "per_page": 3,
  "total": 20,
  "total_pages": 7,
  "items": [
    {"id": 4, "title": "Book 4", "author": "Author", "description": null},
    {"id": 5, "title": "Book 5", "author": "Author", "description": null},
    {"id": 6, "title": "Book 6", "author": "Author", "description": null}
  ]
}
```

| Parameter | Default | Behavior |
| --- | --- | --- |
| `page` | `1` | Positive integer; invalid, empty, zero, or negative values use `1`. |
| `per_page` | `5` | Positive integer; invalid, empty, zero, or negative values use `5`. Values over `100` are capped at `100`. |

Books are ordered by ascending ID so pages are consistent for an unchanged
catalog. A page beyond the last page returns `items: []` while retaining the
requested page and catalog totals. An empty database returns `total: 0` and
`total_pages: 0`. Author and description may be `null`.

The implementation uses SQLAlchemy pagination to fetch only the requested page,
rather than loading the entire catalog into memory. See the
[Flask-SQLAlchemy pagination documentation](https://flask-sqlalchemy.readthedocs.io/en/stable/pagination/).

## Tests

From the repository root:

```bash
pipenv run pytest -q
```

Or, with the local virtual environment:

```bash
.venv/bin/python -m pytest -q
```

Tests use isolated in-memory SQLite databases. Coverage includes defaults,
custom page sizes, partial and out-of-range pages, empty catalogs, invalid
parameters, page-size limits, ordering, independent application instances,
database initialization, and safe seeder imports.

## Schema changes

Flask-Migrate remains available for future schema changes. This lab does not
ship a migration history. To start tracking migrations, run from `server/`:

```bash
pipenv run flask --app app db init
pipenv run flask --app app db migrate -m "Initial schema"
pipenv run flask --app app db upgrade
```

Generate the initial migration against an empty database so it captures the
schema. Use migrations for subsequent schema changes; `init-db` only creates
missing tables.

## Lab submission

After reviewing and testing your changes, commit and push them to your course
repository to submit through Canvas/CodeGrade.
