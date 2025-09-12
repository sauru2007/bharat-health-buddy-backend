import psycopg2

# Database connection details
DB_HOST = "localhost"      # or "127.0.0.1"
DB_NAME = "aihealthcare"   # replace with your database name
DB_USER = "postgres"       # default superuser
DB_PASS = "sauru@2007"   # replace with your password
DB_PORT = "5432"           # default PostgreSQL port

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    print("✅ Connection successful!")

    # Create a cursor
    cur = conn.cursor()

    # Example: create a table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100) UNIQUE
        );
    """)

    # Insert a sample row
    cur.execute("INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id;", 
                ("Alice", "alice@example.com"))
    new_id = cur.fetchone()[0]
    print(f"✅ Inserted new user with id {new_id}")

    # Fetch data
    cur.execute("SELECT * FROM users;")
    rows = cur.fetchall()
    print("📌 Current Users:")
    for row in rows:
        print(row)

    # Commit changes
    conn.commit()

    # Close connections
    cur.close()
    conn.close()
    print("🔒 Connection closed.")

except Exception as e:
    print("❌ Error:", e)
