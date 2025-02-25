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
            
####################
## Page functions ##
####################

def landing_page():
    '''
    Creates the landing page of StreamSegMantX.py containing informal text.
    '''
    st.title("SegMantX")

    st.write("This app employs streamlit to provide a graphical interface of SegMantX.")
    
    st.write(
        "SegMantX is a bioinformatics tool designed to support a user-friendly chaining of local sequence alignments. "
        "This app simplifies the chaining process by a graphical user interface."
    )
    
    st.write(
        "SegMantX embeds BLASTn to generate local alignments as seeds for the chaining process. Skipping the computation of alignments (i.e., seeds) enables to use alternative seed inputs for the chaining process."
    )
    
    st.write(
        "Briefly, SegMantX is organised into five modules:"
    )
    
    st.markdown(
    """
    - Generate alignments: Computes alignments for chaining modules.
    - Self-alignment chaining: Chains local alignments from self-sequence alignment (e.g., duplication detection).
    - Alignment chaining: Chains local alignments between two sequences (e.g., sequence comparisons).
    - Visualize chains: Generates a segmentplot (i.e., segments of chaining results) to visualize yielded chains for a sequence.
    - Fetch chains: Extracts nucleotide sequences using the chained alignments and saves as fasta file.
    """
    )
    
    st.markdown("**Get started by navigating through the menu on the left!**")
    
    st.write(
        "For further details visit:"
    )
    
    st.markdown(
    """
    - GitHub: XXXXXXXXXX
    - DOI: XXXXXXXXXXXXX
    """
    )
    
            
def generate_alignments_page():
    '''
    Function to provide a page for the 'generate_alignments.py' script of SegMantX.
    '''
    st.title("Generate alignment files for chaining")
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
        if query_fasta_file:
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

            
def self_alignment_chaining_page():
    '''
    Function to provide a page for the 'chain_self_alignments.py' script of SegMantX.
    '''
    st.title("Chaining self-sequence alignment")
    st.write("This module may be used towards duplication detection.")
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



def alignment_chaining_page():
    '''
    Function to provide a page for the 'chain_alignments.py' script of SegMantX.
    '''
    st.title("Chaining sequence alignment between two sequences")
    st.write("This module may be used towards sequence comparisons.")
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
                fasta_file_query=fasta_file_query.name,
                fasta_file_subject=fasta_file_subject.name,
                output_file=output_file
            )

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
                 

def fetch_chains_as_sequences_page():
    '''
    Function to provide a page for the 'fetch_nucleotide_chains.py' script of SegMantX.
    '''
    st.title("Fetch nucleotide sequences from chained alignments in FASTA format.")
    st.sidebar.header("Parameters for fetching chains as nucleotide sequences:")
    
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
            if duplication_or_comparison == "Self-alignment chaining":
                sequences = fetch_nucleotide_chains.get_chained_sequences(chained_hits=alignment_coordinate_file, 
                                                        fasta_file=fasta_file_query.name, 
                                                        output_fasta=output_file)
            elif duplication_or_comparison == "Alignment chaining of two sequences":
                sequences = fetch_nucleotide_chains.get_chained_sequences_from_two_sequences(chained_hits=alignment_coordinate_file, 
                                                        fasta_file_query=fasta_file_query.name, 
                                                        fasta_file_subject=fasta_file_subject.name, 
                                                        output_fasta=output_file)
                
            # Old feature - visualizing the whole fasta file is too memory intensive
            #if sequences != None:
            #    seq_file = load_fasta(sequences)
            #    st.text_area("FASTA Content", seq_file, height=600)
            
            st.download_button(
                label="Download FASTA file",
                data=seq_file.encode('utf-8'),
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
            

def visualize_chains_page():
    '''
    Function to provide a page for the 'visualize_chains.py' script of SegMantX.
    '''
    st.title("Generates a segmentplot of yielded chains for a sequence.")
    st.text("Warning: Chains originating from sequences that are characterized by a circular sequence topology may appear with a steep slope. These chains may look abnormal by visual inspection.")
    st.sidebar.header("Parameters for segmentplot visualization")
    
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
        if check_input(chaining_data):
            if duplication_or_comparison == "Self-alignment chaining":
                fig = visualize_chains.segmentplot_of_chains(
                    chained_hits=chaining_data,
                    fasta_file_query=fasta_file_query.name,
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
                    fasta_file_query=fasta_file_query.name,
                    seq_len_query=seq_len_query,
                    fasta_file_subject=fasta_file_subject.name,
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

##########################
## Main page navigation ##
##########################

def main():
    selection = st.sidebar.selectbox("Select Module:", ["Landing page", "Generate alignments", "Self-alignment chaining", "Alignment chaining", "Visualize chains", 'Fetch chains as sequences'])

    if selection == "Landing page":
        landing_page()
    
    elif selection == "Generate alignments":
        generate_alignments_page()
        
    elif selection == "Self-alignment chaining":
        self_alignment_chaining_page()

    elif selection == "Alignment chaining":
        alignment_chaining_page()
        
    elif selection == "Visualize chains":
         visualize_chains_page()
    
    elif selection == 'Fetch chains as sequences':
        fetch_chains_as_sequences_page()

if __name__ == "__main__":
    main()