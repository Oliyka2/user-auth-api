import psycopg
from person import Person


with psycopg.connect("dbname=mydb user=Daniil") as conn:

    with conn.cursor() as cur:

        person = Person()
        person.identity()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS test (
                id SERIAL NOT NULL PRIMARY KEY,
                first_name VARCHAR(80) NOT NULL,
                last_name VARCHAR(80) NOT NULL,
                gender VARCHAR(20) NOT NULL,
                age INT NOT NULL,
                birth_date DATE NOT NULL,
                email VARCHAR(200) UNIQUE NOT NULL,
                password VARCHAR(200),
                key BYTEA NOT NULL
                );
            """)
    
        cur.execute(
            """
            INSERT INTO test (first_name, last_name, gender, age, birth_date, email, password, key)
            VALUES (%(first_name)s, %(last_name)s, %(gender)s, %(age)s, %(birth_date)s, %(email)s, %(password)s, %(key)s)""",
            {'first_name' : person.first_name,'last_name' : person.last_name,
            'gender' : person.gender,'age' : person.age, 'birth_date' : person.person_dates,
            'email' : person.email, 'password' : person.password, 'key' : person.key}
            )
        
        # cur.execute("SELECT * FROM test")
        # rows = cur.fetchall()
        # for row in rows:
        #     print(row)
    
        conn.commit()
        


    