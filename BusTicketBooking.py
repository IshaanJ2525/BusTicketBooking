import streamlit as st
import hashlib
import datetime
import json
import base64
import requests

# --- GitHub Configuration ---
GITHUB_TOKEN = st.secrets["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"]
GITHUB_USERNAME = st.secrets["IshaanJ2525"]
GITHUB_REPO = st.secrets["BusTicketBooking"]
GITHUB_FILEPATH = "data/blockchain.json"  # Path where you want to store the file in the repo

# Function to push the blockchain data to GitHub repo
def push_to_github(file_content):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{GITHUB_FILEPATH}"

    # Check if file exists to get the SHA
    response = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    if response.status_code == 200:
        sha = response.json()["sha"]
    else:
        sha = None

    data = {
        "message": "Update blockchain.json",
        "content": base64.b64encode(file_content.encode()).decode(),
        "branch": "main",
    }
    if sha:
        data["sha"] = sha

    response = requests.put(url, headers={
        "Authorization": f"token {GITHUB_TOKEN}"
    }, data=json.dumps(data))

    return response.status_code == 201 or response.status_code == 200

# --- Define the block and blockchain ---
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

# --- Load Blockchain ---

def load_blockchain():
    try:
        url = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/main/{GITHUB_FILEPATH}"
        response = requests.get(url)
        data = response.json()
        return [Block(**b) for b in data]
    except Exception:
        # Genesis block if no blockchain exists
        return [Block(str(datetime.datetime.now()), "Genesis Block", "0")]

# --- Initialize Blockchain ---
if "chain" not in st.session_state:
    st.session_state.chain = load_blockchain()

# --- Streamlit UI ---

st.title("🚌 Persistent Bus Ticket Booking (Blockchain Simulation)")

name = st.text_input("Your Name")
route = st.selectbox("Route", ["A to B", "B to C", "A to C"])
tickets = st.number_input("Tickets", min_value=1, max_value=5, step=1)

if st.button("Book Ticket"):
    if name:
        # Create a new block
        data = {"name": name, "route": route, "tickets": tickets}
        prev_hash = st.session_state.chain[-1].hash
        timestamp = str(datetime.datetime.now())
        new_block = Block(timestamp, data, prev_hash)
        st.session_state.chain.append(new_block)

        # Convert blockchain to JSON and push to GitHub
        blockchain_json = json.dumps([b.to_dict() for b in st.session_state.chain], indent=2)
        if push_to_github(blockchain_json):
            st.success("🎉 Ticket booked and blockchain saved to GitHub!")
        else:
            st.error("❌ Failed to save blockchain to GitHub.")
    else:
        st.warning("Please enter your name.")

# Show blockchain
st.subheader("📜 Blockchain Ledger")
for i, block in enumerate(st.session_state.chain):
    st.write(f"### Block {i}")
    st.json(block.to_dict())
