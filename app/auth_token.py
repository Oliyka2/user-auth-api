from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends
import jwt

from typing import Any
from datetime import datetime, timedelta

from app.postgres_connect import TestBcryptDBConnection
from app.person import PersonTokenResponse, PersonLogin, TokenData



class AuthToken:
    
    oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")
    secret_key: str
    algorithm: str
    database: TestBcryptDBConnection | None = None
    
    def __init__(self, secret_key: str, algorithm: str = "HS256", database: TestBcryptDBConnection | None = None):
        AuthToken.secret_key = secret_key
        AuthToken.algorithm = algorithm
        AuthToken.database = database 
        

    @staticmethod
    def create_access_token(data: dict, expires_delta: int | None = None):
        to_encode:dict[str, Any] = data.copy()
        # to_encode["birth_date"] = datetime.date(to_encode["birth_date"]).isoformat() if to_encode["birth_date"] else None
        if expires_delta:
            expire = datetime.now() + timedelta(minutes=expires_delta)
        else:
            expire = datetime.now() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        jwt_token: str = jwt.encode(to_encode, key=AuthToken.secret_key, algorithm=AuthToken.algorithm) # type: ignore
        return jwt_token

    @staticmethod
    def verify_token(token: str) -> TokenData:
        try:
            payload: dict[str, Any] = jwt.decode(token, key=AuthToken.secret_key, algorithms=[AuthToken.algorithm]) # type: ignore
            email: str = payload["email"]
            if email is None:
                raise HTTPException(status_code=400, detail="Email not found in token.")
            return TokenData(email=email)
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token.")
        
    @staticmethod
    async def get_current_user(
        token: str = Depends(oauth_scheme)
    ) -> TokenData:
        if AuthToken.database is None or AuthToken.database.connection is None:
            raise ValueError("No database connection. Call connect() first.")
        
        token_data: TokenData = AuthToken.verify_token(token)
        with AuthToken.database.connection.cursor() as cur:
            cur.execute(t"SELECT email FROM test_bcrypt WHERE email = {token_data.email}")
            user: dict | None = cur.fetchone()
            if user is None:
                raise HTTPException(status_code=404, detail="User not found.")
            return token_data
        
    @staticmethod
    async def get_current_active_user(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        if not current_user:
            raise HTTPException(status_code=400, detail="Inactive user.")
        return current_user


