import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Tibbiyot Hisobot Dasturi", layout="wide")

st.title("Tibbiyot Markazi: Innovatsion Hisobot Platformasi")

# Foydalanuvchi roli bo'yicha login
users = {
    "registrator": "registrator123",
    "gaznachi": "gazna123",
    "hamshira": "hamshira123",
    "rahbar": "rahbar123"
}

st.sidebar.header("Foydalanuvchi kirishi")
username = st.sidebar.selectbox("Foydalanuvchini tanlang", list(users.keys()))
password = st.sidebar.text_input("Parol", type="password")

if password != users[username]:
    st.warning("Noto'g'ri parol")
    st.stop()

st.success(f"Xush kelibsiz, {username.title()}!")

# Fayl yuklash
uploaded_file = st.file_uploader("Excel faylni yuklang", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.subheader("Asosiy Ma'lumotlar")
    if username in ["rahbar", "registrator"]:
        st.dataframe(df)

    df["Yotgan Sana"] = pd.to_datetime(df["Yotgan Sana"])
    df["Chiqarilgan Sana"] = pd.to_datetime(df["Chiqarilgan Sana"])

    df["Hafta"] = df["Yotgan Sana"].dt.isocalendar().week
    df["Oy"] = df["Yotgan Sana"].dt.month
    df["Yil"] = df["Yotgan Sana"].dt.year

    st.sidebar.header("Filterlar")
    yil = st.sidebar.selectbox("Yilni tanlang", sorted(df["Yil"].unique()))
    oy = st.sidebar.selectbox("Oyni tanlang", sorted(df["Oy"].unique()))
    bolimlar = st.sidebar.multiselect("Bo'lim(lar)ni tanlang", df["Bo'lim"].unique(), default=df["Bo'lim"].unique())
    shifokorlar = st.sidebar.multiselect("Shifokor(lar)ni tanlang", df["Shifokor"].unique(), default=df["Shifokor"].unique())

    filtr = (df["Yil"] == yil) & (df["Oy"] == oy) & df["Bo'lim"].isin(bolimlar) & df["Shifokor"].isin(shifokorlar)
    filtered_df = df[filtr]

    if username in ["rahbar", "registrator"]:
        st.subheader("Filtrlangan Ma'lumotlar")
        st.dataframe(filtered_df)

    if username in ["rahbar", "gaznachi"]:
        st.subheader("Bo'limlar bo'yicha rentabellik")
        rentabellik = filtered_df.groupby("Bo'lim").agg({
            "Tushum (so'm)": "sum",
            "Chiqim (so'm)": "sum"
        })
        rentabellik["Rentabellik (%)"] = ((rentabellik["Tushum (so'm)"] - rentabellik["Chiqim (so'm)"]) / rentabellik["Chiqim (so'm)"] * 100).round(2)
        st.dataframe(rentabellik)

    if username in ["rahbar"]:
        st.subheader("Shifokorlar samaradorligi")
        samaradorlik = filtered_df.groupby("Shifokor").agg({
            "ID": "count",
            "Tushum (so'm)": "sum"
        }).rename(columns={"ID": "Bemorlar soni"})
        samaradorlik["O'rtacha tushum"] = (samaradorlik["Tushum (so'm)"] / samaradorlik["Bemorlar soni"]).round(2)
        st.dataframe(samaradorlik)

        st.subheader("Vizualizatsiya")
        col1, col2 = st.columns(2)

        with col1:
            st.bar_chart(rentabellik["Rentabellik (%)"])

        with col2:
            st.bar_chart(samaradorlik["O'rtacha tushum"])

    if username in ["hamshira"]:
        st.info("Sizga bemor ro'yxatlari va tibbiy ko'rsatkichlar bilan ishlash imkoniyati berilgan (bu funksiya hali qo‘shilmagan).")
else:
    st.info("Iltimos, Excel faylni yuklang.")
