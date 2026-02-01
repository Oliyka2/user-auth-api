import psycopg       
from dotenv import load_dotenv
from os import getenv

from person import Person
from password_handler import PasswordManager

class TestDBConnection:

    def __init__(self):
        load_dotenv()
        self.db_name = getenv("DBNAME")
        self.db_user = getenv("USER")
        self.db_password = getenv("PASSWORD")
        self.db_host = getenv("HOST")
        self.db_port = getenv("PORT")
        self.connection: psycopg.Connection | None = None


    def connect(self) -> None:
        """Establish a connection to the PostgreSQL database."""

        connect_string = f"dbname={self.db_name} user={self.db_user}\
            password={self.db_password} host={self.db_host} port={self.db_port}"
        
        self.connection = psycopg.connect(connect_string)
        print("Connection to the database was successful.")


    def create_table(self) -> None:
        """Create the test table in the database if it does not exist.
        
        Raises:
            ValueError: If no database connection is established.
        """
        if self.connection is None:
            raise ValueError("No database connection. Call connect() first.")
        
        with self.connection.cursor() as cur:
            cur.execute(
            """
            CREATE TABLE IF NOT EXISTS test (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                gender VARCHAR(30) NOT NULL,
                age INT NOT NULL,
                birth_date DATE NOT NULL,
                email VARCHAR(200) UNIQUE NOT NULL,
                password TEXT NOT NULL,
                key BYTEA NOT NULL
            )""")
            cur.close()

    def insert_data(self) -> None:
        """Insert a new person's data into the test table.

        Raises:
            ValueError: If no database connection is established.
        """
        if self.connection is None:
            raise ValueError("No database connection. Call connect() first.")
        
        person = Person()
        person.identity()
        
        with self.connection.cursor() as cur:
            cur.execute(t"INSERT INTO test  \
                        (first_name, last_name, gender, age, \
                        birth_date, email, password, key) \
                        VALUES \
                        ({person.first_name}, {person.last_name}, {person.gender}, {person.age}, \
                        {person.person_dates}, {person.email}, {person.password}, {person.key})")
        self.connection.commit()

    def get_password(self) -> str | None:
        """Retrieve and decrypt a password for a given email.

        Raises:
            ValueError: If no database connection is established.

        Returns:
            The decrypted password as a string, or None if no user found.
        """
        if self.connection is None:
            raise ValueError("No database connection. Call connect() first.")
        
        mail = input("Enter email to retrieve password: ")

        with self.connection.cursor() as cur:
            cur.execute("""
                SELECT password, key FROM test WHERE email = %(mail)s
                """, {'mail': mail})
            
            row = cur.fetchone()
            if row == None:
                print("No user with this email found.")
                return None
            
            password = row[0]
            key = row[1]
            return PasswordManager().decrypt_password(password, key)
        
    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.commit()
            self.connection.close()
            print("Database connection closed.")

db = TestDBConnection()
db.connect()
# db.create_table()
# db.insert_data()
db.close()
