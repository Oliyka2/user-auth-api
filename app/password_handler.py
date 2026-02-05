from cryptography.fernet import Fernet
import bcrypt


class PasswordBcrypt:
    
    @staticmethod
    def hash_password(plain_password: str) -> str:
        """Hash a plaintext password using bcrypt.

        Arguments:
            plain_password -- The plaintext password to hash.

        Returns:
            The hashed password as a string.
        """        
        return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
    @staticmethod
    def check_password(plain_password: str, hashed_password: str) -> bool:
        """Check if a plaintext password matches a hashed password using bcrypt.

        Arguments:
            plain_password -- The plaintext password to check.
            hashed_password -- The hashed password to compare against.
        Returns:
            True if the passwords match, False otherwise.
        """        
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


class PasswordFernet:
    """Class to manage password encryption and decryption using Fernet symmetric encryption."""

    def __init__(self) -> None:
        self.key: bytes | None = None
        self.password = ''

    def create_key(self) -> bytes:
        """Generate a new Fernet key and store it internally.

        Returns:
            The generated Fernet key.
        """
        self.key = Fernet.generate_key()
        return self.key

    def encrypt_password(self, password: str, my_key: bytes | None = None) -> str:
        """Encrypt a password using the provided or internally stored key.

        Args:
            password: The plaintext password to encrypt.
            my_key: The key to use for encryption.
                If None, uses the internally stored key.

        Raises:
            ValueError: If no key is set or password is less than 5 characters.

        Returns:
            The encrypted password as a string.
        """
        if my_key is None:
            my_key = self.key

        if my_key is None:
            raise ValueError("Encryption key not set. Call create_key() first.")
        
        if len(password) < 5:
            raise ValueError("Password cannot be less than 5 characters.")
        
        encrypted = Fernet(my_key).encrypt(password.encode())
        self.password = encrypted.decode()
        return self.password

    def decrypt_password(self, encrypted_password: str | None = None, my_key: bytes | None = None) -> str| None:
        """Decrypt an encrypted password using the provided or internally stored key.

        Args:
            encrypted_password: The encrypted password to decrypt.
            my_key: The key to use for decryption.

        Raises:
            ValueError: If no key is set or password is empty.

        Returns:
            The decrypted password as a string.
        """
        if my_key is None:
            my_key = self.key

        if my_key is None:
            raise ValueError("Decryption key not set. Call create_key() first.")
        
        if encrypted_password is None:
            encrypted_password = self.password

        if encrypted_password == '':
            raise ValueError("No encrypted password provided.")
        
        decrypted = Fernet(my_key).decrypt(encrypted_password.encode())
        return decrypted.decode()
    
    def strict_decrypt_password(self, encrypted_password: str , my_key: bytes) -> str:
        """Same as decrypt_password but without optional parameters.

        Arguments:
            encrypted_password -- The encrypted password to decrypt.
            my_key -- The key to use for decryption.

        Returns:
            The decrypted password as a string.
        """        
        decrypted = Fernet(my_key).decrypt(encrypted_password.encode())
        return decrypted.decode()
