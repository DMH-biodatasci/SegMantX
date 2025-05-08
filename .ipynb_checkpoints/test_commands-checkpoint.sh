# Create coordinates
python3 alisgcha.py alignments --query test_data/4029.fasta --blast_output test_data/4029.blast.x7 --alignments_output test_data/4029.coordinates.tsv --query_is_circular --duplication 
python3 alisgcha.py alignments  --query test_data/461.fasta --blast_output test_data/461.blast.x7 --alignments_output test_data/461.coordinates.tsv --query_is_circular --duplication
python3 alisgcha.py alignments  --query test_data/ztritici.fasta --blast_output test_data/ztritici.blast.x7 --alignments_output test_data/ztritici.coordinates.tsv --duplication
python3 alisgcha.py alignments  --query test_data/10635.fasta --subject test_data/10567.fasta --blast_output test_data/10635_vs_10567.blast.x7 --alignments_output test_data/10635_vs_10567.coordinates.tsv --query_is_circular --subject_is_circular --comparison



# Segmentation duplication 
python3 alisgcha.py duplication_chaining --input test_data/4029.coordinates.tsv --max_gap 5000 --scaled_distance 1 --fasta test_data/4029.fasta --is_circular --output test_data/4029.segmentation.tsv
python3 alisgcha.py duplication_chaining --input test_data/461.coordinates.tsv --max_gap 5000 --scaled_distance 1 --fasta test_data/461.fasta --is_circular --output test_data/461.segmentation.tsv
python3 alisgcha.py duplication_chaining --input test_data/ztritici.coordinates.tsv --max_gap 5000 --scaled_distance 1 --fasta test_data/ztritici.fasta --output test_data/ztritici.segmentation.tsv

# Sequence comparison
python3 alisgcha.py comparison_chaining --input test_data/10635_vs_10567.coordinates.tsv --fasta_query test_data/10635.fasta --fasta_subject test_data/10567.fasta --max_gap 5000 --scaled_distance 1 --query_is_circular --subject_is_circular --min_len 100 --output test_data/10635_vs_10567.segmentation.tsv

# Get Sequences
python3 alisgcha.py get_sequences --input test_data/4029.segmentation.tsv --fasta_query test_data/4029.fasta --output test_data/4029.segments.fasta
python3 alisgcha.py get_sequences --input test_data/461.segmentation.tsv --fasta_query test_data/461.fasta --output test_data/461.segments.fasta
python3 alisgcha.py get_sequences --input test_data/ztritici.segmentation.tsv --fasta_query test_data/ztritici.fasta --output test_data/ztritici.segments.fasta
python3 alisgcha.py get_sequences --input test_data/10635_vs_10567.segmentation.tsv --fasta_query test_data/10635.fasta  --fasta_subject test_data/10567.fasta --output test_data/10635_vs_10567.segments.fasta

# Plot
python3 alisgcha.py visualize --input test_data/4029.segmentation.tsv --scale kbp --output test_data/4029.html --fasta_query test_data/4029.fasta --query_is_subject
python3 alisgcha.py visualize --input test_data/461.segmentation.tsv --scale kbp --output test_data/461.html --fasta_query  test_data/461.fasta --query_is_subject --genbank test_data/461.gbk
python3 alisgcha.py visualize --input test_data/ztritici.segmentation.tsv --scale kbp --output test_data/ztritici.html --fasta_query  test_data/ztritici.fasta --query_is_subject 
python3 alisgcha.py visualize --input test_data/10635_vs_10567.segmentation.tsv --scale kbp --output test_data/10635_vs_10567.html --fasta_query test_data/10635.fasta --fasta_subject test_data/10567.fasta 
#python3 alisgcha.py visualize --input test_data/ztritici.segmentation.tsv --scale kbp --output test_data/ztritici.html --fasta_A test_data/ztritici.fasta --fasta_B test_data/ztritici.fasta --query_is_subject --genbank test_data/ztritici.gb
