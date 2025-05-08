########################
## Test commands file ##
########################

###################
## 1. Alignments ##
###################

python3 SegMantX.py generate_alignments -q test_data/4029.fasta -b test_data/4029.blast.x7 -a test_data/4029.coordinates.tsv -Q -SA
python3 SegMantX.py generate_alignments  -q test_data/461.fasta -b test_data/461.blast.x7 -a test_data/461.coordinates.tsv -Q -SA
python3 SegMantX.py generate_alignments  -q test_data/ztritici.fasta -b test_data/ztritici.blast.x7 -a test_data/ztritici.coordinates.tsv -SA -T 4 -W 28
python3 SegMantX.py generate_alignments  -q test_data/10635.fasta -s test_data/10567.fasta -b test_data/10635_vs_10567.blast.x7 -a test_data/10635_vs_10567.coordinates.tsv -Q -S 

#################
## 2. Chaining ##
#################

python3 SegMantX.py chain_self_alignments -i test_data/4029.coordinates.tsv -G 5000 -SG 1 -f test_data/4029.fasta -Q -o test_data/4029.segmentation.tsv
python3 SegMantX.py chain_self_alignments -i test_data/461.coordinates.tsv -G 5000 -SG 1 -f test_data/461.fasta -Q -o test_data/461.segmentation.tsv
python3 SegMantX.py chain_self_alignments -i test_data/ztritici.coordinates.tsv -G 5000 -SG 1 -f test_data/ztritici.fasta -o test_data/ztritici.segmentation.tsv
python3 SegMantX.py chain_alignments -i test_data/10635_vs_10567.coordinates.tsv -fq test_data/10635.fasta -fs test_data/10567.fasta -G 5000 -SG 1 -Q -S -ml 100 -o test_data/10635_vs_10567.segmentation.tsv

#############################################
## 3. Fetch chains as nucleotide sequences ##
#############################################

python3 SegMantX.py fetch_nucleotide_chains -i test_data/4029.segmentation.tsv -fq test_data/4029.fasta -o test_data/4029.segments.fasta
python3 SegMantX.py fetch_nucleotide_chains -i test_data/461.segmentation.tsv -fq test_data/461.fasta -o test_data/461.segments.fasta
python3 SegMantX.py fetch_nucleotide_chains -i test_data/ztritici.segmentation.tsv -fq test_data/ztritici.fasta -o test_data/ztritici.segments.fasta
python3 SegMantX.py fetch_nucleotide_chains -i test_data/10635_vs_10567.segmentation.tsv -fq test_data/10635.fasta  -fs test_data/10567.fasta -o test_data/10635_vs_10567.segments.fasta

####################
## 4. Visualizing ##
####################

python3 SegMantX.py visualize_chains -i test_data/4029.segmentation.tsv -S kbp -o test_data/4029.html -fq test_data/4029.fasta -QIS
python3 SegMantX.py visualize_chains -i test_data/461.segmentation.tsv -S kbp -o test_data/461.html -fq  test_data/461.fasta --query_is_subject -gf test_data/461.gbk
python3 SegMantX.py visualize_chains -i test_data/ztritici.segmentation.tsv -S kbp -o test_data/ztritici.html -fq  test_data/ztritici.fasta -QIS 
python3 SegMantX.py visualize_chains -i test_data/10635_vs_10567.segmentation.tsv -S kbp -o test_data/10635_vs_10567.html -fq test_data/10635.fasta -fs test_data/10567.fasta 