from datetime import date


class Person:
    """A class to represent a person with personal details """

    def __init__(self,
                first_name: str='John', last_name: str='Doe',
                gender: str='Not specified', age: int=36,
                email : str | None = None):
        self.first_name : str = first_name
        self.last_name : str = last_name
        self.gender : str = gender
        self.age : int = age
        self.user_dates : date = date(1990, 1, 1)
        self.email : str | None = email


    def identity(self):
        """Gather personal information and calculate age"""
        self.personal_info()
        self.how_old()


    def personal_info(self):
        """Get user input for personal details"""

        self.first_name : str = input("Enter your first name: ")
        self.last_name : str = input("Enter your last name: ")
        self.gender : str = input("Enter your gender: ")
        self.email : str = input("Enter your email (optional): ")

        if self.first_name == '' or self.last_name == '':
            print("First name or last name cannot be empty. Using default values.")
            self.first_name = 'John'
            self.last_name = 'Doe'

        if self.gender == '' :
            print('Gender is empty. Set to Not specified')
            self.gender = 'Not specified'

        if self.email == '':
            self.email = None
    

    def how_old(self):
        """Calculate age based on user input date of birth"""

        now : date = date.today()

        try:
            birth_year : int = int(input("Enter your birth year (YYYY): "))
            birth_month : int = int(input("Enter your birth month (MM): "))
            birth_day : int = int(input("Enter your birth day (DD): "))
        except ValueError:
            print("Invalid input. Using default date of birth: 1990-01-01")
            birth_year, birth_month, birth_day = 1990, 1, 1

        self.user_dates : date = date(birth_year, birth_month, birth_day)
        self.age = (now - self.user_dates).days // 365
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.gender}, {self.age} years old, born on {self.user_dates}, email: {self.email}"



person = Person()
person.identity()
print(person)
