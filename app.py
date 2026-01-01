import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date
import pandas as pd

st.set_page_config("Sistem Latihan Paskibra", layout="wide")

# ======================================================
# GOOGLE SHEET
# ======================================================
def connect_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )
    client = gspread.authorize(creds)
    return client.open("DB_Latihan_Paskibra")


def get_data(sheet_name):
    sheet = connect_sheet()
    return sheet.worksheet(sheet_name).get_all_records()

def save_data(sheet_name, data):
    ws = connect_sheet().worksheet(sheet_name)
    ws.clear()
    ws.append_row(list(data[0].keys()))
    for row in data:
        ws.append_row(list(row.values()))

# ================= LOGIN =================
if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.user = None

if not st.session_state.login:
    st.title("Login Aplikasi Latihan Paskibra")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = get_data("users")

        for user in users:
            u = str(user.get("username", "")).strip()
            p = str(user.get("password", "")).strip()
            r = str(user.get("role", "")).strip().lower()

            if u == username.strip() and p == password.strip():
                st.session_state.login = True
                st.session_state.user = {
                    "username": u,
                    "role": r
                }
                st.success("Login berhasil")
                st.rerun()
                break
        else:
            st.error("Username atau password salah")

    st.stop()


# ======================================================
# SIDEBAR & MENU (TAHAP 1)
# ======================================================
role = st.session_state.user["role"]

if role in ["admin", "pelatih"]:
    menu = st.sidebar.radio("📘 Menu", [
        "🏠 Beranda",
        "📋 Program Latihan",
        "👥 Data Anggota",
        "✅ Absensi",
        "📊 Rekap",
        "🚪 Logout"
    ])
else:
    menu = st.sidebar.radio("📘 Menu", [
        "🏠 Beranda",
        "✅ Absensi",
        "📊 Rekap",
        "🚪 Logout"
    ])

# ======================================================
# LOGOUT
# ======================================================
if menu == "🚪 Logout":
    st.session_state.login = False
    st.session_state.user = None
    st.success("Logout berhasil")
    st.stop()

# ======================================================
# 🏠 BERANDA
# ======================================================
if menu == "🏠 Beranda":
    st.title("🏠 Sistem Manajemen Latihan Paskibra")
    st.write(f"Halo **{st.session_state.user['username']}**")
    st.info("Aplikasi pencatatan latihan, absensi, dan evaluasi Paskibra")

# ======================================================
# 📋 PROGRAM LATIHAN (TAHAP 3 - DASAR)
# ======================================================
elif menu == "📋 Program Latihan":
    if role not in ["admin", "pelatih"]:
        st.error("Akses ditolak")
        st.stop()

    st.title("📋 Program Latihan")
    latihan = get_data("latihan")

    with st.form("tambah_latihan"):
        nama = st.text_input("Nama Latihan")
        materi = st.selectbox("Materi", ["PBB", "PBBT", "Formasi", "Fisik"])
        durasi = st.number_input("Durasi (menit)", 30)
        catatan = st.text_area("Catatan Pelatih")
        tgl = st.date_input("Tanggal", date.today())
        simpan = st.form_submit_button("Simpan")

        if simpan:
            latihan.append({
                "id": len(latihan) + 1,
                "tanggal": str(tgl),
                "materi": materi,
                "durasi": durasi,
                "catatan": catatan
            })
            save_data("latihan", latihan)
            st.success("Latihan ditambahkan")

    st.table(latihan)

# ======================================================
# 👥 DATA ANGGOTA (TAHAP 4)
# ======================================================
elif menu == "👥 Data Anggota":
    if role not in ["admin", "pelatih"]:
        st.error("Akses ditolak")
        st.stop()

    st.title("👥 Data Anggota")
    anggota = get_data("anggota")

    with st.form("tambah_anggota"):
        nama = st.text_input("Nama")
        kelas = st.text_input("Kelas / Angkatan")
        jabatan = st.selectbox("Jabatan", ["Pasukan", "Danton", "Pengurus"])
        status = st.selectbox("Status", ["Aktif", "Nonaktif"])
        simpan = st.form_submit_button("Tambah")

        if simpan:
            anggota.append({
                "id": len(anggota) + 1,
                "nama": nama,
                "kelas": kelas,
                "jabatan": jabatan,
                "status": status
            })
            save_data("anggota", anggota)
            st.success("Anggota ditambahkan")

    st.table(anggota)

# ======================================================
# ✅ ABSENSI (TAHAP 5)
# ======================================================
elif menu == "✅ Absensi":
    st.title("✅ Absensi Latihan")

    latihan = get_data("latihan")
    anggota = get_data("anggota")
    absensi = get_data("absensi")

    if not latihan:
        st.warning("Belum ada latihan")
        st.stop()

    pilih = st.selectbox("Pilih Latihan", latihan, format_func=lambda x: f"{x['tanggal']} - {x['materi']}")

    for a in anggota:
        status = st.radio(
            a["nama"],
            ["Hadir", "Izin", "Alfa"],
            horizontal=True,
            key=a["id"]
        )
        absensi.append({
            "latihan_id": pilih["id"],
            "nama": a["nama"],
            "status": status
        })

    if st.button("Simpan Absensi"):
        save_data("absensi", absensi)
        st.success("Absensi tersimpan")

# ======================================================
# 📊 REKAP (TAHAP 6)
# ======================================================
elif menu == "📊 Rekap":
    st.title("📊 Rekap Kehadiran")

    latihan = get_data("latihan")
    absensi = get_data("absensi")

    if not latihan or not absensi:
        st.info("Data latihan atau absensi belum lengkap")
    else:
        df_latihan = pd.DataFrame(latihan)
        df_absensi = pd.DataFrame(absensi)

        # mapping id_latihan -> tanggal & materi
        latihan_map = {
    str(l["id"]): l["tanggal"]
    for l in latihan
}

rekap = []

for a in absensi:
    latihan_id = str(a["latihan_id"])
    rekap.append({
        "Tanggal": latihan_map.get(latihan_id, "-"),
        "Anggota": a["anggota"],
        "Status": a["status"]
    })

st.table(rekap)


