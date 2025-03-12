---
id: fetch_nucleotide_chains
---

# Fetch nucleotide chains

The `fetch_nucleotide_chains` module uses the yielded chaining results (tab-delimited table) to extract nucleotide chains in FASTA-format from the genomic sequence(s). 

## Input data:
The `fetch_nucleotide_chains` module requires the FASTA-file(s) to extract nucleotide chained sequences using the tab-delimited ouptut table of one of the chaining modules, for example, from SegMantX's `chain_self_alignments` or `chain_alignments` module:

[Click here to visit an example table](https://github.com/DMH-biodatasci/SegMantX/blob/main/docs/tbl/NC_018218.1.chains.tsv)

## Examples:
### I. Fetching chains from self-sequence alignment chaining:
```bash
SegMantX fetch_nucleotide_chains --input_file tests/NZ_AP022172.1.chains.tsv --fasta_file_query tests/NZ_AP022172.1.fasta --output_file tests/NZ_AP022172.1.chains.fasta
```
- `-i or --input_file`: Output file from chaining results as input.
- `-fq or --fasta_file_query`: Fasta file to extract from chains as nucleotide sequences.
- `-o, --output_file`: Output file: Fasta file containing nucleotide chains.

### II. Fetching chains from sequence alignment chaining between two distinct sequences:
```bash
SegMantX fetch_nucleotide_chains --input_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.tsv --fasta_file_query tests/NZ_CP018634.1.fasta  --fasta_file_subject tests/NZ_CP022004.1.fasta --output_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.fasta
```
- `-i or --input_file`: Output file from chaining results as input.
- `-fq or --fasta_file_query`: Fasta file to extract from chains as nucleotide sequences.
- `-fs or --fasta_file_subject`: Fasta file to extract from chains as nucleotide sequences.
- `-o, --output_file`: Output file: Fasta file containing nucleotide chains.

## Output:

Output of fetching nucleotide chains module:

| (Default) output filename | Description |
|:----------:|:-----------:|
| chains.fasta | A fasta file containing the nucleotide sequences of yielded chains. | 



For example:
```bash
>1_query NZ_CP018634.1:90564-130134 (+)
TCACGCACAGGGCACTCGTCTTACAGGCAGGTTTTGAATACAGAAAGCCGGCCGGCATTG
CCGGCTGATATCTGACTGACGCGTCAGTTAATTAATCCGTGGCTTTCCCCACACGGACGG
TTTAATGACAAAAAATACGCCGGACGGCTGATGGTAAATATCCTGGCTGTCAATATAGGG
CGCTATCCATAACGCCGCCGTCTGTTCCCCGGTTCTCAGTGGTCGGGGCGGTACCACAGG
AGAGGCCGTACTGACAGGTGCCACCGTTTTCACCTCCCGGGCAGCCGTAAACAGCGGGTG
TGGTGTCGGCGGTTTCTGCCCGGAACGTGGGGCGATCACTGTCTTTCCGACGGGCGGTGT
...
>1_subject NZ_CP022004.1:90267-50339 (-)
ATGAACCCAGTGATGAGGAGTTTAAAAATGCCATGTCAGTTTATATAAATGATATTGCGG
AGGGATTAAGTTCACTTCCCGAAACAGATCACAGAGTCGTATACCGGGGCCTGAAGCTTG
ATAAGCCCGCATTATCGGATGTGCTGAAGGAATACACTACTATAGGTAATATAATAATAG
ATAAAGCTTTTATGAGTACATCGCCAGATAAGGCATGGATAAATGACACTATTCTCAACA
TATACCTAGAAAAAGGACATAAAGGTAGAATACTCGGAGATGTTGCACATTTTAAGGGAG
AGGCAGAGATGCTTTTCCCTCCAAATACTAAACTCAAAATCGAAAGCATTGTAAATTGTG
...
```