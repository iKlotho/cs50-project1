import os,csv,psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
curr = conn.cursor()
curr.execute("DROP TABLE reviews;")
curr.execute("CREATE TABLE reviews (id SERIAL PRIMARY KEY, review VARCHAR NOT NULL,book_id INTEGER NOT NULL,acc_id INTEGER REFERENCES accounts);")
conn.commit()
print("CREATED")