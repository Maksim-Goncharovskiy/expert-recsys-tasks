import sqlite3
from faker import Faker
import random
from datetime import datetime, timedelta

# Инициализация Faker с русской локалью
fake = Faker('ru_RU')

def create_database():
    """Создание базы данных и таблиц"""
    conn = sqlite3.connect('lib_db.sqlite3')
    cursor = conn.cursor()
    
    # Создание таблиц
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS authors (
            author_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            country TEXT NOT NULL,
            birth_year INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author_id INTEGER,
            genre TEXT NOT NULL,
            publication_year INTEGER,
            is_available BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (author_id) REFERENCES authors (author_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS borrowers (
            borrower_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT,
            phone TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS borrow_records (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            borrower_id INTEGER,
            borrow_date DATE,
            return_date DATE,
            FOREIGN KEY (book_id) REFERENCES books (book_id),
            FOREIGN KEY (borrower_id) REFERENCES borrowers (borrower_id)
        )
    ''')
    
    return conn, cursor

def generate_authors(cursor, count=15):
    """Генерация авторов"""
    authors_data = []
    for i in range(count):
        author = {
            'full_name': fake.name(),
            'country': fake.country(),
            'birth_year': random.randint(1950, 1990)
        }
        authors_data.append(author)
    
    cursor.executemany(
        'INSERT INTO authors (full_name, country, birth_year) VALUES (?, ?, ?)',
        [(a['full_name'], a['country'], a['birth_year']) for a in authors_data]
    )
    return [i+1 for i in range(count)]  # Возвращаем список author_id

def generate_books(cursor, author_ids, count=50):
    """Генерация книг"""
    genres = ['Фантастика', 'Детектив', 'Роман', 'Научная литература', 
              'Исторический роман', 'Биография', 'Поэзия', 'Учебник', 'Триллер']
    
    books_data = []
    for i in range(count):
        book = {
            'title': fake.catch_phrase().title(),
            'author_id': random.choice(author_ids),
            'genre': random.choice(genres),
            'publication_year': random.randint(1990, 2024),
            'is_available': random.choice([True, False])
        }
        books_data.append(book)
    
    cursor.executemany(
        '''INSERT INTO books (title, author_id, genre, publication_year, is_available) 
           VALUES (?, ?, ?, ?, ?)''',
        [(b['title'], b['author_id'], b['genre'], b['publication_year'], b['is_available']) 
         for b in books_data]
    )
    return [i+1 for i in range(count)]  # Возвращаем список book_ids

def generate_borrowers(cursor, count=30):
    """Генерация читателей"""
    borrowers_data = []
    for i in range(count):
        borrower = {
            'full_name': fake.name(),
            'email': fake.email(),
            'phone': fake.phone_number()
        }
        borrowers_data.append(borrower)
    
    cursor.executemany(
        'INSERT INTO borrowers (full_name, email, phone) VALUES (?, ?, ?)',
        [(b['full_name'], b['email'], b['phone']) for b in borrowers_data]
    )
    return [i+1 for i in range(count)]  # Возвращаем список borrower_ids

def generate_borrow_records(cursor, book_ids, borrower_ids, count=40):
    """Генерация истории выдач"""
    records_data = []
    
    for i in range(count):
        book_id = random.choice(book_ids)
        borrower_id = random.choice(borrower_ids)
        
        # Случайная дата выдачи за последние 2 года
        borrow_date = fake.date_between(start_date='-2y', end_date='today')
        
        # 70% книг возвращены, 30% еще на руках
        is_returned = random.random() > 0.3
        return_date = None
        if is_returned:
            # Книга возвращена через 1-30 дней
            return_date = borrow_date + timedelta(days=random.randint(1, 30))
            # Убедимся, что дата возврата не в будущем
            if return_date > datetime.now().date():
                return_date = datetime.now().date()
        
        records_data.append((book_id, borrower_id, borrow_date, return_date))
    
    cursor.executemany(
        '''INSERT INTO borrow_records (book_id, borrower_id, borrow_date, return_date) 
           VALUES (?, ?, ?, ?)''',
        records_data
    )

def add_specific_books_and_authors(cursor):
    """Добавление конкретных книг и авторов для более реалистичных тестов"""
    
    # Добавляем известных авторов
    famous_authors = [
        ('Фёдор Достоевский', 'Россия', 1821),
        ('Лев Толстой', 'Россия', 1828),
        ('Александр Пушкин', 'Россия', 1799),
        ('Агата Кристи', 'Великобритания', 1890),
        ('Стивен Кинг', 'США', 1947)
    ]
    
    cursor.executemany(
        'INSERT INTO authors (full_name, country, birth_year) VALUES (?, ?, ?)',
        famous_authors
    )
    
    # Получаем ID добавленных авторов
    cursor.execute("SELECT author_id FROM authors WHERE full_name = 'Фёдор Достоевский'")
    dostoevsky_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT author_id FROM authors WHERE full_name = 'Агата Кристи'")
    christie_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT author_id FROM authors WHERE full_name = 'Стивен Кинг'")
    king_id = cursor.fetchone()[0]
    
    # Добавляем известные книги
    famous_books = [
        ('Преступление и наказание', dostoevsky_id, 'Роман', 1866, True),
        ('Убийство в Восточном экспрессе', christie_id, 'Детектив', 1934, True),
        ('Оно', king_id, 'Ужасы', 1986, False),
        ('Анна Каренина', dostoevsky_id + 1, 'Роман', 1877, True),  # Толстой следующий за Достоевским
        ('Евгений Онегин', dostoevsky_id + 2, 'Поэзия', 1833, True)  # Пушкин следующий
    ]
    
    cursor.executemany(
        '''INSERT INTO books (title, author_id, genre, publication_year, is_available) 
           VALUES (?, ?, ?, ?, ?)''',
        famous_books
    )

def main():
    """Основная функция генерации базы данных"""
    print("Создание базы данных библиотеки...")
    
    conn, cursor = create_database()
    
    try:
        # Генерация данных
        print("Генерация авторов...")
        author_ids = generate_authors(cursor)
        
        print("Генерация книг...")
        book_ids = generate_books(cursor, author_ids)
        
        print("Генерация читателей...")
        borrower_ids = generate_borrowers(cursor)
        
        print("Генерация истории выдач...")
        generate_borrow_records(cursor, book_ids, borrower_ids)
        
        print("Добавление известных книг и авторов...")
        add_specific_books_and_authors(cursor)
        
        # Сохранение изменений
        conn.commit()
        
        # Вывод статистики
        cursor.execute("SELECT COUNT(*) FROM authors")
        authors_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM books")
        books_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM borrowers")
        borrowers_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM borrow_records")
        records_count = cursor.fetchone()[0]
        
        print(f"\nБаза данных успешно создана!")
        print(f"Авторов: {authors_count}")
        print(f"Книг: {books_count}")
        print(f"Читателей: {borrowers_count}")
        print(f"Записей о выдаче: {records_count}")
        print(f"Файл базы данных: library.db")
        
        # Покажем несколько примеров для проверки
        print("\nПримеры данных:")
        print("\nНесколько авторов:")
        cursor.execute("SELECT * FROM authors LIMIT 3")
        for row in cursor.fetchall():
            print(f"  {row}")
            
        print("\nНесколько книг:")
        cursor.execute('''SELECT b.title, a.full_name, b.genre 
                          FROM books b 
                          JOIN authors a ON b.author_id = a.author_id 
                          LIMIT 3''')
        for row in cursor.fetchall():
            print(f"  {row}")
            
    except Exception as e:
        print(f"Ошибка: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()