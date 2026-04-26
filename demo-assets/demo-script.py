#!/usr/bin/env python3
"""
Auto-generated workflow for: Run MD simulation of 1UBQ
Domain: molecular_dynamics
"""

import subprocess
import sys
import json
from pathlib import Path

WORKFLOW = {
    "query": "Run MD simulation of 1UBQ",
    "domain": "molecular_dynamics",
    "steps": [
        {
            "tool": "wget",
            "command": "wget https://files.rcsb.org/download/1UBQ.pdb",
            "inputs": {},
            "outputs": {
                "structure": "1UBQ.pdb"
            },
            "dependencies": [],
            "description": "Download ubiquitin structure from PDB",
            "auxiliary_files": {},
            "error_handling": {}
        },
        {
            "tool": "gmx",
            "command": "gmx pdb2gmx -f 1UBQ.pdb -o processed.gro -water tip3p -ff amber99sb-ildn",
            "inputs": {
                "structure": "1UBQ.pdb"
            },
            "outputs": {
                "structure": "processed.gro",
                "topology": "topol.top"
            },
            "dependencies": [
                "0"
            ],
            "description": "Process structure and generate topology",
            "auxiliary_files": {},
            "error_handling": {}
        },
        {
            "tool": "gmx",
            "command": "gmx editconf -f processed.gro -o boxed.gro -c -d 1.0 -bt cubic",
            "inputs": {
                "structure": "processed.gro"
            },
            "outputs": {
                "structure": "boxed.gro"
            },
            "dependencies": [
                "1"
            ],
            "description": "Define simulation box",
            "auxiliary_files": {},
            "error_handling": {}
        },
        {
            "tool": "gmx",
            "command": "gmx solvate -cp boxed.gro -cs spc216.gro -o solvated.gro -p topol.top",
            "inputs": {
                "structure": "boxed.gro",
                "topology": "topol.top"
            },
            "outputs": {
                "structure": "solvated.gro",
                "topology": "topol.top"
            },
            "dependencies": [
                "2"
            ],
            "description": "Add water molecules to box",
            "auxiliary_files": {},
            "error_handling": {}
        },
        {
            "tool": "gmx",
            "command": "gmx grompp -f ions.mdp -c solvated.gro -p topol.top -o ions.tpr",
            "inputs": {
                "structure": "solvated.gro",
                "topology": "topol.top"
            },
            "outputs": {
                "tpr": "ions.tpr"
            },
            "dependencies": [
                "3"
            ],
            "description": "Prepare input for ion addition",
            "auxiliary_files": {
                "ions.mdp": "; ions.mdp - preprocessing for genion\nintegrator  = steep\nemtol       = 1000.0\nemstep      = 0.01\nnsteps       = 5000\nnstlist      = 1\ncoulombtype  = PME\nrcoulomb     = 1.0\nrvdw         = 1.0\npbc          = xyz\n"
            },
            "error_handling": {}
        },
        {
            "tool": "gmx",
            "command": "echo 'SOL' | gmx genion -s ions.tpr -o neutralized.gro -p topol.top -pname NA -nname CL -neutral -conc 0.15",
            "inputs": {
                "tpr": "ions.tpr",
                "topology": "topol.top"
            },
            "outputs": {
                "structure": "neutralized.gro",
                "topology": "topol.top"
            },
            "dependencies": [
                "4"
            ],
            "description": "Add ions to neutralize and reach 0.15 M NaCl",
            "auxiliary_files": {},
            "error_handling": {}
        },
        {
            "tool": "gmx",
            "command": "gmx grompp -f em.mdp -c neutralized.gro -p topol.top -o em.tpr",
            "inputs": {
                "structure": "neutralized.gro",
                "topology": "topol.top"
            },
            "outputs": {
                "tpr": "em.tpr"
            },
            "dependencies": [
                "5"
            ],
            "description": "Prepare energy minimization input",
            "auxiliary_files": {
                "em.mdp": "; em.mdp - energy minimization\nintegrator  = steep\nemtol       = 1000.0\nemstep      = 0.01\nnsteps       = 50000\nnstlist      = 1\ncoulombtype  = PME\nrcoulomb     = 1.0\nrvdw         = 1.0\npbc          = xyz\n"
            },
            "error_handling": {}
        },
        {
            "tool": "gmx",
            "command": "gmx mdrun -deffnm em -v",
            "inputs": {
                "tpr": "em.tpr"
            },
            "outputs": {
                "structure": "em.gro",
                "log": "em.log"
            },
            "dependencies": [
                "6"
            ],
            "description": "Run energy minimization",
            "auxiliary_files": {},
            "error_handling": {
                "check_file": "em.gro",
                "fallback": "Increase nsteps in em.mdp and retry"
            }
        },
        {
            "tool": "gmx",
            "command": "gmx grompp -f nvt.mdp -c em.gro -r em.gro -p topol.top -o nvt.tpr",
            "inputs": {
                "structure": "em.gro",
                "topology": "topol.top"
            },
            "outputs": {
                "tpr": "nvt.tpr"
            },
            "dependencies": [
                "7"
            ],
            "description": "Prepare NVT equilibration input",
            "auxiliary_files": {
                "nvt.mdp": "; nvt.mdp - NVT equilibration\ndefine       = -DPOSRES\nintegrator   = md\ndt           = 0.002\nnsteps        = 50000\nnstxout      = 500\nnstvout      = 500\nnstenergy    = 500\nnstlog       = 500\ncontinuation = no\nconstraint_algorithm = lincs\nconstraints  = h-bonds\nlincs_iter   = 1\nlincs_order  = 4\ncoulombtype  = PME\nrcoulomb     = 1.0\nrvdw         = 1.0\nDispCorr     = EnerPres\ntcoupl       = V-rescale\ntc-grps      = Protein Non-Protein\ntau_t        = 0.1     0.1\nref_t        = 300     300\npbc          = xyz\n"
            },
            "error_handling": {}
        },
        {
            "tool": "gmx",
            "command": "gmx mdrun -deffnm nvt -v",
            "inputs": {
                "tpr": "nvt.tpr"
            },
            "outputs": {
                "trajectory": "nvt.xtc",
                "structure": "nvt.gro"
            },
            "dependencies": [
                "8"
            ],
            "description": "Run NVT equilibration (100 ps)",
            "auxiliary_files": {},
            "error_handling": {
                "check_file": "nvt.gro",
                "temperature_target": 300,
                "temperature_tolerance": 10
            }
        },
        {
            "tool": "gmx",
            "command": "gmx grompp -f npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -o npt.tpr",
            "inputs": {
                "structure": "nvt.gro",
                "topology": "topol.top",
                "checkpoint": "nvt.cpt"
            },
            "outputs": {
                "tpr": "npt.tpr"
            },
            "dependencies": [
                "9"
            ],
            "description": "Prepare NPT equilibration input",
            "auxiliary_files": {
                "npt.mdp": "; npt.mdp - NPT equilibration\ndefine       = -DPOSRES\nintegrator   = md\ndt           = 0.002\nnsteps        = 50000\nnstxout      = 500\nnstvout      = 500\nnstenergy    = 500\nnstlog       = 500\ncontinuation = yes\nconstraint_algorithm = lincs\nconstraints  = h-bonds\nlincs_iter   = 1\nlincs_order  = 4\ncoulombtype  = PME\nrcoulomb     = 1.0\nrvdw         = 1.0\nDispCorr     = EnerPres\ntcoupl       = V-rescale\ntc-grps      = Protein Non-Protein\ntau_t        = 0.1     0.1\nref_t        = 300     300\npcoupl       = Parrinello-Rahman\npcoupltype   = isotropic\ntau_p        = 2.0\nref_p        = 1.0\ncompressibility = 4.5e-5\npbc          = xyz\n"
            },
            "error_handling": {}
        },
        {
            "tool": "gmx",
            "command": "gmx mdrun -deffnm npt -v",
            "inputs": {
                "tpr": "npt.tpr"
            },
            "outputs": {
                "trajectory": "npt.xtc",
                "structure": "npt.gro"
            },
            "dependencies": [
                "10"
            ],
            "description": "Run NPT equilibration (100 ps)",
            "auxiliary_files": {},
            "error_handling": {
                "check_file": "npt.gro",
                "pressure_target": 1.0,
                "pressure_tolerance": 5.0,
                "density_target": 1000,
                "density_tolerance": 50
            }
        },
        {
            "tool": "gmx",
            "command": "gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -o md.tpr",
            "inputs": {
                "structure": "npt.gro",
                "topology": "topol.top",
                "checkpoint": "npt.cpt"
            },
            "outputs": {
                "tpr": "md.tpr"
            },
            "dependencies": [
                "11"
            ],
            "description": "Prepare production MD input (100 ns)",
            "auxiliary_files": {
                "md.mdp": "; md.mdp - production MD run\nintegrator   = md\ndt           = 0.002\nnsteps        = 50000000\nnstxout      = 5000\nnstvout      = 5000\nnstenergy    = 5000\nnstlog       = 5000\ncontinuation = yes\nconstraint_algorithm = lincs\nconstraints  = h-bonds\nlincs_iter   = 1\nlincs_order  = 4\ncoulombtype  = PME\nrcoulomb     = 1.0\nrvdw         = 1.0\nDispCorr     = EnerPres\ntcoupl       = V-rescale\ntc-grps      = Protein Non-Protein\ntau_t        = 0.1     0.1\nref_t        = 300     300\npcoupl       = Parrinello-Rahman\npcoupltype   = isotropic\ntau_p        = 2.0\nref_p        = 1.0\ncompressibility = 4.5e-5\npbc          = xyz\n"
            },
            "error_handling": {}
        },
        {
            "tool": "gmx",
            "command": "gmx mdrun -deffnm md -v",
            "inputs": {
                "tpr": "md.tpr"
            },
            "outputs": {
                "trajectory": "md.xtc",
                "structure": "md.gro",
                "energy": "md.edr"
            },
            "dependencies": [
                "12"
            ],
            "description": "Run production MD simulation (100 ns)",
            "auxiliary_files": {},
            "error_handling": {
                "check_file": "md.gro",
                "min_simulation_time_ns": 10
            }
        }
    ],
    "estimated_compute": "~12 hours on 8 CPU cores or ~4 hours on 1 GPU (RTX 3090)",
    "required_software": [
        "GROMACS 2023+",
        "wget"
    ],
    "validation_checks": [
        "Energy minimized to < 1000 kJ/mol/nm",
        "NVT temperature stable at 300 K",
        "NPT pressure stable at 1 bar",
        "Density converged to ~1000 kg/m^3 for water",
        "RMSD stable during production run"
    ]
}

def write_auxiliary_files(step):
    """Write auxiliary files (e.g., MDP, input files) for a step."""
    aux = step.get("auxiliary_files", {})
    for filename, content in aux.items():
        Path(filename).write_text(content)
        print(f"  [Written] {filename}")

def check_error_handling(step, step_idx):
    """Check error handling conditions after a step runs."""
    eh = step.get("error_handling", {})
    if not eh:
        return True
    check_file = eh.get("check_file")
    if check_file and not Path(check_file).exists():
        print(f"  [ERROR] Expected output {check_file} not found")
        fallback = eh.get("fallback")
        if fallback:
            print(f"  [Fallback] {fallback}")
        return False
    return True

def run_step(step, step_idx):
    print(f"[Step {step_idx}] {step['tool']}: {step['description']}")
    write_auxiliary_files(step)
    cmd = step["command"]
    print(f"  Command: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"  [OK] Exit code: {result.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Command failed with exit code {e.returncode}")
        print(f"  stderr: {e.stderr[:500]}")
        check_error_handling(step, step_idx)
        sys.exit(1)
    check_error_handling(step, step_idx)

def main():
    # Step 0: Download ubiquitin structure from PDB
    run_step(WORKFLOW['steps'][0], 0)

    # Step 1: Process structure and generate topology
    run_step(WORKFLOW['steps'][1], 1)

    # Step 2: Define simulation box
    run_step(WORKFLOW['steps'][2], 2)

    # Step 3: Add water molecules to box
    run_step(WORKFLOW['steps'][3], 3)

    # Step 4: Prepare input for ion addition
    run_step(WORKFLOW['steps'][4], 4)

    # Step 5: Add ions to neutralize and reach 0.15 M NaCl
    run_step(WORKFLOW['steps'][5], 5)

    # Step 6: Prepare energy minimization input
    run_step(WORKFLOW['steps'][6], 6)

    # Step 7: Run energy minimization
    run_step(WORKFLOW['steps'][7], 7)

    # Step 8: Prepare NVT equilibration input
    run_step(WORKFLOW['steps'][8], 8)

    # Step 9: Run NVT equilibration (100 ps)
    run_step(WORKFLOW['steps'][9], 9)

    # Step 10: Prepare NPT equilibration input
    run_step(WORKFLOW['steps'][10], 10)

    # Step 11: Run NPT equilibration (100 ps)
    run_step(WORKFLOW['steps'][11], 11)

    # Step 12: Prepare production MD input (100 ns)
    run_step(WORKFLOW['steps'][12], 12)

    # Step 13: Run production MD simulation (100 ns)
    run_step(WORKFLOW['steps'][13], 13)

if __name__ == "__main__":
    main()

