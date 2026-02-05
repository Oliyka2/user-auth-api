from datetime import date
from pydantic import BaseModel, Field, field_validator
from password_handler import PasswordFernet, PasswordBcrypt


class PersonCreate(BaseModel):
    """Schema for creating a new person via API."""
    first_name: str = Field(..., min_length=1, description="The first name of the person.")
    last_name: str = Field(..., min_length=1, description="The last name of the person.")
    gender: str = Field(default='Not specified', description="The gender of the person.")
    birth_date: date = Field(..., description="The birth date of the person.")
    email: str = Field(..., description="The email address of the person.")
    password: str = Field(..., min_length=2, description="The password of the person.")
    
    @staticmethod
    def calculate_age(birth_date: date) -> int:
        """Calculate age based on birth date."""
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    
    @staticmethod
    def key() -> bytes:
        """Generate a new encryption key."""
        return PasswordFernet().create_key()
    
    @staticmethod
    def password_encryption(password: str, my_key: bytes) -> str:
        """Encrypt the password using the provided key."""
        return PasswordFernet().encrypt_password(password, my_key=my_key)
    
    @staticmethod
    def password_decryption(encrypted_password: str, my_key: bytes) -> str:
        """Decrypt the password using the provided key."""
        return PasswordFernet().strict_decrypt_password(encrypted_password, my_key=my_key)
    
    @staticmethod
    def password_bcrypt_hash(password: str) -> str:
        """Hash the password using bcrypt."""
        return PasswordBcrypt.hash_password(password)

    @staticmethod
    def password_bcrypt_check(password: str, hashed_password: str) -> bool:
        """Check the password against the bcrypt hash."""
        return PasswordBcrypt.check_password(password, hashed_password)
    

class PersonResponse(BaseModel):
    """Schema for person data returned from API."""
    id: int = Field(..., description="The unique identifier of the person.")
    first_name: str = Field(..., description="The first name of the person.")
    last_name: str = Field(..., description="The last name of the person.")
    gender: str = Field(..., description="The gender of the person.")
    age: int = Field(..., description="The age of the person.")
    birth_date: date = Field(..., description="The birth date of the person.")
    email: str = Field(..., description="The email address of the person.")
    
class FullPersonResponse(PersonResponse):
    """Schema for full person data including password and key."""
    password: str = Field(..., description="The password of the person.")
    key: bytes = Field(..., description="The key associated with the person.")
    
class PersonBcrypt(PersonResponse):
    """Schema for person data with bcrypt hashed password."""
    hash_password: str = Field(..., description="The bcrypt hashed password of the person.")


class PersonUpdate(BaseModel):
    first_name: str | None = Field(default=None, description="The first name of the person.", examples=[None])
    last_name: str | None = Field(default=None, description="The last name of the person.", examples=[None])
    gender: str | None = Field(default=None, description="The gender of the person.", examples=[None])
    birth_date: date | None = Field(default=None, description="The birth date of the person.", examples=[None])
    password: str | None = Field(default=None, description="The password of the person.", examples=[None])


class Person():
    """A class to represent a person with personal details.

    Attributes:
        first_name: The first name of the person.
        last_name: The last name of the person.
        gender: The gender of the person.
        age: The age of the person.
        birth_date: The birth date of the person.
        email: The email address of the person.
        password: The password of the person.
        key: The key associated with the person.
    """

    def identity(self) -> None:
        """Gather personal information and calculate age."""
        self.key = PasswordFernet().create_key()
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
            self.password = PasswordFernet().encrypt_password(
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

        self.birth_date = date(birth_year, birth_month, birth_day)
        self.age = (now - self.birth_date).days // 365
        
    

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}, {self.gender}, {self.age} years old, born on {self.birth_date}, email: {self.email}"

    def __repr__(self) -> str:
        return f"Person(first_name='{self.first_name}', last_name='{self.last_name}', gender='{self.gender}', age={self.age}, birth_date={repr(self.birth_date)}, email={repr(self.email)})"



