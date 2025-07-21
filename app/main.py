from flask import Flask, jsonify, request

# In-memory storage for books
books = {
    1: {"title": "1984", "author": "George Orwell", "year": 1949},
    2: {"title": "To Kill a Mockingbird", "author": "Harper Lee", "year": 1960},
}

app = Flask(__name__)

# GET /books - Retrieve the list of all books


@app.route('/books', methods=['GET'])
def get_books():
    return jsonify(books)

# GET /books/{id} - Retrieve a specific book by its ID


@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = books.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book)

# POST /books - Add a new book


@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    if not all(k in data for k in ("title", "author", "year")):
        return jsonify({"error": "Missing data"}), 400

    new_id = max(books.keys()) + 1
    books[new_id] = data
    return jsonify(books[new_id]), 201

# PUT /books/{id} - Update a book's details


@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = books.get(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    data = request.get_json()
    book.update(data)
    return jsonify(book)

# DELETE /books/{id} - Delete a book


@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    if book_id not in books:
        return jsonify({"error": "Book not found"}), 404

    del books[book_id]
    return '', 204


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
