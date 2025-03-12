---
id: help
---

# Help

To display SegMantX modules and syntax:
```bash
SegMantX -h
```
The following will be displayed:
```bash
Options: SegMantX.py [ chain_self_alignments | chain_alignments | visualize_chains | fetch_nucleotide_chains | generate_alignments | test_modules | help | version | citation | start_app ]
```

## Options / Parameters for modules using 'help':

### 1. Generate alignments
```bash
SegMantX generate_alignments -h
```
The following will be displayed:
```bash
usage: SegMantX [-h] -q QUERY_FILE [-s SUBJECT_FILE] [-b BLAST_OUTPUT_FILE] [-a ALIGNMENT_HITS_FILE] [-Q] [-S] [-SA] [-e EVALUE]
                [-i MIN_IDENTITY_PERCENTAGE] [-T NUMBER_OF_THREADS] [-W WORD_SIZE]
                module

Computes alignments for chaining modules.

positional arguments:
  module                Name of the module being executed.

options:
  -h, --help            show this help message and exit
  -q, --query_file QUERY_FILE
                        Path to the query nucleotide FASTA file (required).
  -s, --subject_file SUBJECT_FILE
                        Path to the subject nucleotide FASTA file.
  -b, --blast_output_file BLAST_OUTPUT_FILE
                        Path to the output file for BLASTn results (Default: blast_output.txt).
  -a, --alignment_hits_file ALIGNMENT_HITS_FILE
                        Path to the output file containing (main) alignment hit data for the chaining process (Default: alignment_hits.tsv).
  -Q, --is_query_circular
                        Indicates if the query sequence is circular (Default: False).
  -S, --is_subject_circular
                        Indicates if the subject sequence is circular (Default: False).
  -SA, --self_sequence_alignment
                        Indicates to perform a self-sequence alignment (Default: False).
  -e, --evalue EVALUE   E-value threshold for BLASTn (Default: 1e-9).
  -i, --min_identity_percentage MIN_IDENTITY_PERCENTAGE
                        Minimum percentage identity for BLASTn matches (Default: 60).
  -T, --number_of_threads NUMBER_OF_THREADS
                        Number of threads for BLASTn search (Default: 1).
  -W, --word_size WORD_SIZE
                        Word size for BLASTn search (increase it for large genomes) (Default: 11).
```

### 2. Chain self-sequence alignments
```bash
SegMantX chain_self_alignments -h
```
The following will be displayed:
```bash
usage: SegMantX [-h] -i INPUT_FILE [-B] [-G MAX_GAP] [-SG SCALED_GAP] [-Q] [-L SEQUENCE_LENGTH] [-f FASTA_FILE] [-o OUTPUT_FILE] [-ml MIN_LENGTH]
                module

Chains local alignments from self-sequence alignment (e.g., duplication detection).

positional arguments:
  module                Name of the module being executed.

options:
  -h, --help            show this help message and exit
  -i, --input_file INPUT_FILE
                        Input file received from 'generate_alignments' (i.e., five columns: q.start, q.end, s.start, s.end, identity).
                        Alternatively, provide BLAST output format 7 and use --blast_outfmt7 flag).
  -B, --blast_outfmt7   Indicates if the input file is BLAST output format 7 (Default: False).
  -G, --max_gap MAX_GAP
                        Maximum gap size between alignment hits for chaining (default: 5000).
  -SG, --scaled_gap SCALED_GAP
                        Minimum scaled gap between alignment hits for chaining (Default: 1.0).
  -Q, --is_query_circular
                        Indicates a circular sequence topology (Default: False).
  -L, --sequence_length SEQUENCE_LENGTH
                        Size of the sequence (is required with circular sequence topology). Otherwise, provide fasta file (i.e., using
                        --fasta_file) (Default: None).
  -f, --fasta_file FASTA_FILE
                        Fasta file to read out the sequence length. Required if the sequence topology is circular and --sequence_size is not
                        provided manually.
  -o, --output_file OUTPUT_FILE
                        Filename of the chaining output file (Default: chaining_output.tsv).
  -ml, --min_length MIN_LENGTH
                        Minium length of alignment hits for chaining (default: 200).
```

### 3. Chain sequence alignments
```bash
SegMantX chain_alignments -h
```
The following will be displayed:
```bash
usage: SegMantX [-h] -i INPUT_FILE [-B] [-G MAX_GAP] [-SG SCALED_GAP] [-Q] [-S] [-LQ SEQUENCE_LENGTH_QUERY] [-LS SEQUENCE_LENGTH_SUBJECT]
                [-o OUTPUT_FILE] [-ml MIN_LENGTH] [-fq FASTA_FILE_QUERY] [-fs FASTA_FILE_SUBJECT]
                module

Chains local alignments from sequence alignment.

positional arguments:
  module                Name of the module being executed.

options:
  -h, --help            show this help message and exit
  -i, --input_file INPUT_FILE
                        Input file received from 'generate_alignments' (i.e., five columns: q.start, q.end, s.start, s.end, identity).
                        Alternatively, provide BLAST output format 7 and indicate --blast_outfmt7 flag).
  -B, --blast_outfmt7   Indicates if the input file is BLAST output format 7 (Default: False).
  -G, --max_gap MAX_GAP
                        Maximum gap size between alignment hits for chaining (default: 5000).
  -SG, --scaled_gap SCALED_GAP
                        Minimum scaled gap between alignment hits for chaining (Default: 1.0).
  -Q, --is_query_circular
                        Indicates if the query sequence is circular (Default: False).
  -S, --is_subject_circular
                        Indicates if the subject sequence is circular (Default: False).
  -LQ, --sequence_length_query SEQUENCE_LENGTH_QUERY
                        Size of the query sequence (is required with circular sequence topology). Otherwise, provide fasta file (i.e., using
                        --fasta_file_query) (Default: None).
  -LS, --sequence_length_subject SEQUENCE_LENGTH_SUBJECT
                        Size of the subject sequence (is required with circular sequence topology). Otherwise, provide fasta file (i.e., using
                        --fasta_file_subject) (Default: None).
  -o, --output_file OUTPUT_FILE
                        Filename of the chaining output file (Default: chaining_output.tsv).
  -ml, --min_length MIN_LENGTH
                        Minium length of alignment hits for chaining (default: 200).
  -fq, --fasta_file_query FASTA_FILE_QUERY
                        Fasta file to read out the sequence length.
  -fs, --fasta_file_subject FASTA_FILE_SUBJECT
                        Fasta file to read out the sequence length.
```

### 4. Visualize chains
```bash
SegMantX visualize_chains -h
```
The following will be displayed:
```bash
usage: SegMantX [-h] -i INPUT_FILE [-LQ SEQUENCE_LENGTH_QUERY] [-LS SEQUENCE_LENGTH_SUBJECT] [-gf GENBANK_FILE] [-o OUTPUT_FILE] [-S SCALE]
                [-fq FASTA_FILE_QUERY] [-fs FASTA_FILE_SUBJECT] [-QIS] [-W WIDTH] [-H HEIGHT]
                module

Generates a dotplot to visualize yielded chains for a sequence.

positional arguments:
  module                Name of the module being executed.

options:
  -h, --help            show this help message and exit
  -i, --input_file INPUT_FILE
                        Output file from chaining results as input.
  -LQ, --sequence_length_query SEQUENCE_LENGTH_QUERY
                        Size of the query sequence (is required with circular sequence topology). Otherwise, provide fasta file (i.e., using
                        --fasta_file_query) (Default: None).
  -LS, --sequence_length_subject SEQUENCE_LENGTH_SUBJECT
                        Size of the subject sequence (is required with circular sequence topology). Otherwise, provide fasta file (i.e., using
                        --fasta_file_subject) (Default: None).
  -gf, --genbank_file GENBANK_FILE
                        Genbank file to visualize features.
  -o, --output_file OUTPUT_FILE
                        Output file: Interactive plot (i.e., html file).
  -S, --scale SCALE     Scaling the plot to bp, kbp (default), or mbp options:[bp, kbp, mbp].
  -fq, --fasta_file_query FASTA_FILE_QUERY
                        Fasta file to read out the sequence length.
  -fs, --fasta_file_subject FASTA_FILE_SUBJECT
                        Fasta file to read out the sequence length.
  -QIS, --query_is_subject
                        Specify this flag if the query sequence is identical to the subject sequence (i.e., chaining result from self-alignment).
  -W, --width WIDTH     Specifies the figure width.
  -H, --height HEIGHT   Specifies the figure height
```

### 5. Fetch nucleotide chains
```bash
SegMantX fetch_nucleotide_chains -h
```
The following will be displayed:
```bash
usage: SegMantX [-h] -i INPUT_FILE [-fq FASTA_FILE_QUERY] [-o OUTPUT_FILE] [-fs FASTA_FILE_SUBJECT] module

Extracts nucleotide sequences from chained alignments (FASTA format).

positional arguments:
  module                Name of the module being executed.

options:
  -h, --help            show this help message and exit
  -i, --input_file INPUT_FILE
                        Output file from chaining results as input.
  -fq, --fasta_file_query FASTA_FILE_QUERY
                        Fasta file to read out the sequence length.
  -o, --output_file OUTPUT_FILE
                        Output file: Fasta file containing nucleotide chains.
  -fs, --fasta_file_subject FASTA_FILE_SUBJECT
                        Fasta file to read out the sequence length.
```