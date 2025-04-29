import streamlit as st
import hashlib
import datetime

# --- Define the block and blockchain ---

class Block:
    def __init__(self, data, previous_hash):
        self.timestamp = str(datetime.datetime.now())
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.get_hash()

    def get_hash(self):
        content = self.timestamp + str(self.data) + self.previous_hash
        return hashlib.sha256(content.encode()).hexdigest()

# Initialize blockchain list
if "chain" not in st.session_state:
    genesis_block = Block("Genesis Block", "0")
    st.session_state.chain = [genesis_block]

# --- Streamlit UI ---

st.title("🚌 Simple Bus Ticket Booking (Simulated Blockchain)")

name = st.text_input("Your Name")
route = st.selectbox("Route", ["A to B", "B to C", "A to C"])
tickets = st.number_input("Tickets", min_value=1, max_value=5, step=1)

if st.button("Book Ticket"):
    if name:
        data = {"name": name, "route": route, "tickets": tickets}
        prev_hash = st.session_state.chain[-1].hash
        new_block = Block(data, prev_hash)
        st.session_state.chain.append(new_block)
        st.success("Ticket booked and block added!")
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
