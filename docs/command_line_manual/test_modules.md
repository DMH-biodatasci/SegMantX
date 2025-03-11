---
id: test_modules
---

# Test modules

## ✅ Verify Installation & Test SegMantX's Modules
Check if the installation was successful by running:
```bash
cd SegMantX #Navigate to the SegMantX as this module requires 'test_commands.txt'
SegMantX test_modules
```

First, 'test_modules' downloads a test dataset (i.e., FASTA-files: NZ_CP051709.1, NZ_AP022172.1, NC_018218.1, NZ_CP018634.1, NZ_CP022004.1) and runs the core modules (i.e., generate_alignments, chain_self_alignments, chain_alignments, visualize_chains, fetch_nucleotide_chains) on these genomic sequences. You may want to inspect 'test_commands.txt' to see which commands and parameters are being tested. If something is wrong, an error will be displayed on the screen and an error report will be saved as error_report.txt.

A successful run of 'test_modules' will show this:
```bash
Checking alignment coordinates files ...
tests/NZ_CP051709.1.alignment_coordinates.tsv ok.
tests/NZ_AP022172.1.alignment_coordinates.tsv ok.
tests/NC_018218.1.alignment_coordinates.tsv ok.
tests/NZ_CP018634.1_vs_NZ_CP022004.1.alignment_coordinates.tsv ok.


Checking chained alignments files ...
tests/NZ_CP051709.1.chains.tsv ok.
tests/NZ_AP022172.1.chains.tsv ok.
tests/NC_018218.1.chains.tsv ok.
tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.tsv ok.


Checking chained alignments fasta files ...
tests/NZ_CP051709.1.chains.fasta ok.
tests/NZ_AP022172.1.chains.fasta ok.
tests/NC_018218.1.chains.fasta ok.
tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.fasta ok.


Checking plot files ...
tests/NZ_CP051709.1.html ok.
tests/NZ_AP022172.1.html ok.
tests/NC_018218.1.html ok.
tests/NZ_CP018634.1_vs_NZ_CP022004.1.html ok.


All modules are fine using the test data.
```