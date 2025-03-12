---
id: visualize_chains
---

# Visualize chains

The `visualize_chains` module is designed to create an interactive plot visualizing the resulting chains in a segmentplot (or dotplot, but segments are represented instead of dots) from a chaining module.

## Input data:
The `visualize_chains` alignment module expects the tab-delimited ouptut table of one of the chaining modules, for example, from SegMantX's `chain_self_alignments` or `chain_alignments` module:

[Click here to visit an example table](https://github.com/DMH-biodatasci/SegMantX/blob/main/docs/tbl/NZ_AP022172.1.chains.tsv)

## Minimal examples:
### I. Visualizing chains from self-sequence alignment chaining:
```bash
SegMantX visualize_chains --input_file tests/NZ_AP022172.1.chains.tsv --output_file tests/NZ_AP022172.1.html --fasta_file_query  tests/NZ_AP022172.1.fasta --query_is_subject
```
- `-i or --input_file`: Output file from chaining results as input.
- `-o, --output_file`: Output file: Interactive plot (i.e., html file).
- `-fq or --fasta_file_query`: Fasta file to read out the sequence length.
- `-QIS or --query_is_subject`: Specify this flag if the query sequence is identical to the subject sequence (i.e., chaining result from self-alignment). 

Note, that `--fasta_file_query` is used here to provide the sequence length for plotting the right scale on the axes, but it is optional. Addtionally, setting the sequence length becomes mandatory if the chaining results corresponds to a sequence with a circular sequence topology. Alternatively, the sequence length can be set manually (see below).

### II. Visualizing chains from sequence alignment chaining between two distinct sequences:
```bash
SegMantX visualize_chains --input_file  tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.tsv --output_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.html --fasta_file_query tests/NZ_CP018634.1.fasta --fasta_file_subject tests/NZ_CP022004.1.fasta
```
- `-i or --input_file`: Output file from chaining results as input.
- `-o, --output_file`: Output file: Interactive plot (i.e., html file).
- `-fq or --fasta_file_query`: Fasta file to read out the sequence length.
- `-fs or --fasta_file_subject`: Fasta file to read out the sequence length.

Note, that `--fasta_file_query` and `--fasta_file_subject` are used here to provide the sequence lengths for plotting the right scale on the axes, but it is optional. Addtionally, setting the sequence length becomes mandatory if the chaining results corresponds to a sequence with a circular sequence topology. Alternatively, the sequence lengths can be set manually (see below).

## Output:

Output of visualization module:

| (Default) output filename | Description |
|:----------:|:-----------:|
| plot.html | An interactive visualization (segment plot) of chains that can be opened in any web browser. | 

You can view an example interactive plot including visualized genomic features below:

[Click here and download an example plot from our github repo.](https://github.com/DMH-biodatasci/SegMantX/blob/main/docs/img/interactive_example_segmentplot_features.html)

## Further options & parameters:

### Sequence length
The sequence length is required for scaling the axes according to the sequence length(s).

To set the sequence length manually:
- `-LQ, --sequence_length_query`: Size of the query sequence (is required with circular sequence topology). Otherwise, provide fasta file (i.e., using --fasta_file_query) (Default: None).
- `-LS, --sequence_length_subject`: Size of the subject sequence (is required with circular sequence topology). Otherwise, provide fasta file (i.e., using --fasta_file_subject)
        
To set the sequence length manually for query and subject sequence:
```bash
SegMantX visualize_chains --input_file  tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.tsv --output_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.html --fasta_file_query tests/NZ_CP018634.1.fasta --fasta_file_subject tests/NZ_CP022004.1.fasta --sequence_length_query 92831 --sequence_length_subject 59371
```

To determine the sequence length automatically from FASTA-file:
- `-fq or --fasta_file_query`: Fasta file to read out the sequence length.
- `-fs or --fasta_file_subject`: Fasta file to read out the sequence length.
                        
To set the sequence length automatically for the query and subject sequences by providing the FASTA-files:
```bash
SegMantX visualize_chains --input_file  tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.tsv --output_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.html --fasta_file_query tests/NZ_CP018634.1.fasta --fasta_file_subject tests/NZ_CP022004.1.fasta
```

### Using a different scale for the plot axes
To set a different scale for the axes (i.e., bp, kbp or mbp):
- `-S or --scale`: Scaling the plot to bp, kbp (default), or mbp options: bp, kbp, mbp.

Example:
```bash
SegMantX visualize_chains --input_file tests/NZ_AP022172.1.chains.tsv --output_file tests/NZ_AP022172.1.html --fasta_file_query  tests/NZ_AP022172.1.fasta --query_is_subject --scale bp
```

### Visualizing genomic features
To visualize features (i.e., CDS & pseudogenes) from a genbank file on the x-axis:
- `-gf or --genbank_file`: Genbank file to visualize features.
        
To set the maximum gap size to 6000 (in nucleotides):
```bash
SegMantX visualize_chains --input_file tests/NZ_AP022172.1.chains.tsv --output_file tests/NZ_AP022172.1.html --fasta_file_query  tests/NZ_AP022172.1.fasta --query_is_subject --genbank_file tests/NZ_AP022172.1.gbk
```

### Figure width and height
To set the figure widht and height:
  -W, --width WIDTH     Specifies the figure width.
  -H, --height HEIGHT   Specifies the figure height

- `-W or --width`: Specifies the figure width.
- `-H or --height`: Specifies the figure height.
        
To set the figure width and height to 1200 and 800, respectively:
```bash
SegMantX visualize_chains --input_file tests/NZ_AP022172.1.chains.tsv --output_file tests/NZ_AP022172.1.html --fasta_file_query  tests/NZ_AP022172.1.fasta --query_is_subject --width 1200 --height 800
```