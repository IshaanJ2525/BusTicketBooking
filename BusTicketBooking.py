import streamlit as st
import datetime
import pandas as pd
import requests
import base64

# --- GitHub Secrets ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_USERNAME = st.secrets["GITHUB_USERNAME"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]
CSV_FILEPATH = "data/tickets.csv"

# --- GitHub API Functions ---

def get_csv_from_github():
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{CSV_FILEPATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        content = base64.b64decode(response.json()["content"]).decode()
        sha = response.json()["sha"]
        df = pd.read_csv(pd.compat.StringIO(content))
        return df, sha
    else:
        return pd.DataFrame(columns=["timestamp", "name", "route", "tickets"]), None

def update_csv_on_github(df, sha=None):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{CSV_FILEPATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    content_str = df.to_csv(index=False)
    encoded_content = base64.b64encode(content_str.encode()).decode()

    payload = {
        "message": "Update ticket CSV",
        "content": encoded_content,
        "branch": "main"
    }

    if sha:
        payload["sha"] = sha

    response = requests.put(url, headers=headers, json=payload)
    return response.status_code in [200, 201]

# --- Load CSV Data ---
if "tickets_df" not in st.session_state:
    df, sha = get_csv_from_github()
    st.session_state.tickets_df = df
    st.session_state.csv_sha = sha

# --- UI ---
st.title("🚌 Bus Ticket Booking (CSV via GitHub)")

name = st.text_input("Your Name")
route = st.selectbox("Route", ["A to B", "B to C", "A to C"])
tickets = st.number_input("Number of Tickets", min_value=1, max_value=5)

if st.button("Book Ticket"):
    if not name.strip():
        st.error("Name is required!")
    else:
        new_row = {
            "timestamp": str(datetime.datetime.now()),
            "name": name,
            "route": route,
            "tickets": tickets
        }
        st.session_state.tickets_df = pd.concat([st.session_state.tickets_df, pd.DataFrame([new_row])], ignore_index=True)
        success = update_csv_on_github(st.session_state.tickets_df, sha=st.session_state.csv_sha)

        if success:
            st.success("🎟 Ticket booked and saved to GitHub!")
            _, st.session_state.csv_sha = get_csv_from_github()  # Update SHA
        else:
            st.error("❌ Failed to update GitHub file.")

# --- Show Bookings ---
st.subheader("📋 All Bookings")
st.dataframe(st.session_state.tickets_df)
