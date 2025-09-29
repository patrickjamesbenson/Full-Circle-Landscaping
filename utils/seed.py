import os, random
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

FIRST = ["Ava","Liam","Noah","Mia","Olivia","Jack","Isla","Leo","Zoe","Ethan","Chloe","Lucas","Ruby","Max","Sophie","Archie","Grace","Hugo","Evie","Nate"]
LAST  = ["Smith","Brown","Williams","Jones","Taylor","Martin","Thompson","White","Walker","Harris","Lewis","Young","King","Wright","Baker","Green","Hall","Allen","Scott","Adams"]
SUBURBS = ["Hamilton","Mayfield","New Lambton","Kotara","Merewether","Adamstown","Charlestown","Wallsend","Lambton","Jesmond"]
STATES = ["NSW"]

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
    ("Mowing (hour)","Lawn","hour",50.0,90.0,"Labour per hour"),
    ("Edging (hour)","Lawn","hour",45.0,85.0,"Labour per hour"),
    ("Hedging (hour)","Garden","hour",55.0,95.0,"Labour per hour"),
    ("Pressure wash (m2)","Pressure","m2",3.2,6.5,"Includes detergent"),
    ("Mulch (m3)","Materials","m3",55.0,85.0,"Delivered"),
    ("Soil (m3)","Materials","m3",40.0,60.0,"Garden blend"),
    ("Green waste dump (load)","Disposal","unit",25.0,55.0,"Per trailer"),
    ("Call-out minimum (3h)","Callout","unit",0.0,270.0,"Covers travel/setup"),
]

ROLES = [
    ("Marketing","Run channels, collect photos, track ROI","- Run FB posts\n- Order pamphlets\n- Update gallery"),
    ("Sales/Quoting","Qualify, site checks, quotes 24–48h","- Call leads\n- Site photos\n- Produce quotes"),
    ("Scheduling/Dispatch","Plan routes, confirm customers","- Batch by suburb\n- Prep tool lists"),
    ("Field Team Lead","Safety, quality, customer sign-off","- PPE\n- Photos\n- Sign-off"),
    ("Accounts","Invoice/remind, pay bills","- Daily invoicing\n- 7/14 day reminders"),
    ("Owner","Review metrics, improve systems","- Weekly dashboard\n- Monthly price book review")
]

RACI_TASKS = [
    ("Daily lead triage","Sales/Quoting","Owner","Marketing","Scheduling/Dispatch"),
    ("Weekly price review","Owner","Owner","Accounts","Field Team Lead"),
    ("Monthly ROI report","Marketing","Owner","Accounts","Sales/Quoting"),
    ("Site safety checks","Field Team Lead","Owner","Scheduling/Dispatch","Accounts"),
]

JOURNEY_STAGES = [
    ("Awareness","Prospect learns we exist","Marketing"),
    ("Inquiry","Prospect contacts us","Sales/Quoting"),
    ("Qualification","We confirm fit/budget/timing","Sales/Quoting"),
    ("Quote Sent","Formal price is sent","Sales/Quoting"),
    ("Accepted","Customer approves","Sales/Quoting"),
    ("Scheduled","Work is on the calendar","Scheduling/Dispatch"),
    ("Done","Work completed","Field Team Lead"),
    ("Invoiced","Invoice issued","Accounts"),
    ("Paid","Money received","Accounts"),
    ("Referral","Ask for public review","Marketing"),
]

JOURNEY_TOUCHES = [
    ("FB ad click","Awareness"), ("Pamphlet magnet call","Inquiry"), ("Website form","Inquiry"),
    ("Phone call","Inquiry"), ("Site visit","Qualification"), ("Quote email","Quote Sent"),
    ("SMS reminder","Scheduled"), ("Work day on site","Done"), ("Invoice email","Invoiced"),
    ("Thank you + referral ask","Referral")
]

def ensure_seed(conn, today=None):
    cur = conn.cursor()
    if today is None: today = date.today()
    # Avoid double seeding
    if cur.execute("SELECT COUNT(*) as c FROM leads").fetchone()["c"] > 0:
        return

    # Settings
    cur.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)",("company_name","Full Circle Gardens"))
    cur.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)",("owner_name","Tony"))
    cur.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)",("default_gm_pct","0.40"))
    cur.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)",("default_markup_pct","0.67"))

    # Channels / Services / Price items / Roles / RACI / Journey
    for n,o in CHANNELS: cur.execute("INSERT INTO channels(name,owner,notes) VALUES(?,?,?)",(n,o,""))
    for n,d,s,og in SERVICES: cur.execute("INSERT INTO services(name,description,season,is_ongoing) VALUES(?,?,?,?)",(n,d,s,og))
    for n,cat,unit,cost,rate,notes in PRICE_ITEMS:
        cur.execute("INSERT INTO price_items(name,category,unit,unit_cost,unit_rate,notes) VALUES(?,?,?,?,?,?)",(n,cat,unit,cost,rate,notes))
    for r in ROLES: cur.execute("INSERT INTO roles(role_name,description,responsibilities) VALUES (?,?,?)", r)
    for t in RACI_TASKS: cur.execute("INSERT INTO raci(task,R,A,C,I) VALUES (?,?,?,?,?)", t)
    for s in JOURNEY_STAGES: cur.execute("INSERT INTO journey_stages(stage,goal,owner) VALUES (?,?,?)", s)
    for t in JOURNEY_TOUCHES: cur.execute("INSERT INTO journey_touches(touchpoint,stage) VALUES (?,?)", t)

    # Contacts
    random.seed(42)
    contact_ids = []
    for _ in range(140):
        fn, ln = random.choice(FIRST), random.choice(LAST)
        phone = "04" + "".join(str(random.randint(0,9)) for _ in range(8))
        email = f"{fn.lower()}.{ln.lower()}@example.com"
        street = f"{random.randint(1,199)} {random.choice(['King','Queen','High','Station','Park'])} St"
        suburb = random.choice(SUBURBS)
        postcode = str(random.choice([2291,2292,2293,2294,2295,2296,2297,2298]))
        state = random.choice(STATES)
        cur.execute("""INSERT INTO contacts(first_name,last_name,phone,email,street,suburb,postcode,state)
                       VALUES (?,?,?,?,?,?,?,?)""", (fn,ln,phone,email,street,suburb,postcode,state))
        contact_ids.append(cur.lastrowid)

    # Leadgen stats across -6..+6 months
    def month_iter(center, back=6, fwd=6):
        start = (center - relativedelta(months=back)).replace(day=1)
        for i in range(back+fwd+1):
            m = start + relativedelta(months=i)
            yield m

    ch_map = {r["name"]: r["id"] for r in conn.execute("SELECT id,name FROM channels")}
    for m in month_iter(today,6,6):
        is_winter = m.month in [5,6,7,8]
        for cname,cid in ch_map.items():
            base_cost = {"Pamphlet Drop": 300, "Fridge Magnets": 150, "Facebook Ads": 520, "Word of Mouth": 0, "Local FB Groups": 40}[cname]
            cost = max(0, int(random.gauss(base_cost, base_cost*0.18)))
            leads = max(8, int(random.gauss(38 if not is_winter else 22, 7)))
            quotes = max(3, int(leads * random.uniform(0.52, 0.78)))
            jobs = max(2, int(quotes * random.uniform(0.58, 0.85)))
            rev = jobs * random.uniform(320, 820)
            cur.execute("""INSERT INTO leadgen_stats(channel_id,month,cost,leads,quotes,jobs,revenue)
                           VALUES (?,?,?,?,?,?,?)""",(cid, m.strftime("%Y-%m"), cost, leads, quotes, jobs, round(rev,2)))

    # Leads / Quotes / Jobs / Invoices back 6 months and forward 6 months
    services = [s["name"] for s in conn.execute("SELECT name FROM services")]
    price = {r["name"]:(r["id"], r["unit_cost"], r["unit_rate"]) for r in conn.execute("SELECT id,name,unit_cost,unit_rate FROM price_items")}
    crew_choices = ["Tony","Tony;Sam","Tony;Lee","Sam;Lee"]
    start_month = (today - relativedelta(months=6)).replace(day=1)
    end_month = (today + relativedelta(months=6)).replace(day=28)

    curdate = start_month
    while curdate <= end_month:
        days_in_month = (curdate + relativedelta(months=1) - timedelta(days=1)).day
        for _ in range(int(random.gauss(34, 8))):
            d = min(random.randint(1, days_in_month), days_in_month)
            created_at = datetime(curdate.year, curdate.month, d, random.randint(8,16), random.randint(0,59))
            contact_id = random.choice(contact_ids)
            channel_id = random.choice(list(ch_map.values()))
            service = random.choice(services)
            tier = random.choice(["Economy","Business","First"])
            budget = random.choice(["Low","OK","Premium"])
            timing = random.choice(["ASAP","Within 2 weeks","Flexible"])
            cur.execute("""INSERT INTO leads(contact_id, channel_id, service_requested, notes, tier, budget, timing, mql_status, sql_status, status, created_at)
                           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                        (contact_id, channel_id, service, "", tier, budget, timing, 1, random.choice([0,1]), "New", created_at.isoformat()))
            lead_id = cur.lastrowid

            if random.random() < 0.75:
                q_created = created_at + timedelta(days=random.randint(0,5))
                gm = 0.40
                cur.execute("""INSERT INTO quotes(lead_id, created_at, status, total, gm_pct, notes)
                               VALUES (?,?,?,?,?,?)""", (lead_id, q_created.isoformat(), random.choice(["Draft","Sent","Accepted","Declined"]), 0, gm, ""))
                quote_id = cur.lastrowid
                for _li in range(random.randint(2,5)):
                    item_name = random.choice(list(price.keys()))
                    item_id, unit_cost, unit_rate = price[item_name]
                    qty = round(max(0.5, random.gauss(2.2, 1.2)),2)
                    line_total = round(qty * unit_rate, 2)
                    cur.execute("""INSERT INTO quote_items(quote_id,item_id,description,qty,unit_cost,unit_price,line_total)
                                   VALUES (?,?,?,?,?,?,?)""", (quote_id, item_id, item_name, qty, unit_cost, unit_rate, line_total))
                t = conn.execute("SELECT COALESCE(SUM(line_total),0) as tot FROM quote_items WHERE quote_id=?", (quote_id,)).fetchone()["tot"]
                conn.execute("UPDATE quotes SET total=? WHERE id=?", (round(t,2), quote_id))
                if random.random() < 0.68:
                    sched_date = (q_created + timedelta(days=random.randint(2,21))).date()
                    start_hour = random.choice([8,9,10])
                    end_hour = start_hour + random.choice([2,3,4])
                    crew = random.choice(crew_choices)
                    conn.execute("""INSERT INTO jobs(quote_id, scheduled_date, start_time, end_time, crew, status) VALUES (?,?,?,?,?,?)""",
                                 (quote_id, sched_date.isoformat(), f"{start_hour:02d}:00", f"{end_hour:02d}:00", crew, "Scheduled"))
                    job_id = conn.execute("SELECT last_insert_rowid() as id").fetchone()["id"]
                    if random.random() < 0.9:
                        issue = sched_date
                        due = issue + timedelta(days=7)
                        total = round(t * random.uniform(0.95, 1.12), 2)
                        conn.execute("""INSERT INTO invoices(job_id, issue_date, due_date, total, status) VALUES (?,?,?,?,?)""",
                                     (job_id, issue.isoformat(), due.isoformat(), total, "Unpaid"))
                        inv_id = conn.execute("SELECT last_insert_rowid() as id").fetchone()["id"]
                        if random.random() < 0.9:
                            paid_date = due - timedelta(days=random.randint(0,5))
                            method = random.choice(["Card","Bank Transfer","Cash"])
                            conn.execute("""UPDATE invoices SET status=?, paid_date=?, paid_method=? WHERE id=?""",
                                         ("Paid", paid_date.isoformat(), method, inv_id)
                            )
        curdate = (curdate + relativedelta(months=1)).replace(day=1)

    # Expenses sample
    cats = ["Fuel","Servicing","Blades","Insurance","Dump Fees","Advertising","Phone","Accounting","Registration","Workcover","Hosting/Email"]
    base_date = today - relativedelta(months=6)
    for i in range(380):
        d = base_date + timedelta(days=i)
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

    # Sample referrals (latest 3 paid invoices)
    REFS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "referrals")
    os.makedirs(REFS, exist_ok=True)
    invs = conn.execute("""
        SELECT i.job_id, lrow.first_name || ' ' || lrow.last_name AS customer
        FROM invoices i
        JOIN jobs j ON i.job_id=j.id
        JOIN quotes q ON q.id=j.quote_id
        JOIN leads ld ON ld.id=q.lead_id
        JOIN contacts lrow ON lrow.id=ld.contact_id
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
        open(os.path.join(REFS, fname), "w", encoding="utf-8").write(html)
        conn.execute("""INSERT INTO referrals(job_id, customer_name, text, permission, created_at) VALUES (?,?,?,?,datetime('now'))""",
                     (r["job_id"], r["customer"], samples[i % len(samples)], 1))
    conn.commit()
