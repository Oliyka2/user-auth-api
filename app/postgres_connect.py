import psycopg
from psycopg.rows import dict_row, DictRow       
from dotenv import load_dotenv
from os import getenv
from typing import Any

from app.person import Person
from app.password_handler import PasswordFernet

class DBConnect:
    def __init__(self):
        load_dotenv(dotenv_path='/Users/Daniil/Desktop/Project/.env')
        self.db_name = getenv("DBNAME")
        self.db_user = getenv("USER")
        self.db_password = getenv("PASSWORD")
        self.db_host = getenv("HOST")
        self.db_port = getenv("PORT")
        self.connection: psycopg.Connection[DictRow] | None = None
        

    def connect(self) -> None:
        """Establish a connection to the PostgreSQL database."""

        connect_string = f"dbname={self.db_name} user={self.db_user}\
            password={self.db_password} host={self.db_host} port={self.db_port}"
        
        self.connection = psycopg.connect(connect_string, row_factory=dict_row) # type: ignore
        print("Connection to the database was successful.")
    
    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.commit()
            self.connection.close()
            print("Database connection closed.")

class TestDBConnection(DBConnect):

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
                        {person.birth_date}, {person.email}, {person.password}, {person.key})")
        self.connection.commit()
    
    
    def get_data(self, number: int = 100, descending: bool = False) -> list[dict[str, Any]]:
        """Retrieve a specified number of records from the database.

        Keyword Arguments:
            number -- The number of records to retrieve (default 100).
            descending -- Whether to retrieve records in reverse order (default False).

        Raises:
            ValueError: If no database connection is established.

        Returns:
            A list of dictionaries with column names as keys.
        """        
        if self.connection is None:
            raise ValueError("No database connection. Call connect() first.")
        
        if descending == False:
            with self.connection.cursor() as cur:
                cur.execute(t"SELECT * FROM test ORDER BY id ASC LIMIT {number}")
                rows: list[dict] = cur.fetchall() 
                return rows
        else:
            with self.connection.cursor() as cur:
                cur.execute(t"SELECT * FROM test ORDER BY id DESC LIMIT {number}")
                rows: list[dict] = cur.fetchall() 
                return rows
            
    
        
    def get_single_data(self, email: str) -> dict[str, Any] | None:
        """Retrieve a single record from the database by email.

        Arguments:
            email -- The email address of the person to retrieve.

        Raises:
            ValueError: If no database connection is established.

        Returns:
            A dictionary representing the record, or None if not found.
        """        
        
        if self.connection is None:
            raise ValueError("No database connection. Call connect() first.")
        
        with self.connection.cursor() as cur:
            cur.execute(t"SELECT * FROM test WHERE email = {email}")
            row: dict[str, Any] | None = cur.fetchone() 
            if row is None:
                print("No user with this email found.")
                return None
            return row
        
    

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
            if row is None:
                print("No user with this email found.")
                return None
            
            password = row['password']
            key = row['key']
            return PasswordFernet().decrypt_password(password, key)
        
    

class TestBcryptDBConnection(DBConnect):
    
    def create_table_bcrypt(self) -> None:
        """Create the test_bcrypt table in the database if it does not exist.

        Raises:
            ValueError: If no database connection is established.
        """        
        if self.connection is None:
            raise ValueError("No database connection. Call connect() first.")
        
        with self.connection.cursor() as cur:
            cur.execute(
            """
            CREATE TABLE IF NOT EXISTS test_bcrypt (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                gender VARCHAR(30) NOT NULL,
                age INT NOT NULL,
                birth_date DATE NOT NULL,
                email VARCHAR(200) UNIQUE NOT NULL,
                hash_password TEXT NOT NULL
            )""")
            cur.close()
            
    def insert_data_bcrypt(self, person_data: dict[str, Any]) -> None:
        """Insert a new record into the test_bcrypt table.

        Arguments:
            person_data -- A dictionary containing person data to insert.

        Raises:
            ValueError: If no database connection is established.
        """        
        if self.connection is None:
            raise ValueError("No database connection. Call connect() first.")
        
        with self.connection.cursor() as cur:
            cur.execute(t"INSERT INTO test_bcrypt  \
                        (first_name, last_name, gender, age, \
                        birth_date, email, hash_password) \
                        VALUES \
                        ({person_data['first_name']}, {person_data['last_name']}, {person_data['gender']}, {person_data['age']}, \
                        {person_data['birth_date']}, {person_data['email']}, {person_data['hash_password']})")
        self.connection.commit()
    
    def get_data_bcrypt(self, number: int = 100, descending: bool = False) -> list[dict[str, Any]]:
        """Retrieve a specified number of records from the test_bcrypt table.

        Keyword Arguments:
            number -- The number of records to retrieve 
            descending -- Whether to sort the records in descending order 

        Raises:
            ValueError: If no database connection is established.

        Returns:
            A list of dictionaries representing the retrieved records.
        """        
        if self.connection is None:
            raise ValueError("No database connection. Call connect() first.")
        
        if descending == False:
            with self.connection.cursor() as cur:
                cur.execute(t"SELECT * FROM test_bcrypt ORDER BY id ASC LIMIT {number}")
                rows: list[dict] = cur.fetchall() 
                return rows
        else:
            with self.connection.cursor() as cur:
                cur.execute(t"SELECT * FROM test_bcrypt ORDER BY id DESC LIMIT {number}")
                rows: list[dict] = cur.fetchall() 
                return rows
            
    def get_single_data_bcrypt(self, email: str) -> dict[str, Any] | None:
        """Retrieve a single record from the test_bcrypt table by email.

        Arguments:
            email -- The email of the person to retrieve.

        Raises:
            ValueError: If no database connection is established.

        Returns:
            A dictionary representing the retrieved record, or None if not found.
        """        
        if self.connection is None:
            raise ValueError("No database connection. Call connect() first.")
        
        with self.connection.cursor() as cur:
            cur.execute(t"SELECT * FROM test_bcrypt WHERE email = {email}")
            row: dict[str, Any] | None = cur.fetchone() 
            if row is None:
                print("No user with this email found.")
                return None
            return row
        
    def get_hashed_password(self, email: str) -> str | None:
        """Retrieve the hashed password for a given email from the test_bcrypt table.

        Arguments:
            email -- The email of the person whose hashed password to retrieve.

        Raises:
            ValueError: If no database connection is established.

        Returns:
            The hashed password as a string, or None if not found.
        """        
        if self.connection is None:
            raise ValueError("No database connection. Call connect() first.")
        
        with self.connection.cursor() as cur:
            cur.execute(t"SELECT hash_password FROM test_bcrypt WHERE email = {email}")
            row: dict[str, Any] | None = cur.fetchone() 
            if row is None:
                return None
            return row['hash_password']