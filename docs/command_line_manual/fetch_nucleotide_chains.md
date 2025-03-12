---
id: fetch_nucleotide_chains
---

# Fetch nucleotide chains

The `fetch_nucleotide_chains` module uses the yielded chaining results (tab-delimited table) to extract nucleotide chains in FASTA-format from the genomic sequence(s). 

## Input data:
The `fetch_nucleotide_chains` module requires the FASTA-file(s) to extract nucleotide chained sequences using the tab-delimited ouptut table of one of the chaining modules, for example, from SegMantX's `chain_self_alignments` or `chain_alignments` module:

| ID  | Alignment Hits Indices | Query Start | Query End | Subject Start | Subject End | Mean Percent Identity [%] | Query Strand | Subject Strand | N Alignment Hits | Alignment Hit to Chain Contribution [%] | Chain Topology Query | Chain Topology Subject | Query Length | Subject Length |
|----|------------------------|------------|----------|--------------|------------|--------------------------|-------------|---------------|----------------|----------------------------------|------------------|-------------------|-------------|--------------|
| 1  | 18,21,23,25,27        | 90564      | 130134   | 90267        | 50339      | 97.23                    | +           | -             | 5              | 100.0                            | linear           | linear            | 39570       | 39928        |
| 2  | 2,3,5,7               | 2          | 37303    | 87940        | 50339      | 97.17                    | +           | -             | 4              | 100.0                            | linear           | linear            | 37301       | 37601        |
| 3  | 19,20,22,24,26        | 90564      | 121100   | 30896        | 1          | 97.26                    | +           | -             | 5              | 100.0                            | linear           | linear            | 30536       | 30895        |
| 4  | 1,4,6,8               | 2          | 28269    | 28569        | 1          | 97.22                    | +           | -             | 4              | 100.0                            | linear           | linear            | 28267       | 28568        |
| 5  | 10,13,15,17           | 43965      | 63121    | 50307        | 30888      | 96.67                    | +           | -             | 4              | 91.85111714345375                | linear           | linear            | 19156       | 19419        |
| ... | ...                    | ...        | ...      | ...          | ...        | ...                      | ...         | ...           | ...            | ...                              | ...              | ...               | ...         | ...          |


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