---
id: visualize_chains
---

# Visualize chains

The `visualize_chains` module is designed to create an interactive plot visualizing the resulting chains in a segmentplot (or dotplot, but segments are represented instead of dots) from a chaining module.

## Input data:
The `visualize_chains` alignment module expects the tab-delimited ouptut table of one of the chaining modules, for example, from SegMantX's `chain_self_alignments` or `chain_alignments` module:

| ID  | Alignment Hits Indices | Query Start | Query End | Subject Start | Subject End | Mean Percent Identity [%] | Query Strand | Subject Strand | N Alignment Hits | Alignment Hit to Chain Contribution [%] | Chain Topology Query | Chain Topology Subject | Query Length | Subject Length |
|----|------------------------|------------|----------|--------------|------------|--------------------------|-------------|---------------|----------------|----------------------------------|------------------|-------------------|-------------|--------------|
| 1  | 18,21,23,25,27        | 90564      | 130134   | 90267        | 50339      | 97.23                    | +           | -             | 5              | 100.0                            | linear           | linear            | 39570       | 39928        |
| 2  | 2,3,5,7               | 2          | 37303    | 87940        | 50339      | 97.17                    | +           | -             | 4              | 100.0                            | linear           | linear            | 37301       | 37601        |
| 3  | 19,20,22,24,26        | 90564      | 121100   | 30896        | 1          | 97.26                    | +           | -             | 5              | 100.0                            | linear           | linear            | 30536       | 30895        |
| 4  | 1,4,6,8               | 2          | 28269    | 28569        | 1          | 97.22                    | +           | -             | 4              | 100.0                            | linear           | linear            | 28267       | 28568        |
| 5  | 10,13,15,17           | 43965      | 63121    | 50307        | 30888      | 96.67                    | +           | -             | 4              | 91.85111714345375                | linear           | linear            | 19156       | 19419        |
| ... | ...                    | ...        | ...      | ...          | ...        | ...                      | ...         | ...           | ...            | ...                              | ...              | ...               | ...         | ...          |


## Minimal example:
### Visualizing chains from self-sequence alignment chaining:
```bash
SegMantX visualize_chains --input_file tests/NZ_AP022172.1.chains.tsv --output_file tests/NZ_AP022172.1.html --fasta_file_query  tests/NZ_AP022172.1.fasta --query_is_subject
```
- `-i or --input_file`: Output file from chaining results as input.
- `-o, --output_file`: Output file: Interactive plot (i.e., html file).
- `-fq or --fasta_file_query`: Fasta file to read out the sequence length.
- `-QIS or --query_is_subject`: Specify this flag if the query sequence is identical to the subject sequence (i.e., chaining result from self-alignment). 

### Visualizing chains from sequence alignment chaining between two distinct sequences:
```bash
SegMantX visualize_chains --input_file  tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.tsv --output_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.html --fasta_file_query tests/NZ_CP018634.1.fasta --fasta_file_subject tests/NZ_CP022004.1.fasta
```
- `-i or --input_file`: Output file from chaining results as input.
- `-o, --output_file`: Output file: Interactive plot (i.e., html file).
- `-fq or --fasta_file_query`: Fasta file to read out the sequence length.
- `-fs or --fasta_file_subject`: Fasta file to read out the sequence length.

## Output:

Output of visualization module:

| (Default) output filename | Description |
|:----------:|:-----------:|
| plot.html | An interactive visualization (segment plot) of chains that can be opened in any web browser. | 

You can view an example interactive plot below:

<iframe src="../img/interactive_examplge_segmentplot.html" width="100%" height="600px"></iframe>

## Further options & parameters:

### Using BLAST output format 7
To use a file derived from BLAST in output format 7 as input you can use the following flag:
- `-B or --blast_outfmt7`: Indicates if the input file is BLAST output format 7 (Default: False).

Example:
```bash
SegMantX chain_alignments --input_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.blast.x7 -o tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.tsv --blast_outfmt7
```

### Maximum gap size
To set a threshold for the max. gap size (in nucleotides) between alignment hits for chaining:
- `-G or --max_gap`: Maximum gap size between alignment hits for chaining (default: 5000).
        
To set the maximum gap size to 6000 (in nucleotides):
```bash
SegMantX chain_alignments --input_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.alignment_coordinates.tsv -o tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.tsv --max_gap 6000
```

### Scaled gap size
To set a threshold for the scaled gap size between alignment hits for chaining:
- `SG or --scaled_gap`: Minimum scaled gap between alignment hits for chaining (Default: 1.0).
        
To set the scaled gap to 2:
```bash
SegMantX chain_alignments --input_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.alignment_coordinates.tsv -o tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.tsv --scaled_gap 2
```

### Sequence topology of query
Choosing the correct sequence topology ensures that alignment hits on circular sequences (e.g., most plasmids or viral genomes) are correctly chained, even when fragmented due to their linear representation in FASTA-files. This is important for avoiding discontinuous alignments that can occur when aligning circular sequences in a linear format (i.e., FASTA format). The sequence topology is set to linear by default.

The sequence topology for the chaining can be set to circular using:
- `-Q or --is_query_circular`: Indicates a circular sequence topology of query (Default: False).
- `-S or --is_subject_circular`: Indicates a circular sequence topology of subject (Default: False).

Note, that on circular sequence topologies it is necessary to supply the sequence length to SegMantX (e.g., --sequence_length_query, --sequence_length_subject or --fasta_file_query, --fasta_file_subject). See below to see options how to provide the sequence length to SegMantX.

To set a circular sequence topology for query & subject:
```bash
SegMantX chain_alignments --input_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.alignment_coordinates.tsv -o tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.tsv --is_query_circular --is_subject_circular --fasta_file_query tests/NZ_CP018634.1.fasta --fasta_file_subject tests/NZ_CP022004.1.fasta
```
### Sequence length
The sequence length is required for correct alignment chaining on sequences with circular sequence topology.

To set the sequence length manually:
- `-LQ, --sequence_length_query`: Size of the query sequence (is required with circular sequence topology). Otherwise, provide fasta file (i.e., using --fasta_file_query) (Default: None).
- `-LS, --sequence_length_subject`: Size of the subject sequence (is required with circular sequence topology). Otherwise, provide fasta file (i.e., using --fasta_file_subject) (Default: None).
        
To set the sequence length manually for query and subject sequence:
```bash
SegMantX chain_alignments --input_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.alignment_coordinates.tsv -o tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.tsv --is_query_circular --is_subject_circular --sequence_length_query 92831 --sequence_length_subject 59371
```

To determine the sequence length automatically from FASTA-file:
- `-fq, --fasta_file_query`: Fasta file to read out the sequence length. Required if the sequence topology is circular and --sequence_length_query is not provided manually.
- `-fs, --fasta_file_subject`: Fasta file to read out the sequence length. Required if the sequence topology is circular and --sequence_length_subject is not provided manually.
                        
To set the sequence length automatically for the query and subject sequences by providing the FASTA-files:
```bash
SegMantX chain_alignments --input_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.alignment_coordinates.tsv --fasta_file_query tests/NZ_CP018634.1.fasta --fasta_file_subject tests/NZ_CP022004.1.fasta --is_query_circular --is_subject_circular -o tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.tsv
```
                        
### Minimum alignment hit length
To discard alignment hits for chaining according to their length:
- `-ml or --min_length`: Minium length of alignment hits for chaining (default: 200).
        
To set the minimum alignment hit length to 300:
```bash
SegMantX chain_alignments --input_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.alignment_coordinates.tsv -o tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.tsv --min_length 300
```