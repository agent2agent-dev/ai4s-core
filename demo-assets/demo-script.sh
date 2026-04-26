#!/usr/bin/env bash
# Auto-generated workflow for: Run MD simulation of 1UBQ
# Domain: molecular_dynamics
set -euo pipefail

# Write auxiliary files
# Step 4: Prepare input for ion addition
cat > 'ions.mdp' << 'EOF'
; ions.mdp - preprocessing for genion
integrator  = steep
emtol       = 1000.0
emstep      = 0.01
nsteps       = 5000
nstlist      = 1
coulombtype  = PME
rcoulomb     = 1.0
rvdw         = 1.0
pbc          = xyz

EOF

# Step 6: Prepare energy minimization input
cat > 'em.mdp' << 'EOF'
; em.mdp - energy minimization
integrator  = steep
emtol       = 1000.0
emstep      = 0.01
nsteps       = 50000
nstlist      = 1
coulombtype  = PME
rcoulomb     = 1.0
rvdw         = 1.0
pbc          = xyz

EOF

# Step 8: Prepare NVT equilibration input
cat > 'nvt.mdp' << 'EOF'
; nvt.mdp - NVT equilibration
define       = -DPOSRES
integrator   = md
dt           = 0.002
nsteps        = 50000
nstxout      = 500
nstvout      = 500
nstenergy    = 500
nstlog       = 500
continuation = no
constraint_algorithm = lincs
constraints  = h-bonds
lincs_iter   = 1
lincs_order  = 4
coulombtype  = PME
rcoulomb     = 1.0
rvdw         = 1.0
DispCorr     = EnerPres
tcoupl       = V-rescale
tc-grps      = Protein Non-Protein
tau_t        = 0.1     0.1
ref_t        = 300     300
pbc          = xyz

EOF

# Step 10: Prepare NPT equilibration input
cat > 'npt.mdp' << 'EOF'
; npt.mdp - NPT equilibration
define       = -DPOSRES
integrator   = md
dt           = 0.002
nsteps        = 50000
nstxout      = 500
nstvout      = 500
nstenergy    = 500
nstlog       = 500
continuation = yes
constraint_algorithm = lincs
constraints  = h-bonds
lincs_iter   = 1
lincs_order  = 4
coulombtype  = PME
rcoulomb     = 1.0
rvdw         = 1.0
DispCorr     = EnerPres
tcoupl       = V-rescale
tc-grps      = Protein Non-Protein
tau_t        = 0.1     0.1
ref_t        = 300     300
pcoupl       = Parrinello-Rahman
pcoupltype   = isotropic
tau_p        = 2.0
ref_p        = 1.0
compressibility = 4.5e-5
pbc          = xyz

EOF

# Step 12: Prepare production MD input (100 ns)
cat > 'md.mdp' << 'EOF'
; md.mdp - production MD run
integrator   = md
dt           = 0.002
nsteps        = 50000000
nstxout      = 5000
nstvout      = 5000
nstenergy    = 5000
nstlog       = 5000
continuation = yes
constraint_algorithm = lincs
constraints  = h-bonds
lincs_iter   = 1
lincs_order  = 4
coulombtype  = PME
rcoulomb     = 1.0
rvdw         = 1.0
DispCorr     = EnerPres
tcoupl       = V-rescale
tc-grps      = Protein Non-Protein
tau_t        = 0.1     0.1
ref_t        = 300     300
pcoupl       = Parrinello-Rahman
pcoupltype   = isotropic
tau_p        = 2.0
ref_p        = 1.0
compressibility = 4.5e-5
pbc          = xyz

EOF


# Run workflow steps
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
if [ ! -f 'em.gro' ]; then
    echo "[WARNING] Expected output em.gro not found"
    echo "[Fallback] Increase nsteps in em.mdp and retry"
fi
gmx mdrun -deffnm em -v

# Step 8: Prepare NVT equilibration input
echo "[Step 8] gmx: Prepare NVT equilibration input"
gmx grompp -f nvt.mdp -c em.gro -r em.gro -p topol.top -o nvt.tpr

# Step 9: Run NVT equilibration (100 ps)
echo "[Step 9] gmx: Run NVT equilibration (100 ps)"
if [ ! -f 'nvt.gro' ]; then
    echo "[WARNING] Expected output nvt.gro not found"
fi
gmx mdrun -deffnm nvt -v

# Step 10: Prepare NPT equilibration input
echo "[Step 10] gmx: Prepare NPT equilibration input"
gmx grompp -f npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -o npt.tpr

# Step 11: Run NPT equilibration (100 ps)
echo "[Step 11] gmx: Run NPT equilibration (100 ps)"
if [ ! -f 'npt.gro' ]; then
    echo "[WARNING] Expected output npt.gro not found"
fi
gmx mdrun -deffnm npt -v

# Step 12: Prepare production MD input (100 ns)
echo "[Step 12] gmx: Prepare production MD input (100 ns)"
gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -o md.tpr

# Step 13: Run production MD simulation (100 ns)
echo "[Step 13] gmx: Run production MD simulation (100 ns)"
if [ ! -f 'md.gro' ]; then
    echo "[WARNING] Expected output md.gro not found"
fi
gmx mdrun -deffnm md -v

