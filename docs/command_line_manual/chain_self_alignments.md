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


[Click here to visit an example file containing alignments hits coordinate data](https://github.com/DMH-biodatasci/SegMantX/blob/main/docs/tbl/NZ_AP022172.1.alignment_coordinates.tsv)

The input data for `chain_self_alignments` should be supplied in this format as tab-delimited file. Alternatively, a BLAST output format 7 file can be used, for example:

[Click here to visit an example file containing a blast output format 7](https://github.com/DMH-biodatasci/SegMantX/blob/main/docs/tbl/NZ_AP022172.1.blast.x7)

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


[Click here to visit an example table for 'chaining_output.tsv'](https://github.com/DMH-biodatasci/SegMantX/blob/main/docs/tbl/NZ_AP022172.1.chains.tsv)

[Click here to visit an example table for 'chaining_output.tsv.indices'](https://github.com/DMH-biodatasci/SegMantX/blob/main/docs/tbl/NZ_AP022172.1.tsv.indices)

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
SegMantX chain_self_alignments --input_file tests/NZ_AP022172.1.alignment_coordinates.tsv --output_file tests/NZ_AP022172.1.chains.tsv --is_query_circular --fasta_file tests/NZ_AP022172.1.fasta
```
### Sequence length
The sequence length is required for correct alignment chaining on sequences with circular sequence topology.

To set the sequence length manually:
- `-L, --sequence_length`: Size of the sequence (is required with circular sequence topology). Otherwise, provide fasta file (i.e.,
                        using --fasta_file) (Default: None).
        
To set the sequence length manually to 187669:
```bash
SegMantX chain_self_alignments --input_file tests/NZ_AP022172.1.alignment_coordinates.tsv --output_file tests/NZ_AP022172.1.chains.tsv --sequence_length 187669
```

To determine the sequence length automatically from FASTA-file:
- `-f or --fasta_file`: Fasta file to read out the sequence length. Required if the sequence topology is circular and
                        --sequence_size is not provided manually.
                        
To set the sequence length automatically to 187669 by providing the FASTA-file:
```bash
SegMantX chain_self_alignments --input_file tests/NZ_AP022172.1.alignment_coordinates.tsv --output_file tests/NZ_AP022172.1.chains.tsv --fasta_file tests/NZ_AP022172.1.fasta
```
                        
### Minimum alignment hit length
To discard alignment hits for chaining according to their length:
- `-ml or --min_length`: Minium length of alignment hits for chaining (default: 200).
        
To set the minimum alignment hit length to 300:
```bash
SegMantX chain_self_alignments --input_file tests/NC_018218.1.alignment_coordinates.tsv --output_file tests/NC_018218.1.chains.tsv --min_length 300
```