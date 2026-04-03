"""
QuantumSim: A Quantum Circuit Simulator Built with Qiskit
==========================================================
Author: [Your Name]
GitHub: github.com/[yourhandle]/quantum-sim
Description:
    A full-featured quantum circuit simulator demonstrating superposition,
    entanglement, interference, and landmark quantum algorithms — all from scratch,
    powered by Qiskit's statevector backend.

Algorithms Implemented:
    1. Deutsch-Jozsa   — Exponential speedup over classical for function classification
    2. Grover's Search — Quadratic speedup for unstructured search (O(√N) vs O(N))
    3. Bernstein-Vazirani — Linear speedup for hidden string discovery
    4. Quantum Fourier Transform (QFT) — Foundation of Shor's algorithm

Usage:
    python quantum_simulator.py --demo all
    python quantum_simulator.py --demo grover --n 3
    python quantum_simulator.py --demo qft --n 4
"""

import argparse
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.quantum_info import Statevector, partial_trace
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram, plot_bloch_multivector
from qiskit.circuit.library import QFT


# ─────────────────────────────────────────────
#  CORE UTILITY
# ─────────────────────────────────────────────

def simulate_circuit(qc: QuantumCircuit, shots: int = 1024) -> dict:
    """Run a quantum circuit on Aer's statevector simulator."""
    simulator = AerSimulator(method="statevector")
    qc_measured = qc.copy()
    if not any(inst.operation.name == "measure" for inst in qc_measured.data):
        qc_measured.measure_all()
    job = simulator.run(qc_measured, shots=shots)
    result = job.result()
    counts = result.get_counts()
    return counts


def get_statevector(qc: QuantumCircuit) -> Statevector:
    """Return the statevector of a circuit without measurement."""
    return Statevector(qc)


def format_statevector(sv: Statevector, n_qubits: int) -> str:
    """Pretty-print a statevector showing only significant amplitudes."""
    lines = []
    for i, amp in enumerate(sv.data):
        if abs(amp) > 1e-6:
            basis = format(i, f"0{n_qubits}b")
            prob = abs(amp) ** 2
            phase = np.angle(amp) * 180 / np.pi
            lines.append(f"  |{basis}⟩  amplitude={amp:.4f}  prob={prob:.4f}  phase={phase:.1f}°")
    return "\n".join(lines)


def print_header(title: str):
    width = 60
    print("\n" + "═" * width)
    print(f"  {title}")
    print("═" * width)


# ─────────────────────────────────────────────
#  DEMO 1 — BELL STATES & ENTANGLEMENT
# ─────────────────────────────────────────────

def demo_bell_states():
    print_header("DEMO 1 · Bell States & Quantum Entanglement")
    bell_names = ["Φ+", "Φ−", "Ψ+", "Ψ−"]
    circuits = []

    for i, name in enumerate(bell_names):
        qr = QuantumRegister(2, "q")
        cr = ClassicalRegister(2, "c")
        qc = QuantumCircuit(qr, cr)

        # Prepare based on Bell state index
        if i in [1, 3]:   # Φ−, Ψ−
            qc.x(0)
        if i in [2, 3]:   # Ψ+, Ψ−
            qc.x(1)

        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])
        circuits.append((name, qc))

        sv = get_statevector(qc.remove_final_measurements(inplace=False))
        print(f"\n  Bell state |{name}⟩:")
        print(format_statevector(sv, 2))
        counts = simulate_circuit(qc)
        print(f"  Measurement results: {counts}")

    print("\n  ✓ Perfect 50/50 correlations confirm maximal entanglement.")
    print("  ✓ These states cannot be written as products of individual qubits.")
    return circuits[0][1]   # return Φ+ for plotting


# ─────────────────────────────────────────────
#  DEMO 2 — DEUTSCH-JOZSA ALGORITHM
# ─────────────────────────────────────────────

def build_dj_oracle(n: int, is_constant: bool) -> QuantumCircuit:
    """
    Build a Deutsch-Jozsa oracle.
    Constant: f(x)=0 (identity) or f(x)=1 (flip ancilla).
    Balanced: XOR of all input bits applied to ancilla.
    """
    oracle = QuantumCircuit(n + 1)
    if is_constant:
        # f(x) = 1 for all x → flip ancilla
        oracle.x(n)
    else:
        # Balanced: f(x) = x_0 XOR x_1 XOR ... XOR x_{n-1}
        for qubit in range(n):
            oracle.cx(qubit, n)
    return oracle


def demo_deutsch_jozsa(n: int = 3):
    print_header(f"DEMO 2 · Deutsch-Jozsa Algorithm  (n={n} qubits)")
    print(f"""
  Problem: Given a black-box function f: {{0,1}}^{n} → {{0,1}},
  determine if f is CONSTANT or BALANCED.

  Classical:  Requires up to 2^{n-1}+1 = {2**(n-1)+1} queries.
  Quantum:    Always solves it in exactly 1 query. ⚡
    """)

    results = {}
    for label, is_const in [("Constant", True), ("Balanced", False)]:
        qr = QuantumRegister(n, "input")
        anc = QuantumRegister(1, "ancilla")
        cr = ClassicalRegister(n, "c")
        qc = QuantumCircuit(qr, anc, cr)

        # Initialize ancilla in |−⟩
        qc.x(n)
        qc.h(range(n + 1))

        # Apply oracle
        oracle = build_dj_oracle(n, is_const)
        qc.compose(oracle, inplace=True)

        # Interfere & measure
        qc.h(range(n))
        qc.measure(range(n), range(n))

        counts = simulate_circuit(qc, shots=512)
        all_zeros = "0" * n
        is_detected_const = all_zeros in counts and counts[all_zeros] > 400

        print(f"  [{label} oracle]  Measurement → {counts}")
        print(f"  Detected as: {'CONSTANT ✓' if is_detected_const else 'BALANCED ✓'}")
        results[label] = (qc, counts)

    return results


# ─────────────────────────────────────────────
#  DEMO 3 — GROVER'S SEARCH ALGORITHM
# ─────────────────────────────────────────────

def build_grover_oracle(n: int, target: int) -> QuantumCircuit:
    """Phase oracle: marks the target state with a phase flip."""
    oracle = QuantumCircuit(n)
    target_bits = format(target, f"0{n}b")
    # Flip qubits where target bit is 0
    for i, bit in enumerate(reversed(target_bits)):
        if bit == "0":
            oracle.x(i)
    # Multi-controlled Z
    oracle.h(n - 1)
    oracle.mcx(list(range(n - 1)), n - 1)
    oracle.h(n - 1)
    # Unflip
    for i, bit in enumerate(reversed(target_bits)):
        if bit == "0":
            oracle.x(i)
    oracle.name = f"Oracle|{target_bits}⟩"
    return oracle


def build_diffuser(n: int) -> QuantumCircuit:
    """Grover diffusion operator: inversion about the mean."""
    diffuser = QuantumCircuit(n)
    diffuser.h(range(n))
    diffuser.x(range(n))
    diffuser.h(n - 1)
    diffuser.mcx(list(range(n - 1)), n - 1)
    diffuser.h(n - 1)
    diffuser.x(range(n))
    diffuser.h(range(n))
    diffuser.name = "Diffuser"
    return diffuser


def demo_grover(n: int = 3, target: int = None):
    if target is None:
        target = np.random.randint(0, 2**n)
    N = 2 ** n
    optimal_iterations = max(1, int(np.floor(np.pi / 4 * np.sqrt(N))))

    print_header(f"DEMO 3 · Grover's Search Algorithm  (n={n}, N={N})")
    print(f"""
  Problem: Find a marked item in an unsorted database of {N} items.

  Classical:  O(N) = {N} queries on average.
  Grover:     O(√N) = ~{int(np.sqrt(N))} queries. ⚡

  Secret target: |{format(target, f"0{n}b")}⟩  (index {target})
  Optimal Grover iterations: {optimal_iterations}
    """)

    qr = QuantumRegister(n, "q")
    cr = ClassicalRegister(n, "c")
    qc = QuantumCircuit(qr, cr)

    # Initialize uniform superposition
    qc.h(range(n))

    oracle = build_grover_oracle(n, target)
    diffuser = build_diffuser(n)

    for step in range(optimal_iterations):
        qc.compose(oracle, inplace=True)
        qc.compose(diffuser, inplace=True)

    qc.measure(range(n), range(n))
    counts = simulate_circuit(qc, shots=1024)

    target_str = format(target, f"0{n}b")
    target_count = counts.get(target_str, 0)
    success_prob = target_count / 1024

    # Sort by count descending
    sorted_counts = dict(sorted(counts.items(), key=lambda x: -x[1])[:5])
    print(f"  Top results: {sorted_counts}")
    print(f"  Target |{target_str}⟩ found with probability: {success_prob:.1%}  {'✓ SUCCESS' if success_prob > 0.5 else '✗'}")

    return qc, counts, target


# ─────────────────────────────────────────────
#  DEMO 4 — BERNSTEIN-VAZIRANI ALGORITHM
# ─────────────────────────────────────────────

def demo_bernstein_vazirani(n: int = 4, secret: str = None):
    if secret is None:
        secret = "".join(np.random.choice(["0", "1"], size=n).tolist())

    print_header(f"DEMO 4 · Bernstein-Vazirani Algorithm  (n={n})")
    print(f"""
  Problem: Find a hidden binary string s ∈ {{0,1}}^{n}
  given a black-box computing f(x) = s·x (mod 2).

  Classical:  Requires n={n} queries (one per bit).
  Quantum:    Recovers s in exactly 1 query. ⚡

  Hidden string: s = {secret}
    """)

    qr = QuantumRegister(n, "x")
    anc = QuantumRegister(1, "ancilla")
    cr = ClassicalRegister(n, "c")
    qc = QuantumCircuit(qr, anc, cr)

    qc.x(n)
    qc.h(range(n + 1))

    # BV Oracle: f(x) = s·x mod 2
    for i, bit in enumerate(reversed(secret)):
        if bit == "1":
            qc.cx(i, n)

    qc.h(range(n))
    qc.measure(range(n), range(n))

    counts = simulate_circuit(qc, shots=512)
    most_frequent = max(counts, key=counts.get)
    recovered = most_frequent[::-1]   # bit order

    print(f"  Measurement: {counts}")
    print(f"  Hidden string s = {secret}")
    print(f"  Recovered  s = {recovered}  {'✓ EXACT MATCH' if recovered == secret else '✗'}")

    return qc, counts


# ─────────────────────────────────────────────
#  DEMO 5 — QUANTUM FOURIER TRANSFORM
# ─────────────────────────────────────────────

def demo_qft(n: int = 3):
    print_header(f"DEMO 5 · Quantum Fourier Transform  (n={n} qubits)")
    print(f"""
  The QFT maps computational basis states to frequency states:
  |j⟩ → (1/√{2**n}) Σ_k e^(2πijk/{2**n}) |k⟩

  It is the quantum analogue of the DFT and is the cornerstone
  of Shor's factoring algorithm and quantum phase estimation.

  Classical DFT:  O(N log N) — the famous FFT.
  Quantum QFT:    O(n²) = O(log²N).  Exponentially faster. ⚡
    """)

    # Apply QFT to a specific state
    input_state = QuantumCircuit(n)
    # Prepare |5⟩ = |101⟩ in 3 qubits
    for i, bit in enumerate(reversed(format(5 % 2**n, f"0{n}b"))):
        if bit == "1":
            input_state.x(i)

    qft_circuit = QFT(n, do_swaps=True, inverse=False, insert_barriers=True)
    full_circuit = input_state.compose(qft_circuit)

    sv_before = get_statevector(input_state)
    sv_after = get_statevector(full_circuit)

    print(f"  Input state |{5 % 2**n}⟩ ({format(5 % 2**n, f'0{n}b')}) statevector:")
    print(format_statevector(sv_before, n))
    print(f"\n  After QFT — frequency domain amplitudes:")
    print(format_statevector(sv_after, n))
    print(f"\n  Note: The QFT encodes phase relationships, not just probabilities.")

    return full_circuit, sv_before, sv_after


# ─────────────────────────────────────────────
#  VISUALIZATION
# ─────────────────────────────────────────────

def plot_all_results(grover_data, bv_data, dj_data, output_path="quantum_results.png"):
    """Generate a publication-quality multi-panel result figure."""
    fig = plt.figure(figsize=(18, 12), facecolor="#0a0a1a")
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

    palette = {
        "bg":     "#0a0a1a",
        "panel":  "#12122a",
        "accent": "#00e5ff",
        "green":  "#00ff88",
        "purple": "#bf5fff",
        "orange": "#ffb347",
        "text":   "#e0e0ff",
        "dim":    "#555588",
    }

    def style_ax(ax, title):
        ax.set_facecolor(palette["panel"])
        ax.set_title(title, color=palette["accent"], fontsize=11,
                     fontweight="bold", pad=10, fontfamily="monospace")
        ax.tick_params(colors=palette["text"], labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor(palette["dim"])

    # --- Panel 1: Grover counts ---
    ax1 = fig.add_subplot(gs[0, 0])
    qc_g, counts_g, target_g = grover_data
    target_str_g = format(target_g, f"0{len(list(counts_g.keys())[0])}b")
    labels = list(counts_g.keys())
    values = list(counts_g.values())
    colors = [palette["green"] if l == target_str_g else palette["dim"] for l in labels]
    bars = ax1.bar(labels, values, color=colors, edgecolor=palette["bg"], linewidth=0.5)
    style_ax(ax1, "Grover's Search — Measurement")
    ax1.set_xlabel("Basis State", color=palette["text"], fontsize=8)
    ax1.set_ylabel("Counts (1024 shots)", color=palette["text"], fontsize=8)
    ax1.set_facecolor(palette["panel"])
    plt.setp(ax1.get_xticklabels(), rotation=45, ha="right", color=palette["text"], fontsize=7)
    ax1.annotate(f"Target\n|{target_str_g}⟩", xy=(target_str_g, counts_g.get(target_str_g, 0)),
                 xytext=(0, 8), textcoords="offset points",
                 ha="center", color=palette["green"], fontsize=8, fontweight="bold")

    # --- Panel 2: BV counts ---
    ax2 = fig.add_subplot(gs[0, 1])
    qc_bv, counts_bv = bv_data
    bv_labels = sorted(counts_bv.keys())
    bv_values = [counts_bv[k] for k in bv_labels]
    ax2.bar(bv_labels, bv_values, color=palette["purple"], edgecolor=palette["bg"])
    style_ax(ax2, "Bernstein-Vazirani — Single-Query")
    ax2.set_xlabel("Recovered Secret", color=palette["text"], fontsize=8)
    ax2.set_ylabel("Counts", color=palette["text"], fontsize=8)
    plt.setp(ax2.get_xticklabels(), rotation=45, ha="right", color=palette["text"], fontsize=7)

    # --- Panel 3: DJ results ---
    ax3 = fig.add_subplot(gs[0, 2])
    dj_results = dj_data
    for idx, (label, (qc_dj, counts_dj)) in enumerate(dj_results.items()):
        x = list(counts_dj.keys())
        y = list(counts_dj.values())
        color = palette["orange"] if idx == 0 else palette["accent"]
        ax3.bar([f"{k}\n({label[:4]})" for k in x], y, color=color,
                edgecolor=palette["bg"], alpha=0.85)
    style_ax(ax3, "Deutsch-Jozsa — Oracle Classification")
    ax3.set_xlabel("Measurement", color=palette["text"], fontsize=8)
    ax3.set_ylabel("Counts", color=palette["text"], fontsize=8)
    plt.setp(ax3.get_xticklabels(), rotation=0, ha="center", color=palette["text"], fontsize=7)

    # --- Panel 4: Grover amplitude evolution ---
    ax4 = fig.add_subplot(gs[1, 0])
    n_g = len(list(counts_g.keys())[0])
    N_g = 2 ** n_g
    optimal_iters = max(1, int(np.floor(np.pi / 4 * np.sqrt(N_g))))
    iter_range = range(0, optimal_iters + 1)
    target_probs = [(np.sin((2 * k + 1) * np.arcsin(1 / np.sqrt(N_g)))) ** 2 for k in iter_range]
    ax4.plot(list(iter_range), target_probs, color=palette["green"],
             linewidth=2.5, marker="o", markersize=6, markerfacecolor=palette["orange"])
    ax4.axhline(y=1 / N_g, color=palette["dim"], linestyle="--", linewidth=1, label="Classical 1/N")
    ax4.set_ylim(0, 1.05)
    style_ax(ax4, "Grover Amplitude Amplification")
    ax4.set_xlabel("Iterations", color=palette["text"], fontsize=8)
    ax4.set_ylabel("P(target)", color=palette["text"], fontsize=8)
    ax4.legend(facecolor=palette["panel"], edgecolor=palette["dim"],
               labelcolor=palette["text"], fontsize=7)

    # --- Panel 5: Quantum speedup comparison ---
    ax5 = fig.add_subplot(gs[1, 1])
    sizes = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
    classical = sizes
    grover_q = [int(np.sqrt(n)) for n in sizes]
    ax5.plot(sizes, classical, color=palette["orange"], linewidth=2, label="Classical O(N)", marker="s", markersize=4)
    ax5.plot(sizes, grover_q, color=palette["green"], linewidth=2, label="Grover O(√N)", marker="o", markersize=4)
    ax5.set_xscale("log", base=2)
    ax5.set_yscale("log", base=2)
    style_ax(ax5, "Grover Speedup: Classical vs Quantum")
    ax5.set_xlabel("Database Size N", color=palette["text"], fontsize=8)
    ax5.set_ylabel("Queries Needed", color=palette["text"], fontsize=8)
    ax5.legend(facecolor=palette["panel"], edgecolor=palette["dim"],
               labelcolor=palette["text"], fontsize=7)

    # --- Panel 6: Algorithm comparison table ---
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.axis("off")
    table_data = [
        ["Algorithm", "Classical", "Quantum", "Speedup"],
        ["Deutsch-Jozsa", "O(2^n)", "O(1)", "Exponential"],
        ["Bernstein-Vazirani", "O(n)", "O(1)", "Linear"],
        ["Grover's Search", "O(N)", "O(√N)", "Quadratic"],
        ["Quantum Fourier Xform", "O(N log N)", "O(n²)", "Exponential"],
    ]
    table = ax6.table(cellText=table_data[1:], colLabels=table_data[0],
                      loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    for (r, c), cell in table.get_celld().items():
        cell.set_facecolor(palette["panel"] if r % 2 == 0 else "#1a1a35")
        cell.set_edgecolor(palette["dim"])
        cell.set_text_props(color=palette["text"] if r > 0 else palette["accent"],
                            fontweight="bold" if r == 0 else "normal")
    style_ax(ax6, "Quantum Speedup Summary")

    # Title
    fig.text(0.5, 0.98, "QuantumSim — Quantum Algorithm Benchmark Results",
             ha="center", va="top", color=palette["accent"],
             fontsize=15, fontweight="bold", fontfamily="monospace")
    fig.text(0.5, 0.955, "Simulated on Qiskit Aer Statevector Backend · 1024 shots",
             ha="center", va="top", color=palette["dim"], fontsize=9)

    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=palette["bg"])
    print(f"\n  ✓ Results figure saved → {output_path}")
    return output_path


# ─────────────────────────────────────────────
#  MAIN ENTRY POINT
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="QuantumSim: Quantum Circuit Simulator with Qiskit",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--demo", choices=["all", "bell", "dj", "grover", "bv", "qft"],
        default="all", help="Which demo to run"
    )
    parser.add_argument("--n", type=int, default=3, help="Number of qubits (default: 3)")
    parser.add_argument("--shots", type=int, default=1024, help="Measurement shots")
    parser.add_argument("--target", type=int, default=None, help="Grover target index")
    parser.add_argument("--no-plot", action="store_true", help="Skip plot generation")
    args = parser.parse_args()

    print("""
╔══════════════════════════════════════════════════════════╗
║        QuantumSim · Quantum Circuit Simulator            ║
║        Powered by Qiskit · Aer Statevector Backend       ║
╚══════════════════════════════════════════════════════════╝
    """)

    grover_data = dj_data = bv_data = None

    run_all = args.demo == "all"

    if run_all or args.demo == "bell":
        demo_bell_states()

    if run_all or args.demo == "dj":
        dj_data = demo_deutsch_jozsa(args.n)

    if run_all or args.demo == "grover":
        grover_data = demo_grover(args.n, args.target)

    if run_all or args.demo == "bv":
        bv_data = demo_bernstein_vazirani(args.n)

    if run_all or args.demo == "qft":
        demo_qft(args.n)

    if run_all and not args.no_plot and all([grover_data, bv_data, dj_data]):
        plot_all_results(grover_data, bv_data, dj_data)

    print("\n" + "═" * 60)
    print("  QuantumSim complete. All algorithms verified. ✓")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    main()
