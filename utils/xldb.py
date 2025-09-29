# C:\Users\Patrick\Desktop\FullCircle_ControlCentre2\utils\xldb.py
import os
from pathlib import Path
from datetime import date, timedelta, datetime
import pandas as pd
from dateutil.relativedelta import relativedelta
import numpy as np
import random as rnd

APP_ROOT = Path(__file__).resolve().parents[1]
WB_PATH = Path(os.environ.get("FULLCIRCLE_XLSX_PATH", APP_ROOT / "data" / "fullcircle.xlsx"))

SHEETS = {
    "Settings": ["key","value"],
    "Contacts": ["id","first_name","last_name","phone","email","street","suburb","postcode"],
    "Channels": ["id","name","owner","notes"],
    "Services": ["id","name","description","season","is_ongoing"],
    "Price_Book": ["id","name","category","unit","unit_rate","notes"],
    "Leads": ["id","created_at","contact_id","channel_id","service_requested","notes","tier","budget","timing","status","mql","sql"],
    "Quotes": ["id","lead_id","created_at","status","target_gm","total"],
    "Quote_Items": ["id","quote_id","item_id","description","qty","unit_price","cost_estimate","line_total","gm"],
    "Jobs": ["id","quote_id","scheduled_date","start_time","end_time","crew","status"],
    "Invoices": ["id","job_id","issue_date","due_date","total","status","paid_date","paid_method"],
    "AP_Expenses": ["id","date","vendor","category","description","amount"],
    "LeadGen_Metrics": ["id","channel_id","month","cost","leads","quotes","jobs","revenue"],
    "Roles": ["id","role_name","description","responsibilities"],
    "Role_Costs": ["id","role_id","monthly_cost"],
    "Equipment_Items": ["id","name","monthly_cost","selected"],
    "Cadence_Tasks": ["id","name","frequency","day_of_week","day_of_month","hour","minute","owner","active","notes"],
    "Cadence_Log": ["id","task_id","done_date","done"],
    "Essentials": ["id","name","provider","cost","billing_cycle","next_due","notes"],
    "Referrals": ["id","job_id","customer_name","text","permission","created_at","file_path"]
}

def _blank(sheet):
    return pd.DataFrame(columns=SHEETS[sheet])

def ensure_workbook():
    if Path(WB_PATH).exists():
        return
    seed_all()

def read(sheet:str)->pd.DataFrame:
    ensure_workbook()
    try:
        df = pd.read_excel(WB_PATH, sheet_name=sheet, engine="openpyxl")
        for c in SHEETS[sheet]:
            if c not in df.columns: df[c] = pd.Series(dtype=object)
        return df[SHEETS[sheet]]
    except Exception:
        return _blank(sheet)

def _write_all(dfs:dict):
    Path(WB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(WB_PATH, engine="openpyxl", mode="w") as xw:
        for k, df in dfs.items():
            for c in SHEETS[k]:
                if c not in df.columns: df[c] = pd.Series(dtype=object)
            df[SHEETS[k]].to_excel(xw, sheet_name=k, index=False)

def write(sheet:str, df:pd.DataFrame):
    ensure_workbook()
    try:
        all_sheets = pd.read_excel(WB_PATH, sheet_name=None, engine="openpyxl")
    except Exception:
        all_sheets = {}
    out = {}
    for k in SHEETS.keys():
        out[k] = all_sheets.get(k, _blank(k))
    out[sheet] = df.copy()
    _write_all(out)

def get_setting(key:str, default:str=""):
    s = read("Settings")
    m = s.loc[s["key"]==key, "value"]
    return (m.iloc[0] if not m.empty else default)

def set_setting(key:str, value:str):
    s = read("Settings")
    if (s["key"]==key).any():
        s.loc[s["key"]==key,"value"]=value
    else:
        s = pd.concat([s, pd.DataFrame([{"key":key,"value":value}])], ignore_index=True)
    write("Settings", s)

def next_id(df:pd.DataFrame)->int:
    if "id" in df.columns and not df.empty:
        return int(pd.to_numeric(df["id"], errors="coerce").fillna(0).max()) + 1
    return 1

def seed_all():
    rnd.seed(42)
    dfs = {k:_blank(k) for k in SHEETS.keys()}

    dfs["Settings"] = pd.DataFrame([
        {"key":"company_name","value":"Full Circle Gardens"},
        {"key":"owner_name","value":"Tony"},
        {"key":"gm_target","value":"0.40"}
    ])

    dfs["Channels"] = pd.DataFrame([
        (1,"Pamphlet Drop","Tony",""),
        (2,"Fridge Magnets","Tony",""),
        (3,"Facebook Ads","Sam",""),
        (4,"Word of Mouth","Lee",""),
        (5,"Local FB Groups","Tony",""),
    ], columns=SHEETS["Channels"])

    dfs["Services"] = pd.DataFrame([
        (1,"Lawn mowing","Mowing and edging standard lawn","summer",1),
        (2,"Garden maintenance","Weeding, pruning, tidy-ups","summer",1),
        (3,"Hedging","Trim hedges and clean-up","summer",0),
        (4,"Pressure washing","Clean paths/driveways per m²","winter",0),
        (5,"Garden bed rebuild","Small bed rebuilds incl. soil/mulch","winter",0),
        (6,"Gutter clears","Single-storey gutter clearing","winter",0),
    ], columns=SHEETS["Services"])

    dfs["Price_Book"] = pd.DataFrame([
        (1,"Mowing (hour)","Lawn","hour",90.0,"Labour per hour"),
        (2,"Edging (hour)","Lawn","hour",85.0,"Labour per hour"),
        (3,"Hedging (hour)","Garden","hour",95.0,"Labour per hour"),
        (4,"Pressure wash (m2)","Pressure","m2",6.5,"Includes detergent"),
        (5,"Mulch (m3)","Materials","m3",85.0,"Delivered"),
        (6,"Soil (m3)","Materials","m3",60.0,"Garden blend"),
        (7,"Green waste dump (load)","Disposal","unit",55.0,"Per trailer"),
        (8,"Call-out minimum (3h)","Callout","unit",270.0,"Covers travel/setup"),
    ], columns=SHEETS["Price_Book"])

    first = ["Ava","Liam","Noah","Mia","Olivia","Jack","Isla","Leo","Zoe","Ethan","Chloe","Lucas","Ruby","Max","Sophie","Archie","Grace","Hugo","Evie","Nate"]
    last = ["Smith","Brown","Williams","Jones","Taylor","Martin","Thompson","White","Walker","Harris","Lewis","Young","King","Wright","Baker","Green","Hall","Allen","Scott","Adams"]
    streets = ["King St","High St","Park Ave","Glebe Rd","Union St","Railway St","Church St","Baker St"]
    suburbs = ["Hamilton","Mayfield","New Lambton","Kotara","Merewether","Adamstown","Charlestown","Wallsend","Lambton","Jesmond"]
    rows=[]
    for i in range(1,51):
        fn, ln = rnd.choice(first), rnd.choice(last)
        phone = "04" + "".join(str(rnd.randint(0,9)) for _ in range(8))
        email = f"{fn.lower()}.{ln.lower()}@example.com"
        street = f"{rnd.randint(1,199)} {rnd.choice(streets)}"
        rows.append([i,fn,ln,phone,email,street,rnd.choice(suburbs),str(rnd.randint(2280,2330))])
    dfs["Contacts"] = pd.DataFrame(rows, columns=SHEETS["Contacts"])

    from datetime import timedelta as _td
    today = date.today()
    start = (today - relativedelta(months=5)).replace(day=1)
    lg_rows=[]; mid=1
    cid = {r["name"]:r["id"] for _,r in dfs["Channels"].iterrows()}
    mptr=start
    while mptr <= (today + relativedelta(months=5)).replace(day=1):
        is_winter = mptr.month in [5,6,7,8]
        for ch, ch_id in cid.items():
            base_cost = {"Pamphlet Drop":300,"Fridge Magnets":150,"Facebook Ads":420,"Word of Mouth":0,"Local FB Groups":40}[ch]
            cost = max(0, int(rnd.gauss(base_cost, max(5,base_cost*0.18))))
            leads = max(8, int(rnd.gauss(38 if not is_winter else 22, 7)))
            quotes = max(3, int(leads * rnd.uniform(0.52, 0.78)))
            jobs = max(2, int(quotes * rnd.uniform(0.58, 0.85)))
            rev = round(jobs * rnd.uniform(300, 720),2)
            lg_rows.append([mid,ch_id,mptr.strftime("%Y-%m"),cost,leads,quotes, jobs,rev]); mid+=1
        mptr = (mptr + relativedelta(months=1)).replace(day=1)
    dfs["LeadGen_Metrics"] = pd.DataFrame(lg_rows, columns=SHEETS["LeadGen_Metrics"])

    lead_rows=[]; quote_rows=[]; qitem_rows=[]; job_rows=[]; inv_rows=[]
    lid=1; qid=1; qitid=1; jid=1; invid=1
    price_map = {r["name"]:(int(r["id"]), float(r["unit_rate"])) for _,r in dfs["Price_Book"].iterrows()}
    contacts_ids = dfs["Contacts"]["id"].astype(int).tolist()
    channel_ids = dfs["Channels"]["id"].astype(int).tolist()
    services = dfs["Services"]["name"].tolist()
    import random as _r
    start_day = today - relativedelta(months=6)
    total_days = 365
    for _ in range(160):
        created = start_day + _td(days=_r.randint(0,total_days))  # created is a date
        created_iso = datetime(created.year, created.month, created.day, _r.randint(8,16), _r.randint(0,59)).isoformat()
        contact_id = _r.choice(contacts_ids); channel_id = _r.choice(channel_ids); svc = _r.choice(services)
        lead_rows.append([lid, created_iso, contact_id, channel_id, svc, "", _r.choice(["Economy","Business","First"]),
                          _r.choice(["Low","OK","Premium"]), _r.choice(["ASAP","Within 2 weeks","Flexible"]),
                          _r.choice(["New","Contacted","Qualified","Disqualified"]), 1, _r.choice([0,1])])
        if _r.random()<0.7:
            q_created = created + _td(days=_r.randint(0,5))  # date
            quote_rows.append([qid, lid, datetime(q_created.year,q_created.month,q_created.day,10,0).isoformat(),
                               _r.choice(["Draft","Sent","Accepted","Declined"]), 0.40, 0.0])
            q_total=0.0
            for _i in range(_r.randint(2,4)):
                name = _r.choice(list(price_map.keys())); item_id, unit_rate = price_map[name]
                qty = round(max(0.5, _r.gauss(2.2,1.0)),2)
                sell = unit_rate; line_total = round(qty*sell,2)
                qitem_rows.append([qitid,qid,item_id,name,qty,sell,sell*0.6,line_total, round(1-(sell*0.6)/max(0.01,sell),2)])
                q_total += line_total; qitid+=1
            quote_rows[-1][5] = round(q_total,2)
            if _r.random()<0.65:
                scheduled = q_created + _td(days=_r.randint(-90,90))  # date
                job_rows.append([jid,qid,scheduled.isoformat(),f"{_r.choice([8,9,10]):02d}:00",
                                 f"{_r.choice([11,12,13,14]):02d}:00", _r.choice(["Tony","Tony;Sam","Tony;Lee","Sam;Lee"]),
                                 "Done" if scheduled < date.today() else "Scheduled"])
                if _r.random()<0.9:
                    issue = scheduled  # already a date
                    due = issue + _td(days=7)
                    total = round(q_total*_r.uniform(0.95,1.1),2)
                    status = _r.choice(["Unpaid","Paid"])
                    paid_date = (due - _td(days=_r.randint(0,5))).isoformat() if status=="Paid" else None
                    method = _r.choice(["Card","Bank Transfer","Cash"]) if status=="Paid" else None
                    inv_rows.append([invid,jid,issue.isoformat(),due.isoformat(),total,status,paid_date,method]); invid+=1
                jid+=1
            qid+=1
        lid+=1
    dfs["Leads"] = pd.DataFrame(lead_rows, columns=SHEETS["Leads"])
    dfs["Quotes"] = pd.DataFrame(quote_rows, columns=SHEETS["Quotes"])
    dfs["Quote_Items"] = pd.DataFrame(qitem_rows, columns=SHEETS["Quote_Items"])
    dfs["Jobs"] = pd.DataFrame(job_rows, columns=SHEETS["Jobs"])
    dfs["Invoices"] = pd.DataFrame(inv_rows, columns=SHEETS["Invoices"])

    ap_rows=[]; apid=1; base = today - relativedelta(months=5)
    cats = ["Fuel","Servicing","Blades","Insurance","Dump Fees","Advertising","Phone","Accounting","Registration","Workcover","Hosting/Email"]
    vendors = ["BP","7-Eleven","Local Mower","NRMA","Council","Meta","Telco","Bookkeeper","ServiceNSW","ATO","FastMail"]
    import random as _r2
    for i in range(200):
        d = base + timedelta(days=i)
        if _r2.random()<0.4:
            ap_rows.append([apid,d.isoformat(),_r2.choice(vendors),_r2.choice(cats),"Expense",round(abs(_r2.gauss(85,45)),2)])
            apid+=1
    dfs["AP_Expenses"] = pd.DataFrame(ap_rows, columns=SHEETS["AP_Expenses"])

    dfs["Roles"] = pd.DataFrame([
        (1,"Marketing","Run channels, track ROI","FB posts\nPamphlets\nGallery updates"),
        (2,"Sales/Quoting","Qualify, site checks, quotes","Call leads\nSite photos\nQuotes"),
        (3,"Scheduling/Dispatch","Routes, confirm customers","Batch by suburb\nTool lists"),
        (4,"Field Team Lead","Safety, quality, sign-off","PPE\nPhotos\nSign-off"),
        (5,"Accounts","Invoice/remind, pay bills","Daily invoicing\n7/14 day reminders"),
        (6,"Owner","Metrics, systems","Dashboard\nPrice book review"),
        (7,"Landscaper 1 (Tony)","Lead hand","Operate mower\nClient liaison"),
        (8,"Landscaper 2 (Sam)","Crew","Hedging\nPressure wash"),
        (9,"Landscaper 3 (Lee)","Crew","Garden beds\nGutter clears")
    ], columns=SHEETS["Roles"])
    dfs["Role_Costs"] = pd.DataFrame([
        (1,7,6200.0), (2,8,5400.0), (3,9,5200.0), (4,4,6500.0),
    ], columns=SHEETS["Role_Costs"])

    dfs["Equipment_Items"] = pd.DataFrame([
        (1,"Van lease/ins.",980.0,False),
        (2,"Mower (capex->monthly)",220.0,False),
        (3,"Edger/Whipper",45.0,False),
        (4,"Pressure washer",90.0,False),
        (5,"Fuel",420.0,False),
        (6,"Maintenance",180.0,False),
        (7,"Dump fees",120.0,False),
        (8,"Uniform/PPE",60.0,False),
    ], columns=SHEETS["Equipment_Items"])

    dfs["Cadence_Tasks"] = pd.DataFrame([
        (1,"Confirm tomorrow's jobs","daily",None,None,17,0,"Tony",1,""),
        (2,"Invoice yesterday's work","daily",None,None,18,0,"Tony",1,""),
        (3,"Power hour admin","daily",None,None,7,30,"Tony",1,""),
        (4,"Sharpen blades & tool check","weekly",5,None,16,0,"Tony",1,""),
        (5,"Bank reconciliation","weekly",0,None,19,0,"Tony",1,""),
        (6,"Price book review","monthly",None,1,9,0,"Tony",1,""),
    ], columns=SHEETS["Cadence_Tasks"])

    dfs["Essentials"] = pd.DataFrame([
        (1,"Public Liability Insurance","NRMA",89.0,"monthly",(date.today()+timedelta(days=10)).isoformat(),""),
        (2,"Vehicle Insurance","NRMA",110.0,"monthly",(date.today()+timedelta(days=15)).isoformat(),""),
        (3,"WorkCover","icare",140.0,"monthly",(date.today()+timedelta(days=22)).isoformat(),""),
        (4,"Vehicle Rego","Service NSW",220.0,"quarterly",(date.today()+timedelta(days=35)).isoformat(),""),
        (5,"Accounting Software","Xero",65.0,"monthly",(date.today()+timedelta(days=3)).isoformat(),""),
        (6,"Domain & Email","Fastmail",13.0,"monthly",(date.today()+timedelta(days=27)).isoformat(),""),
        (7,"Phone Plan","TelcoCo",49.0,"monthly",(date.today()+timedelta(days=20)).isoformat(),""),
    ], columns=SHEETS["Essentials"])

    dfs["Referrals"] = _blank("Referrals")
    _write_all(dfs)
