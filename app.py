import streamlit as st
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Latihan Paskibra", layout="wide")

# ================= GOOGLE SHEET =================
def connect_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"],
        scope
    )
    client = gspread.authorize(creds)
    return client.open("DB_Latihan_Paskibra")

def get_users():
    sheet = connect_sheet()
    ws = sheet.worksheet("users")
    return ws.get_all_records()

def get_ws_data(sheet_name):
    sheet = connect_sheet()
    ws = sheet.worksheet(sheet_name)
    return ws, ws.get_all_records()

def update_ws_data(sheet_name, row_values):
    ws = connect_sheet().worksheet(sheet_name)
    ws.append_row(row_values)

# ================= LOGIN =================
if "login" not in st.session_state:
    st.session_state.login = False
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.login:
    st.title("Login Aplikasi Latihan Paskibra")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = get_users()
        login_success = False
        for user in users:
            if str(user["username"]).strip() == username.strip() and str(user["password"]).strip() == password.strip():
                st.session_state.login = True
                st.session_state.user = user
                st.success(f"Login berhasil! Halo {username}")
                login_success = True
                st.experimental_rerun()
        if not login_success:
            st.error("Username atau password salah")
    st.stop()

# ================= ROLE & MENU =================
role = st.session_state.user["role"].strip().lower()

if role == "admin":
    menu = st.sidebar.radio(
        "Menu Admin",
        ["Beranda", "Data Anggota", "Program Latihan", "Absensi", "Rekap", "Logout"]
    )
elif role == "anggota":
    menu = st.sidebar.radio(
        "Menu Anggota",
        ["Beranda", "Absensi", "Rekap", "Logout"]
    )

if st.sidebar.button("Logout"):
    st.session_state.login = False
    st.session_state.user = None
    st.experimental_rerun()

# ================= BERANDA =================
if menu == "Beranda":
    st.title("🏠 Sistem Latihan Paskibra")
    ws, data = get_ws_data("anggota")
    st.write("Data anggota dari Google Sheet:")
    st.write(data)
    st.info("Aplikasi manajemen latihan Paskibra berbasis web")

# ================= PROGRAM LATIHAN =================
elif menu == "Program Latihan":
    if role != "admin":
        st.error("❌ Anda tidak memiliki akses ke menu ini")
        st.stop()
    st.title("📋 Program Latihan")
    ws_latihan, latihan = get_ws_data("latihan")
    with st.form("latihan"):
        nama = st.text_input("Nama Latihan")
        materi = st.text_area("Materi")
        tgl = st.date_input("Tanggal", value=date.today())
        simpan = st.form_submit_button("Simpan")
        if simpan:
            update_ws_data("latihan", [len(latihan)+1, nama, materi, str(tgl)])
            st.success("Latihan ditambahkan")

    st.divider()
    ws_latihan, latihan = get_ws_data("latihan")
    for l in latihan:
        with st.expander(f"{l['nama latihan']} ({l['tanggal']})"):
            st.write(l["materi"])

# ================= DATA ANGGOTA =================
elif menu == "Data Anggota":
    if role != "admin":
        st.error("❌ Anda tidak memiliki akses ke menu ini")
        st.stop()
    st.title("👥 Data Anggota")
    ws_anggota, anggota = get_ws_data("anggota")
    with st.form("anggota"):
        nama = st.text_input("Nama")
        kelas = st.text_input("Kelas")
        jabatan = st.selectbox("Jabatan", ["Pasukan", "Danton", "Pengurus"])
        simpan = st.form_submit_button("Tambah")
        if simpan:
            update_ws_data("anggota", [len(anggota)+1, nama, kelas, jabatan])
            st.success("Anggota ditambahkan")

    st.divider()
    ws_anggota, anggota = get_ws_data("anggota")
    st.table(anggota)

# ================= ABSENSI =================
elif menu == "Absensi":
    st.title("✅ Absensi Latihan")
    ws_latihan, latihan = get_ws_data("latihan")
    ws_anggota, anggota = get_ws_data("anggota")
    ws_absensi, absensi = get_ws_data("absensi")

    if not latihan:
        st.warning("Belum ada latihan")
    else:
        pilih = st.selectbox(
            "Pilih Latihan",
            latihan,
            format_func=lambda x: f"{x['nama latihan']} ({x['tanggal']})"
        )
        for a in anggota:
            hadir = st.checkbox(a["nama"], key=a["id"])
            if hadir:
                ws_absensi.append_row([len(absensi)+1, pilih["id"], a["nama"], "Hadir"])
        if st.button("Simpan Absensi"):
            st.success("Absensi tersimpan")

# ================= REKAP =================
elif menu == "Rekap":
    st.title("📊 Rekap Kehadiran")
    ws_absensi, absensi = get_ws_data("absensi")
    st.table(absensi)

# ================= LOGOUT =================
elif menu == "Logout":
    st.session_state.login = False
    st.session_state.user = None
    st.experimental_rerun()
