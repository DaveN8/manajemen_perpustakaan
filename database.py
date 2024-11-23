import mysql.connector
from mysql.connector import Error


class Database:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
        )
        self.cursor = self.connection.cursor()

        self.create_database()

        self.connection.database = "library_management"

        self.create_tables()

    def create_database(self):
        """Create a new database"""
        try:
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS library_management")
            print("Database created successfully")
        except mysql.connector.Error as err:
            print(f"Error creating database: {err}")

    def create_tables(self):
        """Create tables in the database"""
        try:
            # Tabel Anggota
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS members (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nama VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE
                )
            """
            )

            # Tabel Kategori
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS categories (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nama VARCHAR(100) NOT NULL UNIQUE
                )
            """
            )

            # Tabel Buku
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS books (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    judul VARCHAR(100) NOT NULL,
                    pengarang VARCHAR(100) NOT NULL,
                    anggota_id INT,
                    FOREIGN KEY (anggota_id) REFERENCES members (id) ON DELETE SET NULL
                )
            """
            )

            # Tabel Pivot Buku-Kategori
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS book_categories (
                    book_id INT,
                    category_id INT,
                    PRIMARY KEY (book_id, category_id), 
                    FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE,
                    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
                )
            """
            )

            print("Tables created successfully")
        except mysql.connector.Error as err:
            print(f"Error creating tables: {err}")

    def close_connection(self):
        """Close the database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Database connection closed.")
