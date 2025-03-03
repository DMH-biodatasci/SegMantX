#!/usr/bin/env python3
import argparse
import sys
import pandas as pd
import numpy as np
from scipy.sparse.csgraph import connected_components
from scipy.sparse import csr_matrix
from collections import defaultdict
from modules.common_functions import *
from subprocess import run 
import time

################################
## Adjacency Matrix functions ##
################################

def gap_computation(coordinates, max_gap):
    '''
    Takes the alignment coordinates to calculate a matrix containing pairwise gaps between hits.
    '''
    second_elements = np.array([max(x) for x in coordinates])
    first_elements = np.array([min(x) for x in coordinates])
    second_elements_matrix = second_elements[:, np.newaxis]  # Shape (N, 1)
    first_elements_matrix = first_elements[np.newaxis, :]    # Shape (1, N)
    diff_matrix = first_elements_matrix - second_elements_matrix
    diff_matrix = np.ma.masked_less(diff_matrix, -(max_gap))
    diff_matrix[diff_matrix < 0] = 1
    np.fill_diagonal(diff_matrix, 0)
    return np.ma.masked_greater(diff_matrix, max_gap)

def scaled_gap_matrix(coordinates, max_gap, scaled_gap):
    '''
    Constructs the gap and hit size matrices to calculate the scaled gap matrix.
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
    The matrices are converted into an adjacency matrix.
    '''
    scaled_gap_matrix_query = scaled_gap_matrix(query_coordinates, max_gap, scaled_gap)
    scaled_gap_matrix_subject = scaled_gap_matrix(subject_coordinates, max_gap, scaled_gap)
    query_subject_mean_hit_length_to_dist_mat = (scaled_gap_matrix_query + scaled_gap_matrix_subject) / 2
    query_subject_mean_hit_length_to_dist_mat = np.ma.masked_less(query_subject_mean_hit_length_to_dist_mat, scaled_gap)
    adjacency_matrix =  masked_array_to_adjacency_matrix(query_subject_mean_hit_length_to_dist_mat)
    return(adjacency_matrix)

######################################################################
## Functions chaining local alignments into segments (i.e., chains) ##
######################################################################

def label_topology_type_of_chain(chained_hits, seq_len_query=None, seq_len_subject=None):
    '''
    Labeling the topology type of chains: linear / circular
    '''
    if seq_len_query==None or seq_len_subject==None:
        chained_hits['chain_topology_query'] = 'linear'
        chained_hits['chain_topology_subject'] = 'linear'
        return chained_hits
    else:
        chained_hits['chain_topology_query'] = chained_hits.apply(
            lambda row: 'circular' if (row['q.start'] > seq_len_query and row['q.end'] <= seq_len_query) or (row['q.start'] <= seq_len_query and row['q.end'] > seq_len_query) else 'linear',
            axis=1
        )
        chained_hits['chain_topology_subject'] = chained_hits.apply(
            lambda row: 'circular' if (row['s.start'] > seq_len_subject and row['s.end'] <= seq_len_subject) or (row['s.start'] <= seq_len_subject and row['s.end'] > seq_len_subject) else 'linear',
            axis=1
        )
        return chained_hits

def update_circular_sequence_coordinates_towards_linearity(chained_hits, seq_len_query, seq_len_subject):
    '''
    Updates coordinates that are exceeding the sequence length. These coordinates have been artifically created 
    for chaining hits on a sequence characterized by a circular sequence topology.
    '''
    columns_to_update_query = chained_hits.iloc[:, 1:3]    
    filtered_chained_hits_query = chained_hits[(columns_to_update_query > seq_len_query).any(axis=1)]
    columns_to_update_query = filtered_chained_hits_query.iloc[:, 1:3]
    updated_columns_query = columns_to_update_query.where(columns_to_update_query <= seq_len_query, columns_to_update_query - seq_len_query)
    filtered_chained_hits_query.iloc[:, 1:3] = updated_columns_query
    
    columns_to_update_subject = filtered_chained_hits_query.iloc[:, 3:5]
    filtered_chained_hits_subject = filtered_chained_hits_query[(columns_to_update_subject > seq_len_subject).any(axis=1)]
    columns_to_update_subject = filtered_chained_hits_subject.iloc[:, 3:5]
    updated_columns_subject = columns_to_update_subject.where(columns_to_update_subject <= seq_len_subject, columns_to_update_subject - seq_len_subject)
    filtered_chained_hits_subject.iloc[:, 3:5] = updated_columns_subject
    return filtered_chained_hits_subject

def remove_redundant_hits(chained_hits, seq_len_query=None, seq_len_subject=None):
    '''
    Takes the resulting hits and removes smaller hits that are fully covered by larger hits for avoiding redundancy.
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

def chain_hits(indexed_input_df, seq_len_query=None, seq_len_subject=None):
    '''
    Function that combines the merging process of hits into chains after receiving the components data.
    '''
    chained_hits = chain_alignment_hits(indexed_input_df) 
    chained_hits = label_topology_type_of_chain(chained_hits, seq_len_query, seq_len_subject)
    chained_hits = add_query_and_subject_length(chained_hits)
    if not seq_len_query == None and not seq_len_subject == None:
        chained_hits = update_circular_sequence_coordinates_towards_linearity(chained_hits, seq_len_query, seq_len_subject)
    elif seq_len_query == None and not seq_len_subject == None:
        chained_hits = update_circular_sequence_coordinates_towards_linearity(chained_hits, 0, seq_len_subject)
    elif not seq_len_query == None and not seq_len_subject == 0:
        chained_hits = update_circular_sequence_coordinates_towards_linearity(chained_hits, seq_len_query, 0)
    chained_hits = remove_redundant_hits(chained_hits, seq_len_query, seq_len_subject)
    return chained_hits


def chain_sequence_alignment(input_file, max_gap=5000, scaled_gap=1, seq_len_query=None, seq_len_subject=None, is_query_circular=False, is_subject_circular=False, min_len=200, output_file='chaining_output.tsv', blast_outfmt7=False, fasta_file_query='', fasta_file_subject=''):
    '''
    Function combining all steps for the chaining process towards sequence comparison.
    '''
    print("Start checking input and data transformation ... ")
    start = time.time()
    
    ########################################
    ## 0. Initial checks and reading data ##
    ########################################

    if is_query_circular and seq_len_query==None:
        seq_len_query = check_sequence_length(fasta_file_query)
    if is_subject_circular and seq_len_subject==None:
        seq_len_subject = check_sequence_length(fasta_file_subject)
    
    if isinstance(seq_len_query, str):
        return print('Flag --is_query_circular has been set. The sequence size is required for chaining a sequence with circular topology. Set parameter --sequence_length_query or --fasta_file_query.')
    if isinstance(seq_len_subject, str):
        return print('Flag --is_subject_circular has been set. The sequence size is required for chaining a sequence with circular topology. Set parameter --sequence_length_subject or --fasta_file_subject.')
    
    #Conditions for streamlit app
    if isinstance(input_file, pd.DataFrame):
        alignment_coordinate_data = input_file
    elif not blast_outfmt7:
        try:
            alignment_coordinate_data = pd.read_csv(input_file, sep='\t', header=None)
        except pd.errors.ParserError as e:
            return print("ERROR: The input data is not in the correct format (i.e., it should be a tab-delimited file containing five columns: q.start, q.end, s.start, s.end, perc. identity). Please change the --blast_outfmt7 flag or ensure the correct input data format.")
    else:
        try:
            alignment_coordinate_data = pd.read_csv(input_file, sep='\t', comment='#', header=None)[[6,7,8,9,2]]
        except KeyError:
            return print("ERROR: The input data is not in the correct format (i.e., it is not in BLAST output format 7). Please change the --blast_outfmt7 flag or ensure the correct input data format.")
    
    ################################################
    ## 1. Convert local alignment hit coordinates ##
    ################################################
    
    try:
        alignment_coordinate_data.columns = ['q.start', 'q.end', 's.start', 's.end', 'identity']
    except ValueError:
        return print("ERROR: The input data is not in the correct format (i.e., it should be a tab-delimited file containing five columns: q.start, q.end, s.start, s.end, perc. identity or BLAST output format7). Please the --blast_outfmt7 flag or ensure the correct input data format.")
       
    # If no hits except diagonal, return a message
    if alignment_coordinate_data.empty:
        return "No local alignment hits! Please inspect if the input data is appropiate for chaining."
    # Filter hits based on length 
    if not min_len == 0:
        alignment_coordinate_data = alignment_coordinate_data[(abs(alignment_coordinate_data['q.start'] - alignment_coordinate_data['q.end']) > min_len) |
                                          (abs(alignment_coordinate_data['s.start'] - alignment_coordinate_data['s.end']) > min_len)]
    # Add identity column where missing
    alignment_coordinate_data, alignment_coordinate_data_with_identity = add_identity_column_if_missing(alignment_coordinate_data)
    # Sort coordinates and add strand info
    alignment_coordinate_data = add_strand_and_sort_alignment_coordinates(alignment_coordinate_data)
    # Return if there is one or fewer rows
    if len(alignment_coordinate_data) <= 1:
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
    chained_hits = chain_hits(indexed_input_df, seq_len_query, seq_len_subject)
    end = time.time()
    print("Time to chain alignments: {}".format(time.time()-start))
    
    #######################
    ## 5. Save as output ##
    #######################
    
    chained_hits["ID"] = range(1, chained_hits.shape[0]+1)
    chained_hits = chained_hits[['ID'] + [col for col in chained_hits.columns if col != 'ID']]
    if not output_file == '':
        chained_hits.to_csv(output_file, sep='\t', index=None)
        
    return chained_hits


def main():
    parser = argparse.ArgumentParser(description="Chains local alignments from sequence alignment.")

    parser.add_argument("module", type=str, help="Name of the module being executed.")
    parser.add_argument("-i", "--input_file", type=str, required = True, help="Input file received from 'generate_alignments' (i.e., five columns: q.start, q.end, s.start, s.end, identity). Alternatively, provide BLAST output format 7 and indicate --blast_outfmt7 flag).")
    parser.add_argument("-B", "--blast_outfmt7", action="store_true", default=False, help="Indicates if the input file is BLAST output format 7 (Default: False).")
    parser.add_argument("-G", "--max_gap", type=int, default=5000, help="Maximum gap size between alignment hits for chaining (default: 5000).")
    parser.add_argument("-SG", "--scaled_gap", type=float, default=1.0, help="Minimum scaled gap between alignment hits for chaining (Default: 1.0).")
    parser.add_argument("-Q", "--is_query_circular", action="store_true", help="Indicates if the query sequence is circular (Default: False).")
    parser.add_argument("-S", "--is_subject_circular", action="store_true", help="Indicates if the subject sequence is circular (Default: False).")
    parser.add_argument("-LQ", "--sequence_length_query", type=int, default=None, help="Size of the query sequence (is required with circular sequence topology). Otherwise, provide fasta file (i.e., using --fasta_file_query) (Default: None).")
    parser.add_argument("-LS", "--sequence_length_subject", type=int, default=None, help="Size of the subject sequence (is required with circular sequence topology). Otherwise, provide fasta file (i.e., using --fasta_file_subject) (Default: None).")
    parser.add_argument("-o", "--output_file", type=str, default='chaining_output.tsv', help="Filename of the chaining output file (Default: chaining_output.tsv).")
    parser.add_argument("-ml", "--min_length", type=int, default=200, help="Minium length of alignment hits for chaining (default: 200).")
    parser.add_argument("-fq", "--fasta_file_query", type=str, help="Fasta file to read out the sequence length.")
    parser.add_argument("-fs", "--fasta_file_subject", type=str, help="Fasta file to read out the sequence length.")
    
    args = parser.parse_args()
  
    start = time.time()
    print("Starting to chain alignments between two sequences, for example, towards sequence comparison ...")
    print("\n")
    print("Module {} will use the following parameters:".format(args.module))
    print("Input alignment coordinates file: {}".format(args.input_file))
    print("Input file is BLAST ouput format: {}".format(args.blast_outfmt7))
    print("Circular sequence topology (query): {}".format(args.is_query_circular))
    print("Sequence length (query): {}".format(args.sequence_length_query))
    print("FASTA file (query): {}".format(args.fasta_file_query))
    print("Circular sequence topology (subject): {}".format(args.is_subject_circular))
    print("Sequence length (subject): {}".format(args.sequence_length_subject))
    print("FASTA file (subject): {}".format(args.fasta_file_subject))
    print("Maximum gap size [bp]: {}".format(args.max_gap))
    print("Scaled gap size [bp]: {}".format(args.scaled_gap))
    print("Minimum alignment length [bp]: {}".format(args.min_length))
    
    print("Output: {}".format(args.output_file))
    print("\n")
    
    chain_sequence_alignment(
        input_file=args.input_file,
        max_gap=args.max_gap,
        scaled_gap=args.scaled_gap,
        seq_len_query=args.sequence_length_query,
        seq_len_subject=args.sequence_length_subject,
        is_query_circular=args.is_query_circular,
        is_subject_circular=args.is_subject_circular,
        output_file=args.output_file,
        min_len=args.min_length,
        blast_outfmt7=args.blast_outfmt7,
        fasta_file_query=args.fasta_file_query,
        fasta_file_subject=args.fasta_file_subject
    )
    
    print("Total time to run module chain_alignments.py: {}".format(round(time.time()-start, 2))) 
    return 

if __name__ == "__main__":
    main()
    
    