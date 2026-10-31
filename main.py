import os
import sqlite3
import subprocess
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from gprMax.tools.output_stats import get_output_data

# --------------------------------------------------
# 1. CONFIGURATION (The Control Panel)
# --------------------------------------------------
CONFIG = {
    "base_input": "user_model.in",
    "eps_values": [3.0, 5.0, 8.0, 12.0],
    "output_dir": "parametric_results",
    "db_name": "parametric_results/simulations.db",
    "dt": 1.0e-11,
    "component": "Ez"
}

# --------------------------------------------------
# 2. DATABASE LAYER (Persistence)
# --------------------------------------------------
def init_db():
    db_dir = os.path.dirname(CONFIG["db_name"])
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
        
    conn = sqlite3.connect(CONFIG["db_name"])
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            permittivity REAL,
            peak REAL,
            arrival REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(eps, peak, arrival):
    conn = sqlite3.connect(CONFIG["db_name"])
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO results (permittivity, peak, arrival) VALUES (?, ?, ?)",
        (eps, peak, arrival)
    )
    conn.commit()
    conn.close()

# --------------------------------------------------
# 3. ANALYTICS & PLOTTING (Insights)
# --------------------------------------------------
def process_analytics(data_dict):
    report = {}
    plt.figure(figsize=(10, 6))

    for eps, signal in data_dict.items():
        peak = float(np.max(np.abs(signal)))
        arrival = float(np.argmax(np.abs(signal)) * CONFIG["dt"])
        
        report[eps] = {"peak": peak, "arrival": arrival}
        plt.plot(signal, label=f'Eps: {eps}')
        save_to_db(eps, peak, arrival)

    plt.title('GPR Parametric Sweep Analysis')
    plt.legend()
    plt.grid(True)
    
    os.makedirs(CONFIG["output_dir"], exist_ok=True)
    plt.savefig(f"{CONFIG['output_dir']}/analysis_plot.png")
    plt.close()  
    
    return report

# --------------------------------------------------
# 4. CORE ENGINE (Simulation)
# --------------------------------------------------
def run_framework():
    init_db()
    all_signals = {}

    for eps in CONFIG["eps_values"]:
        new_in = f"temp_eps_{eps}.in"
        try:
            with open(CONFIG["base_input"], 'r') as f:
                content = f.read().replace('MATERIAL_EPS', str(eps))

            with open(new_in, 'w') as f:
                f.write(content)

            print(f"🚀 Running Simulation: Eps {eps}")
            subprocess.run(['python', '-m', 'gprMax', new_in, '-n', '1'], check=True)

            out_file = new_in.replace('.in', '.out')
            all_signals[eps] = get_output_data(out_file, 1, CONFIG["component"])

        finally:
            if os.path.exists(new_in):
                os.remove(new_in)
                
        print(f"✅ Finished Eps {eps}")

    process_analytics(all_signals)
    print(f"\n✨ Pipeline Complete! Data saved in {CONFIG['db_name']}")

if __name__ == "__main__":
    run_framework()
