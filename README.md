⚛️ QuantumSim — Quantum Circuit Simulator
Exploring quantum speedups through hands-on implementation of landmark quantum algorithms.

Python Qiskit License Stars

What is QuantumSim?
QuantumSim is a research-grade quantum circuit simulator built on IBM's Qiskit framework. It implements and benchmarks four foundational quantum algorithms that demonstrate provable speedups over classical computation — running entirely on a local statevector simulator with no quantum hardware required.

This project was built to develop an intuition for:

Why quantum superposition and entanglement produce fundamentally different computational power
How quantum interference can be engineered to amplify correct answers
What "quantum speedup" actually means, mathematically and empirically
🧪 Implemented Algorithms
Algorithm	Problem	Classical Cost	Quantum Cost	Speedup
Deutsch-Jozsa	Is f constant or balanced?	O(2ⁿ)	O(1)	Exponential
Bernstein-Vazirani	Find hidden string s	O(n) queries	O(1) query	Linear
Grover's Search	Find marked item in N	O(N)	O(√N)	Quadratic
Quantum Fourier Transform	Fourier transform over Z_N	O(N log N)	O(n²)	Exponential
Plus: Bell State Generation — demonstrating maximally entangled qubits.

📁 Project Structure
quantum-sim/
├── quantum_simulator.py    # Main simulator & algorithm implementations
├── requirements.txt        # Python dependencies
├── quantum_results.png     # Auto-generated benchmark figure
├── notebooks/
│   ├── 01_bell_states.ipynb
│   ├── 02_deutsch_jozsa.ipynb
│   ├── 03_grover.ipynb
│   └── 04_qft.ipynb
└── README.md
🚀 Quick Start
1. Clone & Install
git clone https://github.com/yourhandle/quantum-sim.git
cd quantum-sim
pip install -r requirements.txt
2. Run All Demos
python quantum_simulator.py --demo all
3. Run Individual Algorithms
# Grover's search on a 4-qubit database (16 items)
python quantum_simulator.py --demo grover --n 4

# Deutsch-Jozsa with 5 qubits
python quantum_simulator.py --demo dj --n 5

# Bernstein-Vazirani
python quantum_simulator.py --demo bv --n 6

# Quantum Fourier Transform
python quantum_simulator.py --demo qft --n 4

4. Customize
# Search for a specific target index
python quantum_simulator.py --demo grover --n 3 --target 5

# Increase shots for better statistics
python quantum_simulator.py --demo grover --n 4 --shots 4096

# Skip plot generation (faster)
python quantum_simulator.py --demo all --no-plot
🔬 Deep Dives
Bell States & Entanglement
Quantum entanglement is perhaps the strangest prediction of quantum mechanics: two qubits can share a quantum state such that measuring one instantly determines the other, regardless of distance.

QuantumSim constructs all four Bell states — the maximally entangled two-qubit states — and verifies their measurement statistics:

|Φ+⟩ = (1/√2)(|00⟩ + |11⟩)   ← equal superposition of 00 and 11
|Φ−⟩ = (1/√2)(|00⟩ − |11⟩)   ← same amplitudes, different phase
|Ψ+⟩ = (1/√2)(|01⟩ + |10⟩)   ← anticorrelated
|Ψ−⟩ = (1/√2)(|01⟩ − |10⟩)   ← anticorrelated + phase
Each state yields perfect 50/50 measurement correlations — no classical variable can reproduce this behavior (Bell's theorem).

Grover's Search Algorithm
Grover's algorithm searches an unsorted database of N items in O(√N) steps, versus O(N) classically. The speedup comes from two operations applied repeatedly:

Phase Oracle — Flips the phase of the target state: |target⟩ → −|target⟩
Diffusion Operator — Inversion about the mean amplitude
Each iteration rotates the state vector in a two-dimensional subspace by angle 2θ where sin(θ) = 1/√N. After ⌊π√N/4⌋ iterations, the amplitude of the target state is amplified close to 1.

Probability of finding target:  P(k) = sin²((2k+1)·arcsin(1/√N))
Optimal iterations:              k* = ⌊π√N/4⌋
Quantum Fourier Transform
The QFT maps computational basis states to frequency domain:

|j⟩ → (1/√N) Σₖ e^(2πijk/N) |k⟩
This is the quantum analogue of the DFT, achievable in O(n²) = O(log²N) gates, vs O(N log N) for the classical FFT. It is the algorithmic core of Shor's factoring algorithm.

📊 Results
Running --demo all generates a six-panel benchmark figure (quantum_results.png) showing:

Grover measurement histogram (target state dominates)
Bernstein-Vazirani single-shot recovery
Deutsch-Jozsa constant vs balanced oracle discrimination
Grover amplitude evolution over iterations
Quantum vs classical query complexity (log-log)
Algorithm speedup comparison table
🧠 Key Concepts
Concept	Description
Superposition	A qubit exists in a linear combination of `
Entanglement	Qubits share correlations that cannot be described independently
Interference	Amplitudes add (constructively/destructively) before measurement
Phase kickback	Control qubit acquires a phase from the target: key to many algorithms
Oracle	A black-box quantum gate encoding the problem to be solved
🛠 Technical Details
Backend: Qiskit Aer statevector simulator (exact, no shot noise in state)
Measurement: Configurable shots (default 1024) for realistic sampling
Visualization: Matplotlib dark-theme multi-panel figures
Gate Set: H, X, Y, Z, CNOT, Toffoli (MCX), Phase gates
Python: 3.10+ required
📚 References & Further Reading
Nielsen & Chuang — Quantum Computation and Quantum Information (Cambridge, 2000)
Grover, L.K. (1996) — A fast quantum mechanical algorithm for database search
Deutsch & Jozsa (1992) — Rapid solution of problems by quantum computation
Bernstein & Vazirani (1997) — Quantum complexity theory
IBM Qiskit Textbook
🤝 Contributing
Pull requests are welcome! Areas for extension:

Shor's factoring algorithm
Quantum Phase Estimation
Variational Quantum Eigensolver (VQE)
Error mitigation with Qiskit's ZNE
IBMQ hardware integration
📄 License
MIT License — see LICENSE for details.

"Anyone who is not shocked by quantum theory has not understood it." — Niels Bohr
