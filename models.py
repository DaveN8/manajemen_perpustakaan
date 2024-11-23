from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from database import Database

# Inisialisasi SQLAlchemy
Base = declarative_base()

class Member(Base):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True)
    nama = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)

    # Relasi One-to-Many: Satu anggota dapat meminjam banyak buku
    books = relationship('Book', back_populates='member')

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    judul = Column(String(100), nullable=False)
    pengarang = Column(String(100), nullable=False)
    anggota_id = Column(Integer, ForeignKey('members.id'), nullable=True)

    # Relasi One-to-Many: Buku dipinjam oleh satu anggota
    member = relationship('Member', back_populates='books')

    # Relasi Many-to-Many: Buku memiliki banyak kategori
    categories = relationship('BookCategory', back_populates='book', cascade='all')

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    nama = Column(String(100), nullable=False, unique=True)

    # Relasi Many-to-Many: Kategori memiliki banyak buku
    books = relationship('BookCategory', back_populates='category', cascade='all')

class BookCategory(Base):
    __tablename__ = 'book_categories'

    book_id = Column(Integer, ForeignKey('books.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), primary_key=True)

    # Relasi ke Buku dan Kategori
    book = relationship('Book', back_populates='categories')
    category = relationship('Category', back_populates='books')

# Fungsi untuk membuat koneksi database dan session
def get_session():
    db_connection = Database()
    engine = create_engine('mysql+mysqlconnector://root:@localhost/library_management')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()