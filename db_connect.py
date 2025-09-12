import psycopg2

def connect():
    try:
        conn = psycopg2.connect(
            dbname="aihealthapp",   # database you created
            user="newuser",           # your username
            password="2007",   # your password
            host="localhost",        # local server
            port="5432"              # default port
        )
        print("✅ Database connected successfully!")

        cur = conn.cursor()

        # Example: Create a table
        cur.execute("""
           CREATE TABLE IF NOT EXISTS healthcare.patients (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        age INT,
        disease VARCHAR(100)
            );
        """)
        conn.commit()

        print("✅ Table created successfully!")

        cur.close()
        conn.close()

    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    connect()
