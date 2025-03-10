---
id: module_overview
---

# Workflow & Overview

**SegMantX** is organized into modules. This is a graphical abstract for the suggested workflow:

<p align="center">
  <img src="img/workflow.png" alt="Workflow" width="1000" height="auto">
</p>

1. [Generate alignments](https://dmh-biodatasci.github.io/SegMantX/command_line_manual/generate_alignments.html): processes nucleotide sequence(s) to compute local alignments, optionally formatting them for further analysis. 
2. [Chain self-alignments](https://dmh-biodatasci.github.io/SegMantX/command_line_manual/chain_self_alignments.html): Chains local alignments from self-sequence alignment (e.g., towards duplication detection).
3. [Chaing alignments](https://dmh-biodatasci.github.io/SegMantX/command_line_manual/chain_alignments.html): Chains local alignments between two sequences (e.g., towards sequence comparisons).
4. [Visualize chains](https://dmh-biodatasci.github.io/SegMantX/command_line_manual/visualize_chains.html): Generates a segmentplot (i.e., segments of chaining results) to visualize yielded chains for a sequence (self-alignment) or two sequences (alignment).
5. [Fetch nucleotide chains](https://dmh-biodatasci.github.io/SegMantX/command_line_manual/fetch_nucleotide_chains.html): Extracts yielded chains as nucleotide sequences and saves them as fasta file.
