import os,csv,psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')



print("Creating accounts table!")
curr = conn.cursor()
curr.execute("CREATE TABLE accounts (id SERIAL PRIMARY KEY, user_id VARCHAR NOT NULL,password VARCHAR NOT NULL);")
conn.commit()
print("CREATED")


CREATE TABLE reviews (id SERIAL PRIMARY KEY, review VARCHAR NOT NULL,acc_id INTEGER REFERENCES accounts)