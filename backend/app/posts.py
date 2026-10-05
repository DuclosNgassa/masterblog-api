from flask import Blueprint, jsonify, request

from app.errors.exceptions import APIError

posts_bp = Blueprint('posts', __name__, url_prefix='/api/posts')

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@posts_bp.route('', methods=['GET'])
def get_posts():
    # 1. Get query parameters
    sort_field = request.args.get('sort')
    direction = request.args.get('direction', 'asc').lower()

    # Create a shallow copy of the POSTS list so we don't mutate the original stored list
    sorted_posts = list(POSTS)

    # 2. Handle invalid direction validation if 'sort' is provided
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

        # 3. Sort the posts (case-insensitive for text fields)
        reverse_order = direction == 'desc'
        sorted_posts.sort(
            key=lambda post: post[sort_field].lower(), reverse=reverse_order
        )

    # 4. Return sorted (or original order) list with 200 OK
    return jsonify(sorted_posts), 200


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


@posts_bp.route('/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    # 1. Search for the post with the matching ID
    for index, post in enumerate(POSTS):
        if post["id"] == post_id:
            # 2. Remove the post from the list
            POSTS.pop(index)

            # 3. Return a success response (or 204 No Content)
            return (
                jsonify(
                    {
                        "message": f"Post with ID {post_id} has been deleted successfully.",
                    }
                ),
                200,
            )

    # 4. If post is not found, raise an error (or call abort(404))
    raise APIError(
        message=f"Post with ID {post_id} not found.", status_code=404
    )


@posts_bp.route('/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    # 1. Parse JSON body (handles missing or empty body safely)
    data = request.get_json(silent=True) or {}

    # 2. Extract input fields
    new_title = data.get('title')
    new_content = data.get('content')

    # 3. Validate field types if provided (must be strings)
    if new_title is not None and not isinstance(new_title, str):
        raise APIError(
            message="'title' must be a string if provided.", status_code=400
        )

    if new_content is not None and not isinstance(new_content, str):
        raise APIError(
            message="'content' must be a string if provided.", status_code=400
        )

    # 4. Find the target post
    for post in POSTS:
        if post['id'] == post_id:
            # Update only if provided and not just whitespace, otherwise keep existing
            if new_title is not None and new_title.strip():
                post['title'] = new_title.strip()

            if new_content is not None and new_content.strip():
                post['content'] = new_content.strip()

            # Return updated post with 200 OK status
            return jsonify(post), 200

    # 5. Return 404 if post is not found
    raise APIError(
        message=f'Post with ID {post_id} not found.', status_code=404
    )

@posts_bp.route('/search', methods=['GET'])
def search_posts():
    # 1. Read query parameters from URL: /api/posts/search?title=...&content=...
    title_query = request.args.get('title', '').strip().lower()
    content_query = request.args.get('content', '').strip().lower()

    # If no search parameters were provided at all, return all posts (or empty list)
    if not title_query and not content_query:
        return jsonify([]), 200

    results = []

    # 2. Filter posts matching the criteria (case-insensitive search)
    for post in POSTS:
        post_title = post['title'].lower()
        post_content = post['content'].lower()

        # Match title if title_query is provided
        title_matches = title_query and title_query in post_title
        # Match content if content_query is provided
        content_matches = content_query and content_query in post_content

        if title_matches or content_matches:
            results.append(post)

    # 3. Return matching posts (or [] if no matches found) with 200 OK
    return jsonify(results), 200