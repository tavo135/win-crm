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
it "auth" not in st.session_state:
    st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h2 style='text-align:center'>\U0001F4F6 WIN - CRM</h2>", unsafe_allow_html=True)
    pw = st.text_input("Enter password", type="password")
    if st.button("Login", type="primary", use_contatiner_with=True):
        if pw == APP_PASWORD:
            st.session_state.auth = True
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
def T_plans(n, d): return f"Hola {n}! Estos son los planes WIN para {d}:\n\n{plans_text()}"
def T_close(n, d): return (f"Hola {n}! confirmamos la instalación de tu plan"
    f"{p}. Nuestro técnico te contactará para coordinar la fecha. ¡Bienvenido a WIN!")
def T_thanks(n): return (f"Gracias {n} por confiar en WIN !"
    "Cualquier consulta, estamos para ayudarte. ¡Que disfrutes tu nueva fibra!")

TEMPLATES = [
    ("Initial outreach (S/1.00 promo)", T_initial),
    ("No answer follow-up", T_noanswer),
    ("Full plan details", T_plans),
    ("Closing — confirm installation", lambda n, d: T_close(n, d)),
    ("Thank you — sale confirmed", lambda n, d: T_thanks(n)),
]


