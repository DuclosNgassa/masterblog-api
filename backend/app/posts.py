from flask import Blueprint, jsonify, request

from app.errors.exceptions import APIError

posts_bp = Blueprint('posts', __name__, url_prefix='/api/posts')

POSTS:list[dict] = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@posts_bp.route('', methods=['GET'])
def get_posts():
    sort_field = request.args.get('sort')
    direction = request.args.get('direction', 'asc').lower()

    sorted_posts = list(POSTS)

    if sort_field:
        if sort_field not in ['title', 'content']:
            raise APIError(
                message="Invalid 'sort' parameter. Allowed values are 'title' or 'content'.",
                status_code=400,
            )

        if direction not in ['asc', 'desc']:
            raise APIError(
                message="Invalid 'direction' parameter. Allowed values are 'asc' or 'desc'.",
                status_code=400,
            )

        reverse_order = direction == 'desc'
        sorted_posts.sort(
            key=lambda post: post[sort_field].lower(), reverse=reverse_order
        )

    return jsonify(sorted_posts), 200


@posts_bp.route('', methods=['POST'])
def create_post():
    data = request.get_json(silent=True) or {}

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


@posts_bp.route('/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    for index, post in enumerate(POSTS):
        if post["id"] == post_id:
            POSTS.pop(index)

            return (
                jsonify(
                    {
                        "message": f"Post with ID {post_id} has been deleted successfully.",
                    }
                ),
                200,
            )

    raise APIError(
        message=f"Post with ID {post_id} not found.", status_code=404
    )


@posts_bp.route('/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.get_json(silent=True) or {}

    new_title = data.get('title')
    new_content = data.get('content')

    if new_title is not None and not isinstance(new_title, str):
        raise APIError(
            message="'title' must be a string if provided.", status_code=400
        )

    if new_content is not None and not isinstance(new_content, str):
        raise APIError(
            message="'content' must be a string if provided.", status_code=400
        )

    for post in POSTS:
        if post['id'] == post_id:
            if new_title is not None and new_title.strip():
                post['title'] = new_title.strip()

            if new_content is not None and new_content.strip():
                post['content'] = new_content.strip()

            return jsonify(post), 200

    raise APIError(
        message=f'Post with ID {post_id} not found.', status_code=404
    )

@posts_bp.route('/search', methods=['GET'])
def search_posts():
    title_query = request.args.get('title', '').strip().lower()
    content_query = request.args.get('content', '').strip().lower()

    if not title_query and not content_query:
        return jsonify([]), 200

    results = []

    for post in POSTS:
        post_title = post['title'].lower()
        post_content = post['content'].lower()

        title_matches = title_query and title_query in post_title
        content_matches = content_query and content_query in post_content

        if title_matches or content_matches:
            results.append(post)

    return jsonify(results), 200