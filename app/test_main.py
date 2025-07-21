import pytest
import json
from main import app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_book():
    """Sample book data for testing."""
    return {
        "title": "Test Book",
        "author": "Test Author", 
        "year": 2023
    }


class TestBooksAPI:
    """Test cases for the Books API endpoints."""

    def test_get_all_books(self, client):
        """Test GET /books endpoint."""
        response = client.get('/books')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, dict)
        assert len(data) >= 2  # Initial books

    def test_get_book_by_id(self, client):
        """Test GET /books/{id} endpoint with valid ID."""
        response = client.get('/books/1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['title'] == '1984'
        assert data['author'] == 'George Orwell'

    def test_get_book_not_found(self, client):
        """Test GET /books/{id} endpoint with invalid ID."""
        response = client.get('/books/999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data

    def test_add_new_book(self, client, sample_book):
        """Test POST /books endpoint."""
        response = client.post('/books', 
                             data=json.dumps(sample_book),
                             content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['title'] == sample_book['title']
        assert data['author'] == sample_book['author']

    def test_add_book_missing_data(self, client):
        """Test POST /books endpoint with missing data."""
        incomplete_book = {"title": "Incomplete Book"}
        response = client.post('/books',
                             data=json.dumps(incomplete_book),
                             content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_update_book(self, client):
        """Test PUT /books/{id} endpoint."""
        update_data = {"title": "Updated Title"}
        response = client.put('/books/1',
                            data=json.dumps(update_data),
                            content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['title'] == 'Updated Title'

    def test_update_book_not_found(self, client):
        """Test PUT /books/{id} endpoint with invalid ID."""
        update_data = {"title": "Updated Title"}
        response = client.put('/books/999',
                            data=json.dumps(update_data),
                            content_type='application/json')
        assert response.status_code == 404

    def test_delete_book(self, client):
        """Test DELETE /books/{id} endpoint."""
        # First add a book to delete
        sample_book = {"title": "To Delete", "author": "Test", "year": 2023}
        add_response = client.post('/books',
                                 data=json.dumps(sample_book),
                                 content_type='application/json')
        book_data = json.loads(add_response.data)
        
        # Get the new book ID from the current books
        get_response = client.get('/books')
        books = json.loads(get_response.data)
        book_id = max(books.keys())
        
        # Delete the book
        delete_response = client.delete(f'/books/{book_id}')
        assert delete_response.status_code == 204

    def test_delete_book_not_found(self, client):
        """Test DELETE /books/{id} endpoint with invalid ID."""
        response = client.delete('/books/999')
        assert response.status_code == 404

    def test_api_integration(self, client, sample_book):
        """Test complete CRUD operations flow."""
        # Create
        create_response = client.post('/books',
                                    data=json.dumps(sample_book),
                                    content_type='application/json')
        assert create_response.status_code == 201
        
        # Get all books to find the new book ID
        get_all_response = client.get('/books')
        books = json.loads(get_all_response.data)
        book_id = max(books.keys())
        
        # Read
        read_response = client.get(f'/books/{book_id}')
        assert read_response.status_code == 200
        
        # Update
        update_data = {"title": "Updated Integration Test"}
        update_response = client.put(f'/books/{book_id}',
                                   data=json.dumps(update_data),
                                   content_type='application/json')
        assert update_response.status_code == 200
        
        # Delete
        delete_response = client.delete(f'/books/{book_id}')
        assert delete_response.status_code == 204 