from database import get_db_connection

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL
        )
    """)

    # 2. Parkings Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parking (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        )
    """)

    # 3. Individual parking spots Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS p_lots (
            id SERIAL PRIMARY KEY,
            parking_id INT NOT NULL,
            plot_number VARCHAR(20) NOT NULL,
            FOREIGN KEY (parking_id) REFERENCES parking(id) ON DELETE CASCADE
        )
    """)

    # 4. Reservations Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id SERIAL PRIMARY KEY,
            user_id INT NOT NULL,
            parking_id INT NOT NULL,
            plot_number VARCHAR(50) NOT NULL,
            status VARCHAR(20) DEFAULT 'Reserved',
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (parking_id) REFERENCES parking(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("PostgreSQL tables created successfully!")

if __name__ == "__main__":
    create_tables()