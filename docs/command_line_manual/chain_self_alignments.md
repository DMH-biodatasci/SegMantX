---
id: chain_self_alignments
---

# Chain self-alignments

The `chain_self_alignments` module is designed for the duplication detection by chaining alignment hits from self-sequence alignment. 

## Input data:
The `chain_self_alignments` alignment module expects alignment hits coordinate data, for example, from SegMantX's `generate_alignments` module:

| Query start | Query end | Subject start | Subject end | Percent sequence identity |
|:-----------:|:---------:|:-------------:|:-----------:|:-------------------------:|
| 133470      | 147930    | 64534         | 78969       | 95.1                      |
| ...         | ...       | ...           | ...         | ...                       |
| 329875      | 330416    | 326586         | 327127     | 93                        |

The input data for `chain_self_alignments` should be supplied in this format as tab-delimited file. Alternatively, a BLAST output format 7 file can be used, for example:
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

## Minimal example:
### Chaining local alignments of a self-sequence alignment example towards duplication detection:
```bash
SegMantX chain_self_alignments --input_file tests/NC_018218.1.alignment_coordinates.tsv --output_file tests/NC_018218.1.chains.tsv
```
- `-i or --input_file`: Input file received from 'generate_alignments' (i.e., five columns: q.start, q.end, s.start, s.end, identity). Alternatively, provide BLAST output format 7 and use --blast_outfmt7 flag).
- `-o, --output_file`: Filename of the chaining output file (Default: chaining_output.tsv).

## Output:

Output of self-sequence alignment chaining module:

| (Default) output filename | Description |
|:----------:|:-----------:|
| chaining_output.tsv | Main output file of the chaining procedure containing chaining coordinates and metrics |  
| chaining_output.tsv.indices | Output file to trace back original local alignment hits that have been chained | 

chaining_output.tsv:

| ID  | alignment_hits_indices | q.start | q.end  | s.start | s.end  | mean_percent_identity [%] | q.strand | s.strand | n_alignment_hits | alignment_hit_to_chain_contribution [%] | chain_topology_query | chain_topology_subject | q_length | s_length |
|---- |------------------------|---------|--------|---------|--------|---------------------------|----------|----------|------------------|-----------------------------------------|----------------------|----------------------|---------|---------|
| 1   | 1,7,15,19,21,25,26,...| 135     | 27275  | 6082574 | 6065086 | 88.45                     | +        | -        | 68               | 97.02                                   | linear               | linear               | 27140   | 17488   |
| 2   | 2,8,14,18,23,24,27,...| 135     | 13505  | 6052125 | 6041351 | 86.35                     | +        | -        | 42               | 84.73                                   | linear               | linear               | 13370   | 10774   |
| 3   | 53,55,60,65            | 7181    | 8345   | 7955    | 10238   | 85.04                     | +        | +        | 4                | 100.0                                   | linear               | linear               | 1164    | 2283    |
| 4   | 468,470,473,475        | 388568  | 389342 | 3176215 | 3175457 | 91.85                     | +        | -        | 4                | 72.48                                   | linear               | linear               | 774     | 758     |
| 5   | 469,474                | 388777  | 389209 | 1433399 | 1432987 | 83.33                     | +        | -        | 2                | 100.0                                   | linear               | linear               | 432     | 412     |
| 6   | 472                    | 388999  | 389342 | 4920049 | 4920392 | 95.06                     | +        | +        | 1                | 100.0                                   | linear               | linear               | 343     | 343     |
| 7   | 478                    | 389922  | 390594 | 2819928 | 2820598 | 83.06                     | +        | +        | 1                | 100.0                                   | linear               | linear               | 672     | 670     |
| 8   | 479                    | 391150  | 391952 | 5208377 | 5209196 | 85.61                     | +        | +        | 1                | 100.0                                   | linear               | linear               | 802     | 819     |
| 9   | 480,489                | 391151  | 391950 | 3175457 | 3176217 | 88.43                     | +        | +        | 2                | 72.84                                   | linear               | linear               | 799     | 760     |
| 10  | 481,487                | 391494  | 391148 | 4920049 | 4920395 | 96.38                     | -        | +        | 2                | 100.0                                   | linear               | linear               | 346     | 346     |
| 11  | 482,491                | 391284  | 391952 | 1432987 | 1433677 | 89.37                     | +        | +        | 2                | 100.0                                   | linear               | linear               | 668     | 690     |


chaining_output.tsv.indices:

| Alignment Hits Indices | Query Start | Query End | Subject Start | Subject End | Query Strand | Subject Strand |
|-----------------------|------------|----------|--------------|------------|-------------|---------------|
| 1                     | 135        | 604      | 6082574      | 6082105    | +           | -             |
| 2                     | 135        | 604      | 6052125      | 6051656    | +           | -             |
| 3                     | 135        | 604      | 65642        | 66111      | +           | +             |
| 4                     | 135        | 604      | 30032        | 30501      | +           | +             |
| 5                     | 603        | 1408     | 4914415      | 4913610    | +           | -             |
| 6                     | 603        | 1405     | 3410676      | 3409874    | +           | -             |
| ...                   | ...        | ...      | ...          | ...        | ...         | ...           |


## Further options & parameters:

### Using BLAST output format 7
To use a file derived from BLAST in output format 7 as input you can use the following flag:
- `-B or --blast_outfmt7`: Indicates if the input file is BLAST output format 7 (Default: False).

Example:
```bash
SegMantX chain_self_alignments --input_file NC_018218.1.blast.x7 --output_file tests/NC_018218.1.chains.tsv --blast_outfmt7
```

### Maximum gap size
To set a threshold for the max. gap size (in nucleotides) between alignment hits for chaining:
- `-G or --max_gap`: Maximum gap size between alignment hits for chaining (default: 5000).
        
To set the maximum gap size to 6000 (in nucleotides):
```bash
SegMantX chain_self_alignments --input_file tests/NC_018218.1.alignment_coordinates.tsv --output_file tests/NC_018218.1.chains.tsv --max_gap 6000
```

### Scaled gap size
To set a threshold for the scaled gap size between alignment hits for chaining:
- `SG or --scaled_gap`: Minimum scaled gap between alignment hits for chaining (Default: 1.0).
        
To set the scaled gap to 2:
```bash
SegMantX chain_self_alignments --input_file tests/NC_018218.1.alignment_coordinates.tsv --output_file tests/NC_018218.1.chains.tsv --scaled_gap 2
```

### Sequence topology of query
Choosing the correct sequence topology ensures that alignment hits on circular sequences (e.g., most plasmids or viral genomes) are correctly chained, even when fragmented due to their linear representation in FASTA-files. This is important for avoiding discontinuous alignments that can occur when aligning circular sequences in a linear format (i.e., FASTA format). The sequence topology is set to linear by default.

The sequence topology for the chaining can be set to circular using:
- `-Q or --is_query_circular`: Indicates a circular sequence topology (Default: False).

Note, that on circular sequence topologies it is necessary to supply the sequence length to SegMantX (e.g., --sequence_length or --fasta_file). See below to see options how to provide the sequence length to SegMantX.

To set a circular sequence topology for the query:
```bash
SegMantX chain_self_alignments --input_file tests/NC_018218.1.alignment_coordinates.tsv --output_file tests/NC_018218.1.chains.tsv --is_query_circular --fasta_file tests/NC_018218.1.fasta
```
### Sequence length
The sequence length is required for correct alignment chaining on sequences with circular sequence topology.

To set the sequence length manually:
- `-L, --sequence_length`: Size of the sequence (is required with circular sequence topology). Otherwise, provide fasta file (i.e.,
                        using --fasta_file) (Default: None).
        
To set the sequence length manually to 6088797:
```bash
SegMantX chain_self_alignments --input_file tests/NC_018218.1.alignment_coordinates.tsv --output_file tests/NC_018218.1.chains.tsv --sequence_length 6088797
```

To determine the sequence length automatically from FASTA-file:
- `-f or --fasta_file`: Fasta file to read out the sequence length. Required if the sequence topology is circular and
                        --sequence_size is not provided manually.
                        
To set the sequence length automatically to 6088797 by providing the FASTA-file:
```bash
SegMantX chain_self_alignments --input_file tests/NC_018218.1.alignment_coordinates.tsv --output_file tests/NC_018218.1.chains.tsv --fasta_file tests/NC_018218.1.fasta
```
                        
### Minimum alignment hit length
To discard alignment hits for chaining according to their length:
- `-ml or --min_length`: Minium length of alignment hits for chaining (default: 200).
        
To set the minimum alignment hit length to 300:
```bash
SegMantX chain_self_alignments --input_file tests/NC_018218.1.alignment_coordinates.tsv --output_file tests/NC_018218.1.chains.tsv --min_length 300
```