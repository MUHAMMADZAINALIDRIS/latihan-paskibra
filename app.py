import streamlit as st
import json
from datetime import date

DATA_FILE = "data_latihan.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

st.set_page_config(page_title="Program Latihan Paskibra", layout="wide")

st.title("📋 Program Latihan Paskibra")

menu = st.sidebar.selectbox("Menu", ["Input Latihan", "Data Latihan"])

data = load_data()

# ================= INPUT =================
if menu == "Input Latihan":
    st.subheader("➕ Tambah Latihan")

    nama = st.text_input("Nama Kegiatan")
    materi = st.text_area("Materi Latihan")
    tanggal = st.date_input("Tanggal", value=date.today())

    if st.button("Simpan"):
        data.append({
            "nama": nama,
            "materi": materi,
            "tanggal": str(tanggal)
        })
        save_data(data)
        st.success("Latihan berhasil disimpan")

# ================= DATA =================
else:
    st.subheader("📊 Data Latihan")

    for i, d in enumerate(data):
        with st.expander(f"{d['nama']} ({d['tanggal']})"):
            st.write(d["materi"])
            if st.button("🗑 Hapus", key=i):
                data.pop(i)
                save_data(data)
                st.experimental_rerun()
