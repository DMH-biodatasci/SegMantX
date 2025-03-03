#!/usr/bin/env python3
import argparse
import sys
import pandas as pd 
import numpy as np 
from scipy.sparse.csgraph import connected_components
from scipy.sparse import csr_matrix
from collections import defaultdict
from modules.common_functions import *
import time

##########################################################
## Functions to convert local alignment hit coordinates ##
##########################################################

def remove_duplicate_hits(alignment_coordinate_data):
    """
    Ensure unique hits in the DataFrame by adjusting query and subject coordinates.
    This step is required for the duplication detection on the same sequence
    as query and subject hits are mapped to the same sequence and avoids redundancy.
    """
    condition = (alignment_coordinate_data['q.start'] + alignment_coordinate_data['q.end']) > (alignment_coordinate_data['s.start'] + alignment_coordinate_data['s.end'])
    alignment_coordinate_data.loc[condition, ['q.start', 's.start']] = alignment_coordinate_data.loc[condition, ['s.start', 'q.start']].values
    alignment_coordinate_data.loc[condition, ['q.end', 's.end']] = alignment_coordinate_data.loc[condition, ['s.end', 'q.end']].values
    alignment_coordinate_data = alignment_coordinate_data.drop_duplicates(subset=['q.start', 'q.end', 's.start', 's.end'], keep='first')
    return alignment_coordinate_data

def filter_multimer_hits(alignment_coordinate_data, seq_len):
    '''
    Removes hits that have been artificially created towards duplication detection on the same sequence,
    if the sequence has a circular topology.
    '''
    condition = ~(((alignment_coordinate_data.iloc[:, 0] == 1) & (alignment_coordinate_data.iloc[:, 1] == seq_len)) | 
              ((alignment_coordinate_data.iloc[:, 2] == 1) & (alignment_coordinate_data.iloc[:, 3] == seq_len)))
    return alignment_coordinate_data[condition]

################################
## Adjacency Matrix functions ##
################################

def gap_computation(coordinates, max_gap):
    '''
    Takes the alignment coordinates to calculate a matrix containing pairwise gaps between hits.
    '''
    second_elements = np.array([max(x) for x in coordinates])
    first_elements = np.array([min(x) for x in coordinates])
    second_elements_matrix = second_elements[:, np.newaxis]  
    first_elements_matrix = first_elements[np.newaxis, :]    
    diff_matrix = first_elements_matrix - second_elements_matrix
    np.fill_diagonal(diff_matrix, 0)
    transposed_diff_matrix = diff_matrix.T
    diff_matrix_copy = diff_matrix.copy()
    abs_transposed_diff_matrix = np.abs(transposed_diff_matrix)
    abs_diff_matrix_copy = np.abs(diff_matrix_copy)
    min_abs_matrix = np.minimum(abs_transposed_diff_matrix, abs_diff_matrix_copy)
    min_gap_matrix = np.where(abs_transposed_diff_matrix < abs_diff_matrix_copy, transposed_diff_matrix, diff_matrix_copy)
    min_gap_matrix[(min_gap_matrix < 0) & (min_gap_matrix > -max_gap)] = 1
    return np.ma.masked_greater(min_gap_matrix, max_gap)

def scaled_gap_matrix(coordinates, max_gap, scaled_gap):
    '''
    Constructs the gap and hit length matrices to calculate the scaled gap matrix.
    '''
    gap_matrix = gap_computation(coordinates, max_gap)
    sum_of_lengths_matrix = sum_of_lengths_computation(coordinates)
    with np.errstate(divide='ignore', invalid='ignore'):
        scaled_gap_matrix = sum_of_lengths_matrix / gap_matrix
        scaled_gap_matrix = np.ma.masked_less(scaled_gap_matrix, scaled_gap)
        scaled_gap_matrix = np.maximum(scaled_gap_matrix.filled(0), scaled_gap_matrix.filled(0).T)
        scaled_gap_matrix[scaled_gap_matrix == 0] = -1
        return np.ma.masked_less(scaled_gap_matrix, 0)
    
def create_adjacency_matrix(query_coordinates, subject_coordinates, max_gap, scaled_gap):
    '''
    Takes the query and subject alignment coordinates to calculate separate scaled gap matrices.
    The matrices are converted into adjacency matrices.
    '''
    scaled_gap_matrix_query = scaled_gap_matrix(query_coordinates, max_gap, scaled_gap)
    scaled_gap_matrix_subject = scaled_gap_matrix(subject_coordinates, max_gap, scaled_gap)
    query_subject_mean_hit_length_to_gap_matrix = (scaled_gap_matrix_query + scaled_gap_matrix_subject) / 2
    query_subject_mean_hit_length_to_gap_matrix = np.ma.masked_less(query_subject_mean_hit_length_to_gap_matrix, scaled_gap)
    adjacency_matrix =  masked_array_to_adjacency_matrix(query_subject_mean_hit_length_to_gap_matrix)
    return(adjacency_matrix)

######################################################################
## Functions chaining local alignments into segments (i.e., chains) ##
######################################################################

def label_topology_type_of_chain(chained_hits, seq_len=None):
    '''
    Labeling the topology type of chains: linear / circular
    '''
    if seq_len==None:
        chained_hits['chain_topology_query'] = 'linear'
        chained_hits['chain_topology_subject'] = 'linear'
        return chained_hits
    else:
        chained_hits['chain_topology_query'] = chained_hits.apply(
            lambda row: 'circular' if (row['q.start'] > seq_len and row['q.end'] <= seq_len) or (row['q.start'] <= seq_len and row['q.end'] > seq_len) else 'linear',
            axis=1
        )
        chained_hits['chain_topology_subject'] = chained_hits.apply(
            lambda row: 'circular' if (row['s.start'] > seq_len and row['s.end'] <= seq_len) or (row['s.start'] <= seq_len and row['s.end'] > seq_len) else 'linear',
            axis=1
        )
        return chained_hits

def update_circular_sequence_coordinates_towards_linearity(chained_hits, seq_len):
    '''
    Updates coordinates that are exceeding the sequence length. These coordinates have been artifically created 
    for chaining hits on a sequence characterized by a circular sequence topology.
    '''
    columns_to_update = chained_hits.iloc[:, 1:5]
    filtered_chained_hits = chained_hits[(columns_to_update > seq_len).any(axis=1)]
    columns_to_update = filtered_chained_hits.iloc[:, 1:5]
    updated_columns = columns_to_update.where(columns_to_update <= seq_len, columns_to_update - seq_len)
    filtered_chained_hits.iloc[:, 1:5] = updated_columns
    return filtered_chained_hits

def remove_redundant_hits(chained_hits, seq_len_query=None, seq_len_subject=None):
    '''
    Takes the resulting chains and removes smaller hits that are fully covered by larger chains for avoiding redundancy.
    '''
    seq_len_subject = seq_len_query
    chained_hits_sorted = chained_hits.sort_values(by='q_length', ascending=False).reset_index(drop=True)
    q_starts = chained_hits_sorted['q.start'].to_numpy()
    q_ends = chained_hits_sorted['q.end'].to_numpy()
    s_starts = chained_hits_sorted['s.start'].to_numpy()
    s_ends = chained_hits_sorted['s.end'].to_numpy()
    chain_topology_type_query = chained_hits_sorted['chain_topology_query'].to_numpy() == 'linear'
    chain_topology_type_subject = chained_hits_sorted['chain_topology_subject'].to_numpy() == 'linear'
    chains_to_keep = np.full(chained_hits_sorted.shape[0], True)
    
    def get_coords(start, end, is_linear, size):
        '''
        Helper function to determinte chain coordinates with circular support.
        '''
        if not start < end:
            tmp_start = start.copy()
            start = end
            end = tmp_start
        if is_linear:
            return np.arange(start, end+1)
        if size is not None:
            return np.concatenate((np.arange(end, size+1), np.arange(1, start+1)))
        return np.arange(start, end+1)

    query_chains_coordinates_list = []
    subject_chains_coordinates_list = []
    
    for i in range(chained_hits_sorted.shape[0]):
        query_chains_coordinates_list.append(get_coords(q_starts[i], q_ends[i], chain_topology_type_query[i], seq_len_query))
        subject_chains_coordinates_list.append(get_coords(s_starts[i], s_ends[i], chain_topology_type_subject[i], seq_len_subject))
    
    for i in range(len(query_chains_coordinates_list)):
        for j in range(i+1, len(query_chains_coordinates_list)):
            query_check = np.all(np.isin(query_chains_coordinates_list[j], query_chains_coordinates_list[i]))
            subject_check = np.all(np.isin(subject_chains_coordinates_list[j], subject_chains_coordinates_list[i]))
            if query_check and subject_check:
                chains_to_keep[j] = False

    chained_hits_filtered = chained_hits_sorted[chains_to_keep].drop_duplicates(subset=['q.start', 'q.end', 's.start', 's.end']).reset_index(drop=True)
    return chained_hits_filtered

def duplicate_duplicates(chained_hits):
    '''
    Function duplicates unique chain coordinates as the chains correspond to the same sequence.
    (Intially, duplicate hits have been removed for chaining purposes.)
    '''
    df = chained_hits.copy()
    df['temp_q_start'] = df['q.start']
    df['q.start'] = df['s.start']
    df['s.start'] = df['temp_q_start']

    df['temp_q_end'] = df['q.end']
    df['q.end'] = df['s.end']
    df['s.end'] = df['temp_q_end']
    df = df.drop(columns=['temp_q_start', 'temp_q_end'])
    
    duplicated_chains_df = pd.concat([chained_hits, df])
    return duplicated_chains_df

def chain_hits(indexed_input_df, seq_len=None):
    '''
    Function that combines the merging process of hits into chains after receiving the components data.
    '''
    chained_hits = chain_alignment_hits(indexed_input_df)
    chained_hits = label_topology_type_of_chain(chained_hits, seq_len)
    chained_hits = add_query_and_subject_length(chained_hits)
    
    if not seq_len == None:
        chained_hits = update_circular_sequence_coordinates_towards_linearity(chained_hits, seq_len)
    
    condition1 = (chained_hits['q.start'] == chained_hits['s.start']) & (chained_hits['q.end'] == chained_hits['s.end'])
    condition2 = (chained_hits['q.start'] == chained_hits['s.end']) & (chained_hits['q.end'] == chained_hits['s.start'])
    chained_hits = chained_hits[~(condition1 | condition2)]
    
    if seq_len != None:
        chained_hits = remove_redundant_hits(chained_hits, seq_len)
    
    #if seq_len != None:
    chained_hits = duplicate_duplicates(chained_hits)
    return chained_hits


def chain_self_sequence_alignment(input_file=None, max_gap=5000, scaled_gap=1, seq_len=None, is_query_circular=False, output_file='chaining_output.tsv', min_len=0, fasta_file='', blast_outfmt7=False):
    '''
    Function combining all steps for the chaining process towards duplication detection.
    '''
    
    print("Start checking input and data transformation ... ")
    start = time.time()
    
    ########################################
    ## 0. Initial checks and reading data ##
    ########################################
    
    # Checks if the sequence length is required
    if is_query_circular and seq_len==None:
        seq_len = check_sequence_length(fasta_file)
        if isinstance(seq_len, str):
            return print(seq_len)
    
    #Streamlit condition
    if isinstance(input_file, pd.DataFrame):
        alignment_coordinate_data = input_file
    # Checks and uses the input file format
    elif not blast_outfmt7:
        try:
            alignment_coordinate_data = pd.read_csv(input_file, sep='\t', header=None)
        except pd.errors.ParserError as e:
            return print("The input data is not in the correct format (i.e., it should be a tab-delimited file containing five columns: q.start, q.end, s.start, s.end, perc. identity). Please change the --blast_outfmt7 flag or ensure the correct input data format.")
    else:
        try:
            alignment_coordinate_data = pd.read_csv(input_file, sep='\t', comment='#', header=None)[[6,7,8,9,2]]
        except KeyError:
            return print("The input data is not in the correct format (i.e., it is not in BLAST output format 7). Please change the --blast_outfmt7 flag or ensure the correct input data format.")

    ################################################
    ## 1. Convert local alignment hit coordinates ##
    ################################################

    if is_query_circular:   
        alignment_coordinate_data = filter_multimer_hits(alignment_coordinate_data, seq_len)
    # Remove diagonal hits (i.e., q.start == s.start and q.end == s.end) - these are hits resulting from performing BLAST on a sequence to itself
    alignment_coordinate_data = alignment_coordinate_data[(alignment_coordinate_data.iloc[:, 0] != alignment_coordinate_data.iloc[:, 2]) & 
                                      (alignment_coordinate_data.iloc[:, 1] != alignment_coordinate_data.iloc[:, 3])]
    try:
        alignment_coordinate_data.columns = ['q.start', 'q.end', 's.start', 's.end', 'identity']
    except ValueError:
        return print("ERROR: The input data is not in the correct format (i.e., it should be a tab-delimited file containing five columns: q.start, q.end, s.start, s.end, perc. identity or BLAST output format7). Please the --blast_outfmt7 flag or ensure the correct input data format.")
    # If no hits except diagonal, return a message
    if alignment_coordinate_data.empty:
        empty_df = pd.DataFrame()
        empty_df.to_csv(output_file, sep='\t', index=None)
        return "No local alignment hits! Please inspect if the input data is appropiate for chaining."
    # Filter hits based on length 
    if not min_len == 0:
        alignment_coordinate_data = alignment_coordinate_data[(abs(alignment_coordinate_data['q.start'] - alignment_coordinate_data['q.end']) > min_len) |
                                          (abs(alignment_coordinate_data['s.start'] - alignment_coordinate_data['s.end']) > min_len)]
    # Return if there is only one or no hit
    if len(alignment_coordinate_data) <= 1:
        empty_df = pd.DataFrame()
        empty_df.to_csv(output_file, sep='\t', index=None)
        return "No local alignment hits! Please inspect if the input data is appropiate for chaining."
    # Remove duplicate hits
    alignment_coordinate_data = remove_duplicate_hits(alignment_coordinate_data)
    # Add identity column where missing
    alignment_coordinate_data, alignment_coordinate_data_with_identity = add_identity_column_if_missing(alignment_coordinate_data)
    # Sort coordinates and add strand info
    alignment_coordinate_data = add_strand_and_sort_alignment_coordinates(alignment_coordinate_data)
    # Return if there is one or fewer rows
    if len(alignment_coordinate_data) <= 1:
        empty_df = pd.DataFrame()
        empty_df.to_csv(output_file, sep='\t', index=None)
        return alignment_coordinate_data
    # Add indices and order by query
    distinct_alignment_coordinate_data_with_indices = add_indices_and_order_by_query(alignment_coordinate_data, output_file)
    # Create identity index table
    identity_index_table = create_identity_index_table(distinct_alignment_coordinate_data_with_indices, alignment_coordinate_data_with_identity)
    # Return a message if fewer than two local alignments are found
    if len(distinct_alignment_coordinate_data_with_indices) < 2:
        empty_df = pd.DataFrame()
        empty_df.to_csv(output_file, sep='\t', index=None)
        result = "No chains have been found!"
    else:
        result = identity_index_table
    # Split query and subject data
    splitted_query_and_subject_data = split_query_and_subject(distinct_alignment_coordinate_data_with_indices)
    # Combine the resulting DataFrames and tables into a final list
    combined_list = [alignment_coordinate_data, alignment_coordinate_data_with_identity, distinct_alignment_coordinate_data_with_indices, identity_index_table]
    # Append splitted query and subject data to the combined list
    result_list = combined_list + splitted_query_and_subject_data
    
    print("Time to check input and to transform data: {}".format(time.time()-start))
    
    #########################
    ## 2. Adjacency Matrix ##
    #########################
    
    print("Start computing scaled gaps and adjacency matrix ...")
    start = time.time()
    splitted_query_data = result_list[4]
    splitted_subject_data = result_list[5]
    sorted_keys = sorted(splitted_query_data.keys())
    # Create sorted coordinate arrays based on sorted keys
    query_coordinates = [np.array(splitted_query_data[key]) for key in sorted_keys]
    subject_coordinates = [np.array(splitted_subject_data[key]) for key in sorted_keys]
    adjacency_matrix = create_adjacency_matrix(query_coordinates, subject_coordinates, max_gap, scaled_gap)
    print("Time to create adjacency matrix: {}".format(time.time()-start))
    
    ###########################
    ## 3. Extract components ##
    ###########################
    
    print("Start computing scaled gaps and adjacency matrix ...")
    start = time.time()
    components = list(extract_connected_components_in_adjacency_matrix(adjacency_matrix, sorted_keys))
    indexed_input_df = merge_component_alignment_data(result_list[2], result_list[3], components)
    print("Time to extract components from adjacency matrix: {}".format(time.time()-start))
    
    ###################
    ## 4. Chain hits ##
    ###################
    
    print("Start chaining alignments ...")
    chained_hits = chain_hits(indexed_input_df, seq_len)
    end = time.time()
    print("Time to chain alignments: {}".format(time.time()-start))
    #######################
    ## 5. Save as output ##
    #######################
    
    chained_hits["ID"] = range(1, chained_hits.shape[0]+1)
    chained_hits = chained_hits[['ID'] + [col for col in chained_hits.columns if col != 'ID']]
    
    if not output_file == '':
    
        if chained_hits.shape[0] == 0:
            empty_df = pd.DataFrame()
            empty_df.to_csv(output_file, sep='\t', index=None)
        else:
            chained_hits.to_csv(output_file, sep='\t', index=None)
    
    return chained_hits

def main():
    parser = argparse.ArgumentParser(description="Chains local alignments from self-sequence alignment (e.g., duplication detection).")
    
    parser.add_argument("module", type=str, help="Name of the module being executed.")
    parser.add_argument("-i", "--input_file", required=True, type=str, help="Input file received from 'generate_alignments' (i.e., five columns: q.start, q.end, s.start, s.end, identity). Alternatively, provide BLAST output format 7 and use --blast_outfmt7 flag).")
    parser.add_argument("-B", "--blast_outfmt7", action="store_true", default=False, help="Indicates if the input file is BLAST output format 7 (Default: False).")
    parser.add_argument("-G", "--max_gap", type=int, default=5000, help="Maximum gap size between alignment hits for chaining (default: 5000).")
    parser.add_argument("-SG", "--scaled_gap", type=float, default=1.0, help="Minimum scaled gap between alignment hits for chaining (Default: 1.0).")
    parser.add_argument("-Q", "--is_query_circular", action="store_true", default=False, help="Indicates a circular sequence topology (Default: False).")
    parser.add_argument("-L", "--sequence_length", type=int, default=None, help="Size of the sequence (is required with circular sequence topology). Otherwise, provide fasta file (i.e., using --fasta_file) (Default: None).")
    parser.add_argument("-f", "--fasta_file", type=str, help="Fasta file to read out the sequence length. Required if the sequence topology is circular and --sequence_size is not provided manually.")
    parser.add_argument("-o", "--output_file", type=str, default='chaining_output.tsv', help="Filename of the chaining output file (Default: chaining_output.tsv).")
    parser.add_argument("-ml", "--min_length", type=int, default=200, help="Minium length of alignment hits for chaining (default: 200).")
    args = parser.parse_args()
    
    start = time.time()
    print("Starting to chain self-sequence alignments, for example, towards duplication detection ...")
    print("\n")
    print("Module {} will use the following parameters:".format(args.module))
    print("Input alignment coordinates file: {}".format(args.input_file))
    print("Input file is BLAST ouput format: {}".format(args.blast_outfmt7))
    print("Circular sequence topology (query): {}".format(args.is_query_circular))
    print("Sequence length: {}".format(args.sequence_length))
    print("FASTA file: {}".format(args.fasta_file))
    print("Maximum gap size [bp]: {}".format(args.max_gap))
    print("Scaled gap: {}".format(args.scaled_gap))
    print("Minimum alignment length [bp]: {}".format(args.min_length))
    
    print("Output: {}".format(args.output_file))
    print("\n")
    
    chain_self_sequence_alignment(
        input_file=args.input_file,
        max_gap=args.max_gap,
        scaled_gap=args.scaled_gap,
        seq_len=args.sequence_length,
        is_query_circular=args.is_query_circular,
        output_file=args.output_file,
        min_len=args.min_length,
        blast_outfmt7=args.blast_outfmt7,
        fasta_file=args.fasta_file 
    )
    
    print("Total time to run module chain_self_alignments.py: {}".format(round(time.time()-start, 2)))  
    
    return 

if __name__ == "__main__":
    main()
    
