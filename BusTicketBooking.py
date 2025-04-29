import streamlit as st
import hashlib
import datetime
import json
import base64
import requests

# --- GitHub Config ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_USERNAME = st.secrets["GITHUB_USERNAME"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]
GITHUB_FILEPATH = "blockchain.json"

# --- Blockchain Model ---
class Block:
    def __init__(self, timestamp, data, previous_hash, hash_val=None):
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = hash_val or self.calculate_hash()

    def calculate_hash(self):
        block_string = self.timestamp + json.dumps(self.data) + self.previous_hash
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
        }

    @staticmethod
    def from_dict(data):
        return Block(data["timestamp"], data["data"], data["previous_hash"], data["hash"])

# --- GitHub Functions ---
def get_github_file():
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{GITHUB_FILEPATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        content = base64.b64decode(r.json()["content"]).decode()
        sha = r.json()["sha"]
        return json.loads(content), sha
    else:
        return None, None

def update_github_file(data_json, sha=None):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{GITHUB_FILEPATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    content_encoded = base64.b64encode(data_json.encode()).decode()

    payload = {
        "message": "Update blockchain",
        "content": content_encoded,
        "branch": "main"
    }
    if sha:
        payload["sha"] = sha

    r = requests.put(url, headers=headers, json=payload)
    return r.status_code in [200, 201]

# --- Load Blockchain ---
def load_blockchain():
    data, _ = get_github_file()
    if data:
        return [Block.from_dict(b) for b in data]
    else:
        # Create Genesis block
        genesis = Block(str(datetime.datetime.now()), "Genesis Block", "0")
        return [genesis]

# --- Streamlit UI ---
st.title("🚌 Bus Ticket Booking on Blockchain (GitHub Synced)")

if "blockchain" not in st.session_state:
    st.session_state.blockchain = load_blockchain()

name = st.text_input("Enter your name")
route = st.selectbox("Select your route", ["A to B", "B to C", "A to C"])
tickets = st.number_input("Number of tickets", min_value=1, max_value=5, step=1)

if st.button("Book Ticket"):
    if not name.strip():
        st.error("Please enter your name.")
    else:
        data = {"name": name, "route": route, "tickets": tickets}
        previous_hash = st.session_state.blockchain[-1].hash
        timestamp = str(datetime.datetime.now())
        new_block = Block(timestamp, data, previous_hash)
        st.session_state.blockchain.append(new_block)

        # Save to GitHub
        json_data = json.dumps([b.to_dict() for b in st.session_state.blockchain], indent=2)
        _, current_sha = get_github_file()
        if update_github_file(json_data, sha=current_sha):
            st.success("✅ Ticket booked and blockchain updated!")
        else:
            st.error("❌ Failed to update GitHub file.")

# --- Show Blockchain ---
st.subheader("📜 Blockchain Ledger")
for idx, block in enumerate(st.session_state.blockchain):
    st.markdown(f"**Block {idx}**")
    st.json(block.to_dict())
