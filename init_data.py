import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_tables():
    """Create all necessary database tables"""
    conn = sqlite3.connect('bookstore.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Books table with genres
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            genre TEXT NOT NULL,
            stock INTEGER DEFAULT 0,
            cover_image TEXT,
            isbn TEXT,
            publisher TEXT,
            pages INTEGER,
            is_featured BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Orders table
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            total_amount REAL,
            status TEXT DEFAULT 'pending',
            payment_method TEXT,
            shipping_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Order items table
    c.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            book_id INTEGER,
            quantity INTEGER,
            price REAL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (book_id) REFERENCES books (id)
        )
    ''')
    
    # Cart table
    c.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            book_id INTEGER,
            quantity INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (book_id) REFERENCES books (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database tables created successfully!")

def reset_auto_increment():
    """Reset SQLite auto-increment counters"""
    conn = sqlite3.connect('bookstore.db')
    c = conn.cursor()
    
    # Reset SQLite sequence for each table
    tables = ['users', 'books', 'orders', 'order_items', 'cart']
    for table in tables:
        try:
            c.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
            print(f"Reset auto-increment for {table} table")
        except Exception as e:
            print(f"Error resetting {table}: {e}")
    
    conn.commit()
    conn.close()

def clear_existing_data():
    """Clear all existing data and reset auto-increment"""
    conn = sqlite3.connect('bookstore.db')
    c = conn.cursor()
    
    # Clear all data from tables (in correct order to respect foreign keys)
    c.execute('DELETE FROM cart')
    c.execute('DELETE FROM order_items')
    c.execute('DELETE FROM orders')
    c.execute('DELETE FROM books')
    c.execute('DELETE FROM users')
    
    conn.commit()
    conn.close()
    print("Cleared all existing data from tables")

def init_sample_data():
    """Initialize sample data for the bookstore"""
    conn = sqlite3.connect('bookstore.db')
    c = conn.cursor()
    
    # Create admin user
    try:
        c.execute('''
            INSERT INTO users (username, email, password_hash, is_admin) 
            VALUES (?, ?, ?, ?)
        ''', ('admin', 'admin@bookstore.com', hash_password('admin123'), True))
        print("[OK] Admin user created: username='admin', password='admin123'")
    except sqlite3.IntegrityError:
        print("Admin user already exists")
    
    # Create regular user
    try:
        c.execute('''
            INSERT INTO users (username, email, password_hash) 
            VALUES (?, ?, ?)
        ''', ('john_doe', 'john@example.com', hash_password('password123')))
        print("[OK] Regular user created: username='john_doe', password='password123'")
    except sqlite3.IntegrityError:
        print("Regular user already exists")
    
    # Sample books data - 10 genres with 10 books each
    sample_books = []
    
    # Fiction Books
    fiction_books = [
        ('The Great Gatsby', 'F. Scott Fitzgerald', 'A classic novel of the Jazz Age', 12.99, 'Fiction', 50, 'great_gatsby.jpg', '9780743273565', 'Scribner', 180, 1),
        ('To Kill a Mockingbird', 'Harper Lee', 'A novel about racial inequality and moral growth', 14.99, 'Fiction', 30, 'mockingbird.jpg', '9780061120084', 'J.B. Lippincott & Co.', 281, 1),
        ('1984', 'George Orwell', 'Dystopian social science fiction novel', 10.99, 'Fiction', 25, '1984.jpg', '9780451524935', 'Secker & Warburg', 328, 0),
        ('Pride and Prejudice', 'Jane Austen', 'Romantic novel of manners', 9.99, 'Fiction', 40, 'pride_prejudice.jpg', '9780141439518', 'T. Egerton', 432, 1),
        ('The Catcher in the Rye', 'J.D. Salinger', 'Coming-of-age story', 11.99, 'Fiction', 20, 'catcher_rye.jpg', '9780316769174', 'Little, Brown and Company', 277, 0),
        ('The Lord of the Rings', 'J.R.R. Tolkien', 'Epic high fantasy novel', 24.99, 'Fiction', 15, 'lotr.jpg', '9780544003415', 'Allen & Unwin', 1178, 1),
        ('The Hobbit', 'J.R.R. Tolkien', 'Fantasy novel and children\'s book', 13.99, 'Fiction', 35, 'hobbit.jpg', '9780547928227', 'Allen & Unwin', 310, 1),
        ('Brave New World', 'Aldous Huxley', 'Dystopian novel', 10.99, 'Fiction', 22, 'brave_new_world.jpg', '9780060850524', 'Chatto & Windus', 288, 0),
        ('The Alchemist', 'Paulo Coelho', 'Philosophical novel', 8.99, 'Fiction', 60, 'alchemist.jpg', '9780061122415', 'HarperCollins', 208, 1),
        ('The Kite Runner', 'Khaled Hosseini', 'Historical fiction novel', 12.99, 'Fiction', 28, 'kite_runner.jpg', '9781594631931', 'Riverhead Books', 371, 1)
    ]
    
    # Mystery Books
    mystery_books = [
        ('The Da Vinci Code', 'Dan Brown', 'Mystery thriller novel', 14.99, 'Mystery', 45, 'davinci_code.jpg', '9780307474278', 'Doubleday', 489, 1),
        ('Gone Girl', 'Gillian Flynn', 'Psychological thriller novel', 13.99, 'Mystery', 32, 'gone_girl.jpg', '9780307588371', 'Crown Publishing Group', 432, 1),
        ('The Girl with the Dragon Tattoo', 'Stieg Larsson', 'Crime novel', 12.99, 'Mystery', 26, 'dragon_tattoo.jpg', '9780307454546', 'Norstedts Förlag', 465, 0),
        ('The Silent Patient', 'Alex Michaelides', 'Psychological thriller', 11.99, 'Mystery', 38, 'silent_patient.jpg', '9781250301697', 'Celadon Books', 336, 1),
        ('Big Little Lies', 'Liane Moriarty', 'Domestic thriller novel', 10.99, 'Mystery', 29, 'big_little_lies.jpg', '9780399587191', 'G.P. Putnam\'s Sons', 460, 0),
        ('The Woman in the Window', 'A.J. Finn', 'Psychological thriller', 12.99, 'Mystery', 24, 'woman_window.jpg', '9780062678416', 'William Morrow', 427, 1),
        ('Sharp Objects', 'Gillian Flynn', 'Mystery novel', 11.99, 'Mystery', 18, 'sharp_objects.jpg', '9780307341556', 'Shaye Areheart Books', 254, 0),
        ('In the Woods', 'Tana French', 'Crime novel', 13.99, 'Mystery', 22, 'in_the_woods.jpg', '9780143113492', 'Hodder & Stoughton', 429, 1),
        ('The No. 1 Ladies\' Detective Agency', 'Alexander McCall Smith', 'Detective novel', 9.99, 'Mystery', 41, 'detective_agency.jpg', '9781400034772', 'Pantheon Books', 235, 0),
        ('The Cuckoo\'s Calling', 'Robert Galbraith', 'Crime fiction novel', 12.99, 'Mystery', 27, 'cuckoos_calling.jpg', '9780316206846', 'Little, Brown and Company', 449, 1)
    ]
    
    # Science Fiction Books
    scifi_books = [
        ('Dune', 'Frank Herbert', 'Epic science fiction novel', 15.99, 'Science Fiction', 33, 'dune.jpg', '9780441172719', 'Chilton Books', 412, 1),
        ('Foundation', 'Isaac Asimov', 'Science fiction novel', 11.99, 'Science Fiction', 28, 'foundation.jpg', '9780553293357', 'Gnome Press', 255, 1),
        ('Neuromancer', 'William Gibson', 'Cyberpunk novel', 10.99, 'Science Fiction', 19, 'neuromancer.jpg', '9780441569595', 'Ace', 271, 0),
        ('The Martian', 'Andy Weir', 'Science fiction novel', 12.99, 'Science Fiction', 37, 'martian.jpg', '9780553418026', 'Crown Publishing Group', 369, 1),
        ('Snow Crash', 'Neal Stephenson', 'Science fiction novel', 11.99, 'Science Fiction', 23, 'snow_crash.jpg', '9780553380958', 'Bantam Spectra', 440, 0),
        ('Ender\'s Game', 'Orson Scott Card', 'Military science fiction novel', 9.99, 'Science Fiction', 31, 'enders_game.jpg', '9780812550702', 'Tor Books', 324, 1),
        ('The Left Hand of Darkness', 'Ursula K. Le Guin', 'Science fiction novel', 10.99, 'Science Fiction', 16, 'left_hand.jpg', '9780441478125', 'Ace Books', 304, 0),
        ('Hyperion', 'Dan Simmons', 'Science fiction novel', 13.99, 'Science Fiction', 21, 'hyperion.jpg', '9780553283686', 'Doubleday', 482, 1),
        ('Ready Player One', 'Ernest Cline', 'Science fiction novel', 11.99, 'Science Fiction', 44, 'ready_player_one.jpg', '9780307887436', 'Crown Publishing Group', 374, 1),
        ('The Three-Body Problem', 'Liu Cixin', 'Science fiction novel', 14.99, 'Science Fiction', 26, 'three_body.jpg', '9780765377067', 'Chongqing Press', 399, 0)
    ]
    
    # Fantasy Books
    fantasy_books = [
        ('Harry Potter and the Sorcerer\'s Stone', 'J.K. Rowling', 'Fantasy novel about a young wizard', 13.99, 'Fantasy', 55, 'harry_potter.jpg', '9780590353427', 'Bloomsbury', 320, 1),
        ('A Game of Thrones', 'George R.R. Martin', 'Epic fantasy novel', 16.99, 'Fantasy', 18, 'game_of_thrones.jpg', '9780553103540', 'Bantam Spectra', 694, 1),
        ('The Name of the Wind', 'Patrick Rothfuss', 'Fantasy novel', 12.99, 'Fantasy', 23, 'name_of_wind.jpg', '9780756404741', 'DAW Books', 662, 1),
        ('The Way of Kings', 'Brandon Sanderson', 'Epic fantasy novel', 15.99, 'Fantasy', 19, 'way_of_kings.jpg', '9780765326355', 'Tor Books', 1007, 1),
        ('Mistborn: The Final Empire', 'Brandon Sanderson', 'Fantasy novel', 11.99, 'Fantasy', 27, 'mistborn.jpg', '9780765311788', 'Tor Books', 541, 0),
        ('The Lightning Thief', 'Rick Riordan', 'Fantasy adventure novel', 9.99, 'Fantasy', 42, 'lightning_thief.jpg', '9780786856299', 'Miramax Books', 377, 1),
        ('American Gods', 'Neil Gaiman', 'Fantasy novel', 12.99, 'Fantasy', 21, 'american_gods.jpg', '9780062059888', 'William Morrow', 465, 0),
        ('The Color of Magic', 'Terry Pratchett', 'Fantasy comedy novel', 10.99, 'Fantasy', 33, 'color_magic.jpg', '9780062225672', 'Colin Smythe', 228, 1),
        ('The Eye of the World', 'Robert Jordan', 'Epic fantasy novel', 14.99, 'Fantasy', 16, 'eye_world.jpg', '9780812511819', 'Tor Books', 814, 1),
        ('Assassin\'s Apprentice', 'Robin Hobb', 'Fantasy novel', 11.99, 'Fantasy', 24, 'assassin_apprentice.jpg', '9780553573394', 'Bantam Spectra', 448, 0)
    ]
    
    # Romance Books
    romance_books = [
        ('The Notebook', 'Nicholas Sparks', 'Romantic novel', 8.99, 'Romance', 65, 'notebook.jpg', '9780553816719', 'Warner Books', 214, 1),
        ('Pride and Prejudice', 'Jane Austen', 'Romantic novel of manners', 9.99, 'Romance', 48, 'pride_romance.jpg', '9780141439518', 'T. Egerton', 432, 1),
        ('Outlander', 'Diana Gabaldon', 'Historical romance novel', 13.99, 'Romance', 22, 'outlander.jpg', '9780440212560', 'Delacorte Press', 850, 1),
        ('The Bride', 'Julie Garwood', 'Historical romance novel', 7.99, 'Romance', 38, 'the_bride.jpg', '9780671744219', 'Pocket Books', 384, 0),
        ('The Wedding', 'Nicholas Sparks', 'Romantic novel', 8.99, 'Romance', 41, 'the_wedding.jpg', '9780446615863', 'Warner Books', 276, 1),
        ('It Ends With Us', 'Colleen Hoover', 'Contemporary romance novel', 10.99, 'Romance', 35, 'it_ends_us.jpg', '9781501110368', 'Atria Books', 384, 1),
        ('The Hating Game', 'Sally Thorne', 'Romantic comedy novel', 9.99, 'Romance', 29, 'hating_game.jpg', '9780062439598', 'William Morrow', 384, 0),
        ('The Spanish Love Deception', 'Elena Armas', 'Romantic comedy novel', 11.99, 'Romance', 26, 'spanish_love.jpg', '9781662500229', 'Atria Books', 496, 1),
        ('Beach Read', 'Emily Henry', 'Contemporary romance novel', 10.99, 'Romance', 31, 'beach_read.jpg', '9781984806734', 'Berkley', 361, 1),
        ('The Love Hypothesis', 'Ali Hazelwood', 'Romantic comedy novel', 9.99, 'Romance', 34, 'love_hypothesis.jpg', '9780593336823', 'Berkley', 384, 0)
    ]
    
    # Thriller Books
    thriller_books = [
        ('The Girl on the Train', 'Paula Hawkins', 'Psychological thriller novel', 11.99, 'Thriller', 37, 'girl_train.jpg', '9781594633669', 'Riverhead Books', 336, 1),
        ('The Silent Patient', 'Alex Michaelides', 'Psychological thriller', 11.99, 'Thriller', 38, 'silent_thriller.jpg', '9781250301697', 'Celadon Books', 336, 1),
        ('The Reversal', 'Michael Connelly', 'Legal thriller novel', 10.99, 'Thriller', 24, 'the_reversal.jpg', '9780316069489', 'Little, Brown', 448, 0),
        ('The Couple Next Door', 'Shari Lapena', 'Psychological thriller', 9.99, 'Thriller', 42, 'couple_next.jpg', '9780735221086', 'Pamela Dorman Books', 308, 1),
        ('Behind Closed Doors', 'B.A. Paris', 'Psychological thriller', 8.99, 'Thriller', 33, 'behind_doors.jpg', '9781250121004', 'St. Martin\'s Press', 304, 0),
        ('The Wife Between Us', 'Greer Hendricks', 'Psychological thriller', 10.99, 'Thriller', 27, 'wife_between.jpg', '9781250130921', 'St. Martin\'s Press', 346, 1),
        ('Then She Was Gone', 'Lisa Jewell', 'Psychological thriller', 9.99, 'Thriller', 31, 'then_she.jpg', '9781501154645', 'Atria Books', 359, 1),
        ('The Nightingale', 'Kristin Hannah', 'Historical thriller', 12.99, 'Thriller', 19, 'nightingale.jpg', '9780312577223', 'St. Martin\'s Press', 440, 1),
        ('The Guest List', 'Lucy Foley', 'Mystery thriller', 10.99, 'Thriller', 28, 'guest_list.jpg', '9780062868930', 'William Morrow', 320, 0),
        ('One by One', 'Ruth Ware', 'Mystery thriller', 11.99, 'Thriller', 25, 'one_by_one.jpg', '9781982150461', 'Gallery/Scout Press', 384, 1)
    ]
    
    # Biography Books
    biography_books = [
        ('Steve Jobs', 'Walter Isaacson', 'Biography of Apple co-founder', 15.99, 'Biography', 28, 'steve_jobs.jpg', '9781451648539', 'Simon & Schuster', 656, 1),
        ('Becoming', 'Michelle Obama', 'Memoir by former First Lady', 18.99, 'Biography', 35, 'becoming.jpg', '9781524763138', 'Crown Publishing', 448, 1),
        ('Educated', 'Tara Westover', 'Memoir about self-education', 14.99, 'Biography', 26, 'educated.jpg', '9780399590504', 'Random House', 334, 1),
        ('The Diary of a Young Girl', 'Anne Frank', 'Autobiographical book', 8.99, 'Biography', 52, 'anne_frank.jpg', '9780553296983', 'Contact Publishing', 283, 0),
        ('Elon Musk', 'Ashlee Vance', 'Biography of Elon Musk', 16.99, 'Biography', 21, 'elon_musk.jpg', '9780062301239', 'Ecco', 400, 1),
        ('I Know Why the Caged Bird Sings', 'Maya Angelou', 'Autobiography', 10.99, 'Biography', 33, 'caged_bird.jpg', '9780345514400', 'Random House', 289, 1),
        ('The Wright Brothers', 'David McCullough', 'Biography of aviation pioneers', 13.99, 'Biography', 18, 'wright_brothers.jpg', '9781476728742', 'Simon & Schuster', 320, 0),
        ('Alexander Hamilton', 'Ron Chernow', 'Biography of Alexander Hamilton', 17.99, 'Biography', 16, 'alexander_hamilton.jpg', '9781594200090', 'Penguin Press', 818, 1),
        ('The Story of My Life', 'Helen Keller', 'Autobiography', 7.99, 'Biography', 44, 'helen_keller.jpg', '9780451529732', 'Doubleday', 240, 1),
        ('Long Walk to Freedom', 'Nelson Mandela', 'Autobiography', 12.99, 'Biography', 22, 'mandela.jpg', '9780316548182', 'Little, Brown', 656, 0)
    ]
    
    # History Books
    history_books = [
        ('Sapiens: A Brief History of Humankind', 'Yuval Noah Harari', 'History of human evolution', 16.99, 'History', 32, 'sapiens.jpg', '9780062316097', 'Harper', 443, 1),
        ('Guns, Germs, and Steel', 'Jared Diamond', 'History of human societies', 15.99, 'History', 24, 'guns_germs.jpg', '9780393317558', 'W. W. Norton', 480, 1),
        ('A People\'s History of the United States', 'Howard Zinn', 'History of the United States', 18.99, 'History', 19, 'peoples_history.jpg', '9780060838652', 'Harper & Row', 729, 0),
        ('The Silk Roads', 'Peter Frankopan', 'History of the world', 17.99, 'History', 21, 'silk_roads.jpg', '9781101912379', 'Bloomsbury', 636, 1),
        ('The Rise and Fall of the Third Reich', 'William L. Shirer', 'History of Nazi Germany', 22.99, 'History', 14, 'third_reich.jpg', '9781451651683', 'Simon & Schuster', 1248, 1),
        ('1776', 'David McCullough', 'History of American Revolution', 14.99, 'History', 27, '1776.jpg', '9780743226714', 'Simon & Schuster', 386, 0),
        ('The Crusades', 'Thomas Asbridge', 'History of the Crusades', 13.99, 'History', 18, 'crusades.jpg', '9780060787288', 'HarperCollins', 784, 1),
        ('SPQR: A History of Ancient Rome', 'Mary Beard', 'History of Ancient Rome', 16.99, 'History', 23, 'spqr.jpg', '9780871404237', 'Liveright', 606, 1),
        ('The Second World War', 'Antony Beevor', 'History of World War II', 19.99, 'History', 16, 'ww2.jpg', '9780316023740', 'Little, Brown', 863, 0),
        ('A Short History of Nearly Everything', 'Bill Bryson', 'History of science', 15.99, 'History', 29, 'short_history.jpg', '9780767908184', 'Broadway Books', 544, 1)
    ]
    
    # Science Books
    science_books = [
        ('A Brief History of Time', 'Stephen Hawking', 'Popular science book', 12.99, 'Science', 36, 'brief_history.jpg', '9780553380163', 'Bantam Books', 212, 1),
        ('The Selfish Gene', 'Richard Dawkins', 'Evolutionary biology book', 11.99, 'Science', 28, 'selfish_gene.jpg', '9780192860927', 'Oxford University Press', 224, 1),
        ('Cosmos', 'Carl Sagan', 'Popular science book', 13.99, 'Science', 31, 'cosmos.jpg', '9780345331359', 'Random House', 365, 0),
        ('The Gene: An Intimate History', 'Siddhartha Mukherjee', 'History of genetics', 16.99, 'Science', 22, 'the_gene.jpg', '9781476733500', 'Scribner', 592, 1),
        ('The Emperor of All Maladies', 'Siddhartha Mukherjee', 'Biography of cancer', 15.99, 'Science', 19, 'emperor_maladies.jpg', '9781439107959', 'Scribner', 571, 1),
        ('The Double Helix', 'James D. Watson', 'Discovery of DNA structure', 10.99, 'Science', 25, 'double_helix.jpg', '9780743216302', 'Atheneum', 226, 0),
        ('The Elegant Universe', 'Brian Greene', 'String theory explained', 14.99, 'Science', 20, 'elegant_universe.jpg', '9780375708114', 'W. W. Norton', 448, 1),
        ('The Man Who Knew Infinity', 'Robert Kanigel', 'Biography of Ramanujan', 12.99, 'Science', 23, 'infinity.jpg', '9780671750619', 'Scribner', 438, 1),
        ('The Immortal Life of Henrietta Lacks', 'Rebecca Skloot', 'Medical history', 13.99, 'Science', 27, 'henrietta_lacks.jpg', '9781400052189', 'Crown Publishing', 381, 0),
        ('The Sixth Extinction', 'Elizabeth Kolbert', 'Environmental science', 11.99, 'Science', 24, 'sixth_extinction.jpg', '9780805092998', 'Henry Holt', 319, 1)
    ]
    
    # Children Books
    children_books = [
        ('The Very Hungry Caterpillar', 'Eric Carle', 'Children\'s picture book', 6.99, 'Children', 75, 'hungry_caterpillar.jpg', '9780399226908', 'World Publishing Company', 26, 1),
        ('Where the Wild Things Are', 'Maurice Sendak', 'Children\'s picture book', 7.99, 'Children', 62, 'wild_things.jpg', '9780060254926', 'Harper & Row', 48, 1),
        ('Goodnight Moon', 'Margaret Wise Brown', 'Children\'s book', 5.99, 'Children', 88, 'goodnight_moon.jpg', '9780060775858', 'Harper & Brothers', 32, 0),
        ('Charlotte\'s Web', 'E.B. White', 'Children\'s novel', 8.99, 'Children', 45, 'charlottes_web.jpg', '9780061124952', 'Harper & Brothers', 192, 1),
        ('The Cat in the Hat', 'Dr. Seuss', 'Children\'s book', 6.99, 'Children', 67, 'cat_hat.jpg', '9780394800011', 'Random House', 61, 1),
        ('Harry Potter and the Philosopher\'s Stone', 'J.K. Rowling', 'Children\'s fantasy novel', 12.99, 'Children', 38, 'harry_children.jpg', '9780747532743', 'Bloomsbury', 223, 1),
        ('The Lion, the Witch and the Wardrobe', 'C.S. Lewis', 'Children\'s fantasy novel', 9.99, 'Children', 41, 'lion_witch.jpg', '9780060234812', 'Geoffrey Bles', 172, 0),
        ('Matilda', 'Roald Dahl', 'Children\'s novel', 8.99, 'Children', 52, 'matilda.jpg', '9780141301068', 'Jonathan Cape', 240, 1),
        ('The Tale of Peter Rabbit', 'Beatrix Potter', 'Children\'s book', 4.99, 'Children', 95, 'peter_rabbit.jpg', '9780723247708', 'Frederick Warne & Co.', 56, 1),
        ('Green Eggs and Ham', 'Dr. Seuss', 'Children\'s book', 6.99, 'Children', 73, 'green_eggs.jpg', '9780394800165', 'Random House', 62, 0)
    ]
    
    # Combine all books
    sample_books.extend(fiction_books)
    sample_books.extend(mystery_books)
    sample_books.extend(scifi_books)
    sample_books.extend(fantasy_books)
    sample_books.extend(romance_books)
    sample_books.extend(thriller_books)
    sample_books.extend(biography_books)
    sample_books.extend(history_books)
    sample_books.extend(science_books)
    sample_books.extend(children_books)
    
    # Insert sample books
    try:
        c.executemany('''
            INSERT INTO books 
            (title, author, description, price, genre, stock, cover_image, isbn, publisher, pages, is_featured)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_books)
        
        book_count = c.execute('SELECT COUNT(*) FROM books').fetchone()[0]
        print(f"[OK] Successfully added {book_count} books to the database")
        
    except Exception as e:
        print(f"[ERROR] Error inserting books: {e}")
    
    conn.commit()
    conn.close()
    print("[OK] Sample data initialization completed!")

def verify_data():
    """Verify that data was inserted correctly with proper IDs"""
    conn = sqlite3.connect('bookstore.db')
    c = conn.cursor()
    
    print("\n" + "="*50)
    print("DATA VERIFICATION")
    print("="*50)
    
    # Check users
    users = c.execute('SELECT id, username, is_admin FROM users ORDER BY id').fetchall()
    print(f"\nUSERS (Total: {len(users)}):")
    for user in users:
        role = "Admin" if user[2] else "User"
        print(f"  ID: {user[0]}, Username: {user[1]}, Role: {role}")
    
    # Check books count by genre
    genres = c.execute('SELECT genre, COUNT(*) FROM books GROUP BY genre ORDER BY genre').fetchall()
    total_books = sum(g[1] for g in genres)
    print(f"\nBOOKS BY GENRE (Total: {total_books}):")
    for genre, count in genres:
        print(f"  {genre}: {count} books")
    
    # Check first few books to verify IDs
    books_sample = c.execute('SELECT id, title, genre FROM books ORDER BY id LIMIT 5').fetchall()
    print(f"\nSAMPLE BOOKS (First 5):")
    for book in books_sample:
        print(f"  ID: {book[0]}, Title: {book[1][:30]}..., Genre: {book[2]}")
    
    conn.close()

if __name__ == '__main__':
    print("STARTING DATABASE INITIALIZATION...")
    print("="*50)
    
    # Step 1: Create tables
    create_tables()
    
    # Step 2: Clear existing data and reset auto-increment
    clear_existing_data()
    reset_auto_increment()
    
    # Step 3: Initialize sample data
    init_sample_data()
    
    # Step 4: Verify data
    verify_data()
    
    print("\n" + "="*50)
    print("BOOKSTORE SETUP COMPLETE!")
    print("="*50)
    print("\nLOGIN CREDENTIALS:")
    print("  Admin Panel: http://localhost:5000/admin/login")
    print("  Username: admin")
    print("  Password: admin123")
    print("\n  Regular User:")
    print("  Username: john_doe")
    print("  Password: password123")
    print("\n  Main Store: http://localhost:5000")
    print("="*50)
    print("\nNOTE: User IDs and Order IDs will now start from 1 every time!")
    print("="*50)