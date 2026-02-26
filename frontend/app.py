# frontend with streamlit

import streamlit as st
import requests

API = "http://127.0.0.1:8000"

st.title("📚 Library Management System")

menu = st.sidebar.selectbox(
    "Menu",
    [
        "SCIENCES",
        "ARTS",
        "SOCIALS",
        "ECONOMICS",
        "RELIGION",
        "GENERAL STUDIES",
        "Borrow Book",
        "Return Book"
    ]
)

if menu == "Borrow Book":
    user_id = st.number_input("User ID")
    book_id = st.number_input("Book ID")

    if st.button("Borrow"):
        res = requests.post(f"{API}/borrow/{user_id}/{book_id}")
        st.write(res.json())

elif menu == "Return Book":
    borrow_id = st.number_input("Borrow Record ID")

    if st.button("Return"):
        res = requests.post(f"{API}/return/{borrow_id}")
        st.write(res.json())

else:
    st.header(f"{menu} Section")
    st.write("Books display can be added here.")