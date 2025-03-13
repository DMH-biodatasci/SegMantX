#!/usr/bin/env python3
import streamlit as st
import pandas as pd
from modules import *
import os
import time
from io import StringIO
from Bio import SeqIO
import copy

######################
## Helper functions ##
######################

def load_fasta(file):
    with open(file, 'r') as f:
        fasta_content = f.read()
    return fasta_content       
            
def create_tmp_fasta(fasta):
    if fasta is not None:
        temp_file_path = os.path.join(fasta.name)
        with open(temp_file_path, "wb") as f:
            f.write(fasta.getbuffer())
            
def check_input(input_file):
    if isinstance(input_file, pd.DataFrame):
        return True
    elif input_file:
        return True

def show_manual_generate_alignments():
    '''
    Displays the manual when an error occurs.
    '''
    st.markdown("""
    ## **User guidance**
    - Use the sidebar menu to upload required files, modify parameters and change output filenames.
    
    ### **Step 1. Select the purpose:**
    - **'Duplication detection'**: Computes a self-sequence alignment. The output of the self-sequence alignment may be passed to the self-alignment chaining module to detect duplications. 
    - **'Sequence comparison'**: Performs an alignment between two sequences (query and subject). The output of the sequence alignment between two sequences may be passed to the alignment chaining module to compare sequences.
    
    ### **Step 2. Upload FASTA file(s):**
    - **'Duplication detection'** requires a single sequence in FASTA format (query).
    - **'Sequence comparison'** requires two sequences in FASTA format (query and subject).
    
    ### **Step 3. Select the sequence topology of your sequence(s):**
    - Choosing the correct sequence topology ensures that alignment hits on **circular sequences** (such as most plasmids or viral genomes) are correctly chained, even when fragmented due to their linear representation in FASTA files.  
    - This is important for avoiding **discontinuous alignments** that can occur when working with circular sequences in a linear format (i.e., FASTA format).
    
    ### **Step 4. Adjust optional parameters:**
    
    #### E-value (Controls alignment sensitivity):
    - The **E-value** in BLAST estimates the number of random alignments expected by chance. It helps filtering low-confidence matches and retaining biologically relevant seeds for chaining.
    - Example E-value settings:  
        - High specificity: `1e-9` (Fewer, more reliable seeds) - RECOMMENDED  
        - 'Balanced approach': `1e-5` (Balance of sensitivity and specificity)  
        - Higher sensitivity: `1e-1` (Morfe seeds, but may introduce noise—use cautiously) - NOT RECOMMENDED
        
    #### Minimum percentage sequence identity
    - This parameter sets a threshold for sequence alignments hits being considered for chaining according to a percentage sequence identity (i.e., alignment hits below the threshold are excluded).
    
    #### Word Size (Defines the seed length):
    - The **word size** defines the length of the initial exact match (seed) required for alignment extension.
    - Choose a higher word size to speed up the alignment generation and chaining on larger sequences.
    - Example word size settings:  
        - For short sequences (e.g., plasmids): `Word size = 7-11` (More sensitive, detects weak matches)  
        - For longer genomic sequences (e.g., chromosomes): `Word size = 20-30` (Faster, focuses on strong matches)
    
    #### Threads:
    - **Threads** refer to the number of CPU cores used to parallelize BLAST computations.
    - More threads allow for faster processing by handling multiple alignment tasks simultaneously, improving overall speed and efficiency.
    
    ### **Step 5. Choose filenames for your output files:**
    - **Export BLAST output (Format 7)**: Choose a filename for the alignment computation results in **BLAST output format 7**.
    - **Export main alignment hit data**: Choose a filename for the main alignment hit data used by the chaining modules. The data is stored in a **tab-delimited file** with the following five columns:
        - **Query start**
        - **Query end**
        - **Subject start**
        - **Subject end**
        - **Percentage sequence identity**
        
    ### **Step 6. Click the 'Generate alignments for chaining' button to run it.**
    - A table containing the results will appear
    - The data will be exported automatically
    """)
    
def show_manual_self_alignment_chaining():
    '''
    Displays the manual when an error occurs.
    '''
    st.markdown("""
    ## **User guidance**
    - Use the sidebar menu to upload required files, modify parameters and change output filenames.
    
    ### **Step 1. Select True/False for 'Use output loaded in memory from generate alignments page'**
    - True: The input loaded in memory from the generate alignments page will be used as input (no data upload required).
    - False: The input data/file for the self-alignment chaining needs to be uploaded by the user.
    - Note, this parameter will not affect the analysis if there is no data in memory (i.e., input upload is still required).
    - Some conditional parameters may disappear from the page if 'True' is selected.
    
    ### **Step 2. Upload alignment data file :**
    - Select an alignment data file from your local computer. 
    - This step is necessary if False was selected in **Step 1**
    - The alignment (or seed) data file from your local computer should fulfill the following requirements:
        1. A tab-delimited file 
        2. Five columns containing: Query start, Query end, Subject start, Subject end, Percentage sequence identity
    - Alternatively, a BLAST output format 7 file can be used as input -> Set 'Input file is BLAST output format 7' to True!
    
    ### **Step 3. Set True/False for 'Input file is BLAST output format 7':**
    - False: if the input data is a tab-delimited file containing five columns (see **Step 2**).
    - True: if the input data is a BLAST output format 7 file.
    
    ### **Step 4. Select the sequence topology of your sequence:**
    - Choosing the correct sequence topology ensures that alignment hits on **circular sequences** (such as most plasmids or viral genomes) are correctly chained, even when fragmented due to their linear representation in FASTA files.  
    - This is important for avoiding **discontinuous alignments** that can occur when working with circular sequences in a linear format (i.e., FASTA format).
    - IMPORTANT: If this option is set to True, it becomes mandatory to provide either the FASTA sequence or the sequence length itself.
    
    ### **Step 5. Provide the sequence length for your sequence(s):**
    #### Upload fasta file of query:
    - Required for correct alignment chaining on sequences with circular sequence topology
    - Automatic sequence length extraction from FASTA file if 'Circular sequence topology' has been set to True
    - Alternatively, you may provide the sequence length itself.
    
    #### Sequence length of query:
    - Required for correct alignment chaining on sequences with circular sequence topology
    - Alternatively, you may provide the FASTA file of the query sequence to determine the sequence length automatically.
    
    ### **Step 6. Adjust parameters / options:**
    
    #### Max. gap size [bp]:
    - Maximum gap size between alignment hits for chaining
    
    #### Scaled gap:
    - Minimum scaled gap between alignment hits for chaining. The scaled gap is a threshold metric that chains local alignments with a hit to gap length proportion lower than the selected scaled gap. 
    
    #### Minimum alignment hit length:
    - Minium length of alignment hits to consider them as seeds for chaining
    
    ### **Step 7. Choose filenames for your output files:**
    - **Export chained alignments to**: Choose a filename to save the tab-delimited output table of the chaining procedure.

    ### **Step 8. Click the 'Run self-sequence alignment chaining' button to run it.**
    - A table containing the results will appear
    - The data will be exported automatically
    """)
    
def show_manual_alignment_chaining():
    '''
    Displays the manual when an error occurs.
    '''
    st.markdown("""
    ## **User guidance**
    - Use the sidebar menu to upload required files, modify parameters and change output filenames.
    
    ### **Step 1. Select True/False for 'Use output loaded in memory from generate alignments page'**
    - True: The input loaded in memory from the generate alignments page will be used as input (no data upload required).
    - False: The input data/file for the alignment chaining needs to be uploaded by the user.
    - Note, this parameter will not affect the analysis if there is no data in memory (i.e., input upload is still required).
    - Some conditional parameters may disappear from the page if 'True' is selected.
    
    ### **Step 2. Upload alignment data file :**
    - Select an alignment data file from your local computer. 
    - This step is necessary if False was selected in **Step 1**
    - The alignment (or seed) data file from your local computer should fulfill the following requirements:
        1. A tab-delimited file 
        2. Five columns containing: Query start, Query end, Subject start, Subject end, Percentage sequence identity
    - Alternatively, a BLAST output format 7 file can be used as input -> Set 'Input file is BLAST output format 7' to True!
    
    ### **Step 3. Set True/False for 'Input file is BLAST output format 7':**
    - False: if the input data is a tab-delimited file containing five columns (see **Step 2**).
    - True: if the input data is a BLAST output format 7 file.
    
    ### **Step 4. Select the sequence topology of your sequences:**
    - Choosing the correct sequence topology ensures that alignment hits on **circular sequences** (such as most plasmids or viral genomes) are correctly chained, even when fragmented due to their linear representation in FASTA files.  
    - This is important for avoiding **discontinuous alignments** that can occur when working with circular sequences in a linear format (i.e., FASTA format).
    - IMPORTANT: If this option is set to True, it becomes mandatory to provide either the FASTA sequence or the sequence length itself for the corresponding sequence (i.e., query and/or subject sequences).
    
    ### **Step 5. Provide the sequence length for your sequence(s):**
    #### Upload fasta file of query & subject:
    - Required for correct alignment chaining on sequences with circular sequence topology
    - Automatic sequence length extraction from FASTA file(s) if 'Circular sequence topology' has been set to True
    - Alternatively, you may provide the sequence lengths themselves.
    
    #### Sequence length of query & subject:
    - Required for correct alignment chaining on sequences with circular sequence topology
    - Alternatively, you may provide the FASTA file of the query (& subject) sequence to determine the sequence length automatically.
    
    ### **Step 6. Adjust parameters / options:**
    
    #### Max. gap size [bp]:
    - Maximum gap size between alignment hits for chaining
    
    #### Scaled gap:
    - Minimum scaled gap between alignment hits for chaining. The scaled gap is a threshold metric that chains local alignments with a hit to gap length proportion lower than the selected scaled gap. 
        
    #### Minimum alignment hit length:
    - Minium length of alignment hits to consider them as seeds for chaining
    
    ### **Step 7. Choose filenames for your output files:**
    - **Export chained alignments to**: Choose a filename to save the tab-delimited output table of the chaining procedure.

    ### **Step 8. Click the 'Run sequence alignment chaining' button to run it.**
    - A table containing the results will appear
    - The data will be exported automatically
    """)
    
def show_manual_visualize_chains():
    '''
    Displays the manual when an error occurs.
    '''
    st.markdown("""
    ## **User guidance**
    - Use the sidebar menu to upload required files, modify parameters and change output filenames.
    
    ### **Step 1. Select True/False for 'Use output loaded in memory from self-alignment chaining or alignment chaining page.'**
    - True: The input loaded in memory from the self-alignment chaining or alignment chaining page will be used as input (no data upload required).
    - False: The input data/file(se) to visualize chains for a given sequence need to be uploaded by the user.
    - Note, this parameter will not affect the analysis if there is no data in memory (i.e., input upload is still required).
    - Some conditional parameters may disappear from the page if 'True' is selected.
    - CAUTION: If 'True' is selected the most recent results in memory will be used! 
    
    ### **Step 2. Upload chained alignments file:**
    - Select a chained alignment data file from your local computer. 
    - This step is necessary if False was selected in **Step 1**
    - The selected file should be the main output of one of the chaining modules (i.e., self-alignment chaining or alignment chaining).
    
    ### **Step 3. Select input type:**
    - Self-alignment chaining: The input data originates from the self-alignment chaining (i.e., query=subject). The same sequence will be used in the visualization for x- and y-axis.
    - Alignment chaining of two sequences: The input data originates from the alignment chaining (i.e., query is not subject). The query sequence will be used for the x-axis and the subject sequence will be used for the y-axis.
    
    ### **Step 4. Provide the sequence length for your sequence(s):**
    #### Upload fasta file of query & subject:
    - Required for correct x- and y-axis length and ticks
    - Automatic sequence length extraction from FASTA file(s) 
    - Alternatively, you may provide the sequence lengths themselves.
    
    #### Sequence length your sequence(s):
    - Required for correct x- and y-axis length and ticks
    - Alternatively, you may provide the FASTA file of the query (& subject) sequence to determine the sequence length automatically.
    
    ### **Step 5. Adjust parameters / options:**
    
    #### Scale:
    - Select the scale for the x- and y-axis: bp (basepairs), kbp (kilo-basepairs), mbp (mega-basepairs)
    
    #### Upload genbank file for feature visualization:
    - If a genbank file is provided, features (i.e., CDSs and pseudogenes) are visualized as rectangles 
    - Note, that this will increase the running time for large sequences (i.e., it depends on the amount of features).
    
    ### **Step 6. Choose filenames for your output files:**
    - **Export plot to**: Choose a filename to save an interactive plot (.html file) which can be opened using any browser.

    ### **Step 7. Click the 'Visualize chains' button to run it.**
    - An interactive segmentplot will appear
    - The plot will be exported automatically, but a download button is provided as well
    - You may resume to the user guidance, when clicking the download button
    """)
    
def show_manual_fetch_nucleotide_chains():
    '''
    Displays the manual when an error occurs.
    '''
    st.markdown("""
    ## **User guidance**
    - Use the sidebar menu to upload required files, modify parameters and change output filenames.
    
    ### **Step 1. Select True/False for 'Use output loaded in memory from self-alignment chaining or alignment chaining page.'**
    - True: The input loaded in memory from the self-alignment chaining or alignment chaining page will be used as input (no data upload required).
    - False: The input data/file(se) to fetch chains as nucleotide sequences for given sequence(s) need to be uploaded by the user.
    - Note, this parameter will not affect the analysis if there is no data in memory (i.e., input upload is still required).
    - Some conditional parameters may disappear from the page if 'True' is selected.
    - CAUTION: If 'True' is selected the most recent results in memory will be used! 
    
    ### **Step 2. Upload chained alignments file:**
    - Select a chained alignment data file from your local computer. 
    - This step is necessary if False was selected in **Step 1**
    - The selected file should be the main output of one of the chaining modules (i.e., self-alignment chaining or alignment chaining).
    
    ### **Step 3. Select input type:**
    - Self-alignment chaining: The input data originates from the self-alignment chaining (i.e., query=subject). The chains as nucleotide sequences in FASTA-format will be extracted from one sequence.
    - Alignment chaining of two sequences: The input data originates from the alignment chaining (i.e., query is not subject). The chains as nucleotide sequences in FASTA-format will be extracted from the query and subject sequence. Hint: Ensure that the query and subject sequences are consistently designated as such throughout the entire analysis.
        
    ### **Step 5. Provide FASTA file(s) to extract the chains as nucleotide sequences:**
    #### Upload FASTA file of query (& subject):
    - Now the coordinates of the chained alignments will be used as a basis to extract nucleotide sequences (i.e., chains) from the FASTA sequence(s).
    
    ### **Step 7. Choose filenames for your output files:**
    - **Export nucleotide chains to**: Choose a filename to save the FASTA file containing nucleotide chains.
    - Hint: If the chains of two sequences have been extracted one FASTA file will be created. Corresponding nucleotide chains originating from the query and subject sequences are labeled in the header, for example, 1_query and 1_subject, 2_query, 2_subject ... , n_query, n_subject.

    ### **Step 8. Click the 'Fetch nucleotide chains' button to run it.**
    - A download button will appear
    - The FASTA file will be exported automatically, but a download button is provided as well
    - You may resume to the user guidance, when clicking the download button
    """)
          
####################
## Page functions ##
####################

def landing_page():
    '''
    Creates the landing page of StreamSegMantX.py containing informal text.
    '''
    #st.title("SegMantX")
    image_path_mascot = os.path.expandvars("$CONDA_PREFIX/bin/img/polished_mascot_segmantx.png")
    st.image(image_path_mascot,  width=300, use_container_width=False)
    st.write("This app employs streamlit to provide a graphical interface of SegMantX.")
    
    st.write(
        "SegMantX is a bioinformatics tool designed to support a user-friendly chaining of local sequence alignments. "
        "This app simplifies the chaining process by providing a graphical user interface. Note, that the app only handles the chaining process of a sequence one by one."
    )
    
    st.write(
        "SegMantX embeds BLASTn to generate local alignments as seeds for the chaining process. It's possible to skip the recommended alignment generation step based on BLASTn if the user provides alternative input data as seeds for the chaining process organized in a tab-delimited file containing the following five columns: Query start, Query end, Subject start, Subject end, Percentage sequence identity."
    )
    
    st.write(
        "Briefly, SegMantX is organised into five modules:"
    )
    image_path_workflow = os.path.expandvars("$CONDA_PREFIX/bin/img/workflow.png")
    st.image(image_path_workflow,  use_container_width=True)
    
    st.markdown(
    """
    1. Generate alignments: processes nucleotide sequence(s) to compute local alignments, optionally formatting them for further analysis. 
    2. Self-alignment chaining: Chains local alignments from self-sequence alignment (e.g., towards duplication detection).
    3. Alignment chaining: Chains local alignments between two sequences (e.g., towards sequence comparisons).
    4. Visualize chains: Generates a segmentplot (i.e., segments of chaining results) to visualize yielded chains for a sequence (self-alignment) or two sequences (alignment).
    5. Fetch chains as sequences: Extracts yielded chains as nucleotide sequences and saves them as fasta file.
    """
    )
    
    st.markdown("**Get started by navigating through the sidebar menu on the left!**")
    
    st.write(
        "For further details visit also:"
    )
    
    st.markdown(
    """
    - GitHub: https://github.com/DMH-biodatasci/SegMantX
    - Manual pages: https://dmh-biodatasci.github.io/SegMantX/
    - DOI: XXXXXXXXXXXXX
    """
    )
    
            
def generate_alignments_page():
    '''
    Function to provide a page for the 'generate_alignments.py' script of SegMantX.
    '''
    st.title("Generate alignment files for chaining")
    
    placeholder = st.empty()
    with placeholder.container():
        show_manual_generate_alignments()
        
    st.sidebar.header("Parameters for alignment computation:")
    duplication_or_comparison = st.sidebar.selectbox("Purpose", ["Duplication detection", "Sequence comparison"])
    st.sidebar.write("Note, that 'duplication detection' computes a self-sequence alignment and 'sequence comparison' performs alignments among two sequences.")
    query_fasta_file = st.sidebar.file_uploader("Upload query fasta file", type=["fasta"])
    is_query_circular = st.sidebar.selectbox("Circular sequence topology of query sequence", [False, True])
    if duplication_or_comparison == 'Sequence comparison':
        subject_fasta_file = st.sidebar.file_uploader("Upload subject fasta file", type=["fasta"])
        is_subject_circular = st.sidebar.selectbox("Circular sequence topology of subject sequence", [False, True])
    st.sidebar.write("BLASTn computation parameters:")
    evalue = st.sidebar.number_input("E-Value", min_value=1e-20, max_value=1e-0, value=1e-9, format="%.1e")
    perc_identity = st.sidebar.number_input("Percentage sequence identity", min_value=0, max_value=100, value=60)
    st.sidebar.write("For larger sequences (e.g., chromosomes) it is recommended to increase the word size (e.g., >28)")
    word_size = st.sidebar.number_input("Word size", min_value=1, max_value=100, value=11)
    threads = st.sidebar.number_input("Threads", min_value=1, max_value=100, value=1)
    blast_output = st.sidebar.text_input("Export BLAST output format 7 to:", value='blast_output.txt')
    coordinates_output = st.sidebar.text_input("Export main alignment hit data to:", value='alignment_hits.tsv')

    try:
        if not query_fasta_file == None:
            create_tmp_fasta(query_fasta_file)
    except UnboundLocalError:
        pass
    try:
        if not subject_fasta_file == None:
            create_tmp_fasta(subject_fasta_file)
    except UnboundLocalError:
        pass
    
    if st.sidebar.button("Generate alignments for chaining"):
        try:
            if query_fasta_file:
                placeholder.empty()
                if duplication_or_comparison == 'Duplication detection':
                    alignment_df = generate_alignments.blastn_self_sequence_alignment(
                        query=query_fasta_file.name,
                        blast_output=blast_output,
                        alignments_output=coordinates_output,
                        is_circular=is_query_circular,
                        evalue=evalue,
                        min_identity_percentage=perc_identity,
                        threads=threads,
                        word_size=word_size
                    )
                elif duplication_or_comparison == "Sequence comparison":
                    alignment_df = generate_alignments.blastn_sequence_alignment(
                        query=query_fasta_file.name, 
                        subject=subject_fasta_file.name, 
                        blast_output=blast_output, 
                        alignments_output=coordinates_output,
                        is_query_circular=is_query_circular,
                        is_subject_circular=is_subject_circular,
                        evalue=evalue,
                        min_identity_percentage=perc_identity,
                        threads=threads,
                        word_size=word_size
                    )
                alignment_df_with_headers = alignment_df.copy(deep=True)
                alignment_df_with_headers.columns = ['Query start [bp]', 'Query end [bp]', 'Subject start [bp]', 'Subject end [bp]', 'Perc. identity [%]']
                st.dataframe(alignment_df_with_headers, use_container_width=True)

                st.session_state["alignment_result"] = alignment_df
                tsv_data = alignment_df_with_headers.to_csv(sep='\t', index=False)

                st.download_button(
                    label="Download local alignment hits as .tsv file.",
                    data=tsv_data,
                    file_name=coordinates_output,
                    mime="text/tab-separated-values"
                )

                try:
                    os.remove(query_fasta_file.name)
                except UnboundLocalError:
                    pass
                except FileNotFoundError:
                    pass
                try:
                    os.remove(subject_fasta_file.name)
                except UnboundLocalError:
                    pass
                except FileNotFoundError:
                    pass
        except Exception as e:
            st.error("An ERROR occured. Please check the user guidance for the module generate alignments.")
            show_manual_generate_alignments()

            
def self_alignment_chaining_page():
    '''
    Function to provide a page for the 'chain_self_alignments.py' script of SegMantX.
    '''
    st.title("Chaining self-sequence alignment")
    st.write("This module is designed towards duplication detection and requires the output from 'Generate alignments' with the selected purpose 'Duplication detection' as input.")
    
    placeholder = st.empty()
    with placeholder.container():
        show_manual_self_alignment_chaining()

    st.sidebar.header("Parameters for self-sequence alignment chaining:")
    use_session_data = st.sidebar.selectbox("Use output loaded in memory from generate alignments page", [False, True])
    if use_session_data and "alignment_result" in st.session_state:
        alignment_coordinate_file = st.session_state["alignment_result"]
        blast_outfmt7 = False
    else:
        alignment_coordinate_file = st.sidebar.file_uploader("Upload alignment data file", type=["csv", "tsv", "txt", "blast", "out"])
        blast_outfmt7 = st.sidebar.selectbox("Input file is BLAST output format 7", [False, True])
    sequence_is_circular = st.sidebar.selectbox("Circular sequence topology of query sequence", [False, True])
    max_gap = st.sidebar.number_input("Max. gap size [bp]", min_value=0, value=5000)
    scaled_gap = st.sidebar.number_input("Scaled gap", min_value=0.0, value=1.0)
    fasta_file = st.sidebar.file_uploader("Upload fasta file of query", type=["fasta"])
    replicon_size = st.sidebar.number_input("Sequence length of query (optional, if fasta file is provided)", min_value=0, value=0)
    min_len = st.sidebar.number_input("Minimum alignment hit length", min_value=0, value=200)
    output_file = st.sidebar.text_input("Export chained alignments to:", value='chaining_output.tsv')
    
    check_value = check_input(alignment_coordinate_file)
    
    try:
        if not fasta_file == None:
            create_tmp_fasta(fasta_file)
    except UnboundLocalError:
        pass
    
    if st.sidebar.button("Run self-sequence alignment chaining"):
        if check_value:
            try:
                placeholder.empty()
                chaining_df = chain_self_alignments.chain_self_sequence_alignment(
                    input_file=alignment_coordinate_file,
                    max_gap=max_gap,
                    scaled_gap=scaled_gap,
                    seq_len=replicon_size if replicon_size > 0 else None,
                    is_query_circular=sequence_is_circular,
                    min_len=min_len,
                    blast_outfmt7=blast_outfmt7,
                    fasta_file=fasta_file.name,
                    output_file=output_file
                )
            
                if chaining_df is None or isinstance(chaining_df, str) or chaining_df.empty:
                    st.write(chaining_df)
                    st.write("The input data format is wrong, mandatory parameters/files are missing, or no valid data was found.")

                else:
                    st.dataframe(chaining_df, use_container_width=True)
                    st.session_state["chaining_result"] = chaining_df

                    tsv_data = chaining_df.to_csv(sep='\t', index=False)

                    st.download_button(
                        label="Download chaining results as .tsv file.",
                        data=tsv_data,
                        file_name=output_file,
                        mime="text/tab-separated-values"
                    )
                try:
                    os.remove(fasta_file.name)
                except UnboundLocalError:
                    pass
                except FileNotFoundError:
                    pass
            except Exception as e:
                st.error("An ERROR occured. Please check the user guidance for the module self-alignment chaining.")
                st.error('{}'.format(e))
                show_manual_self_alignment_chaining() 
        

def alignment_chaining_page():
    '''
    Function to provide a page for the 'chain_alignments.py' script of SegMantX.
    '''
    st.title("Chaining sequence alignment between two sequences")
    st.write("This module is designed towards sequence comparisons and requires the output from 'Generate alignments' with the selected purpose 'Sequence comparison' as input.")
    
    placeholder = st.empty()
    with placeholder.container():
        show_manual_alignment_chaining()

    st.sidebar.header("Parameters for chaining alignments between two sequences:")
    
    use_session_data = st.sidebar.selectbox("Use output loaded in memory from generate alignments page", [False, True])
    if use_session_data and "alignment_result" in st.session_state:
        alignment_coordinate_file = st.session_state["alignment_result"]
        blast_outfmt7 = False
    else:
        alignment_coordinate_file = st.sidebar.file_uploader("Upload alignment data file", type=["csv", "tsv", "txt", "blast", "out"])
        blast_outfmt7 = st.sidebar.selectbox("Input is BLAST output format 7", [False, True])
        
    is_query_circular = st.sidebar.selectbox("Circular sequence topology of query sequence", [False, True])
    is_subject_circular = st.sidebar.selectbox("Circular sequence topology of subject sequence", [False, True])
    max_gap = st.sidebar.number_input("Max Gap", min_value=0, value=5000)
    scaled_gap = st.sidebar.number_input("Scaled Gap", min_value=0.0, value=1.0)
    fasta_file_query = st.sidebar.file_uploader("Upload fasta file of query", type=["fasta"])
    seq_len_query = st.sidebar.number_input("Sequence length of query (optional, if fasta file is provided)", min_value=0, value=0)
    fasta_file_subject = st.sidebar.file_uploader("Upload fasta file of subject", type=["fasta"])
    seq_len_subject = st.sidebar.number_input("Sequence length of subject (optional, if fasta file is provided)", min_value=0, value=0)
    min_len = st.sidebar.number_input("Minimum alignment hit length", min_value=0, value=200)
    output_file = st.sidebar.text_input("Export chained alignments to:", value='chaining_output.tsv')
    
    check_value = check_input(alignment_coordinate_file)
    
    try:
        if not fasta_file_query == None:
            create_tmp_fasta(fasta_file_query)
    except UnboundLocalError:
        pass
    try:
        if not fasta_file_subject == None:
            create_tmp_fasta(fasta_file_subject)
    except UnboundLocalError:
        pass
    
    
    if st.sidebar.button("Run sequence alignment chaining"):
        if check_value:
            try:
                placeholder.empty()
                chaining_df = chain_alignments.chain_sequence_alignment(
                    input_file=alignment_coordinate_file,
                    max_gap=max_gap,
                    scaled_gap=scaled_gap,
                    seq_len_query=seq_len_query if seq_len_query > 0 else None,
                    seq_len_subject=seq_len_subject if seq_len_subject > 0 else None,
                    is_query_circular=is_query_circular,
                    is_subject_circular=is_subject_circular,
                    min_len=min_len,
                    blast_outfmt7=blast_outfmt7,
                    fasta_file_query= None if fasta_file_query == None else fasta_file_query.name,
                    fasta_file_subject= None if fasta_file_subject == None else fasta_file_subject.name,
                    output_file=output_file
                )
                
            
                if chaining_df is None or isinstance(chaining_df, str) or chaining_df.empty:
                    st.write("The input data format is wrong, mandatory parameters/files are missing, or no valid data was found.")
                else:
                    st.dataframe(chaining_df, use_container_width=True)
                    st.session_state["chaining_result"] = chaining_df

                    tsv_data = chaining_df.to_csv(sep='\t', index=False)

                    st.download_button(
                        label="Download chaining results as .tsv file.",
                        data=tsv_data,
                        file_name=output_file,
                        mime="text/tab-separated-values"
                    )
                try:
                    os.remove(fasta_file_query.name)
                except UnboundLocalError:
                    pass
                except FileNotFoundError:
                    pass
                try:
                    os.remove(fasta_file_subject.name)
                except UnboundLocalError:
                    pass
                except FileNotFoundError:
                    pass
                
            except Exception as e:
                st.error("An ERROR occured. Please check the user guidance for the module alignment chaining.")
                show_manual_alignment_chaining() 
                 

def fetch_chains_as_sequences_page():
    '''
    Function to provide a page for the 'fetch_nucleotide_chains.py' script of SegMantX.
    '''
    st.title("Fetch nucleotide sequences from chained alignments in FASTA format.")
    st.sidebar.header("Parameters for fetching chains as nucleotide sequences:")
    
    placeholder = st.empty()
    with placeholder.container():
        show_manual_fetch_nucleotide_chains()
    
    use_session_data = st.sidebar.selectbox("Use output loaded in memory from self-alignment chaining or alignment chaining page", [False, True])
    if use_session_data and "chaining_result" in st.session_state:
        st.sidebar.header("Note, recent results loaded in memory of this session from self-alignment chaining or alignment chaining page will be used. The most recent chaining results obtained will be used.")
        alignment_coordinate_file = st.session_state["chaining_result"]
    else:
        alignment_coordinate_file = st.sidebar.file_uploader("Upload chained alignments file", type=["csv", "tsv", "txt", "blast", "out"])
    duplication_or_comparison = st.sidebar.selectbox("Input type", ["Self-alignment chaining", "Alignment chaining of two sequences"])
    if duplication_or_comparison == "Self-alignment chaining":
        fasta_file_query = st.sidebar.file_uploader("Upload fasta file of query", type=["fasta"])
        output_file = st.sidebar.text_input("Export nucleotide chain sequences to:", value='chains.fasta')
    elif duplication_or_comparison == "Alignment chaining of two sequences":
        fasta_file_query = st.sidebar.file_uploader("Upload fasta file of query", type=["fasta"])
        fasta_file_subject = st.sidebar.file_uploader("Upload fasta file of subject", type=["fasta"])
        output_file = st.sidebar.text_input("Export nucleotide chain sequences to:", value='chains.fasta')
            
    try:
        if not fasta_file_query == None:
            create_tmp_fasta(fasta_file_query)
    except UnboundLocalError:
        pass
    try:
        if not fasta_file_subject == None:
            create_tmp_fasta(fasta_file_subject)
    except UnboundLocalError:
        pass
    
    check_value = check_input(alignment_coordinate_file)
    
    if st.sidebar.button("Fetch nucleotide sequences"):
        if check_value:
            try:
                placeholder.empty()
                if duplication_or_comparison == "Self-alignment chaining":
                    sequences = fetch_nucleotide_chains.get_chained_sequences(chained_hits=alignment_coordinate_file, 
                                                            fasta_file= None if fasta_file_query == None else fasta_file_query.name,
                                                            output_fasta=output_file)
                elif duplication_or_comparison == "Alignment chaining of two sequences":
                    sequences = fetch_nucleotide_chains.get_chained_sequences_from_two_sequences(chained_hits=alignment_coordinate_file, 
                                                            fasta_file_query= None if fasta_file_query == None else fasta_file_query.name, 
                                                            fasta_file_subject= None if fasta_file_subject == None else fasta_file_subject.name,
                                                            output_fasta=output_file)

                # Old feature - visualizing the whole fasta file is too memory intensive
                #if sequences != None:
                #    seq_file = load_fasta(sequences)
                #    st.text_area("FASTA Content", seq_file, height=600)

                st.download_button(
                    label="Download FASTA file",
                    data=load_fasta(sequences).encode('utf-8'),
                    file_name=output_file,
                    mime='text/plain'
                )

                try:
                    os.remove(fasta_file_query.name)
                except UnboundLocalError:
                    pass
                except FileNotFoundError:
                    pass
                try:
                    os.remove(fasta_file_subject.name)
                except UnboundLocalError:
                    pass
                except FileNotFoundError:
                    pass
            except Exception as e:
                st.error("An ERROR occured. Please check the user guidance for the module fetch chains as sequences.")
                show_manual_fetch_nucleotide_chains() 
            

def visualize_chains_page():
    '''
    Function to provide a page for the 'visualize_chains.py' script of SegMantX.
    '''
    st.title("Generates a segmentplot of yielded chains for a sequence.")
    st.text("Warning: Chains originating from sequences that are characterized by a circular sequence topology may appear with a steep slope. These chains may look abnormal by visual inspection.")
    st.sidebar.header("Parameters for segmentplot visualization")
    
    placeholder = st.empty()
    with placeholder.container():
        show_manual_visualize_chains()
    
    use_session_data = st.sidebar.selectbox("Use output loaded in memory from self-alignment chaining or alignment chaining page", [False, True])
    if use_session_data and "chaining_result" in st.session_state:
        st.sidebar.header("Note, that recent results loaded in memory of this session from self-alignment chaining or alignment chaining page will be used. The most recent chaining results will be used.")
        chaining_data = st.session_state["chaining_result"]
    else:
        chaining_data = st.sidebar.file_uploader("Upload chained alignments file", type=["csv", "tsv", "txt", "blast", "out"])
    
    duplication_or_comparison = st.sidebar.selectbox("Input type", ["Self-alignment chaining", "Alignment chaining of two sequences"])
    if duplication_or_comparison == "Self-alignment chaining":
        fasta_file_query = st.sidebar.file_uploader("Upload fasta file of query", type=["fasta"])
        seq_len_query = st.sidebar.number_input("Replicon Size", value=0)
        scale = st.sidebar.selectbox("Scale", ["kbp", "bp", "mbp"])
        genbank = st.sidebar.file_uploader("Upload genbank file for feature visualization", type=["gb", "gbk"])
        output_file = st.sidebar.text_input("Export plot to:", value='plot.html')
        seq_len_subject = 0
        
    elif duplication_or_comparison == "Alignment chaining of two sequences":
        fasta_file_query = st.sidebar.file_uploader("Upload fasta file of query", type=["fasta"])
        seq_len_query = st.sidebar.number_input("Sequence length of query (optional, if fasta file is provided)", value=0)
        fasta_file_subject = st.sidebar.file_uploader("Upload fasta file of subject", type=["fasta"])
        seq_len_subject = st.sidebar.number_input("Sequence length of subject (optional, if fasta file is provided)", value=0)
        scale = st.sidebar.selectbox("Scale", ["kbp", "bp", "mbp"])
        genbank = st.sidebar.file_uploader("Upload genbank file for feature visualization", type=["gb", "gbk"])
        output_file = st.sidebar.text_input("Export plot to:", value='plot.html')
    
    if seq_len_query == 0:
        seq_len_query = None
    if seq_len_subject == 0:
        seq_len_subject = None
        
    try:
        if not fasta_file_query == None:
            create_tmp_fasta(fasta_file_query)
    except UnboundLocalError:
        pass
    try:
        if not fasta_file_subject == None:
            create_tmp_fasta(fasta_file_subject)
    except UnboundLocalError:
        pass
    try:
        if not genbank == None:
            genbank_name = genbank.name
            create_tmp_fasta(genbank)
        else:
            genbank_name = None
    except UnboundLocalError:
        genbank_name = None
        pass
        
    
    if st.sidebar.button("Visualize chains"):
        try:
            if check_input(chaining_data):
                placeholder.empty()
                if duplication_or_comparison == "Self-alignment chaining":
                    fig = visualize_chains.segmentplot_of_chains(
                        chained_hits=chaining_data,
                        fasta_file_query= None if fasta_file_query == None else fasta_file_query.name,
                        seq_len_query=seq_len_query,
                        genbank=genbank_name,
                        scale = scale,
                        query_is_subject=True,
                        output_file=output_file,
                        width=800,
                        height=600
                    )
                elif duplication_or_comparison == "Alignment chaining of two sequences":
                    fig = visualize_chains.segmentplot_of_chains(
                        chained_hits=chaining_data,
                        fasta_file_query= None if fasta_file_query == None else fasta_file_query.name,
                        seq_len_query=seq_len_query,
                        fasta_file_subject= None if fasta_file_subject == None else fasta_file_subject.name,
                        seq_len_subject=seq_len_subject,
                        genbank=genbank_name,
                        scale = scale,
                        query_is_subject=False,
                        output_file=output_file,
                        width=800,
                        height=600
                    )

                with open("plot.html", "r") as f:
                    html_content = f.read()
                st.components.v1.html(html_content, width=800, height=600)

                st.download_button(
                    label="Download plot as HTML",
                    data=fig.to_html(),
                    file_name=output_file,
                    mime="text/html"
                )

                try:
                    os.remove(fasta_file_query.name)
                except UnboundLocalError:
                    pass
                except FileNotFoundError:
                    pass
                try:
                    os.remove(fasta_file_subject.name)
                except UnboundLocalError:
                    pass
                except FileNotFoundError:
                    pass
                if genbank_name != None:
                    try:
                        os.remove(genbank_name)
                    except UnboundLocalError:
                        pass
                    except FileNotFoundError:
                        pass
        except Exception as e:
            st.error("An ERROR occured. Please check the user guidance for the module visualize chains.")
            show_manual_visualize_chains()

##########################
## Main page navigation ##
##########################

def main():
    selection = st.sidebar.selectbox("Select Module:", ["Landing page", "1. Generate alignments", "2. Self-alignment chaining", "3. Alignment chaining", "4. Visualize chains", '5. Fetch chains as sequences'])

    if selection == "Landing page":
        landing_page()
    
    elif selection == "1. Generate alignments":
        generate_alignments_page()
        
    elif selection == "2. Self-alignment chaining":
        self_alignment_chaining_page()

    elif selection == "3. Alignment chaining":
        alignment_chaining_page()
        
    elif selection == "4. Visualize chains":
         visualize_chains_page()
    
    elif selection == '5. Fetch chains as sequences':
        fetch_chains_as_sequences_page()

if __name__ == "__main__":
    main()