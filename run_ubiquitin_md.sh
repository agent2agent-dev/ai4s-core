#!/usr/bin/env bash
# Auto-generated workflow for: Simulate the protein 1UBQ (ubiquitin) in a cubic water box with 0.15 M NaCl at 300 K for 100 ns using the AMBER99SB-ILDN force field. Use GROMACS with a 2 fs timestep and save coordinates every 10 ps.
# Domain: molecular_dynamics
set -euo pipefail

# Step 0: Download ubiquitin structure from PDB
echo "[Step 0] wget: Download ubiquitin structure from PDB"
wget https://files.rcsb.org/download/1UBQ.pdb

# Step 1: Process structure and generate topology
echo "[Step 1] gmx: Process structure and generate topology"
gmx pdb2gmx -f 1UBQ.pdb -o processed.gro -water tip3p -ff amber99sb-ildn

# Step 2: Define simulation box
echo "[Step 2] gmx: Define simulation box"
gmx editconf -f processed.gro -o boxed.gro -c -d 1.0 -bt cubic

# Step 3: Add water molecules to box
echo "[Step 3] gmx: Add water molecules to box"
gmx solvate -cp boxed.gro -cs spc216.gro -o solvated.gro -p topol.top

# Step 4: Prepare input for ion addition
echo "[Step 4] gmx: Prepare input for ion addition"
gmx grompp -f ions.mdp -c solvated.gro -p topol.top -o ions.tpr

# Step 5: Add ions to neutralize and reach 0.15 M NaCl
echo "[Step 5] gmx: Add ions to neutralize and reach 0.15 M NaCl"
echo 'SOL' | gmx genion -s ions.tpr -o neutralized.gro -p topol.top -pname NA -nname CL -neutral -conc 0.15

# Step 6: Prepare energy minimization input
echo "[Step 6] gmx: Prepare energy minimization input"
gmx grompp -f em.mdp -c neutralized.gro -p topol.top -o em.tpr

# Step 7: Run energy minimization
echo "[Step 7] gmx: Run energy minimization"
gmx mdrun -deffnm em -v

# Step 8: Prepare NVT equilibration input
echo "[Step 8] gmx: Prepare NVT equilibration input"
gmx grompp -f nvt.mdp -c em.gro -r em.gro -p topol.top -o nvt.tpr

# Step 9: Run NVT equilibration (100 ps)
echo "[Step 9] gmx: Run NVT equilibration (100 ps)"
gmx mdrun -deffnm nvt -v

# Step 10: Prepare NPT equilibration input
echo "[Step 10] gmx: Prepare NPT equilibration input"
gmx grompp -f npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -o npt.tpr

# Step 11: Run NPT equilibration (100 ps)
echo "[Step 11] gmx: Run NPT equilibration (100 ps)"
gmx mdrun -deffnm npt -v

# Step 12: Prepare production MD input (100 ns)
echo "[Step 12] gmx: Prepare production MD input (100 ns)"
gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -o md.tpr

# Step 13: Run production MD simulation (100 ns)
echo "[Step 13] gmx: Run production MD simulation (100 ns)"
gmx mdrun -deffnm md -v
