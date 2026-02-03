from fastapi import FastAPI, HTTPException

from postgres_connect import TestDBConnection
from person import PersonCreate, FullPersonResponse, PersonUpdate

app: FastAPI = FastAPI() # fastapi dev /Users/Daniil/Desktop/Project/app/main.py --port 9999
database: TestDBConnection = TestDBConnection()



@app.get("/data", response_model=list[FullPersonResponse])
async def get_data_to_user(number: int = 100, descending: bool = False):
    return database.get_data(number=number, descending=descending)

    
@app.post("/signing", response_model=FullPersonResponse, status_code=201)    
async def insert_data_to_db(data: PersonCreate):
    if database.connection is None:
        raise ValueError("No database connection. Call connect() first.")
    
    age = PersonCreate.calculate_age(birth_date=data.birth_date)
    key = PersonCreate.key()
    password_encrypted = PersonCreate.password_encryption(
        data.password,
        my_key=key
    )
    with database.connection.cursor() as cur:
        cur.execute(t"INSERT INTO test  \
                    (first_name, last_name, gender, age, \
                    birth_date, email, password, key) \
                    VALUES \
                    ({data.first_name}, {data.last_name}, {data.gender}, {age}, \
                    {data.birth_date}, {data.email}, {password_encrypted}, {key}) \
                    RETURNING *")
        database.connection.commit()
        created_person: dict = cur.fetchone() # type: ignore
        return created_person
    
@app.put("/data/{email}", response_model=FullPersonResponse)    
async def update_data_in_db(email: str, data: PersonUpdate):
    if database.connection is None:
        raise ValueError("No database connection. Call connect() first.")
    
    with database.connection.cursor() as cur:
        cur.execute(t"SELECT key FROM test WHERE email = {email}")
        private: dict | None = cur.fetchone() 
        
        if private is None:
            raise HTTPException(status_code=404, detail="Person not found")
        
        private_key: bytes = private['key']
        
        age = PersonCreate.calculate_age(birth_date=data.birth_date) if data.birth_date is not None else None
        new_password_encrypted: str | None = None
        if data.password is not None:
            new_password_encrypted = PersonCreate.password_encryption(
                data.password,
                my_key=private_key
            )
        cur.execute(t"UPDATE test SET first_name = COALESCE({data.first_name}, first_name), \
                    last_name = COALESCE({data.last_name}, last_name), \
                    gender = COALESCE({data.gender}, gender), \
                    age = COALESCE({age}, age), \
                    birth_date = COALESCE({data.birth_date}, birth_date), \
                    password = COALESCE({new_password_encrypted}, password), \
                    key = {private_key} \
                    WHERE email = {email} \
                    RETURNING *")
        database.connection.commit()
        updated_person: dict = cur.fetchone() # type: ignore
        return updated_person
    
@app.delete("/data/{email}", response_model=FullPersonResponse)    
async def delete_data_from_db(email: str):
    if database.connection is None:
        raise ValueError("No database connection. Call connect() first.")
    
    with database.connection.cursor() as cur:
        cur.execute(t"DELETE FROM test WHERE email = {email} RETURNING *")
        database.connection.commit()
        deleted_person: dict | None = cur.fetchone() 
        
        if deleted_person is None:
            raise HTTPException(status_code=404, detail="Person not found")
        
        return deleted_person

@app.get("/data/{email}", response_model=FullPersonResponse)
async def get_person_by_email(email: str):
    if database.connection is None:
        raise ValueError("No database connection. Call connect() first.")
    
    with database.connection.cursor() as cur:
        cur.execute(t"SELECT * FROM test WHERE email = {email}")
        person: dict | None = cur.fetchone() 
        
        if person is None:
            raise HTTPException(status_code=404, detail="Person not found")
        
        return person
    
@app.get("/password/{email}", response_model=str | None)
async def get_password_by_email(email: str):
    if database.connection is None:
        raise ValueError("No database connection. Call connect() first.")
    
    with database.connection.cursor() as cur:
        cur.execute(t"SELECT password, key FROM test WHERE email = {email}")
        row: dict | None = cur.fetchone() 
        
        if row is None:
            raise HTTPException(status_code=404, detail="Person not found")
        
        encrypted_password: str = row['password']
        key: bytes = row['key']
        
        decrypted_password: str = PersonCreate.password_decryption(
            encrypted_password,
            my_key=key
        )
        
        return decrypted_password