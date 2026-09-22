# ======================================================================
# WIN CRM - Fibra Óptica | Sales & Benefits Dept
#Free & open source: Python + streamlit + SQLite
# ======================================================================
import streamlit as st
import sqlite3
import pandas as pd 
from datetime import datetime, date, timedelta
st.set_page_config(page_title="WIN CRM", page_icon="\U0001F4F6", layout="wide")
DB = "crm.db"
# ---------- PASSWORD GATE  ----------
APP_PASWORD = "win2024"
if "auth" not in st.session_state:
    st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h2 style='text-align:center'>\U0001F4F6 WIN - CRM</h2>", unsafe_allow_html=True)
    pw = st.text_input("Enter password", type="password")
    if st.button("Login", type="primary", use_contatiner_with=True):
        if pw == APP_PASWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Wrong password")
        st.stop()
# ---------- DATABASE ----------
def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row 
    return conn
def init_db():
    c= db()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS clients(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, dni TEXT, phone TEXT, email TEXT,
            district TEXT, address TEXT,
            coverage TEXT DEFAULT 'Pending',
            coverage_date TEXT,
            plan TEXT, status TEXT DEFAULT 'Active',
            notes TEXT, created TEXT);
        CREATE TABLE IF NOT EXISTS comms(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER, type TEXT, message TEXT,
            response TEXT, ts TEXT);
        CREATE TABLE IF NOT EXISTS followups(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER, fdate TEXT, ftime TEXT,
            status TEXT DEFAULT 'Pending');
        """)
    c.commit()
    c.close()


init_db()
def q(sql, params=()):
    c= db(); r = c.execute(sql, params).fetchall(); c.close(); return r

def ex(sql, params=()):
    c = db(); c.execute(sql, params); c.commit(); c.close()

# ---------- PLAN DATA ----------
PLANS_LIMA = [
    ("400 Mbps", 79.00, "Solo internet"),
    ("450 Mbps", 89.00, "Solo internet"),
    ("750 Mbps", 109.00, "Solo internet"),
    ("750 Mbps + WinTV Premium", 119.90, "Internet + TV"),
    ("850 Mbps + WinTV Liga 1 Max Premium", 129.90, "Internet + TV + futbol" ),
    ("1000 Mbps (Mesh en comodato)", 139.00, "Solo internet + Mesh"),
    ("1000 Mbps + WinTV Premium + Mesh en comodato", 139.90, "Internet + TV + Mesh"),
    ("1000 Mbps + WinTV Liga 1 Max Premium + Mesh o WinBox en comodato (a escoger)", 149.90, "Top: Internet + TV + Futbol + Mesh/WinBox"),
    ("850 Mbps + DGO Hogar + Prime Video + Liga 1 Max + Mesh en comodato", 139.90, "Mega bundle: todo incluido"),
]
PLANS_PROVINCIA = [
    ("450 Mbps", 79.00, "Solo internet"),
    ("550 Mbps", 89.00, "Solo internet"),
    ("550 Mbps + WinTV Premium", 89.90, "Internet + TV"),
    ("750 Mbps", 99.00, "Solo internet"),
    ("750 Mbps + WinTV Premium", 99.90, "Internet + TV" ),
    ("1000 Mbps", 129.00, "Solo internet"),
    ("1000 Mbps + WinTV Liga 1 Max Premium + Mesh en comodato ", 129.90, "Top: Internet + TV + Futbol + Mesh"),
    ("1000 Mbps + DGO Hogar + Prime Video + Liga 1 Max + Mesh en comodato", 129.90, "Mega bundle: todo incluido"),
]
EXTRAS = [
    ("1 Mesh (repetidor)", 9.90),
    ("1 WinBox (convertidor)", 15.00),
    ("2 WinBox (convertidor)", 30.00),
    ("Fono Win - 1000 min. a celulares, ilimitado a fijos (solo Provincia, S/1 x 6 meses, luego S/10)", 10.00),
]
PROMO = "2 PRIMEROS MESES S/1.00"


def plans_text(zona):
    plans = PLANS_LIMA if zona == "LIMA" else PLANS_PROVINCIA
    t = "WIN - PLANES\n" + zona + "\n" + PROMO + "\n\n"
    for n, p, d in plans:
        t += f"• {n} — S/ {p:.2f}/mes ({d})\n"
    t += "\nExtras:\n"
    for n, p in EXTRAS:
        t += f"• {n} — S/ {p:.2f}/mes\n"
    return t

# ---------- TEMPLATES ----------
def T_initial(n, d): return (f"Hola {n}! Buenas noticias: confirmamos que tu zona"
    f"({d}) tiene cobertura WIN \n\n{PROMO}\n\n"
    "¿Te interesa ver los planes disponibles?")

def T_noanswer(n, d): return (f"Hola {n}, te volvemos a contactar de WIN."
    f"Tenemos conbertura en {d} y la promo de 2 meses por S/1.00 sigue vigente."
    "¿Reservamos tu instalación?")
def T_plans(n, d, zona="LIMA"): return f"Hola {n}! Estos son los planes WIN para {d}:\n\n{plans_text()}"
def T_close(n, plan, d): return (f"Hola {n}! confirmamos la instalación de tu plan {plan}."
    " Nuestro técnico te contactará para coordinar la fecha. ¡Bienvenido a WIN!")

def T_thanks(n): return (f"Gracias {n} por confiar en WIN !"
    "Cualquier consulta, estamos para ayudarte. ¡Que disfrutes tu nueva fibra!")

TEMPLATES = [
    ("Initial outreach (S/1.00 promo)", T_initial),
    ("No answer follow-up", T_noanswer),
    ("Full plan details", T_plans),
    ("Closing — confirm installation", T_close),
    ("Thank you — sale confirmed", lambda n, d: T_thanks(n)),
]

# ---------- CSS (mobile friendly, touch friendly) ----------
st.markdown("""<style>
<div.stButton>button{min-height:48px;fony-size:1.05rem;}
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea{font-size:1.05rem;}
.big-num{font-size:2rem;font-weight:700;text-align:center;}
.card{background:#f5f7ff;border-radius:12px;padding:16px;text-align:center;}
</style>""", unsafe_allow_html=True)
st.sidebar.title("WIN CRM")
page = st.sidebar.radio("Menu", ["Dashboard", "Clients", "Messaging", "Plans & Pricing", "Export & Backup"]
)
COVERAGE = ["Confirmed", "Peding", "Unavailable"]
STATUS = ["Pending", "Done", "No Answer", "Closed"]
 # --------- 1. DASHBOARD ----------

 if page.startswith("\U0001F3E0"):
    st.title("Dashboard")
    clients = q("SELECT * FROM clients")
    total = len(clients)
    confirmed = sum(1 for c in clients if c["coverage"].startswith("Confirmed"))
    closed = sum(1 for c in clients if c["status"] == "Closed")
    pending_fu = q("SELECT COUNT(*) n FROM followups WHERE status='Pending'")[0]["n"]
    today = date.today().isoformat()
    todays = q("""SELECT f.*, c.name FROM followups f JOIN clients c ON c.id=f.client_id WHERE f.status='Pending' AND f.fdate<=?""", (today,))

    c1, c2, c3, c4 = st.columns(4)
    for col, val, label, color in [(c1, total, "Total Clients", "gray"), (c2,confirmed,"Coverage Confirmed", "green"), (c3,pending_fu, "Pending Follow-ups", "orange"), (c4,closed,"CLosed Sales", "blue")]:
        col.markdown(f"<div class='card'><div class='big-num' style='color:{color}'>{val}</div)"f"<div>{label}</div></div>", unsafe_allow_html=True)
    st.subheader("Today's Follow-ups")
    if todays:
        df = pd.DataFrame(todays)
        ev = st.data_editor(df[["id", "name", "fdate", "ftime", "status"]], hide_index=True, use_container_width=True, column_config={"status": st.column_config.SelectboxColumn(options=STATUS)})
        for r in ev.to_dict("records"):
            orig = next(x for x in todays if x["id"] == x["id"] == r["id"])
            if r["status"] != orig["status"]:
                ex("UPDATE followups SET status=? WHERE id=?", (r["status"], r["id"]))
        st.info("Change a follow-up's status above to update it instantly.")
    else:
        st.success("No follow-ups due today")
    st.divider()
    if st.button("Quick Add New Client", use_container_width=True, type='primary'):
        st.session_state.goto = "Clients"
        st.session_state.quickadd = True
        st.rerun()

# ---------- 2. CLIENT MANAGEMENT ----------

elif page.startswitch("\U0001f465"):
    st.title("Client Management")
    with st.expander(" Add New Client", expanded=st.session_state.get("quickadd", False)):
        with st.form("add"):
            a, b = st.columns(2)
            name = a.text_input("Full name *")
            phone = a.text_input("Phone / WhatsApp *")
            dni = a.text_input("DNI *")
            email = b.text_input("Email")
            district = b.text_input("District *")
            plan = b.selectbox("Plan interest", ["—"]+ plans)
            address = st.text_input("Address notes")
            cov = st.selectbox("Coverage status", COVERAGE)
            notes = st.text_area("Notes")
            if st.form_submit_button("Save Client", use_container_width=True, type="primary"):
                if name and phone and district:
                    ex("""INSERT INTO clients(name,dni,phone,email,district,address,coverage,coverage_date,plan,notes,created)VALUES(?,?,?,?,?,?,?,?,?,?,?)""", (name, dni, phone, email, district, address, cov, date.today().isoformat(), plan, notes, datetime.now().isoformat()))
                    st.success("Client saved!")
                    st.session_state.quickadd = False
                    st.rerun()
                else:
                    st.error("Name, phone and district are required.")
    
    st.subheader(" Search & Filter")
    f1, f2, f3 = st.columns(3)
    s = f1.text_input("Search name / phone")
    d = f1.text_input("District")
    cf = f3.selectbox("Coverage", ["ALL"] + COVERAGE)
    pf = st.selectbox("Plan interest", ["ALL", "—"]+ plans)

    sql, p = "SELECT * FROM clients WHERE status='Active'", []
    if s: sql += " AND (name LIKE ? OR phone LIKE ?)"; p += [f"%{s}%"]*2
    if d: sql += " AND district LIKE ?"; p.append(f"%{d}%")
    if pf not in ("ALL", "—"): sql += "AND plan=?; p.append(pf)
    rows = q(sql, tuple(p))
    st.write(f"**{len(rows)} client(s) found**")

    for c in rows:
        badge = {"Confirmed": "\U0001F7E2", "Pending": "\U0001F552", "Unavailable": "\U0001F534"}[c["coverage"]]
        with st.expander(f"{badge} {c['name']} — {c['phone']} ({c ['district']})"):
            cid = c["id"]
            t1, t2 = st.tabs(["Edit", "History & Follow-ups"])
            with t1:
                with st.form(f"e{cid}"):
                    r1, r2 = st.columns(2)
                    nname = r2.text_input("Name", c["name"])
                    nphone = r1.text_input("Phone", c["phone"])
                    ndni = r1.text_input("DNI", c["dni"])
                    nemail = r2.text_input("Email", c["email"])
                    ndist = r2.text_input("District", c["district"])
                    nplan = r2.selectbox("Plan", ["—"] +  plans, index=(plans.index(c["plan"])+ 1 if c ["plan"]in plans else 0)
                    naddr = st.text_input("Address", c ["address"])
                    ncov = st.selectbox("Coverage", COVERAGE, index=COVERAGE.index(c["coverage"]))
                    nstat = st.selectbox("Sales status", ["Active", "Closed", "Archived"], index =["Active", "Closed", "Archived"].index(c["status"]))
                    nnotes = st.text_area("Notes", c["notes"])
                    if st.form_submit_button("Update"):
                        ex("""UPDATE clients SET name=?, phone=?, dni=?, email=?,district=?, address=?, coverage=?, coverage_date=CASE WHEN coverage=? THEN coverage_date ELSE ? END, plan=?, notes=?, status=? WHERE id=?""", (nname,nphone,ndni,nemail,ndist,naddr,ncov,c["coverage"], date.today().isoformat(),nplan,nnotes,nstat,cid))
                        st.return()
                if st.button(f"Delete permanently". key=f"d{cid}"):
                    ex("DELETE FROM clients WHERE id=?", (cid,))
                    ex("DELETE FROM comms WHERE client_id=?", (cid,))
                    ex("DELETE FROM followups WHERE client_id=?", (cid,))
                    st.rerun()
            with t2:
                for m in q("SELECT * FROM comms WHERE client_id=? ORDER BY ts DESC", (cid,)):


                 
