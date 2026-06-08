import pg8000.dbapi

def get_connection():
    conn = pg8000.dbapi.connect(
        host="ep-fragrant-water-alyos8cz-pooler.c-3.eu-central-1.aws.neon.tech",
        database="neondb",
        user="neondb_owner",
        password="npg_cXHMGpT80QUt",
        port=5432
    )
    return conn

def create_tables():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id SERIAL PRIMARY KEY,
            customer_name TEXT,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            item_id SERIAL PRIMARY KEY,
            order_id INTEGER REFERENCES orders(order_id),
            designation TEXT,
            dimensions TEXT,
            quantity INTEGER,
            target_lames INTEGER,
            target_profiles INTEGER,
            components TEXT,
            progress_cnc INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

def add_production_order(customer_name, items_list):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("INSERT INTO orders (customer_name) VALUES (%s) RETURNING order_id", (customer_name,))
    order_id = cur.fetchone()[0]
    
    for item in items_list:
        components_str = ", ".join(item['components'])
        cur.execute('''
            INSERT INTO order_items (order_id, designation, dimensions, quantity, target_lames, target_profiles, components)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (order_id, item['designation'], item['dims'], item['qty'], item['lames'], item['profiles'], components_str))
    
    conn.commit()
    cur.close()
    conn.close()