import psycopg2

# وضعنا رابط Neon كاملاً كما نسخته أنت من الموقع
NEON_URL = "postgresql://neondb_owner:npg_cXHMGpT80QUt@ep-fragrant-water-alyos8cz.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require"

def get_connection():
    # الاتصال المباشر عبر الرابط
    return psycopg2.connect(NEON_URL)

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