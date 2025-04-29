import streamlit as st
import hashlib
import datetime
import json
import base64
import requests

# --- GitHub Configuration from Streamlit Secrets ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_USERNAME = st.secrets["GITHUB_USERNAME"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]
GITHUB_FILEPATH = "data/blockchain.json"  # Path in repo

# --- Blockchain Classes ---

class Block:
    def __init__(self, timestamp, data, previous_hash, hash_val=None):
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = hash_val or self.get_hash()

    def get_hash(self):
        content = self.timestamp + json.dumps(self.data) + self.previous_hash
        return hashlib.sha256(content.encode()).hexdigest()

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }

    @staticmethod
    def from_dict(d):
        return Block(d["timestamp"], d["data"], d["previous_hash"], d["hash"])

# --- GitHub Save/Load Functions ---

def push_to_github(content_str):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{GITHUB_FILEPATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # Get current file SHA if it exists
    r = requests.get(url, headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None

    data = {
        "message": "Update blockchain data",
        "content": base64.b64encode(content_str.encode()).decode(),
        "branch": "main"
    }
    if sha:
        data["sha"] = sha

    r = requests.put(url, headers=headers, json=data)
    return r.status_code in [200, 201]

def load_from_github():
    url = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/main/{GITHUB_FILEPATH}"
    r = requests.get(url)
    if r.status_code == 200:
        blocks = json.loads(r.text)
        return [Block.from_dict(b) for b in blocks]
    else:
        genesis = Block(str(datetime.datetime.now()), "Genesis Block", "0")
        return [genesis]

# --- Blockchain Initialization ---
if "chain" not in st.session_state:
    st.session_state.chain = load_from_github()

# --- UI ---
st.title("🚌 Bus Ticket Booking with Blockchain (GitHub-Synced)")

name = st.text_input("Enter your name:")
route = st.selectbox("Select your route:", ["A to B", "B to C", "A to C"])
tickets = st.number_input("Number of tickets:", min_value=1, max_value=5, step=1)

if st.button("🎟 Book Ticket"):
    if name.strip() == "":
        st.warning("Please enter your name.")
    else:
        data = {"name": name, "route": route, "tickets": tickets}
        prev_hash = st.session_state.chain[-1].hash
        timestamp = str(datetime.datetime.now())
        new_block = Block(timestamp, data, prev_hash)
        st.session_state.chain.append(new_block)

        blockchain_json = json.dumps([b.to_dict() for b in st.session_state.chain], indent=2)
        if push_to_github(blockchain_json):
            st.success("✅ Ticket booked and blockchain updated on GitHub.")
        else:
            st.error("❌ Failed to update blockchain on GitHub.")

# --- Blockchain Display ---
st.subheader("📜 Blockchain Ledger")
for i, block in enumerate(st.session_state.chain):
    st.markdown(f"**Block {i}**")
    st.json(block.to_dict())
