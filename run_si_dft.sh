#!/usr/bin/env bash
# Auto-generated workflow for: Calculate the electronic band structure of silicon (diamond cubic) using DFT with the PBE exchange-correlation functional. Use a plane-wave cutoff of 40 Ry and a 8x8x8 k-point grid for SCF. Plot the band structure along the Gamma-X-W-L-Gamma high-symmetry path.
# Domain: density_functional_theory
set -euo pipefail

# Step 0: Download silicon structure (diamond cubic)
echo "[Step 0] wget: Download silicon structure (diamond cubic)"
wget https://materialsproject.org/static/cifs/Si.cif -O Si.cif

# Step 1: Convert CIF to Quantum ESPRESSO input format
echo "[Step 1] cif2cell: Convert CIF to Quantum ESPRESSO input format"
cif2cell Si.cif -p quantum-espresso -o Si.pw.in

# Step 2: Self-consistent field (SCF) calculation
echo "[Step 2] pw.x: Self-consistent field (SCF) calculation"
mpirun -np 8 pw.x -in Si.scf.in > Si.scf.out

# Step 3: Non-SCF band structure calculation along high-symmetry path
echo "[Step 3] pw.x: Non-SCF band structure calculation along high-symmetry path"
mpirun -np 8 pw.x -in Si.bands.in > Si.bands.out

# Step 4: Post-process band structure data
echo "[Step 4] bands.x: Post-process band structure data"
bands.x -in Si.bands.pp.in > Si.bands.pp.out

# Step 5: Calculate density of states
echo "[Step 5] dos.x: Calculate density of states"
dos.x -in Si.dos.in > Si.dos.out

# Step 6: Plot band structure
echo "[Step 6] gnuplot: Plot band structure"
gnuplot plot_bands.gnu
