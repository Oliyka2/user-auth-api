from fastapi import FastAPI, HTTPException

from postgres_connect import TestBcryptDBConnection
from person import PersonCreate, PersonUpdate, PersonBcrypt

app: FastAPI = FastAPI() # fastapi dev /Users/Daniil/Desktop/Project/app/main.py --port 9999
database: TestBcryptDBConnection = TestBcryptDBConnection()

@app.get("/data", response_model=list[PersonBcrypt])
async def get_data_to_user(number: int = 100, descending: bool = False):
    return database.get_data_bcrypt(number=number, descending=descending)


@app.post("/signing", response_model=PersonBcrypt, status_code=201)    
async def insert_data_to_db(data: PersonCreate):
    if database.connection is None:
        raise ValueError("No database connection. Call connect() first.")
    
    age = PersonCreate.calculate_age(birth_date=data.birth_date)
    password_hashed = PersonCreate.password_bcrypt_hash(data.password)
    
    with database.connection.cursor() as cur:
        cur.execute(t"INSERT INTO test_bcrypt  \
                    (first_name, last_name, gender, age, \
                    birth_date, email, hash_password) \
                    VALUES \
                    ({data.first_name}, {data.last_name}, {data.gender}, {age}, \
                    {data.birth_date}, {data.email}, {password_hashed}) \
                    RETURNING *")
        database.connection.commit()
        created_person: dict = cur.fetchone() # type: ignore
        return created_person

@app.put("/data/{email}", response_model=PersonBcrypt)    
async def update_data_in_db(email: str, password: str, data: PersonUpdate):
    if database.connection is None:
        raise ValueError("No database connection. Call connect() first.")
    
    with database.connection.cursor() as cur:
        cur.execute(t"SELECT hash_password FROM test_bcrypt WHERE email = {email}")
        private: dict | None = cur.fetchone() 
        
        if private is None:
            raise HTTPException(status_code=404, detail="Person not found")
        
        hashed_password: str = private['hash_password']
        password_check: bool = PersonCreate.password_bcrypt_check(
            password,
            hashed_password
        )
        if not password_check:
            raise HTTPException(status_code=403, detail="Incorrect password or email")
        
        age = PersonCreate.calculate_age(birth_date=data.birth_date) if data.birth_date is not None else None
        new_password_encrypted: str | None = None
        if data.password is not None:
            new_password_encrypted = PersonCreate.password_bcrypt_hash(
                data.password,
            )
        else:
            new_password_encrypted= PersonCreate.password_bcrypt_hash(password) 
                           
        cur.execute(t"UPDATE test_bcrypt SET first_name = COALESCE({data.first_name}, first_name), \
                    last_name = COALESCE({data.last_name}, last_name), \
                    gender = COALESCE({data.gender}, gender), \
                    age = COALESCE({age}, age), \
                    birth_date = COALESCE({data.birth_date}, birth_date), \
                    hash_password = COALESCE({new_password_encrypted}, hash_password) \
                    WHERE email = {email} \
                    RETURNING *")
        database.connection.commit()
        updated_person: dict = cur.fetchone() # type: ignore
        return updated_person
    
@app.delete("/data/{email}", response_model=PersonBcrypt)    
async def delete_data_from_db(email: str, password: str):
    if database.connection is None:
        raise ValueError("No database connection. Call connect() first.")
    
    with database.connection.cursor() as cur:
        cur.execute(t"SELECT hash_password FROM test_bcrypt WHERE email = {email}")
        row: dict | None = cur.fetchone() 
        
        if row is None:
            raise HTTPException(status_code=404, detail="Person not found")
        
        encrypted_password: str = row['hash_password']
        
        password_check: bool = PersonCreate.password_bcrypt_check(
            password,
            encrypted_password)
        
        if not password_check:
            raise HTTPException(status_code=403, detail="Incorrect password or email")
    
    with database.connection.cursor() as cur:
        cur.execute(t"DELETE FROM test_bcrypt WHERE email = {email} RETURNING *")
        database.connection.commit()
        deleted_person: dict | None = cur.fetchone() 
        
        if deleted_person is None:
            raise HTTPException(status_code=404, detail="Person not found")
        
        return deleted_person
    
@app.get("/data/{email}", response_model=PersonBcrypt)
async def get_person_by_email(email: str):
    if database.connection is None:
        raise ValueError("No database connection. Call connect() first.")
    
    with database.connection.cursor() as cur:
        cur.execute(t"SELECT * FROM test_bcrypt WHERE email = {email}")
        person: dict | None = cur.fetchone() 
        
        if person is None:
            raise HTTPException(status_code=404, detail="Person not found")
        
        return person
    
@app.get("/login/{email}", response_model=dict | None)
async def login(email: str, password: str):
    if database.connection is None:
        raise ValueError("No database connection. Call connect() first.")
    
    with database.connection.cursor() as cur:
        cur.execute(t"SELECT hash_password FROM test_bcrypt WHERE email = {email}")
        row: dict | None = cur.fetchone() 
        
        if row is None:
            raise HTTPException(status_code=404, detail="Person not found")
        
        hashed_password: str = row['hash_password']
        
        password_check: bool = PersonCreate.password_bcrypt_check(
            password,
            hashed_password
        )
        if not password_check:
            raise HTTPException(status_code=403, detail="Incorrect password or email")
        return {"message": "Login successful"}