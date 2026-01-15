import psycopg

DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_PORT = "5429"

connection = psycopg.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS stocks (
        id SERIAL PRIMARY KEY,
        ticker VARCHAR(255) NOT NULL,
        price DECIMAL(10, 2) NOT NULL
    );
""")

cursor.execute("""
    INSERT INTO stocks (ticker, price) VALUES
    ('a', 2.00),
    ('b', 6.00),
    ('c', 3.50),
    ('d', 4.75),
    ('e', 5.25);
""")

connection.commit()

cursor.close()
connection.close()


