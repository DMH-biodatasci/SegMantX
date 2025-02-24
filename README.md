# SegMantX

**SegMantX** is a bioinformatics tool to chain local alignments. Initially, designed towards detection of DNA duplications in genomic sequences, it also provides a module to chain local alignments between two different sequences (e.g., for sequence comparisons). 
SegMantX has been tested mostly using BLASTn local alignments as seeds for chaining, although, alternative inputs for the chaining modules from different alignment approaches are also possible. Resulting chains can be visualized or fetched as nucleotide sequences. SegMantX provides a python-based command line tool and an app including a graphical user interface based on Streamlit. 

## Citation
If you use SegMantX in your research, please cite:

> **Dustin M Hanke, Tal Dagan**, "Title of Paper," *Journal Name*, Year, DOI: [DOI link]

## 📥 Installation

To install SegMantX, follow these steps:

### Prerequisites
Ensure you have Anaconda or Miniconda installed. 

### Installation Steps
```bash
# Clone the repository
git clone https://github.com/yourusername/SegMantX.git
cd SegMantX

# Create and activate a new conda environment from the provided .yml file
conda env create -f SegMantX.yml 

#Otherwise, specify the platform:
conda env create -f SegMantX_test.yml --platform linux-64 #On Linux and Windows
conda env create -f SegMantX_test.yml --platform linux-aarch64 #Alternatively, linux-aarch64 on Linux
conda env create -f SegMantX_test.yml --platform osx-64 #On MacOS

conda activate SegMantX
```

## Usage

### 🧩 SegMantX Modules  

Briefly, **SegMantX** is organized into modules:  

Main modules:
- **generate_alignments.py**: Computes alignments via BLASTn for the chaining modules.  
- **chain_self_alignments.py**: Chains local alignments from self-sequence alignment (e.g., towards duplication detection).  
- **chain_alignments.py**: Chains local alignments between two sequences (e.g., towards sequence comparisons).  
- **visualize_chains.py**: Generates a **segmentplot** (i.e., segments of chaining results) to visualize yielded chains for a sequence.
- **fetch_nucleotide_chains.py**: Extracts nucleotide sequences using the chained alignments and saves them as a **FASTA file**.

Additional module:
- **test_modules.py**: Downloads a test dataset and verifies the modules. 

Addtional SegMantX options:
- **help**: python3 SegMantX.py help - print out of module overview. 
- **help**: python3 SegMantX.py version - print out of SegMantX's version. 
- **help**: python3 SegMantX.py citation - print out of DOI. 

### ✅ 1. Verify Installation & Test SegMantX's Modules
Check if the installation was successful by running:
```bash
python SegMantX.py test_modules
#Confirm to download the test dataset with 'yes'
```

### SegMantX as command-line tool

Run SegMantX with the following command to see further options of SegMantX:
```bash
python SegMantX.py -h
```

Run a SegMantX module with the following command to display usage and parameters:
```bash
python SegMantX.py [module] -h
# e.g., python SegMantX.py generate_alignments.py -h
```

#### Generate alignments
Run SegMantX's **generate_alignments.py** module to compute seeds for the chaining process:
```bash
#Compute a self-sequence alignment:
python3 SegMantX.py generate_alignments  --query_file tests/NZ_AP022172.1.fasta --blast_output_file tests/NZ_AP022172.1.blast.x7 --alignment_hits_file tests/NZ_AP022172.1.alignment_coordinates.tsv --is_query_circular --self_sequence_alignment

##Compute a sequence alignment between two sequences:
python3 SegMantX.py generate_alignments  --query_file tests/NZ_CP018634.1.fasta --subject_file tests/NZ_CP022004.1.fasta --blast_output_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.blast.x7 --alignment_hits_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.alignment_coordinates.tsv --is_query_circular --is_subject_circular 
```

Output of generate alignments:
| (Default) output filename | Description |
|:----------:|:-----------:|
| blast_output.txt | Output file of BLASTn search in output format 7 |  
| alignment_hits.tsv | Output file restricted to q.start, q.end, s.end, s.start, and percentage sequence identity from BLASTn search, which is sufficient for the chaining modules | 


#### Self-sequence alignment chaining
Run SegMantX's **chain_self_alignments.py** module for chaining a self-sequence alignment (e.g., towards duplication detection):
```bash
python3 SegMantX.py chain_self_alignments --input_file tests/NZ_AP022172.1.alignment_coordinates.tsv --max_gap 5000 --scaled_gap 1 --fasta_file tests/NZ_AP022172.1.fasta --is_query_circular --output_file tests/NZ_AP022172.1.chains.tsv
```

#### Sequence alignment chaining 
Run SegMantX's **chain_alignments.py** module for chaining a sequence alignment (e.g., towards sequence comparison):
```bash
python3 SegMantX.py chain_alignments --input_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.alignment_coordinates.tsv --fasta_file_query tests/NZ_CP018634.1.fasta --fasta_file_subject tests/NZ_CP022004.1.fasta --max_gap 5000 --scaled_gap 1 --is_query_circular --is_subject_circular --min_length 100 -o tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.tsv
```

Output of chaining modules:
| (Default) output filename | Description |
|:----------:|:-----------:|
| chaining_output.tsv | Main output file of the chaining procedure containing chaining coordinates and metrics |  
| chaining_output.tsv.indices | Output file to trace back original local alignment hits that have been chained | 

#### Visualization
Run SegMantX's **visualize_chains.py** module to visualize chains in an interactive segmentplot:
```bash
#Visualize chaining results of one sequence (i.e., towards duplication detection)
python3 SegMantX.py visualize_chains --input_file tests/NZ_AP022172.1.chains.tsv --scale kbp --output_file tests/NZ_AP022172.1.html --fasta_file_query  tests/NZ_AP022172.1.fasta --query_is_subject --genbank_file tests/NZ_AP022172.1.gbk

#Visualize chaining results of two sequences (i.e., towards sequence comparison)
python3 SegMantX.py visualize_chains --input_file  tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.tsv --scale kbp --output_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.html --fasta_file_query tests/NZ_CP018634.1.fasta --fasta_file_subject tests/NZ_CP022004.1.fasta
```
Output of visualization module:
| (Default) output filename | Description |
|:----------:|:-----------:|
| plot.html | An interactive visualization (segment plot) of chains that can be opened in any web browser. |  


#### Get chains as nucleotide sequences
Run SegMantX's **fetch_nucleotide_chains.py** module to extract chains as nucleotide sequences from a fasta file:
```bash
#Get sequences for duplication downstream analysis:
python3 SegMantX.py fetch_nucleotide_chains --input_file tests/NZ_AP022172.1.chains.tsv --fasta_file_query tests/NZ_AP022172.1.fasta --output_file tests/NZ_AP022172.1.chains.fasta

#Get sequences for sequence comparison downstream analysis:
python3 SegMantX.py fetch_nucleotide_chains --input_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.tsv --fasta_file_query tests/NZ_CP018634.1.fasta  --fasta_file_subject tests/NZ_CP022004.1.fasta --output_file tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.fasta
```

Output of visualization module:
| (Default) output filename | Description |
|:----------:|:-----------:|
| chains.fasta | A fasta file containing the nucleotide sequences of yielded chains. |  

### SegMantX as app
Run the SegMantX app with the following command:
```bash
streamlit run app.py
```

Briefly, the app provides a graphical user interface to SegMantX's main modules via the following pages:

App pages:
- **Landing page**: Contains a brief description of the SegMantX app. 
- **Generate alignments**: Graphical user interface to apply **generate_alignments.py** 
- **Self-alignment chaining**: Graphical user interface to apply **chain_self_alignments.py**  
- **Alignment chaining**: Graphical user interface to apply **chain_alignments.py**  
- **Visualize chains**: Graphical user interface to apply **visualize_chains.py**  
- **Fetch chains**: Graphical user interface to apply **fetch_nucleotide_chains.py**  

### 📡 SegMantX as an Online Resource  
Note: The online version of **SegMantX** is provided as a **free Streamlit deployment**. While this allows easy access without local installation, please keep in mind the following limitations:  

- **Limited Computational Resources**: The free Streamlit Cloud version provides **only 1 CPU core and 1GB RAM**, which may not be sufficient for large-scale data processing.  
- **File Size Limits**: The maximum upload size is limited (can be increased but still limited).  
- **Session Timeouts**: Apps may **shut down due to inactivity** or **crash when handling large datasets**.  
- **No Guaranteed Maintenance**: This deployment is provided **as is**, and we do not ensure continuous uptime or long-term support.  
- **Better for Small Datasets**: For large-scale processing, it is **highly recommended to install SegMantX locally** using the provided Conda environment.  

🔗 **Website:** *[Insert your Streamlit app URL here]*  


## Contact
For questions, support, or bug report, open an issue.

