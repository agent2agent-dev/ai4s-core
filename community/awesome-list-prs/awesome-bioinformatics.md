## Add ai4s-core to Awesome Bioinformatics

**Name**: ai4s-core
**Link**: https://github.com/agent2agent-dev/ai4s-core
**Description**: Natural language workflow generator for bioinformatics pipelines. Generate validated scripts for RNA-seq, ATAC-seq, phylogenetics, genome assembly, and variant calling from plain English descriptions.

**Why it fits this list:**
ai4s-core brings natural language interfaces to bioinformatics by automating pipeline setup for common analyses. It generates step-by-step workflows with tool-specific parameters and includes domain validation for sequencing quality thresholds, read depth requirements, and reference genome compatibility.

**Example:**
```bash
$ ai4s plan "RNA-seq differential expression analysis with 3 replicates per condition" --format bash
→ Generates: QC, alignment, quantification, DE analysis workflow
```

**Key bioinformatics features:**
- RNA-seq, ATAC-seq, ChIP-seq, phylogenetics, genome assembly, variant calling
- Validates sequencing quality thresholds, read depth, reference genome compatibility
- Generates Snakemake-compatible workflow definitions
- Local LLM support — sensitive genomic data stays on your machine
- MIT license, 44 tests passing

**License**: MIT
**Language**: Python

---

*This PR adds ai4s-core to the awesome-bioinformatics list. Happy to adjust placement or description based on maintainer feedback.*
