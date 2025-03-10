---
id: quick_start
---

# Quick start

## Purpose:

**SegMantX** is a bioinformatics tool designed for chaining local alignments towards the detection of DNA duplications in genomic sequences. The application purposes of SegMantX are:

1. Duplication detection
2. Sequence comparison

## Input data:

**SegMantX** only requires a (genomic) nucleotide sequence in FASTA-format. First, SegMantX's [suggested workflow](https://dmh-biodatasci.github.io/SegMantX/module_overview.html) integrates BLASTn to compute local alignments as seeds for the chaining process. 

Alternatively, the generation of local alignments using BLASTn is optional as the chaining modules accept any input (i.e., seed or alignment coordinates) that provide the following exemplified data:

| Query start | Query end | Subject start | Subject end | Percent sequence identity |
|:-----------:|:---------:|:-------------:|:-----------:|:-------------------------:|
| 133470      | 147930    | 64534         | 78969       | 95.1                      |
| ...         | ...       | ...           | ...         | ...                       |
| 329875      | 330416    | 326586         | 327127     | 93                        |

## Installation:

Please clone the SegMantX repository:

```bash
# Clone the repository
git clone https://github.com/DMH-biodatasci/SegMantX.git
cd SegMantX
```

Afterwards, choose an installation procedure that works for your machine:

Hint: The platform-independent installation may be required for older Miniconda versions.

- [Linux](https://dmh-biodatasci.github.io/SegMantX/installation/linux.html)
- [MacOS](https://dmh-biodatasci.github.io/SegMantX/installation/macos.html)
- [Windows](https://dmh-biodatasci.github.io/SegMantX/installation/windows.html)
- [Platform-independent installation](https://dmh-biodatasci.github.io/SegMantX/installation/independent.html)
- [Docker](https://dmh-biodatasci.github.io/SegMantX/installation/docker.html)


## ✅ Verify Installation & Test SegMantX's Modules
Check if the installation was successful by running:
```bash
cd SegMantX #Navigate to the SegMantX directory as this module requires 'test_commands.txt' and 'test' directory
SegMantX test_modules
```

## Get started

Below we show two examples running SegMantX on the test dataset towards the (I.) duplication detection and (II.) sequence comparison. For a detailed description and manual of individual modules visit:

Core modules:
- [generate_alignments](https://dmh-biodatasci.github.io/SegMantX/command_line_manual/generate_alignments.html)
- [chain_self_alignments](https://dmh-biodatasci.github.io/SegMantX/command_line_manual/chain_self_alignments.html)
- [chain_alignments](https://dmh-biodatasci.github.io/SegMantX/command_line_manual/chain_alignments.html)
- [visualize_chains](https://dmh-biodatasci.github.io/SegMantX/command_line_manual/visualize_chains.html)
- [fetch_nucleotide_chains](https://dmh-biodatasci.github.io/SegMantX/command_line_manual/fetch_nucleotide_chains.html)

Optional modules (and help):
- [test_modules](https://dmh-biodatasci.github.io/SegMantX/command_line_manual/test_modules.html)
- [help](https://dmh-biodatasci.github.io/SegMantX/command_line_manual/help.html)
- [version](https://dmh-biodatasci.github.io/SegMantX/command_line_manual/version.html)
- [citation](https://dmh-biodatasci.github.io/SegMantX/command_line_manual/citation.html)

### I. Workflow towards duplication detection

The following workflow demonstrates the duplication detection computing a self-alignment of a (circular) plasmid sequence. Afterwards, the hits in the self-alignment will processed in the chaining module. An interactive plot visualizing resulting segments (or chains) and a FASTA-file containing the nucleotide chains will be created.

Hint: Use --is_query_circular only if your sequence has a circular sequence topology (e.g., circular plasmids)

1. Run SegMantX's **generate_alignments** module to compute seeds for the chaining process:
```bash
#Compute a self-sequence alignment:
SegMantX generate_alignments --query_file tests/NZ_AP022172.1.fasta --blast_output_file tests/NZ_AP022172.1.blast.x7 --alignment_hits_file tests/NZ_AP022172.1.alignment_coordinates.tsv --is_query_circular --self_sequence_alignment
```

2. Run SegMantX's **chain_self_alignments** module for chaining a self-sequence alignment (e.g., towards duplication detection):
```bash
SegMantX chain_self_alignments --input_file tests/NZ_AP022172.1.alignment_coordinates.tsv --max_gap 5000 --scaled_gap 1 --fasta_file tests/NZ_AP022172.1.fasta --is_query_circular --output_file tests/NZ_AP022172.1.chains.tsv
```

3. Run SegMantX's **fetch_nucleotide_chains** module to extract chains as nucleotide sequences from a FASTA-file:
```bash
#Visualize chaining results of one sequence (i.e., towards duplication detection)
SegMantX visualize_chains --input_file tests/NZ_AP022172.1.chains.tsv --scale kbp --output_file tests/NZ_AP022172.1.html --fasta_file_query  tests/NZ_AP022172.1.fasta --query_is_subject --genbank_file tests/NZ_AP022172.1.gbk
```

4. Run SegMantX's **visualize_chains** module to visualize chains in an interactive segmentplot:
```bash
#Get sequences for duplication downstream analysis:
SegMantX fetch_nucleotide_chains --input_file tests/NZ_AP022172.1.chains.tsv --fasta_file_query tests/NZ_AP022172.1.fasta --output_file tests/NZ_AP022172.1.chains.fasta
```

### II. Workflow towards sequence comparisons
The following workflow demonstrates the sequence comparison computing an alignment between two (circular) plasmid sequences. Afterwards, the hits in the alignment will processed in the chaining module. An interactive plot visualizing resulting segments (or chains) between the two plasmid sequences and a FASTA-file containing the nucleotide chains will be created.

1. Run SegMantX's **generate_alignments** module to compute seeds for the chaining process:
```bash
##Compute a sequence alignment between two sequences:
SegMantX generate_alignments  --query_file tests/NZ_CP018634.1.fasta --subject_file tests/NZ_CP022004.1.fasta --blast_output_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.blast.x7 --alignment_hits_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.alignment_coordinates.tsv --is_query_circular --is_subject_circular 
```

2. Run SegMantX's **chain_alignments** module for chaining a sequence alignment (e.g., towards sequence comparison):
```bash
SegMantX chain_alignments --input_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.alignment_coordinates.tsv --fasta_file_query tests/NZ_CP018634.1.fasta --fasta_file_subject tests/NZ_CP022004.1.fasta --max_gap 5000 --scaled_gap 1 --is_query_circular --is_subject_circular --min_length 100 -o tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.tsv
```

3. Run SegMantX's **visualize_chains** module to visualize chains in an interactive segmentplot:
```bash
#Visualize chaining results of two sequences (i.e., towards sequence comparison)
SegMantX visualize_chains --input_file  tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.tsv --scale kbp --output_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.html --fasta_file_query tests/NZ_CP018634.1.fasta --fasta_file_subject tests/NZ_CP022004.1.fasta
```

4. Run SegMantX's **fetch_nucleotide_chains** module to extract chains as nucleotide sequences from a FASTA-file:
```bash
#Get sequences for sequence comparison downstream analysis:
SegMantX fetch_nucleotide_chains --input_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.tsv --fasta_file_query tests/NZ_CP018634.1.fasta  --fasta_file_subject tests/NZ_CP022004.1.fasta --output_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.fasta
```