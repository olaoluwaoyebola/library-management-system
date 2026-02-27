import requests
import streamlit as st

DEFAULT_API = "http://127.0.0.1:8000"
DEFAULT_SECTIONS = [
    "SCIENCES",
    "ARTS",
    "SOCIALS",
    "ECONOMICS",
    "RELIGION",
    "GENERAL STUDIES",
]


st.set_page_config(page_title="Library Management System", layout="wide")
st.title("Library Management System")
st.caption("FastAPI backend + Streamlit frontend")


def api_request(method: str, base_url: str, path: str, **kwargs):
    url = f"{base_url}{path}"
    try:
        response = requests.request(method, url, timeout=15, **kwargs)
    except requests.RequestException as exc:
        st.error(f"API request failed: {exc}")
        return None

    try:
        payload = response.json() if response.text else {}
    except ValueError:
        payload = {"detail": response.text}

    if response.status_code >= 400:
        message = payload.get("detail", "Request failed")
        st.error(f"{response.status_code}: {message}")
        return None
    return payload


def render_table(rows, empty_message: str = "No records found.") -> None:
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info(empty_message)


api_base = st.sidebar.text_input("Backend URL", value=DEFAULT_API).rstrip("/")
menu_placeholder = ["Dashboard", "Books", "Students", "Borrow Book", "Return Book", "Defaulters"]

health = api_request("GET", api_base, "/health")
if not health:
    st.stop()

sections = api_request("GET", api_base, "/sections") or []
if not sections:
    # Fall back to required section names so UI remains usable.
    sections = [{"id": 0, "name": name, "book_count": 0} for name in DEFAULT_SECTIONS]

section_names = [section["name"] for section in sections]
section_map = {section["name"]: section["id"] for section in sections}
sections_ready = all(section_map[name] > 0 for name in section_names)
menu = st.sidebar.radio("Navigation", menu_placeholder + [f"Section: {name}" for name in section_names])


if menu == "Dashboard":
    dashboard = api_request("GET", api_base, "/dashboard")
    if dashboard:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Sections", dashboard["total_sections"])
        col2.metric("Books (Titles)", dashboard["total_books"])
        col3.metric("Students", dashboard["total_students"])
        col4.metric("Active Borrows", dashboard["active_borrows"])

        col5, col6, col7, col8 = st.columns(4)
        col5.metric("Available Copies", dashboard["available_books"])
        col6.metric("Out of Stock Titles", dashboard["out_of_stock_books"])
        col7.metric("Overdue Borrows", dashboard["overdue_borrows"])
        col8.metric("Outstanding Fines", f"#{dashboard['outstanding_fines']:.2f}")

        st.subheader("Current Borrowed Books")
        active_borrows = api_request("GET", api_base, "/borrows", params={"only_active": True}) or []
        render_table(active_borrows, "No active borrows yet.")


elif menu == "Books":
    st.subheader("Book Inventory")
    tab_add, tab_inventory = st.tabs(["Add Book", "View / Restock"])

    with tab_add:
        if not sections_ready:
            st.warning("Sections are not synced from the API yet. Retry when backend is ready.")
        with st.form("add_book_form", clear_on_submit=True):
            title = st.text_input("Title")
            author = st.text_input("Author")
            version = st.text_input("Version / Edition")
            cost = st.number_input("Cost", min_value=0.0, step=100.0, format="%.2f")
            total_copies = st.number_input("Total Copies", min_value=1, step=1)
            section_name = st.selectbox("Section", options=section_names)
            submitted = st.form_submit_button("Add Book", disabled=not sections_ready)

            if submitted:
                payload = {
                    "title": title,
                    "author": author,
                    "version": version,
                    "cost": float(cost),
                    "total_copies": int(total_copies),
                    "section_id": section_map[section_name],
                }
                created = api_request("POST", api_base, "/books", json=payload)
                if created:
                    st.success("Book added successfully.")

    with tab_inventory:
        col_filter1, col_filter2 = st.columns(2)
        section_filter = col_filter1.selectbox("Filter by Section", options=["ALL"] + section_names)
        include_out_of_stock = col_filter2.checkbox("Include Out of Stock", value=True)

        params = {"include_out_of_stock": include_out_of_stock}
        if section_filter != "ALL" and section_map[section_filter] > 0:
            params["section_id"] = section_map[section_filter]
        books = api_request("GET", api_base, "/books", params=params) or []

        render_table(books, "No books found for selected filter.")

        if books:
            with st.expander("Restock Book"):
                options = {f"#{book['id']} - {book['title']} ({book['version']})": book["id"] for book in books}
                selected = st.selectbox("Book", options=list(options.keys()))
                add_copies = st.number_input("Copies to Add", min_value=1, step=1)

                if st.button("Restock Selected Book"):
                    book_id = options[selected]
                    updated = api_request(
                        "PATCH",
                        api_base,
                        f"/books/{book_id}/stock",
                        json={"added_copies": int(add_copies)},
                    )
                    if updated:
                        st.success("Book stock updated.")
                        st.rerun()


elif menu == "Students":
    st.subheader("Student Records")
    col_form, col_list = st.columns([1, 1.2])

    with col_form:
        with st.form("add_student_form", clear_on_submit=True):
            full_name = st.text_input("Full Name")
            matric_number = st.text_input("Matric Number")
            email = st.text_input("Email")
            department = st.text_input("Department (optional)")
            submitted = st.form_submit_button("Add Student")
            if submitted:
                payload = {
                    "full_name": full_name,
                    "matric_number": matric_number,
                    "email": email,
                    "department": department or None,
                }
                created = api_request("POST", api_base, "/students", json=payload)
                if created:
                    st.success("Student added successfully.")
                    st.rerun()

    with col_list:
        students = api_request("GET", api_base, "/students") or []
        render_table(students, "No students registered yet.")


elif menu == "Borrow Book":
    st.subheader("Borrow a Book")
    students = api_request("GET", api_base, "/students") or []
    books = api_request("GET", api_base, "/books", params={"include_out_of_stock": False}) or []

    if not students:
        st.warning("Add at least one student before borrowing.")
    elif not books:
        st.warning("No available books to borrow.")
    else:
        student_options = {
            f"#{student['id']} - {student['full_name']} ({student['matric_number']})": student["id"]
            for student in students
        }
        book_options = {
            f"#{book['id']} - {book['title']} [{book['section_name']}] (Avail: {book['available_copies']})": book["id"]
            for book in books
        }

        with st.form("borrow_form"):
            selected_student = st.selectbox("Student", options=list(student_options.keys()))
            selected_book = st.selectbox("Book", options=list(book_options.keys()))
            lend_days = st.number_input("Lend Days", min_value=1, max_value=30, value=7, step=1)
            submitted = st.form_submit_button("Borrow Book")

            if submitted:
                payload = {
                    "student_id": student_options[selected_student],
                    "book_id": book_options[selected_book],
                    "lend_days": int(lend_days),
                }
                borrowed = api_request("POST", api_base, "/borrow", json=payload)
                if borrowed:
                    st.success(
                        f"Book borrowed. Due date: {borrowed['due_at']}. "
                        f"Status: {borrowed['status']}"
                    )
                    st.rerun()

    st.markdown("### Active Borrows")
    active = api_request("GET", api_base, "/borrows", params={"only_active": True}) or []
    render_table(active, "No active borrow records.")


elif menu == "Return Book":
    st.subheader("Return Borrowed Book")
    active_borrows = api_request("GET", api_base, "/borrows", params={"only_active": True}) or []
    if not active_borrows:
        st.info("There are no active borrows to return.")
    else:
        options = {
            (
                f"Record #{record['id']} | {record['student_name']} -> {record['book_title']} "
                f"| Due: {record['due_at']} | Status: {record['status']}"
            ): record["id"]
            for record in active_borrows
        }
        selected = st.selectbox("Select Borrow Record", options=list(options.keys()))
        if st.button("Return Book"):
            borrow_id = options[selected]
            returned = api_request("POST", api_base, f"/return/{borrow_id}")
            if returned:
                st.success(
                    f"Book returned. Fine: #{returned['fine_amount']:.2f}. "
                    f"Returned at: {returned['returned_at']}"
                )
                st.rerun()


elif menu == "Defaulters":
    st.subheader("Defaulters and Outstanding Fines")
    defaulters = api_request("GET", api_base, "/defaulters") or []
    total_outstanding = sum(item.get("outstanding_fine", 0.0) for item in defaulters)
    st.metric("Total Outstanding Fine", f"#{total_outstanding:.2f}")
    render_table(defaulters, "No defaulters currently.")


else:
    section_name = menu.split("Section: ", 1)[1]
    section_id = section_map.get(section_name, 0)
    st.subheader(f"{section_name} Section")

    params = {"include_out_of_stock": True}
    if section_id > 0:
        params["section_id"] = section_id

    books = api_request(
        "GET",
        api_base,
        "/books",
        params=params,
    ) or []

    col_a, col_b, col_c = st.columns(3)
    total_titles = len(books)
    available_titles = sum(1 for book in books if book["available_copies"] > 0)
    out_of_stock_titles = total_titles - available_titles

    col_a.metric("Titles in Section", total_titles)
    col_b.metric("Available Titles", available_titles)
    col_c.metric("Out of Stock Titles", out_of_stock_titles)

    render_table(books, f"No books in {section_name} yet.")
