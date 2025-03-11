---
id: generate_alignments
---

# Generate alignments

The `generate_alignments` module facilitates sequence alignment generations files that can be further processed by the chaining modules for duplication detection and sequence comparison.

## Input data:
The `generate_alignments` alignment module expects a plain FASTA-file (e.g., genomic sequence):
```bash
>NC_018218.1 Zymoseptoria tritici IPO323 chromosome 1, whole genome shotgun sequence
CCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCT
AACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTAACCCTCACCCTCACCCTCGGT
CGTACGGCGTGACAATGTCTCCAGAATCGATTTGGTCTTGACGAAAGCAGCGCACATAGCACTTCCGGAT
GATTTTGTCGCATGCTTTGTCAAACACGACGTCCGTAAGTACTAGCTCGTTCGGCCTAGCTTTCGCGCCC
GTCTGCTGCTCGCTCTTCCGCAAGAATTGACGCAGAACGACGCGCCGCTTCTGGGTATCGAACTCGATAA
TTTGGGCTGGCTGGAGCCGGTCCTCGTCAAGGTCGTCATTCCATTCGCGGACGAGGACGGTGTCACCAAT
TGCATATTTGCTCCGGCACTCGTCGAATATAGGAACGTCATGCTTGCACTGGCACCTAAAGTCGCTTGCT
...
```

## Minimal examples:
### I. Self-sequence alignment example towards duplication detection:
```bash
SegMantX generate_alignments --query_file tests/NC_018218.1.fasta --blast_output_file tests/NC_018218.1.blast.x7 --alignment_hits_file tests/NC_018218.1.alignment_coordinates.tsv --self_sequence_alignment
```
- `-q or --query_file`: Path to the query nucleotide FASTA file (required).
- `-b or --blast_output_file`: Path to the output file for BLASTn results (Default: blast_output.txt). 
- `-a or --alignment_hits_file`: Path to the output file containing (main) alignment hit data for the chaining process (Default: alignment_hits.tsv).
- `-SA or --self_sequence_alignment`: Indicates to perform a self-sequence alignment (Default: False).

### II. Sequence alignment example towards sequence comparison:
```bash
SegMantX generate_alignments  --query_file tests/NZ_CP018634.1.fasta --subject_file tests/NZ_CP022004.1.fasta --blast_output_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.blast.x7 --alignment_hits_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.alignment_coordinates.tsv 
```
- `-q or --query_file`: Path to the query nucleotide FASTA file (required).
- `-s or --subject_file`: Path to the subject nucleotide FASTA file (required).
- `-b or --blast_output_file`: Path to the output file for BLASTn results (Default: blast_output.txt). 
- `-a or --alignment_hits_file`: Path to the output file containing (main) alignment hit data for the chaining process (Default: alignment_hits.tsv).

## Output:

| (Default) output filename | Description |
|:------------------------:|:-----------|
| blast_output.txt | Output file of BLASTn search in output format 7 |  
| alignment_hits.tsv | Output file restricted to q.start, q.end, s.start, s.end, and percentage sequence identity from BLASTn search, which is sufficient for the chaining modules |

blast_output.txt:
```bash
# BLASTN 2.16.0+
# Query: NC_018218.1 Zymoseptoria tritici IPO323 chromosome 1, whole genome shotgun sequence
# Database: tests/NC_018218.1.fasta
# Fields: query acc.ver, subject acc.ver, % identity, alignment length, mismatches, gap opens, q. start, q. end, s. start, s. end, evalue, bit score
# 4303 hits found
NC_018218.1     NC_018218.1     100.000 6088797 0       0       1       6088797 1       6088797 0.0     1.124e+07
NC_018218.1     NC_018218.1     95.661  22033   953     3       55342   77374   19732   41761   0.0     35388
NC_018218.1     NC_018218.1     95.661  22033   953     3       19732   41761   55342   77374   0.0     35388
NC_018218.1     NC_018218.1     92.300  10247   725     38      6031036 6041231 42685   32452   0.0     14493
NC_018218.1     NC_018218.1     92.299  10245   729     37      32452   42685   6041231 6031036 0.0     14493
...
```

alignment_hits.tsv:

| Query Start | Query End | Subject Start | Subject End | Percentage Sequence Identity |
|------------|----------|--------------|------------|-----------------------------|
| 1          | 6088797  | 1            | 6088797    | 100.0                       |
| 55342      | 77374    | 19732        | 41761      | 95.661                      |
| 19732      | 41761    | 55342        | 77374      | 95.661                      |
| 6031036    | 6041231  | 42685        | 32452      | 92.3                         |
| 32452      | 42685    | 6041231      | 6031036    | 92.299                       |
| 6031937    | 6041231  | 77374        | 68062      | 92.637                       |
| 68062      | 77374    | 6041231      | 6031937    | 92.636                       |
| 3223924    | 3233399  | 436768       | 427318     | 92.119                       |
| 427318     | 436768   | 3233399      | 3223924    | 92.119                       |
| 6075122    | 6084427  | 6044722      | 6053978    | 91.976                       |
| 6044722    | 6053978  | 6075122      | 6084427    | 91.976                       |
| ...        | ...      | ...          | ...        | ...                          |


## Further options & parameters

### Sequence topology
Choosing the correct sequence topology ensures that alignment hits on circular sequences (e.g., most plasmids or viral genomes) are correctly chained, even when fragmented due to their linear representation in FASTA-files. This is important for avoiding discontinuous alignments that can occur when aligning circular sequences in a linear format (i.e., FASTA format). The sequence topology is set to linear by default.

The sequence topology for the alignment can be set to circular using:
- `-Q or --is_query_circular`: Indicates if the query sequence is circular (Default: False).
- `-S or --is_subject_circular`: Indicates if the subject sequence is circular (Default: False).

Circular sequence topology in a self-sequence alignment towards duplication detection:
```bash
SegMantX generate_alignments --query_file tests/NZ_AP022172.1.fasta --blast_output_file tests/NZ_AP022172.1.blast.x7 --alignment_hits_file tests/NZ_AP022172.1.alignment_coordinates.tsv --is_query_circular --self_sequence_alignment
```

Circular sequence topology in an sequence alignment towards sequence comparison:
```bash
SegMantX generate_alignments  --query_file tests/NZ_CP018634.1.fasta --subject_file tests/NZ_CP022004.1.fasta --blast_output_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.blast.x7 --alignment_hits_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.alignment_coordinates.tsv --is_query_circular --is_subject_circular 
```

### E-Value
The E-value in BLAST estimates the number of random alignments expected by chance. It helps filtering low-confidence matches and retaining biologically relevant seeds for chaining.
- Example E-value settings:  
        - High specificity: `1e-9` (Fewer, more reliable seeds) - RECOMMENDED  
        - 'Balanced approach': `1e-5` (Balance of sensitivity and specificity)  
        - Higher sensitivity: `1e-1` (More seeds, but may introduce noise—use cautiously) - NOT RECOMMENDED
        
The E-value for BLASTn computation can be set using:
- `-e or --evalue`: E-value threshold for BLASTn (Default: 1e-9).

Example run setting E-value to `1e-10`:
```bash
SegMantX generate_alignments --query_file tests/NC_018218.1.fasta --blast_output_file tests/NC_018218.1.blast.x7 --alignment_hits_file tests/NC_018218.1.alignment_coordinates.tsv --self_sequence_alignment --evalue 1e-10
```

### Word size
The word size defines the length of the initial exact match (seed) required for alignment extension. Choose a higher word size to speed up the alignment generation and chaining on larger sequences.

- Example word size settings:  
    - For short sequences (e.g., plasmids): `Word size = 7-11` (More sensitive, detects weak matches)  
    - For longer genomic sequences (e.g., chromosomes): `Word size = 20-30` (Faster, focuses on strong matches)
    
The word size for BLASTn computation can be set using:
- `-W or --word_size`: Word size for BLASTn search (increase it for large genomes) (Default: 11).

Example run setting word size to 28:
```bash
SegMantX generate_alignments --query_file tests/NC_018218.1.fasta --blast_output_file tests/NC_018218.1.blast.x7 --alignment_hits_file tests/NC_018218.1.alignment_coordinates.tsv --self_sequence_alignment --word_size 28
```

### Threads
Threads refer to the number of CPU cores used to parallelize BLASTn computations. More threads allow for faster processing by handling multiple alignment tasks simultaneously, improving overall speed and efficiency.

The number of threads for BLASTn computation can be set using:
- `-T or --number_of_threads`: Number of threads for BLASTn search (Default: 1).

Example run setting threads to 4:
```bash
SegMantX generate_alignments --query_file tests/NC_018218.1.fasta --blast_output_file tests/NC_018218.1.blast.x7 --alignment_hits_file tests/NC_018218.1.alignment_coordinates.tsv --self_sequence_alignment --number_of_threads 4
```

### Minimum percentage sequence identity
This parameter sets a threshold for sequence alignments hits being considered for chaining according to a percentage sequence identity (i.e., alignment hits below the threshold are excluded).

The percentage sequence identity for BLASTn computation can be set using:
- `-i or --min_identity_percentage`: Minimum percentage identity for BLASTn matches (Default: 60).

Example run setting minimumg percentage sequence identity to 70:
```bash
SegMantX generate_alignments --query_file tests/NC_018218.1.fasta --blast_output_file tests/NC_018218.1.blast.x7 --alignment_hits_file tests/NC_018218.1.alignment_coordinates.tsv --self_sequence_alignment --min_identity_percentage 70
```
