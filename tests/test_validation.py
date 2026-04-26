"""
Test validation engine with domain-specific rules.
"""

import pytest
from ai4s_core.orchestrator import WorkflowOrchestrator, WorkflowPlan, WorkflowStep
from ai4s_core.validation import RuleRegistry, ValidationReport, ValidationIssue, Severity


class TestValidationEngine:
    def test_registry_init(self):
        """Test that RuleRegistry initializes with built-in rules."""
        reg = RuleRegistry()
        md_rules = reg.get_rules("molecular_dynamics")
        assert len(md_rules) > 0
        # Should have global rules + domain rules
        assert any(r.name == "non_empty_steps" for r in md_rules)
        assert any(r.name == "md_has_minimization" for r in md_rules)

    def test_validate_non_empty_steps(self):
        """Test that empty workflow is flagged."""
        reg = RuleRegistry()
        plan = WorkflowPlan(query="test", domain="molecular_dynamics", steps=[])
        report = reg.validate(plan)
        assert not report.passed
        assert any(i.field == "steps" and "no steps" in i.message.lower() for i in report.issues)

    def test_validate_md_minimization(self):
        """Test that MD workflow without minimization gets a warning."""
        reg = RuleRegistry()
        plan = WorkflowPlan(
            query="test",
            domain="molecular_dynamics",
            steps=[
                WorkflowStep(tool="gmx", command="gmx mdrun -deffnm run", description="Run MD"),
                WorkflowStep(tool="gmx", command="gmx mdrun -deffnm run2", description="Run more"),
                WorkflowStep(tool="gmx", command="gmx mdrun -deffnm run3", description="Run even more"),
            ],
        )
        report = reg.validate(plan)
        # Should have a warning about missing minimization
        assert any("minimization" in i.message.lower() for i in report.warnings())

    def test_validate_md_equilibration(self):
        """Test that MD workflow without equilibration gets a warning."""
        reg = RuleRegistry()
        plan = WorkflowPlan(
            query="test",
            domain="molecular_dynamics",
            steps=[
                WorkflowStep(tool="gmx", command="gmx mdrun -deffnm em", description="Energy minimization"),
                WorkflowStep(tool="gmx", command="gmx mdrun -deffnm run", description="Production run"),
                WorkflowStep(tool="gmx", command="gmx mdrun -deffnm run2", description="More production"),
                WorkflowStep(tool="gmx", command="gmx mdrun -deffnm run3", description="Even more"),
            ],
        )
        report = reg.validate(plan)
        assert any("equilibration" in i.message.lower() for i in report.warnings())

    def test_validate_md_temperature(self):
        """Test temperature validation catches extreme values."""
        reg = RuleRegistry()
        plan = WorkflowPlan(
            query="test",
            domain="molecular_dynamics",
            steps=[
                WorkflowStep(
                    tool="gmx",
                    command="gmx mdrun -deffnm nvt -ref_t=5000",
                    description="NVT at 5000K",
                ),
            ],
        )
        report = reg.validate(plan)
        assert any("temperature" in i.message.lower() for i in report.warnings())

    def test_validate_md_timestep(self):
        """Test timestep validation catches values that are too large."""
        reg = RuleRegistry()
        plan = WorkflowPlan(
            query="test",
            domain="molecular_dynamics",
            steps=[
                WorkflowStep(
                    tool="gmx",
                    command="gmx mdrun -deffnm run -dt=0.01",
                    description="Run with large timestep",
                ),
            ],
        )
        report = reg.validate(plan)
        assert any("timestep" in i.message.lower() for i in report.errors())

    def test_validate_dft_ecutwfc(self):
        """Test DFT cutoff energy validation."""
        reg = RuleRegistry()
        plan = WorkflowPlan(
            query="test",
            domain="density_functional_theory",
            steps=[
                WorkflowStep(
                    tool="pw.x",
                    command="pw.x -in scf.in && cat scf.in | grep ecutwfc=5",
                    description="SCF with low cutoff",
                ),
            ],
        )
        report = reg.validate(plan)
        assert any("ecutwfc" in i.message.lower() for i in report.errors())

    def test_validate_dft_kpoints(self):
        """Test DFT k-point mesh validation."""
        reg = RuleRegistry()
        plan = WorkflowPlan(
            query="test",
            domain="density_functional_theory",
            steps=[
                WorkflowStep(
                    tool="pw.x",
                    command="pw.x -in scf.in && echo 'K_POINTS' && echo '1 1 1'",
                    description="SCF with coarse k-points",
                ),
            ],
        )
        report = reg.validate(plan)
        assert any("k-point" in i.message.lower() for i in report.warnings())

    def test_validate_qc_basis_set(self):
        """Test quantum chemistry basis set validation."""
        reg = RuleRegistry()
        plan = WorkflowPlan(
            query="test",
            domain="quantum_chemistry",
            steps=[
                WorkflowStep(
                    tool="orca",
                    command="orca input.inp && cat input.inp | grep \"basis='STO-3G'\"",
                    description="Optimization with minimal basis",
                ),
            ],
        )
        report = reg.validate(plan)
        assert any("basis" in i.message.lower() for i in report.warnings())

    def test_validate_bio_quality_control(self):
        """Test bioinformatics QC validation."""
        reg = RuleRegistry()
        plan = WorkflowPlan(
            query="test",
            domain="bioinformatics",
            steps=[
                WorkflowStep(tool="hisat2", command="hisat2 -x genome", description="Alignment"),
                WorkflowStep(tool="featurecounts", command="featureCounts", description="Counting"),
            ],
        )
        report = reg.validate(plan)
        assert any("quality control" in i.message.lower() for i in report.warnings())

    def test_validate_bio_alignment(self):
        """Test bioinformatics alignment validation."""
        reg = RuleRegistry()
        plan = WorkflowPlan(
            query="test",
            domain="bioinformatics",
            steps=[
                WorkflowStep(tool="fastqc", command="fastqc reads.fq", description="QC"),
                WorkflowStep(tool="deseq2", command="Rscript deseq2.R", description="DE analysis"),
                WorkflowStep(tool="featurecounts", command="featureCounts", description="Counting"),
            ],
        )
        report = reg.validate(plan)
        assert any("alignment" in i.message.lower() for i in report.warnings())

    def test_circular_dependencies(self):
        """Test circular dependency detection."""
        reg = RuleRegistry()
        plan = WorkflowPlan(
            query="test",
            domain="molecular_dynamics",
            steps=[
                WorkflowStep(tool="a", command="a", dependencies=["1"]),
                WorkflowStep(tool="b", command="b", dependencies=["0"]),
            ],
        )
        report = reg.validate(plan)
        assert not report.passed
        assert any("circular" in i.message.lower() for i in report.errors())

    def test_invalid_dependency_index(self):
        """Test out-of-range dependency detection."""
        reg = RuleRegistry()
        plan = WorkflowPlan(
            query="test",
            domain="molecular_dynamics",
            steps=[
                WorkflowStep(tool="a", command="a", dependencies=["5"]),
            ],
        )
        report = reg.validate(plan)
        assert not report.passed
        assert any("invalid dependency" in i.message.lower() for i in report.errors())

    def test_report_merge(self):
        """Test ValidationReport merge functionality."""
        r1 = ValidationReport()
        r1.add(ValidationIssue(severity=Severity.WARNING, step_index=0, field="test", message="warn"))
        
        r2 = ValidationReport()
        r2.add(ValidationIssue(severity=Severity.ERROR, step_index=1, field="test", message="err"))
        
        r1.merge(r2)
        assert len(r1.issues) == 2
        assert not r1.passed
        assert len(r1.warnings()) == 1
        assert len(r1.errors()) == 1

    def test_all_domains_have_rules(self):
        """Test that all registered domains have validation rules."""
        reg = RuleRegistry()
        domains = ["molecular_dynamics", "density_functional_theory", "quantum_chemistry", "bioinformatics"]
        for domain in domains:
            rules = reg.get_rules(domain)
            assert len(rules) >= 3, f"Domain {domain} should have at least 3 rules (global + domain)"
            domain_specific = [r for r in rules if r.name not in ["non_empty_steps", "valid_dependencies", "no_circular_deps"]]
            assert len(domain_specific) >= 2, f"Domain {domain} should have at least 2 domain-specific rules"
