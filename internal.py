from concurrent.futures import ThreadPoolExecutor
import os
import subprocess
import sys
from gprMax.tools.output_stats import get_output_data
import matplotlib.pyplot as plt
import numpy as np

# Simulation Settings
base_input_file = 'user_model.in'
permittivity_values = [3.0, 5.0, 8.0]
output_dir = 'parametric_results'

os.makedirs(output_dir, exist_ok=True)


def run_simulation(eps_value):
    new_filename = os.path.join(output_dir, f'model_eps_{eps_value}.in')

    with open(base_input_file, 'r') as f:
        content = f.read()

    updated_content = content.replace('MATERIAL_EPS', str(eps_value))

    with open(new_filename, 'w') as f:
        f.write(updated_content)

    print(f'🚀 Running gprMax simulation for Eps: {eps_value}...')
    try:
        subprocess.run(
            [sys.executable, '-m', 'gprMax', new_filename, '-n', '1'],
            check=True,
        )

        output_file = new_filename.replace('.in', '.out')
        rx_data = get_output_data(output_file, 1, 'Ez')
        return eps_value, rx_data
    finally:
        # Cleanup temporary input file safely
        if os.path.exists(new_filename):
            os.remove(new_filename)


def run_parametric_sweep():
    plt.figure(figsize=(12, 6))

    # Parallelize simulations across permittivity values
    with ThreadPoolExecutor(max_workers=min(4, os.cpu_count() or 1)) as executor:
        results = list(executor.map(run_simulation, permittivity_values))

    # Sort results by permittivity for consistent plotting
    results.sort(key=lambda x: x[0])
