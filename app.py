import streamlit as st
from supabase import create_client, Client
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    # Try fetching from Streamlit secrets first (for cloud deployment), then fallback to local os environment variables
    url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        st.error("Supabase URL or Key is missing. Please check your .env file or Streamlit secrets.")
        st.stop()
    return create_client(url, key)

supabase: Client = init_supabase()

def fetch_data(table_name):
    try:
        response = supabase.table(table_name).select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def delete_record(table_name, record_id):
    try:
        supabase.table(table_name).delete().eq("id", record_id).execute()
        st.success("Record deleted successfully!")
    except Exception as e:
        st.error(f"Error deleting record: {e}")

st.set_page_config(page_title="Hotel Database", page_icon="🏨", layout="wide")

st.title("Hotel Database Management 🏨")

# Sidebar navigation
page = st.sidebar.selectbox("Navigate", ["Guests", "Staff", "Kitchen", "Suppliers", "Services"])

if page == "Guests":
    st.header("Guest Management 🛏️")
    
    # View Data
    st.subheader("Current Guests")
    df_guests = fetch_data("guests")
    if not df_guests.empty:
        # Reorder columns for better display
        cols = ['id', 'first_name', 'last_name', 'email', 'phone', 'check_in_date', 'check_out_date', 'room_number']
        # only keep existing columns in case schema hasn't fully applied
        cols = [c for c in cols if c in df_guests.columns]
        st.dataframe(df_guests[cols], use_container_width=True)
    else:
        st.info("No guests found.")
        
    # Add Data
    st.subheader("Add New Guest")
    with st.form("add_guest_form"):
        col1, col2 = st.columns(2)
        first_name = col1.text_input("First Name")
        last_name = col2.text_input("Last Name")
        email = col1.text_input("Email")
        phone = col2.text_input("Phone")
        check_in = col1.date_input("Check-in Date")
        check_out = col2.date_input("Check-out Date")
        room_number = st.text_input("Room Number")
        
        submitted = st.form_submit_button("Add Guest")
        if submitted:
            data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "check_in_date": str(check_in),
                "check_out_date": str(check_out),
                "room_number": room_number
            }
            supabase.table("guests").insert(data).execute()
            st.success("Guest added!")
            st.rerun()

    # Delete Data
    if not df_guests.empty:
        st.subheader("Delete Guest")
        guest_to_delete = st.selectbox("Select guest to delete", df_guests['id'].tolist(), format_func=lambda x: f"{df_guests[df_guests['id'] == x]['first_name'].values[0]} {df_guests[df_guests['id'] == x]['last_name'].values[0]} ({x})")
        if st.button("Delete Guest"):
            delete_record("guests", guest_to_delete)
            st.rerun()

elif page == "Staff":
    st.header("Staff Management 👨‍💼")
    
    # View Data
    st.subheader("Current Staff")
    df_staff = fetch_data("staff")
    if not df_staff.empty:
        cols = ['id', 'first_name', 'last_name', 'role', 'phone', 'hire_date']
        cols = [c for c in cols if c in df_staff.columns]
        st.dataframe(df_staff[cols], use_container_width=True)
    else:
        st.info("No staff found.")
        
    # Add Data
    st.subheader("Add New Staff")
    with st.form("add_staff_form"):
        col1, col2 = st.columns(2)
        first_name = col1.text_input("First Name")
        last_name = col2.text_input("Last Name")
        role = col1.text_input("Role (e.g., Manager, Housekeeper)")
        phone = col2.text_input("Phone")
        hire_date = st.date_input("Hire Date")
        
        submitted = st.form_submit_button("Add Staff")
        if submitted:
            data = {
                "first_name": first_name,
                "last_name": last_name,
                "role": role,
                "phone": phone,
                "hire_date": str(hire_date)
            }
            supabase.table("staff").insert(data).execute()
            st.success("Staff added!")
            st.rerun()
            
    # Delete Data
    if not df_staff.empty:
        st.subheader("Delete Staff")
        staff_to_delete = st.selectbox("Select staff to delete", df_staff['id'].tolist(), format_func=lambda x: f"{df_staff[df_staff['id'] == x]['first_name'].values[0]} {df_staff[df_staff['id'] == x]['last_name'].values[0]} ({x})")
        if st.button("Delete Staff"):
            delete_record("staff", staff_to_delete)
            st.rerun()

elif page == "Kitchen":
    st.header("Kitchen Inventory 🍳")
    
    # View Data
    st.subheader("Current Inventory")
    df_kitchen = fetch_data("kitchen")
    if not df_kitchen.empty:
        cols = ['id', 'item_name', 'quantity', 'unit', 'expiry_date']
        cols = [c for c in cols if c in df_kitchen.columns]
        st.dataframe(df_kitchen[cols], use_container_width=True)
    else:
        st.info("No kitchen items found.")
        
    # Add Data
    st.subheader("Add Kitchen Item")
    with st.form("add_kitchen_form"):
        item_name = st.text_input("Item Name")
        col1, col2 = st.columns(2)
        quantity = col1.number_input("Quantity", min_value=0.0, format="%.2f")
        unit = col2.text_input("Unit (e.g., kg, liters, boxes)")
        expiry_date = st.date_input("Expiry Date")
        
        submitted = st.form_submit_button("Add Item")
        if submitted:
            data = {
                "item_name": item_name,
                "quantity": quantity,
                "unit": unit,
                "expiry_date": str(expiry_date)
            }
            supabase.table("kitchen").insert(data).execute()
            st.success("Item added!")
            st.rerun()
            
    # Delete Data
    if not df_kitchen.empty:
        st.subheader("Delete Item")
        item_to_delete = st.selectbox("Select item to delete", df_kitchen['id'].tolist(), format_func=lambda x: f"{df_kitchen[df_kitchen['id'] == x]['item_name'].values[0]} ({x})")
        if st.button("Delete Item"):
            delete_record("kitchen", item_to_delete)
            st.rerun()

elif page == "Suppliers":
    st.header("Supplier Management 🚚")
    
    # View Data
    st.subheader("Current Suppliers")
    df_suppliers = fetch_data("suppliers")
    if not df_suppliers.empty:
        cols = ['id', 'name', 'contact_person', 'phone', 'email', 'supplied_items']
        cols = [c for c in cols if c in df_suppliers.columns]
        st.dataframe(df_suppliers[cols], use_container_width=True)
    else:
        st.info("No suppliers found.")
        
    # Add Data
    st.subheader("Add Supplier")
    with st.form("add_supplier_form"):
        name = st.text_input("Supplier Name")
        contact_person = st.text_input("Contact Person")
        col1, col2 = st.columns(2)
        phone = col1.text_input("Phone")
        email = col2.text_input("Email")
        supplied_items = st.text_area("Supplied Items (Comma separated)")
        
        submitted = st.form_submit_button("Add Supplier")
        if submitted:
            data = {
                "name": name,
                "contact_person": contact_person,
                "phone": phone,
                "email": email,
                "supplied_items": supplied_items
            }
            supabase.table("suppliers").insert(data).execute()
            st.success("Supplier added!")
            st.rerun()
            
    # Delete Data
    if not df_suppliers.empty:
        st.subheader("Delete Supplier")
        supplier_to_delete = st.selectbox("Select supplier to delete", df_suppliers['id'].tolist(), format_func=lambda x: f"{df_suppliers[df_suppliers['id'] == x]['name'].values[0]} ({x})")
        if st.button("Delete Supplier"):
            delete_record("suppliers", supplier_to_delete)
            st.rerun()

elif page == "Services":
    st.header("Hotel Services 🛎️")
    
    # View Data
    st.subheader("Current Services")
    df_services = fetch_data("services")
    if not df_services.empty:
        cols = ['id', 'service_name', 'description', 'price']
        cols = [c for c in cols if c in df_services.columns]
        st.dataframe(df_services[cols], use_container_width=True)
    else:
        st.info("No services found.")
        
    # Add Data
    st.subheader("Add Service")
    with st.form("add_service_form"):
        service_name = st.text_input("Service Name (e.g., Spa, Gym)")
        description = st.text_area("Description")
        price = st.number_input("Price", min_value=0.0, format="%.2f")
        
        submitted = st.form_submit_button("Add Service")
        if submitted:
            data = {
                "service_name": service_name,
                "description": description,
                "price": price
            }
            supabase.table("services").insert(data).execute()
            st.success("Service added!")
            st.rerun()
            
    # Delete Data
    if not df_services.empty:
        st.subheader("Delete Service")
        service_to_delete = st.selectbox("Select service to delete", df_services['id'].tolist(), format_func=lambda x: f"{df_services[df_services['id'] == x]['service_name'].values[0]} ({x})")
        if st.button("Delete Service"):
            delete_record("services", service_to_delete)
            st.rerun()
