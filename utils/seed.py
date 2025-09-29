import os
from datetime import datetime, timedelta
import random
from dateutil.relativedelta import relativedelta

FIRST_NAMES = ["Ava","Liam","Noah","Mia","Olivia","Jack","Isla","Leo","Zoe","Ethan","Chloe","Lucas","Ruby","Max","Sophie","Archie","Grace","Hugo","Evie","Nate"]
LAST_NAMES = ["Smith","Brown","Williams","Jones","Taylor","Martin","Thompson","White","Walker","Harris","Lewis","Young","King","Wright","Baker","Green","Hall","Allen","Scott","Adams"]
SUBURBS = ["Hamilton","Mayfield","New Lambton","Kotara","Merewether","Adamstown","Charlestown","Wallsend","Lambton","Jesmond"]
CHANNELS = [("Pamphlet Drop","Tony"),("Fridge Magnets","Tony"),("Facebook Ads","Sam"),("Word of Mouth","Lee"),("Local FB Groups","Tony")]
SERVICES = [
    ("Lawn mowing","Mowing and edging standard lawn","summer",1),
    ("Garden maintenance","Weeding, pruning, tidy-ups","summer",1),
    ("Hedging","Trim hedges and clean-up","summer",0),
    ("Pressure washing","Clean paths/driveways per m²","winter",0),
    ("Garden bed rebuild","Small bed rebuilds incl. soil/mulch","winter",0),
    ("Gutter clears","Single-storey gutter clearing","winter",0),
]
PRICE_ITEMS = [
    ("Mowing (hour)","Lawn","hour",90.0,"Labour per hour"),
    ("Edging (hour)","Lawn","hour",85.0,"Labour per hour"),
    ("Hedging (hour)","Garden","hour",95.0,"Labour per hour"),
    ("Pressure wash (m2)","Pressure","m2",6.5,"Includes detergent"),
    ("Mulch (m3)","Materials","m3",85.0,"Delivered/retailed"),
    ("Soil (m3)","Materials","m3",60.0,"Garden blend"),
    ("Green waste dump (load)","Disposal","unit",55.0,"Per trailer"),
    ("Call-out minimum (3h)","Callout","unit",270.0,"Covers travel/setup"),
]

def ensure_seed(conn, today=None):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c FROM leads")
    if cur.fetchone()["c"] > 0:
        return

    for n,o in CHANNELS:
        cur.execute("INSERT INTO channels(name, owner, notes) VALUES (?,?,?)",(n,o,""))
    for n,d,s,ong in SERVICES:
        cur.execute("INSERT INTO services(name, description, season, is_ongoing) VALUES (?,?,?,?)",(n,d,s,ong))
    for n,cat,unit,rate,notes in PRICE_ITEMS:
        cur.execute("INSERT INTO price_items(name, category, unit, unit_rate, notes) VALUES (?,?,?,?,?)",(n,cat,unit,rate,notes))

    cur.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)",("company_name","Full Circle Gardens"))
    cur.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)",("owner_name","Tony"))

    if today is None:
        today = datetime.now().date()
    start_month = (today - relativedelta(months=5)).replace(day=1)

    ch_map = {r["name"]: r["id"] for r in conn.execute("SELECT id,name FROM channels")}
    all_services = [s["name"] for s in conn.execute("SELECT name FROM services")]
    price_map = {r["name"]:(r["id"], r["unit_rate"]) for r in conn.execute("SELECT id,name,unit_rate FROM price_items")}
    random.seed(42)
    crew_choices = ["Tony","Tony;Sam","Tony;Lee","Sam;Lee"]

    month_ptr = start_month
    while month_ptr <= today.replace(day=1):
        month_str = month_ptr.strftime("%Y-%m")
        is_winter = month_ptr.month in [5,6,7,8]
        for cname in ch_map:
            base_cost = {"Pamphlet Drop": 300, "Fridge Magnets": 150, "Facebook Ads": 420, "Word of Mouth": 0, "Local FB Groups": 40}[cname]
            cost = max(0, int(random.gauss(base_cost, base_cost*0.18)))
            leads = max(6, int(random.gauss(34 if not is_winter else 20, 6)))
            quotes = max(3, int(leads * random.uniform(0.5, 0.8)))
            jobs = max(2, int(quotes * random.uniform(0.6, 0.85)))
            rev = jobs * random.uniform(300, 720)
            cur.execute("""INSERT INTO leadgen_stats(channel_id, month, cost, leads, quotes, jobs, revenue)
                           VALUES (?,?,?,?,?,?,?)""", (ch_map[cname], month_str, cost, leads, quotes, jobs, round(rev,2)))
        # Leads/quotes/jobs
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta as _rel
        days_in_month = (month_ptr + _rel(months=1) - timedelta(days=1)).day
        for _ in range(max(1, int(random.gauss(30 if not is_winter else 22, 6)))):
            d = random.randint(1, days_in_month)
            created_at = datetime(year=month_ptr.year, month=month_ptr.month, day=min(d, days_in_month))
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
            if random.random() < 0.75:
                q_created = created_at
                cur.execute("""INSERT INTO quotes(lead_id, created_at, status, total, notes)
                               VALUES (?,?,?,?,?)""", (lead_id, q_created.isoformat(), random.choice(["Draft","Sent","Accepted","Declined"]), 0, ""))
                quote_id = cur.lastrowid
                for _li in range(random.randint(2,5)):
                    item_name = random.choice(list(price_map.keys()))
                    item_id, unit_rate = price_map[item_name]
                    qty = round(max(0.5, random.gauss(2.2, 1.2)),2)
                    line_total = round(qty * float(unit_rate), 2)
                    cur.execute("""INSERT INTO quote_items(quote_id, item_id, description, qty, unit_price, line_total)
                                   VALUES (?,?,?,?,?,?)""", (quote_id, item_id, item_name, qty, unit_rate, line_total))
                t = conn.execute("SELECT SUM(line_total) as tot FROM quote_items WHERE quote_id=?", (quote_id,)).fetchone()["tot"] or 0
                conn.execute("UPDATE quotes SET total=? WHERE id=?", (round(t,2), quote_id))
                if random.random() < 0.68:
                    sched_date = created_at.date()
                    start_hour = random.choice([8,9,10])
                    end_hour = start_hour + random.choice([2,3,4])
                    crew = random.choice(crew_choices)
                    conn.execute("""INSERT INTO jobs(quote_id, scheduled_date, start_time, end_time, crew, status)
                                    VALUES (?,?,?,?,?,?)""", (quote_id, sched_date.isoformat(), f"{start_hour:02d}:00", f"{end_hour:02d}:00", crew, "Scheduled"))
                    job_id = conn.execute("SELECT last_insert_rowid() as id").fetchone()["id"]
                    if random.random() < 0.9:
                        issue = sched_date
                        from datetime import timedelta as _td
                        due = issue + _td(days=7)
                        total = round(t * random.uniform(0.95, 1.12), 2)
                        conn.execute("""INSERT INTO invoices(job_id, issue_date, due_date, total, status) VALUES (?,?,?,?,?)""",
                                     (job_id, issue.isoformat(), due.isoformat(), total, "Unpaid"))
                        inv_id = conn.execute("SELECT last_insert_rowid() as id").fetchone()["id"]
                        if random.random() < 0.9:
                            paid_date = due
                            method = random.choice(["Card","Bank Transfer","Cash"])
                            conn.execute("""UPDATE invoices SET status=?, paid_date=?, paid_method=? WHERE id=?""",
                                         ("Paid", paid_date.isoformat(), method, inv_id))
        from dateutil.relativedelta import relativedelta as _rel2
        month_ptr = (month_ptr + _rel2(months=1)).replace(day=1)

    # Expenses
    cats = ["Fuel","Servicing","Blades","Insurance","Dump Fees","Advertising","Phone","Accounting","Registration","Workcover","Hosting/Email"]
    base_date = today - relativedelta(months=5)
    for i in range(200):
        from datetime import timedelta as _td2
        d = base_date + _td2(days=i)
        if random.random() < 0.35:
            conn.execute("""INSERT INTO ap_expenses(date, vendor, category, description, amount)
                            VALUES (?,?,?,?,?)""", (d.isoformat(), random.choice(["BP","7-Eleven","Local Mower","NRMA","Council","Meta","Telco","Bookkeeper","ServiceNSW","ATO","FastMail"]),
                                                     random.choice(cats), "Expense", round(abs(random.gauss(85,45)),2)))

    # Cadence tasks
    tasks = [
        ("Confirm tomorrow's jobs","daily",None,None,17,0,"Tony"),
        ("Invoice yesterday's work","daily",None,None,18,0,"Tony"),
        ("Morning admin power hour","daily",None,None,7,30,"Tony"),
        ("Sharpen blades & tool check","weekly",5,None,16,0,"Tony"),
        ("Bank reconciliation","weekly",0,None,19,0,"Tony"),
        ("Price book review","monthly",None,1,9,0,"Tony"),
        ("Marketing review & plan","monthly",None,1,10,30,"Tony"),
        ("Quarterly safety toolbox","monthly",None,15,8,0,"Tony")
    ]
    for name,freq,dow,dom,h,m,owner in tasks:
        conn.execute("""INSERT INTO cadence_tasks(name, frequency, day_of_week, day_of_month, hour, minute, owner, active, notes)
                        VALUES (?,?,?,?,?,?,?,?,?)""", (name,freq,dow,dom,h,m,owner,1,""))

    essentials = [
        ("Public Liability Insurance","NRMA",89.0,"monthly",today.isoformat(),""),
        ("Vehicle Insurance","NRMA",110.0,"monthly",today.isoformat(),""),
        ("WorkCover","icare",140.0,"monthly",today.isoformat(),""),
        ("Vehicle Rego","Service NSW",220.0,"quarterly",today.isoformat(),""),
        ("Accounting Software","Xero",65.0,"monthly",today.isoformat(),""),
        ("Domain & Email","Fastmail",13.0,"monthly",today.isoformat(),""),
        ("Phone Plan","TelcoCo",49.0,"monthly",today.isoformat(),""),
    ]
    for n,p,c,cycle,due,notes in essentials:
        conn.execute("""INSERT INTO essentials(name, provider, cost, billing_cycle, next_due, notes)
                        VALUES (?,?,?,?,?,?)""",(n,p,c,cycle,due,notes))

    roles = [
        ("Marketing","Run channels, collect photos, track ROI","- Run Facebook posts\n- Order pamphlets/magnets\n- Update before/after gallery"),
        ("Sales/Quoting","Qualify, site checks, quotes 24–48h","- Call leads\n- Site photos\n- Produce quotes"),
        ("Scheduling/Dispatch","Plan routes, confirm customers","- Batch by suburb\n- Prep tool lists"),
        ("Field Team Lead","Safety, quality, customer sign-off","- PPE\n- Photos\n- Sign-off"),
        ("Accounts","Invoice/remind, pay bills","- Daily invoicing\n- 7/14 day reminders"),
        ("Owner","Review metrics, improve systems","- Weekly dashboard\n- Monthly price book review"),
        ("Landscaper 1 (Tony)","Lead hand","- Operate mower/edger\n- Client liaison"),
        ("Landscaper 2 (Sam)","Crew","- Hedging\n- Pressure wash"),
        ("Landscaper 3 (Lee)","Crew","- Garden beds\n- Gutter clears")
    ]
    for r in roles:
        conn.execute("""INSERT INTO roles(role_name, description, responsibilities) VALUES (?,?,?)""", r)

    conn.commit()

    # Seed sample referral HTMLs
    ref_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "referrals")
    os.makedirs(ref_dir, exist_ok=True)
    invs = conn.execute("""
        SELECT i.job_id, l.name as customer
        FROM invoices i
        JOIN jobs j ON i.job_id=j.id
        JOIN quotes q ON q.id=j.quote_id
        JOIN leads l ON l.id=q.lead_id
        WHERE i.status='Paid'
        ORDER BY date(i.paid_date) DESC
        LIMIT 3
    """).fetchall()
    samples = [
        "The team was on time and my lawn has never looked better. Highly recommended.",
        "Great communication, fair quote, and tidy work. Will book the maintenance plan.",
        "They pressure-washed our paths and the place looks brand new."
    ]
    now = datetime.now()
    for i, r in enumerate(invs):
        fname = f"ref_job{r['job_id']}_{now.strftime('%Y%m%d_%H%M%S')}_{i}.html"
        html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Referral - {r['customer']}</title></head>
<body style="font-family:Georgia,serif;background:#F0EBDD;color:#34382F;padding:24px;">
<h2>Full Circle Gardens — Customer Referral</h2>
<p><strong>Customer:</strong> {r['customer']}</p>
<blockquote style="font-size:1.2rem;line-height:1.5;border-left:4px solid #C6723D;margin:0;padding-left:16px;">
{samples[i % len(samples)]}
</blockquote>
<p><small>Saved: {now.strftime('%d %b %Y %H:%M')}</small></p>
</body></html>"""
        open(os.path.join(ref_dir, fname), "w", encoding="utf-8").write(html)
        conn.execute("""INSERT INTO referrals(job_id, customer_name, text, permission, created_at) VALUES (?,?,?,?,datetime('now'))""",
                     (r["job_id"], r["customer"], samples[i % len(samples)], 1))
    conn.commit()
