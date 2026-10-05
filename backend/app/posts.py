from flask import Blueprint, jsonify, request

from app.errors.exceptions import APIError

posts_bp = Blueprint('posts', __name__, url_prefix='/api/posts')

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@posts_bp.route('', methods=['GET'])
def get_posts():
    return jsonify(POSTS)


@posts_bp.route('', methods=['POST'])
def create_post():
    data = request.get_json(silent=True)

    if not data:
        raise APIError('Request body must be valid JSON', status_code=400)

    title = data.get('title')
    content = data.get('content')

    if not title:
        raise APIError(
            message='Validation failed',
            status_code=400,
            details={'required_fields': ['title']},
        )
    if not content:
        raise APIError(
            message='Validation failed',
            status_code=400,
            details={'required_fields': ['content']},
        )

    new_post = {
        'id': max(post['id'] for post in POSTS) + 1,
        'title': title,
        'content': content,
    }
    POSTS.append(new_post)

    return jsonify({'id': str(id), 'title': title, 'content': content}), 201
