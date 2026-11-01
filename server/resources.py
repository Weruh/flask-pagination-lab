from flask import request
from flask_restful import Resource

from models import Book, BookSchema


class Books(Resource):
    def get(self):
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=5, type=int)

        # Normalize invalid input and bound the data returned per request.
        page = max(1, page)
        per_page = min(100, per_page) if per_page > 0 else 5
        pagination = Book.query.order_by(Book.id).paginate(
            page=page, per_page=per_page, max_per_page=100, error_out=False
        )

        return {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'total_pages': pagination.pages,
            'items': BookSchema(many=True).dump(pagination.items),
        }, 200
