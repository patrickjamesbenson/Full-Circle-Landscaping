from datetime import datetime, timedelta
import random
from dateutil.relativedelta import relativedelta

FIRST_NAMES = ["Ava","Liam","Noah","Mia","Olivia","Jack","Isla","Leo","Zoe","Ethan","Chloe","Lucas","Ruby","Max","Sophie","Archie","Grace","Hugo","Evie","Nate"]
LAST_NAMES = ["Smith","Brown","Williams","Jones","Taylor","Martin","Thompson","White","Walker","Harris","Lewis","Young","King","Wright","Baker","Green","Hall","Allen","Scott","Adams"]
SUBURBS = ["Hamilton","Mayfield","New Lambton","Kotara","Merewether","Adamstown","Charlestown","Wallsend","Lambton","Jesmond"]
CHANNELS = [
    ("Pamphlet Drop", "Tony"),
    ("Fridge Magnets", "Tony"),
    ("Facebook Ads", "Sam"),
    ("Word of Mouth", "Lee")
]
SERVICES = [
    ("Lawn mowing", "Mowing and edging standard lawn", "summer", 1),
    ("Garden maintenance", "Weeding, pruning, tidy-ups", "summer", 1),
    ("Hedging", "Trim hedges and clean-up", "summer", 0),
    ("Pressure washing", "Clean paths/driveways per m²", "winter", 0),
    ("Garden bed rebuild", "Small bed rebuilds incl. soil/mulch", "winter", 0),
    ("Gutter clears", "Single-storey gutter clearing", "winter", 0),
]
PRICE_ITEMS = [
    ("Mowing (hour)", "Lawn", "hour", 90.0, "Labour per hour"),
    ("Edging (hour)", "Lawn", "hour", 85.0, "Labour per hour"),
    ("Hedging (hour)", "Garden", "hour", 95.0, "Labour per hour"),
    ("Pressure wash (m2)", "Pressure", "m2", 6.5, "Includes detergent"),
    ("Mulch (m3)", "Materials", "m3", 85.0, "Delivered/retailed"),
    ("Soil (m3)", "Materials", "m3", 60.0, "Garden blend"),
    ("Green waste dump (load)", "Disposal", "unit", 55.0, "Per trailer"),
    ("Call-out minimum (3h)", "Callout", "unit", 270.0, "Covers travel/setup"),
]

def ensure_seed(conn, today=None):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c FROM leads")
    count = cur.fetchone()["c"]
    if count > 0:
        return  # already seeded

    # Insert channels
    for name, owner in CHANNELS:
        cur.execute("INSERT INTO channels(name, owner, notes) VALUES (?,?,?)", (name, owner, ""))

    # Insert services
    for n, d, s, ong in SERVICES:
        pass

    for n, d, s, ong in SERVICES:
        cur.execute("INSERT INTO services(name, description, season, is_ongoing) VALUES (?,?,?,?)", (n, d, s, ong))

    # Insert price items
    for n, cat, unit, rate, notes in PRICE_ITEMS:
        cur.execute("INSERT INTO price_items(name, category, unit, unit_rate, notes) VALUES (?,?,?,?,?)", (n, cat, unit, rate, notes))

    # Settings
    cur.execute("INSERT OR REPLACE INTO settings(key, value) VALUES (?,?)", ("company_name", "Tony's Landscapes"))
    cur.execute("INSERT OR REPLACE INTO settings(key, value) VALUES (?,?)", ("owner_name", "Tony"))

    # Leadgen stats and transactional data across last 6 months
    if today is None:
        today = datetime.now().date()
    start_month = (today - relativedelta(months=5)).replace(day=1)

    # helper to get channel ids
    cur.execute("SELECT id, name FROM channels")
    ch_rows = cur.fetchall()
    ch_map = {r["name"]: r["id"] for r in ch_rows}

    # Create monthly stats and also generate leads/quotes/jobs/invoices
    all_services = [s["name"] for s in conn.execute("SELECT name FROM services")]
    price_map = {r["name"]: (r["id"], r["unit_rate"]) for r in conn.execute("SELECT id,name,unit_rate FROM price_items")}

    random.seed(42)
    crew_choices = ["Tony","Tony;Sam","Tony;Lee","Sam;Lee"]

    month_ptr = start_month
    while month_ptr <= today.replace(day=1):
        month_str = month_ptr.strftime("%Y-%m")
        # baseline seasonality
        is_winter = month_ptr.month in [5,6,7,8]  # Southern hemisphere-ish winter (May-Aug)
        for cname in ch_map:
            base_cost = {"Pamphlet Drop": 250, "Fridge Magnets": 120, "Facebook Ads": 380, "Word of Mouth": 0}[cname]
            cost = max(0, int(random.gauss(base_cost, base_cost*0.15)))
            leads = max(5, int(random.gauss(30 if not is_winter else 18, 6)))
            quotes = max(3, int(leads * random.uniform(0.5, 0.8)))
            jobs = max(2, int(quotes * random.uniform(0.6, 0.85)))
            rev = jobs * random.uniform(280, 680)
            cur.execute("""INSERT INTO leadgen_stats(channel_id, month, cost, leads, quotes, jobs, revenue)
                           VALUES (?,?,?,?,?,?,?)""", (ch_map[cname], month_str, cost, leads, quotes, jobs, round(rev,2)))
        # Create individual leads on random days of month
        days_in_month = (month_ptr + relativedelta(months=1) - timedelta(days=1)).day
        for _ in range(int(random.gauss(25 if not is_winter else 18, 5))):
            d = random.randint(1, days_in_month)
            created_at = datetime(year=month_ptr.year, month=month_ptr.month, day=min(d, days_in_month), hour=random.randint(8,16), minute=random.randint(0,59))
            name = random.choice(FIRST_NAMES) + " " + random.choice(LAST_NAMES)
            phone = "04" + "".join([str(random.randint(0,9)) for _ in range(8)])
            email = name.split()[0].lower() + "@example.com"
            suburb = random.choice(SUBURBS)
            channel_id = random.choice(list(ch_map.values()))
            service = random.choice(all_services if not is_winter else [s for s in all_services if "Pressure" in s or "rebuild" in s or "Gutter" in s or "Garden" in s])
            tier = random.choice(["Economy","Business","First"])
            budget = random.choice(["Low","OK","Premium"])
            timing = random.choice(["ASAP","Within 2 weeks","Flexible"])
            cur.execute("""INSERT INTO leads(name, phone, email, suburb, channel_id, service_requested, notes, tier, budget, timing, mql_status, sql_status, status, created_at)
                           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (name, phone, email, suburb, channel_id, service, "", tier, budget, timing, 1, random.choice([0,1]), "New", created_at.isoformat()))
            lead_id = cur.lastrowid
            # Some become quotes
            if random.random() < 0.7:
                q_created = created_at + timedelta(days=random.randint(0,5))
                cur.execute("""INSERT INTO quotes(lead_id, created_at, status, total, notes)
                               VALUES (?,?,?,?,?)""", (lead_id, q_created.isoformat(), random.choice(["Draft","Sent","Accepted","Declined"]), 0, ""))
                quote_id = cur.lastrowid
                # 2-4 line items
                for _li in range(random.randint(2,4)):
                    item_name = random.choice(list(price_map.keys()))
                    item_id, unit_rate = price_map[item_name]
                    qty = round(max(0.5, random.gauss(2.0, 1.0)),2)
                    line_total = round(qty * unit_rate, 2)
                    cur.execute("""INSERT INTO quote_items(quote_id, item_id, description, qty, unit_price, line_total)
                                   VALUES (?,?,?,?,?,?)""", (quote_id, item_id, item_name, qty, unit_rate, line_total))
                # update total
                t = conn.execute("SELECT SUM(line_total) as tot FROM quote_items WHERE quote_id=?", (quote_id,)).fetchone()["tot"] or 0
                conn.execute("UPDATE quotes SET total=? WHERE id=?", (round(t,2), quote_id))
                # Some accepted -> job
                if random.random() < 0.65:
                    sched_date = (q_created + timedelta(days=random.randint(2,14))).date()
                    start_hour = random.choice([8,9,10])
                    end_hour = start_hour + random.choice([2,3,4])
                    crew = random.choice(crew_choices)
                    conn.execute("""INSERT INTO jobs(quote_id, scheduled_date, start_time, end_time, crew, status)
                                    VALUES (?,?,?,?,?,?)""", (quote_id, sched_date.isoformat(), f"{start_hour:02d}:00", f"{end_hour:02d}:00", crew, "Scheduled"))
                    job_id = conn.execute("SELECT last_insert_rowid() as id").fetchone()["id"]
                    # Some completed & invoiced
                    if random.random() < 0.85:
                        issue = sched_date
                        due = issue + timedelta(days=7)
                        total = round(t * random.uniform(0.95, 1.1), 2)
                        conn.execute("""INSERT INTO invoices(job_id, issue_date, due_date, total, status) VALUES (?,?,?,?,?)""",
                                     (job_id, issue.isoformat(), due.isoformat(), total, "Unpaid"))
                        inv_id = conn.execute("SELECT last_insert_rowid() as id").fetchone()["id"]
                        # Some paid
                        if random.random() < 0.9:
                            paid_date = due - timedelta(days=random.randint(0,5))
                            method = random.choice(["Card","Bank Transfer","Cash"])
                            conn.execute("""UPDATE invoices SET status=?, paid_date=?, paid_method=? WHERE id=?""",
                                         ("Paid", paid_date.isoformat(), method, inv_id))
        month_ptr = (month_ptr + relativedelta(months=1)).replace(day=1)

    # Seed some AP expenses
    cats = ["Fuel","Servicing","Blades","Insurance","Dump Fees","Advertising","Phone","Accounting"]
    base_date = today - relativedelta(months=5)
    for i in range(180):
        d = base_date + timedelta(days=i*1)
        if random.random() < 0.25:
            conn.execute("""INSERT INTO ap_expenses(date, vendor, category, description, amount)
                            VALUES (?,?,?,?,?)""", (d.isoformat(), random.choice(["BP","7-Eleven","Local Mower","NRMA","Council","Meta","Telco","Bookkeeper"]),
                                                     random.choice(cats), "Expense", round(abs(random.gauss(80,40)),2)))
    # Cadence tasks
    tasks = [
        ("Confirm tomorrow's jobs", "daily", None, None, 17, 0, "Tony"),
        ("Invoice yesterday's work", "daily", None, None, 18, 0, "Tony"),
        ("Sharpen blades & tool check", "weekly", 5, None, 16, 0, "Tony"),
        ("Price book review", "monthly", None, 1, 9, 0, "Tony"),
        ("Marketing review & plan", "monthly", None, 1, 10, 30, "Tony")
    ]
    for name, freq, dow, dom, h, m, owner in tasks:
        conn.execute("""INSERT INTO cadence_tasks(name, frequency, day_of_week, day_of_month, hour, minute, owner, active, notes)
                        VALUES (?,?,?,?,?,?,?,?,?)""", (name, freq, dow, dom, h, m, owner, 1, ""))

    # Essentials
    essentials = [
        ("Public Liability Insurance", "NRMA", 89.0, "monthly", (today + relativedelta(days=10)).isoformat(), ""),
        ("Vehicle Insurance", "NRMA", 110.0, "monthly", (today + relativedelta(days=15)).isoformat(), ""),
        ("Accounting Software", "Xero", 65.0, "monthly", (today + relativedelta(days=3)).isoformat(), ""),
        ("Phone Plan", "TelcoCo", 49.0, "monthly", (today + relativedelta(days=20)).isoformat(), ""),
    ]
    for n, p, c, cycle, due, notes in essentials:
        conn.execute("""INSERT INTO essentials(name, provider, cost, billing_cycle, next_due, notes)
                        VALUES (?,?,?,?,?,?)""", (n, p, c, cycle, due, notes))

    # Roles (basic)
    roles = [
        ("Marketing", "Run channels, collect photos, track ROI", "- Run Facebook posts\n- Order pamphlets/magnets\n- Update before/after gallery"),
        ("Sales/Quoting", "Qualify, site checks, quotes 24–48h", "- Call leads\n- Site photos\n- Produce quotes"),
        ("Scheduling/Dispatch", "Plan routes, confirm customers", "- Batch by suburb\n- Prep tool lists"),
        ("Field Team Lead", "Safety, quality, customer sign-off", "- PPE\n- Photos\n- Sign-off"),
        ("Accounts", "Invoice/remind, pay bills", "- Daily invoicing\n- 7/14 day reminders"),
        ("Owner", "Review metrics, improve systems", "- Weekly dashboard\n- Monthly price book review")
    ]
    for r in roles:
        conn.execute("""INSERT INTO roles(role_name, description, responsibilities) VALUES (?,?,?)""", r)

    conn.commit()
