import streamlit as st
import hashlib
import datetime
import json
import os

BLOCKCHAIN_FILE = "blockchain.json"

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

# --- Load/Save Blockchain ---

def load_blockchain():
    if os.path.exists(BLOCKCHAIN_FILE):
        with open(BLOCKCHAIN_FILE, "r") as f:
            data = json.load(f)
            return [Block.from_dict(b) for b in data]
    else:
        genesis = Block(str(datetime.datetime.now()), "Genesis Block", "0")
        return [genesis]

def save_blockchain(chain):
    with open(BLOCKCHAIN_FILE, "w") as f:
        json.dump([b.to_dict() for b in chain], f, indent=2)

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
        data = {"name": name, "route": route, "tickets": tickets}
        prev_hash = st.session_state.chain[-1].hash
        timestamp = str(datetime.datetime.now())
        new_block = Block(timestamp, data, prev_hash)
        st.session_state.chain.append(new_block)
        save_blockchain(st.session_state.chain)
        st.success("🎟 Ticket booked and block saved!")
    else:
        st.error("Please enter your name.")

# Show blockchain
st.subheader("📜 Blockchain Ledger")
for i, block in enumerate(st.session_state.chain):
    st.write(f"### Block {i}")
    st.write("Timestamp:", block.timestamp)
    st.write("Data:", block.data)
    st.write("Hash:", block.hash)
    st.write("Previous Hash:", block.previous_hash)
