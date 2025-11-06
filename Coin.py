# =======================================================
# Quantum Coin Arcade 🎮
# Streamlit + Qiskit Gamified Bloch Sphere Simulator (v3)
# By: Lubaisha Shaikh
# =======================================================

import streamlit as st
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_bloch_multivector
import pandas as pd
import numpy as np

# -------------------------------------------------------
# 🎨 PAGE CONFIG
# -------------------------------------------------------
st.set_page_config(page_title="Quantum Coin Arcade", page_icon="🪙", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"] {
  font-family: 'Poppins', sans-serif;
  background: linear-gradient(145deg, #0F2027, #203A43, #2C5364);
  color: #f5f5f5;
}
h1, h2, h3 {
  color: #00f5ff;
  text-shadow: 0 0 12px rgba(0,245,255,0.6);
}
.stButton>button {
  border-radius: 10px !important;
  font-weight: 600;
  color: white !important;
  background: linear-gradient(90deg, #ff8a00, #e52e71);
  transition: all 0.3s ease;
  border: none;
}
.stButton>button:hover {
  transform: scale(1.07);
  box-shadow: 0 0 20px rgba(255,138,0,0.5);
}
.info-box {
  background: rgba(255,255,255,0.08);
  border-left: 4px solid #00f5ff;
  padding: 12px;
  border-radius: 10px;
  font-size: 14px;
  margin-bottom: 10px;
}
.metric-box {
  background: rgba(255,255,255,0.08);
  border-radius: 12px;
  text-align: center;
  padding: 15px;
  backdrop-filter: blur(10px);
}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# 🧠 SESSION STATE
# -------------------------------------------------------
if "qc" not in st.session_state:
    st.session_state.qc = QuantumCircuit(4)
if "points" not in st.session_state:
    st.session_state.points = 0
if "level" not in st.session_state:
    st.session_state.level = 1
if "mission" not in st.session_state:
    st.session_state.mission = 0

# -------------------------------------------------------
# 🎯 MISSIONS
# -------------------------------------------------------
missions = [
    "🌗 Create Superposition on all qubits using H gate.",
    "🔗 Entangle any two qubits with CNOT.",
    "⚡ Apply Phase Flip (Z) on any qubit.",
    "💫 Generate Bell State on Q0 & Q1.",
    "💥 Flip all qubits using X gates.",
    "🎭 Use three different gates in one game.",
    "🏁 Return to |0000⟩ in < 5 moves."
]

# -------------------------------------------------------
# 💡 GATE INFO TOOLTIP
# -------------------------------------------------------
def explain_gate(gate):
    explanations = {
        "H": "Hadamard gate — puts qubit into superposition (both 0 and 1).",
        "X": "Pauli-X — flips qubit (0→1, 1→0).",
        "Z": "Pauli-Z — phase flip (invisible on Bloch but changes phase).",
        "S": "S gate — rotates phase by 90°.",
        "T": "T gate — rotates phase by 45°.",
        "Rx": "Rotation around X-axis.",
        "Ry": "Rotation around Y-axis.",
        "Rz": "Rotation around Z-axis (phase).",
        "CNOT": "Entangles two qubits — control influences target."
    }
    st.markdown(f"<div class='info-box'>💡 {explanations.get(gate, 'Select a gate to learn about it!')}</div>", unsafe_allow_html=True)

# -------------------------------------------------------
# 🪄 TRUTH TABLE GENERATOR (LOGICAL, NON-SIMULATION)
# -------------------------------------------------------
def generate_truth_table(qc, num_qubits):
    truth_table = []
    for i in range(2 ** num_qubits):
        input_state = format(i, f"0{num_qubits}b")
        output_state = input_state

        if any(instr.operation.name == 'x' for instr in qc.data):
            output_state = ''.join('1' if b == '0' else '0' for b in input_state)
        elif any(instr.operation.name == 'h' for instr in qc.data):
            output_state = 'Superposed'
        elif any(instr.operation.name == 'cx' for instr in qc.data):
            output_state = 'Entangled'

        truth_table.append([f"|{input_state}⟩", f"|{output_state}⟩"])
    return pd.DataFrame(truth_table, columns=["Input State", "Output State"])

# -------------------------------------------------------
# 🧩 PLOT BLOCH SPHERE
# -------------------------------------------------------
def plot_bloch(qc):
    state = Statevector.from_instruction(qc)
    fig = plot_bloch_multivector(state)
    fig.set_size_inches(12, 7)
    return fig

def award_points(p):
    st.session_state.points += p
    if st.session_state.points >= 250 * st.session_state.level:
        st.session_state.level += 1
        st.balloons()
        st.success(f"🎉 Level {st.session_state.level} Unlocked!")

# -------------------------------------------------------
# 🎮 SIDEBAR CONTROL PANEL
# -------------------------------------------------------
st.sidebar.title("🎮 Quantum Control Panel")
num_qubits = st.sidebar.slider("Number of Qubits", 1, 4, 4)
gate = st.sidebar.selectbox("Choose Gate", ["H", "X", "Z", "S", "T", "Rx", "Ry", "Rz", "CNOT"])
explain_gate(gate)

if gate.startswith("R"):
    theta = st.sidebar.slider("Rotation Angle (radians)", 0.0, 2*np.pi, np.pi/2)
else:
    theta = None

qubit_choices = list(range(num_qubits))
selected_qubits = st.sidebar.multiselect("Select Qubits", qubit_choices, default=[0])

if gate == "CNOT":
    control = st.sidebar.selectbox("Control Qubit", qubit_choices, index=0)
    target = st.sidebar.selectbox("Target Qubit", qubit_choices, index=1)
else:
    control = target = None

# -------------------------------------------------------
# ⚙️ APPLY GATE LOGIC
# -------------------------------------------------------
if st.sidebar.button("🪙 Apply Operation"):
    qc = st.session_state.qc
    if gate == "CNOT" and control != target:
        qc.cx(control, target)
    else:
        for q in selected_qubits:
            if gate in ["H", "X", "Z", "S", "T"]:
                getattr(qc, gate.lower())(q)
            elif gate in ["Rx", "Ry", "Rz"]:
                getattr(qc, gate.lower())(theta, q)
    st.session_state.qc = qc
    award_points(30)
    st.toast(f"✅ {gate} applied successfully to qubits {selected_qubits}!", icon="✨")

if st.sidebar.button("♻ Reset Circuit"):
    st.session_state.qc = QuantumCircuit(4)
    st.toast("Circuit Reset!", icon="🔄")

if st.sidebar.button("🎯 Next Mission"):
    st.session_state.mission = (st.session_state.mission + 1) % len(missions)
    st.success("✨ New Mission Unlocked!")

# -------------------------------------------------------
# 🖥️ MAIN INTERFACE
# -------------------------------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.title("🪙 Quantum Coin Arcade")
    st.caption("Learn quantum mechanics the fun way — flip, rotate, and entangle qubits like coins!")
    fig = plot_bloch(st.session_state.qc)
    st.pyplot(fig)
    st.subheader("⚙️ Quantum Circuit")
    st.pyplot(st.session_state.qc.draw("mpl"))
    st.subheader("🧮 Truth Table")
    df = generate_truth_table(st.session_state.qc, num_qubits)
    st.dataframe(df, use_container_width=True)

with col2:
    st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
    st.metric("⭐ Points", st.session_state.points)
    st.metric("🏆 Level", st.session_state.level)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='info-box'>🎯 Mission:<br>{missions[st.session_state.mission]}</div>", unsafe_allow_html=True)
    st.progress(min(st.session_state.points % 250 / 250, 1.0))

st.markdown("---")
st.caption("Built with 💜 by Lubaisha Shaikh | Powered by Streamlit + Qiskit")
