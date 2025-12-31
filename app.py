import streamlit as st
import json
from datetime import date

st.set_page_config(page_title="Latihan Paskibra", layout="wide")

# ================= UTIL =================
def load(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return []

def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

users = load("users.json")
anggota = load("anggota.json")
latihan = load("latihan.json")
absensi = load("absensi.json")

# ================= LOGIN =================
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Login Pelatih")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        for user in users:
            if user["username"] == u and user["password"] == p:
                st.session_state.login = True
                st.session_state.user = user
                st.rerun()
        st.error("Username atau password salah")

    st.stop()

# ================= SIDEBAR =================
st.sidebar.title("📘 Menu")
menu = st.sidebar.radio(
    "Pilih Menu",
    ["Beranda", "Program Latihan", "Data Anggota", "Absensi", "Rekap"]
)

if st.sidebar.button("Logout"):
    st.session_state.login = False
    st.rerun()

# ================= BERANDA =================
if menu == "Beranda":
    st.title("🏠 Sistem Latihan Paskibra")
    st.info("Aplikasi manajemen latihan Paskibra berbasis web")

# ================= PROGRAM LATIHAN =================
elif menu == "Program Latihan":
    st.title("📋 Program Latihan")

    with st.form("latihan"):
        nama = st.text_input("Nama Latihan")
        materi = st.text_area("Materi")
        tgl = st.date_input("Tanggal", value=date.today())
        simpan = st.form_submit_button("Simpan")

        if simpan:
            latihan.append({
                "id": len(latihan)+1,
                "nama": nama,
                "materi": materi,
                "tanggal": str(tgl)
            })
            save("latihan.json", latihan)
            st.success("Latihan ditambahkan")

    st.divider()

    for l in latihan:
        with st.expander(f"{l['nama']} ({l['tanggal']})"):
            st.write(l["materi"])

# ================= DATA ANGGOTA =================
elif menu == "Data Anggota":
    st.title("👥 Data Anggota")

    with st.form("anggota"):
        nama = st.text_input("Nama")
        kelas = st.text_input("Kelas")
        jabatan = st.selectbox("Jabatan", ["Pasukan", "Danton", "Pengurus"])
        simpan = st.form_submit_button("Tambah")

        if simpan:
            anggota.append({
                "id": len(anggota)+1,
                "nama": nama,
                "kelas": kelas,
                "jabatan": jabatan
            })
            save("anggota.json", anggota)
            st.success("Anggota ditambahkan")

    st.divider()
    st.table(anggota)

# ================= ABSENSI =================
elif menu == "Absensi":
    st.title("✅ Absensi Latihan")

    if not latihan:
        st.warning("Belum ada latihan")
    else:
        pilih = st.selectbox(
            "Pilih Latihan",
            latihan,
            format_func=lambda x: f"{x['nama']} ({x['tanggal']})"
        )

        for a in anggota:
            hadir = st.checkbox(a["nama"], key=a["id"])
            if hadir:
                absensi.append({
                    "latihan": pilih["id"],
                    "anggota": a["nama"],
                    "status": "Hadir"
                })

        if st.button("Simpan Absensi"):
            save("absensi.json", absensi)
            st.success("Absensi tersimpan")

# ================= REKAP =================
elif menu == "Rekap":
    st.title("📊 Rekap Kehadiran")
    st.table(absensi)
