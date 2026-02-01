from datetime import date
from password_handler import PasswordManager


class Person:
    """A class to represent a person with personal details.

    Attributes:
        first_name: The first name of the person.
        last_name: The last name of the person.
        gender: The gender of the person.
        age: The age of the person.
        person_dates: The birth date of the person.
        email: The email address of the person.
        password: The password of the person.
        key: The key associated with the person.
    """

    def __init__(
        self,
        first_name: str = 'John',
        last_name: str = 'Doe',
        gender: str = 'Not specified',
        age: int = 36,
        person_dates: date = date(1990, 1, 1),
        email: str = '',
        password: str = ''
    ) -> None:
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.gender: str = gender
        self.age: int = age
        self.person_dates: date = person_dates
        self.email: str = email
        self.password: str = password
        self.key: bytes = PasswordManager().create_key()


    def identity(self) -> None:
        """Gather personal information and calculate age."""
        self.personal_info()
        self.how_old()


    def personal_info(self) -> None:
        """Get user input for personal details."""
        self.first_name = input("Enter your first name: ")
        self.last_name = input("Enter your last name: ")
        self.gender = input("Enter your gender: ")
        self.email = input("Enter your email: ")
        try:
            password_input = input("Enter your password: ")
            self.password = PasswordManager().encrypt_password(
                password_input,
                my_key=self.key
            )
        except ValueError as ve :
            raise ve

        if self.first_name == '' or self.last_name == '':
            print("First name or last name cannot be empty. Using default values.")
            self.first_name = 'John'
            self.last_name = 'Doe'

        if self.gender == '':
            print('Gender is empty. Set to Not specified')
            self.gender = 'Not specified'

    def how_old(self) -> None:
        """Calculate age based on user input date of birth."""
        now = date.today()

        try:
            birth_year = int(input("Enter your birth year (YYYY): "))
            birth_month = int(input("Enter your birth month (MM): "))
            birth_day = int(input("Enter your birth day (DD): "))
        except ValueError:
            print("Invalid input. Using default date of birth: 1990-01-01")
            birth_year, birth_month, birth_day = 1990, 1, 1

        self.person_dates = date(birth_year, birth_month, birth_day)
        self.age = (now - self.person_dates).days // 365

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}, {self.gender}, {self.age} years old, born on {self.person_dates}, email: {self.email}"

    def __repr__(self) -> str:
        return f"Person(first_name='{self.first_name}', last_name='{self.last_name}', gender='{self.gender}', age={self.age}, person_dates={repr(self.person_dates)}, email={repr(self.email)})"



