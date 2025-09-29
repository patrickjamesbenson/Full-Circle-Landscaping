import os, sqlite3
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "app.db")

def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = dict_factory
    return conn

def init_db(conn):
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT)")
    c.execute("""CREATE TABLE IF NOT EXISTS contacts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT, last_name TEXT, phone TEXT, email TEXT,
        street TEXT, suburb TEXT, postcode TEXT, state TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS channels(
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, owner TEXT, notes TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS services(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, description TEXT, season TEXT CHECK(season IN ('summer','winter','all')) DEFAULT 'all',
        is_ongoing INTEGER DEFAULT 0
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS price_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, category TEXT, unit TEXT, unit_cost REAL DEFAULT 0, unit_rate REAL DEFAULT 0, notes TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS leads(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contact_id INTEGER, channel_id INTEGER, service_requested TEXT,
        notes TEXT, tier TEXT, budget TEXT, timing TEXT,
        mql_status INTEGER DEFAULT 0, sql_status INTEGER DEFAULT 0, status TEXT DEFAULT 'New', created_at TEXT,
        FOREIGN KEY(contact_id) REFERENCES contacts(id),
        FOREIGN KEY(channel_id) REFERENCES channels(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS quotes(
        id INTEGER PRIMARY KEY AUTOINCREMENT, lead_id INTEGER, created_at TEXT, status TEXT, total REAL DEFAULT 0, gm_pct REAL DEFAULT 0, notes TEXT,
        FOREIGN KEY(lead_id) REFERENCES leads(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS quote_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT, quote_id INTEGER, item_id INTEGER, description TEXT,
        qty REAL, unit_cost REAL, unit_price REAL, line_total REAL,
        FOREIGN KEY(quote_id) REFERENCES quotes(id), FOREIGN KEY(item_id) REFERENCES price_items(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS jobs(
        id INTEGER PRIMARY KEY AUTOINCREMENT, quote_id INTEGER, scheduled_date TEXT, start_time TEXT, end_time TEXT, crew TEXT, status TEXT,
        FOREIGN KEY(quote_id) REFERENCES quotes(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS invoices(
        id INTEGER PRIMARY KEY AUTOINCREMENT, job_id INTEGER, issue_date TEXT, due_date TEXT, total REAL, status TEXT, paid_date TEXT, paid_method TEXT,
        FOREIGN KEY(job_id) REFERENCES jobs(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS ap_expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, vendor TEXT, category TEXT, description TEXT, amount REAL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS leadgen_stats(
        id INTEGER PRIMARY KEY AUTOINCREMENT, channel_id INTEGER, month TEXT, cost REAL, leads INTEGER, quotes INTEGER, jobs INTEGER, revenue REAL,
        FOREIGN KEY(channel_id) REFERENCES channels(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS roles(
        id INTEGER PRIMARY KEY AUTOINCREMENT, role_name TEXT, description TEXT, responsibilities TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS raci(
        id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT, R TEXT, A TEXT, C TEXT, I TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS journey_stages(
        id INTEGER PRIMARY KEY AUTOINCREMENT, stage TEXT, goal TEXT, owner TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS journey_touches(
        id INTEGER PRIMARY KEY AUTOINCREMENT, touchpoint TEXT, stage TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS cadence_tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, frequency TEXT, day_of_week INTEGER, day_of_month INTEGER,
        hour INTEGER, minute INTEGER, owner TEXT, active INTEGER DEFAULT 1, notes TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS cadence_log(
        id INTEGER PRIMARY KEY AUTOINCREMENT, task_id INTEGER, done_date TEXT, done INTEGER DEFAULT 0
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS referrals(
        id INTEGER PRIMARY KEY AUTOINCREMENT, job_id INTEGER, customer_name TEXT, text TEXT, permission INTEGER DEFAULT 0, created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS job_photos(
        id INTEGER PRIMARY KEY AUTOINCREMENT, job_id INTEGER, file_path TEXT
    )""")
    conn.commit()
