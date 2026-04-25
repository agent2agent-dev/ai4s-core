# Auto-generated Snakemake workflow for: Simulate the protein 1UBQ (ubiquitin) in a cubic water box with 0.15 M NaCl at 300 K for 100 ns using the AMBER99SB-ILDN force field. Use GROMACS with a 2 fs timestep and save coordinates every 10 ps.
# Domain: molecular_dynamics

rule step_0_wget:
    output:
        structure="1UBQ.pdb"
    shell:
        """wget https://files.rcsb.org/download/1UBQ.pdb"""

rule step_1_gmx:
    input:
        structure="1UBQ.pdb"
    output:
        structure="processed.gro"
        topology="topol.top"
    shell:
        """gmx pdb2gmx -f 1UBQ.pdb -o processed.gro -water tip3p -ff amber99sb-ildn"""

rule step_2_gmx:
    input:
        structure="processed.gro"
    output:
        structure="boxed.gro"
    shell:
        """gmx editconf -f processed.gro -o boxed.gro -c -d 1.0 -bt cubic"""

rule step_3_gmx:
    input:
        structure="boxed.gro"
        topology="topol.top"
    output:
        structure="solvated.gro"
        topology="topol.top"
    shell:
        """gmx solvate -cp boxed.gro -cs spc216.gro -o solvated.gro -p topol.top"""

rule step_4_gmx:
    input:
        structure="solvated.gro"
        topology="topol.top"
    output:
        tpr="ions.tpr"
    shell:
        """gmx grompp -f ions.mdp -c solvated.gro -p topol.top -o ions.tpr"""

rule step_5_gmx:
    input:
        tpr="ions.tpr"
        topology="topol.top"
    output:
        structure="neutralized.gro"
        topology="topol.top"
    shell:
        """echo 'SOL' | gmx genion -s ions.tpr -o neutralized.gro -p topol.top -pname NA -nname CL -neutral -conc 0.15"""

rule step_6_gmx:
    input:
        structure="neutralized.gro"
        topology="topol.top"
    output:
        tpr="em.tpr"
    shell:
        """gmx grompp -f em.mdp -c neutralized.gro -p topol.top -o em.tpr"""

rule step_7_gmx:
    input:
        tpr="em.tpr"
    output:
        structure="em.gro"
        log="em.log"
    shell:
        """gmx mdrun -deffnm em -v"""

rule step_8_gmx:
    input:
        structure="em.gro"
        topology="topol.top"
    output:
        tpr="nvt.tpr"
    shell:
        """gmx grompp -f nvt.mdp -c em.gro -r em.gro -p topol.top -o nvt.tpr"""

rule step_9_gmx:
    input:
        tpr="nvt.tpr"
    output:
        trajectory="nvt.xtc"
        structure="nvt.gro"
    shell:
        """gmx mdrun -deffnm nvt -v"""

rule step_10_gmx:
    input:
        structure="nvt.gro"
        topology="topol.top"
        checkpoint="nvt.cpt"
    output:
        tpr="npt.tpr"
    shell:
        """gmx grompp -f npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -o npt.tpr"""

rule step_11_gmx:
    input:
        tpr="npt.tpr"
    output:
        trajectory="npt.xtc"
        structure="npt.gro"
    shell:
        """gmx mdrun -deffnm npt -v"""

rule step_12_gmx:
    input:
        structure="npt.gro"
        topology="topol.top"
        checkpoint="npt.cpt"
    output:
        tpr="md.tpr"
    shell:
        """gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -o md.tpr"""

rule step_13_gmx:
    input:
        tpr="md.tpr"
    output:
        trajectory="md.xtc"
        structure="md.gro"
        energy="md.edr"
    shell:
        """gmx mdrun -deffnm md -v"""
