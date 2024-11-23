from flask import Flask, render_template, request, redirect, url_for, flash
from models import get_session, Member, Book, Category, BookCategory

app = Flask(__name__)
app.secret_key = 'WhatIsThis'  # Ganti dengan secret key yang aman

# Inisialisasi session database
session = get_session()

@app.route('/', methods=['GET', 'POST'])
def index():
    # Ambil semua kategori dari database untuk ditampilkan di filter
    categories = session.query(Category).all()
    members = session.query(Member).all()

    # Ambil kategori yang dipilih dari parameter URL
    selected_category_id = request.args.get('kategori', None)

    if selected_category_id:
        # Jika ada kategori yang dipilih, ambil buku yang sesuai
        books = session.query(Book).join(BookCategory).filter(BookCategory.category_id == selected_category_id).all()
    else:
        # Jika tidak ada kategori yang dipilih, ambil semua buku
        books = session.query(Book).all()

    return render_template('index.html', books=books, categories=categories, members=members)

# Route untuk mengelola anggota (CRUD)
@app.route('/members')
def members():
    all_members = session.query(Member).all()
    return render_template('member/view_member.html', members=all_members)

@app.route('/add_member', methods=['GET','POST'])
def add_member():
    if request.method == 'POST':
        nama = request.form['nama']
        email = request.form['email']
        
        if not nama or not email:
            flash('Nama dan Email tidak boleh kosong!')
            return redirect(url_for('members'))

        new_member = Member(nama=nama, email=email)
        
        session.add(new_member)
        session.commit()
        
        flash('Anggota berhasil ditambahkan!')
        return redirect(url_for('members'))
    
    return render_template('member/add_member.html')

@app.route('/edit_member/<int:id>', methods=['GET', 'POST'])
def edit_member(id):
    member = session.query(Member).filter(Member.id == id).first()

    if not member:
        flash('Anggota tidak ditemukan!')
        return redirect(url_for('members'))

    if request.method == 'POST':
        member.nama = request.form['nama']
        member.email = request.form['email']
        
        if not member.nama or not member.email:
            flash('Nama dan Email tidak boleh kosong!')
            return render_template('member/edit_member.html', member=member)  

        session.commit()
        flash('Anggota berhasil diperbarui!')
        return redirect(url_for('members'))

    return render_template('member/edit_member.html', member=member)

@app.route('/delete_member/<int:id>', methods=['POST']) 
def delete_member(id):
    member = session.query(Member).filter(Member.id == id).first()
    if member:
        session.delete(member)  # Delete from the database
        session.commit()
        flash('Anggota berhasil dihapus!')
    else:
        flash('Anggota tidak ditemukan!')
    return redirect(url_for('members'))

# Route untuk mengelola buku (CRUD)
@app.route('/books')
def books():
    all_books = session.query(Book).all()
    all_members = session.query(Member).all()
    # Menampilkan semua buku beserta anggotanya (jika ada)
    for book in all_books:
        if book.member:
            print(f"Buku: {book.judul}, Dipinjam oleh: {book.member.nama}")
        else:
            print(f"Buku: {book.judul}, Status: Tersedia")

    return render_template('buku/view_buku.html', books=all_books, members=all_members)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        judul = request.form['judul']
        pengarang = request.form['pengarang']
        anggota_id = request.form.get('anggota_id') or None
        category_ids = request.form.getlist('category_id')

        if not judul or not pengarang or not category_ids:
            flash('Judul, Pengarang, dan Kategori tidak boleh kosong!')
            return redirect(url_for('add_book'))

        new_book = Book(judul=judul, pengarang=pengarang, anggota_id=anggota_id)
        session.add(new_book)
        session.commit()

        for category_id in category_ids:
            new_pivot = BookCategory(book_id=new_book.id, category_id=category_id)
            session.add(new_pivot)

        session.commit()

        flash('Buku berhasil ditambahkan!')

        return redirect(url_for('books'))
    
    all_categories = session.query(Category).all()
    return render_template('buku/add_buku.html', categories=all_categories)

@app.route('/edit_book/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    book = session.query(Book).filter(Book.id == id).first()

    if request.method == 'POST':
        book.judul = request.form['judul']
        book.pengarang = request.form['pengarang']
        book.anggota_id = request.form.get('anggota_id') or None
        category_ids = request.form.getlist('category_id')

        if not book.judul or not book.pengarang or not category_ids:
            flash('Judul, Pengarang, Kategori tidak boleh kosong!')
            return redirect(url_for('edit_book', id=id))
        
        session.query(BookCategory).filter(BookCategory.book_id == id).delete()
        session.flush()
        session.commit()

        for category_id in category_ids:
            book_category = BookCategory(book_id=book.id, category_id=category_id)
            session.add(book_category)

        session.commit()
        flash('Buku berhasil diperbarui!')
        return redirect(url_for('books'))
    
    all_categories = session.query(Category).all()
    selected_categories = [bc.category_id for bc in book.categories]

    return render_template('buku/edit_buku.html', book=book, categories=all_categories, selected_categories=selected_categories)

@app.route('/delete_book/<int:id>', methods=['POST'])
def delete_book(id):
    book = session.query(Book).filter(Book.id == id).first()
    if book:
        session.delete(book)
        session.commit()
        flash('Buku berhasil dihapus!')
    else:
        flash('Buku tidak ditemukan!')
    return redirect(url_for('books'))

# Route untuk mengelola kategori (CRUD)
@app.route('/categories')
def categories():
    all_categories = session.query(Category).all()
    return render_template('kategori/view_kategori.html', categories=all_categories)

@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        nama_kategori = request.form['nama']

        if not nama_kategori:
            flash('Nama kategori tidak boleh kosong!')
            return redirect(url_for('categories'))

        new_category = Category(nama=nama_kategori)

        session.add(new_category)
        session.commit()

        flash('Kategori berhasil ditambahkan!')

        return redirect(url_for('categories'))
    
    return render_template('kategori/add_kategori.html')

@app.route('/edit_category/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    category = session.query(Category).filter(Category.id == id).first()

    if request.method == 'POST':
        category.nama = request.form['nama']

        if not category.nama:
            flash('Nama kategori tidak boleh kosong!')
            return redirect(url_for('edit_category', id=id))

        session.commit()
        flash('Kategori berhasil diperbarui!')
        return redirect(url_for('categories'))

    return render_template('kategori/edit_kategori.html', category=category)

@app.route('/delete_category/<int:id>', methods=['POST'])
def delete_category(id):
    category = session.query(Category).filter(Category.id == id).first()
    if category:
        session.delete(category)
        session.commit()
        flash('Kategori berhasil dihapus!')
    else:
        flash('Kategori Tidak Ditemukan!')
    return redirect(url_for('categories'))

# Route Mengelola Pinjaman
@app.route('/borrow_book/<int:id>', methods=['GET', 'POST'])
def borrow_book(id):
    # Ambil buku berdasarkan ID
    book = session.query(Book).filter(Book.id == id).first()

    if request.method == 'POST':
        anggota_id = request.form['anggota_id']  # Ambil ID anggota dari formulir

        # Validasi: Pastikan ada anggota yang dipilih
        if not anggota_id:
            flash('Silakan pilih anggota untuk meminjam buku!')
            return redirect(url_for('borrow_book', id=id))
        
        # Cek apakah buku sudah dipinjam
        if book.anggota_id is not None:
            flash('Buku ini sudah dipinjam oleh anggota lain!')
            return redirect(url_for('/'))

        # Update ID anggota pada buku
        book.anggota_id = anggota_id

        session.commit()  # Simpan perubahan ke database
        flash('Buku berhasil dipinjam!')
        return redirect(url_for('index'))

    # Jika metode GET, ambil semua anggota untuk ditampilkan di formulir
    all_members = session.query(Member).all()
    return render_template('pinjam/add_pinjam.html', book=book, members=all_members)

@app.route('/return_book/<int:id>', methods=['GET','POST'])
def return_book(id):
    # Ambil buku berdasarkan ID
    book = session.query(Book).filter(Book.id == id).first()

    # Set ID anggota menjadi None (mengembalikan buku)
    book.anggota_id = None

    session.commit()  # Simpan perubahan ke database
    flash('Buku berhasil dikembalikan!')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)