from flask import Flask, render_template, jsonify, abort, request, url_for

app = Flask(__name__)

books = [
    {
        "id": 1,
        "title": "Lập trình Python",
        "author": "Nguyễn Văn A",
        "year": 2024,
        "category": "Lập trình",
        "available": True
    },
    {
        "id": 2,
        "title": "Lập trình Java",
        "author": "Trần Văn B",
        "year": 2023,
        "category": "Lập trình",
        "available": True
    },
    {
        "id": 3,
        "title": "Cơ sở dữ liệu",
        "author": "Lê Văn C",
        "year": 2022,
        "category": "Cơ sở dữ liệu",
        "available": False
    },
    {
        "id": 4,
        "title": "Mạng máy tính",
        "author": "Phạm Văn D",
        "year": 2021,
        "category": "Mạng",
        "available": True
    },
    {
        "id": 5,
        "title": "Phân tích hệ thống",
        "author": "Nguyễn Thị E",
        "year": 2025,
        "category": "Phân tích hệ thống",
        "available": False
    }
]


# Trang chủ
@app.route("/")
def index():
    total_books = len(books)
    available_books = sum(1 for book in books if book["available"])

    return render_template(
        "index.html",
        total_books=total_books,
        available_books=available_books
    )


# Danh sách sách + lọc theo thể loại
@app.route("/books")
def book_list():
    category = request.args.get("category")

    if category:
        filtered_books = [
            book for book in books
            if book["category"] == category
        ]
    else:
        filtered_books = books

    categories = sorted(set(book["category"] for book in books))

    return render_template(
        "books.html",
        books=filtered_books,
        categories=categories,
        selected_category=category
    )


# Chi tiết sách
@app.route("/books/<int:book_id>")
def book_detail(book_id):
    book = next((book for book in books if book["id"] == book_id), None)

    if book is None:
        abort(404, description=f"Không có sách với ID = {book_id}")

    return render_template("book_detail.html", book=book)


# API danh sách sách
@app.route("/api/books")
def api_books():
    return jsonify(books)


# API chi tiết sách
@app.route("/api/books/<int:book_id>")
def api_book_detail(book_id):
    book = next((book for book in books if book["id"] == book_id), None)

    if book is None:
        return jsonify({
            "error": f"Không có sách với ID = {book_id}"
        }), 404

    return jsonify(book)


# Trang 404 tùy biến
@app.errorhandler(404)
def page_not_found(error):
    return render_template(
        "404.html",
        message=error.description if hasattr(error, "description") else "Trang không tồn tại"
    ), 404


if __name__ == "__main__":
    app.run(debug=True)