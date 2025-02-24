#!/usr/bin/env python3
import pandas as pd
import numpy as np
from scipy.sparse.csgraph import connected_components
from scipy.sparse import csr_matrix
from collections import defaultdict
from Bio import SeqIO

#############################################
## 0. Functions containing required checks ##
#############################################

def get_sequence_length(fasta_file):
    '''
    Returns the length of a nucleotide sequence from a FASTA file.
    '''
    for record in SeqIO.parse(fasta_file, "fasta"):
        return len(record.seq)
    
def check_sequence_length(fasta_file):
    '''
    Checks if sequence length is available from fasta file.
    '''
    if fasta_file == '' or fasta_file == None:
        return 'Flag --is_query_circular or --is_subject_circular has been set to True. The sequence size is required for chaining alignments on a circular sequence topology. Set corresponding parameters: --sequence_length_query and/or --sequence_length_subject or --fasta_file_query and/or --fasta_file_subject.'
    else:
        return get_sequence_length(fasta_file)

####################################################
## Functions to convert local alignment hits data ##
####################################################

def add_identity_column_if_missing(alignment_coordinate_data):
    '''
    Add an percent identity column with missing values (NaN) to the DataFrame if the input only containts 4 columns. 
    A copy of the original DataFrame with the new column is returned along with a version 
    containing only the first 4 columns.
    '''
    if alignment_coordinate_data.shape[1] == 4:
        alignment_coordinate_data['identity'] = np.nan
        alignment_coordinate_data_with_identity = alignment_coordinate_data.copy()
        alignment_coordinate_data = alignment_coordinate_data.iloc[:, :4]
    else:
        alignment_coordinate_data_with_identity = alignment_coordinate_data.copy()
        alignment_coordinate_data = alignment_coordinate_data.iloc[:, :4]  
    return alignment_coordinate_data, alignment_coordinate_data_with_identity

def order_query_subject_per_row(alignment_coordinate_data):
    '''
    Reorder query and subject coordinates in each row so that the sum of query start and 
    end coordinates is always less than or equal to the sum of subject start and end coordinates.
    '''
    condition = (alignment_coordinate_data['q.start'] + alignment_coordinate_data['q.end']) > (alignment_coordinate_data['s.start'] + alignment_coordinate_data['s.end'])
    alignment_coordinate_data.loc[condition, ['q.start', 's.start']] = alignment_coordinate_data.loc[condition, ['s.start', 'q.start']].values
    alignment_coordinate_data.loc[condition, ['q.end', 's.end']] = alignment_coordinate_data.loc[condition, ['s.end', 'q.end']].values
    alignment_coordinate_data.columns = ['V1', 'V2', 'V3', 'V4', 'V6', 'V7']
    return alignment_coordinate_data

def add_strand_and_sort_alignment_coordinates(alignment_coordinate_data):
    '''
    Add strand information for query and subject coordinates, and sort coordinates in each row.
    '''
    alignment_coordinate_data['q.strand'] = np.where(alignment_coordinate_data['q.start'] < alignment_coordinate_data['q.end'], '+', '-')
    alignment_coordinate_data['s.strand'] = np.where(alignment_coordinate_data['s.start'] < alignment_coordinate_data['s.end'], '+', '-')
    query_subject_ordered_data = order_query_subject_per_row(alignment_coordinate_data.copy())
    return pd.concat([alignment_coordinate_data, query_subject_ordered_data], axis=1)

def add_indices_and_order_by_query(alignment_coordinate_data, output):
    '''
    Create a distinct subset of local alignment hits based on the first 6 columns, sort the hits by 
    the 'q.start' coordinate, and add a unique 'indices' index to each row.
    '''
    alignment_coordinate_data_distinct_hits = alignment_coordinate_data.iloc[:, :6].copy()
    alignment_coordinate_data_distinct_hits = alignment_coordinate_data_distinct_hits.sort_values(by=alignment_coordinate_data_distinct_hits.columns[0])
    alignment_coordinate_data_distinct_hits['indices'] = range(1, len(alignment_coordinate_data_distinct_hits) + 1)
    save_file = alignment_coordinate_data_distinct_hits[["indices","q.start","q.end","s.start","s.end","q.strand","s.strand"]]
    save_file.columns = ['alignment_hits_indices'] + list(save_file.columns[1:])
    save_file.to_csv('{0}.indices'.format(output), sep='\t',index=None)
    return alignment_coordinate_data_distinct_hits

def create_identity_index_table(alignment_coordinates_4_col_distinct, alignment_coordinates_identity):
    '''
    Function merges distinct coordinates with the percent sequence identity column and indices
    '''
    identity_df = pd.merge(alignment_coordinates_4_col_distinct, alignment_coordinates_identity, on=['q.start', 'q.end', 's.start', 's.end'])
    identity_df = identity_df[['indices', 'identity']]
    identity_df['indices'] = identity_df['indices'].astype(str)
    return identity_df

def split_query_and_subject(distinct_alignment_coordinate_data_with_indices):
    '''
    Splits query and subject alignment hit coordinates and returns them as list together with further additional data.
    '''
    alignment_coordinates_query = distinct_alignment_coordinate_data_with_indices.sort_values(by=['q.start', 'q.end', 'indices'])[['q.start', 'q.end', 'indices']]
    alignment_coordinates_subject = distinct_alignment_coordinate_data_with_indices.sort_values(by=['s.start', 's.end', 'indices'])[['s.start', 's.end', 'indices']]
    alignment_coordinates_query_dict = alignment_coordinates_query.set_index('indices').T.to_dict('list')
    alignment_coordinates_subject_dict = alignment_coordinates_subject.set_index('indices').T.to_dict('list')
    alignment_coordinates_query_dict = {k: list(v) for k, v in alignment_coordinates_query_dict.items()}
    alignment_coordinates_subject_dict = {k: list(v) for k, v in alignment_coordinates_subject_dict.items()}
    splitted_query_and_subject_data = [alignment_coordinates_query, alignment_coordinates_subject]
    return [alignment_coordinates_query_dict, alignment_coordinates_subject_dict] + splitted_query_and_subject_data

################################
## Adjacency Matrix functions ##
################################

def return_local_alignment_hit_lengths(local_alignment_hit_coordinates):
    '''
    Local alignment hit length calculation returned as np.array
    '''
    return np.array([abs(coord[0]-coord[1]) for coord in local_alignment_hit_coordinates])

def pairwise_sum_of_local_alignment_hit_lengths(local_alignment_hit_length_array):
    '''
    Function for summing up pairwise local alignment hit lengths
    '''
    indices = np.arange(len(local_alignment_hit_length_array))
    i, j = np.meshgrid(indices, indices, indexing='ij')
    pairwise_sums_of_local_alignment_hit_lengths_array = local_alignment_hit_length_array[i] + local_alignment_hit_length_array[j]
    return pairwise_sums_of_local_alignment_hit_lengths_array

def sum_of_lengths_computation(local_alignment_hit_coordinates):
    '''
    Combining function to calculate the pairwise sum of local alignment hit lengths
    '''
    hit_length_array = return_local_alignment_hit_lengths(local_alignment_hit_coordinates)
    pairwise_sums_of_local_alignment_hit_lengths_array = pairwise_sum_of_local_alignment_hit_lengths(hit_length_array)
    return np.maximum(pairwise_sums_of_local_alignment_hit_lengths_array, pairwise_sums_of_local_alignment_hit_lengths_array.T)

def masked_array_to_adjacency_matrix(matrix):
    '''
    Convert a matrix into an adjacency matrix
    '''
    matrix = matrix.filled(0)
    adjacency_matrix = np.where(matrix > 0, 1, 0) #Values (scaled gaps) above 1 will returned as 1 
    return adjacency_matrix

##############################################################
## Functions to extract components from an adjacency matrix ##
##############################################################

def extract_connected_components_in_adjacency_matrix(adjacency_matrix, names):
    '''
    Extract connected components from undirected adjacency matrix
    '''
    adjacency_sparse = csr_matrix(adjacency_matrix)
    n_components, labels = connected_components(csgraph=adjacency_sparse, directed=False, return_labels=True)
    components = defaultdict(list)
    for idx, label in enumerate(labels):
        components[label].append(names[idx])
    components = dict(components)
    return components.values()

def assign_connected_component_label(value_list, connected_components_dict):
    '''
    Helper function to assign matching components in alignment hit coordinates data
    '''
    for key, label in connected_components_dict.items():
        if value_list in label: 
            return key
    return 'Unknown' 

def merge_component_alignment_data(alignment_coordinate_data, alignment_coordinate_data_with_identity, connected_components):
    '''
    Function to combine connected components, alignment hit coordinates data and percentage identity dataframe
    '''
    component_dict = {'Component{}'.format(i): x for i, x in enumerate(connected_components)}
    alignment_coordinate_data_with_identity['indices'] = alignment_coordinate_data_with_identity['indices'].astype(int)
    components_alignment_hits_and_identity_df = pd.merge(alignment_coordinate_data, alignment_coordinate_data_with_identity, on='indices', how='inner')
    components_alignment_hits_and_identity_df['label'] = components_alignment_hits_and_identity_df['indices'].apply(lambda x: assign_connected_component_label(x, component_dict))
    return components_alignment_hits_and_identity_df

#########################################
## Merge hits intos segments functions ##
#########################################


def calculate_local_alignment_contribution_in_chains(hits_to_chain, query_coordinate1, query_coordinate2):
    '''
    Function to calculate the percentage of local alignment hits to gap lengths in chains
    '''

    if query_coordinate1 < query_coordinate2:
        sorted_query_coordinates = np.arange(query_coordinate1, query_coordinate2)
    else:
        sorted_query_coordinates = np.arange(query_coordinate2, query_coordinate1)
    
    hits_to_chain_copy = hits_to_chain.copy()
    adjusted_coordinate_range = hits_to_chain_copy[['q.start', 'q.end']].apply(lambda x: (min(x), max(x)), axis=1)
    hits_to_chain_copy['q.start'], hits_to_chain_copy['q.end'] = zip(*adjusted_coordinate_range)
    hits_to_chain_copy['range_series'] = pd.IntervalIndex.from_arrays(hits_to_chain_copy['q.start'], hits_to_chain_copy['q.end'], closed='left')

    # Get the intervals
    coordinate_intervals = hits_to_chain_copy['range_series']
    
    # Create an array of values in intervals using NumPy
    values_in_intervals = np.concatenate([np.arange(interval.left, interval.right) for interval in coordinate_intervals])
    # Convert to a set for faster lookup
    #values_in_intervals_set = set(values_in_intervals)

    # Filter values in values_in_intervals that are not in values_in_intervals
    local_alignment_positions_in_chain = set(sorted_query_coordinates) - set(values_in_intervals)

    # Calculate the local alignment contribution percentage in chains
    try:
        return 100 - ((len(local_alignment_positions_in_chain) / len(sorted_query_coordinates)) * 100)
    except ZeroDivisionError:
        return 0


def chain_alignment_hits(local_alignments_df, label_column='label'):
    '''
    Chains local alignment hits that are labeled as connected component into a single chain per label (i.e., group).
    '''
    
    def determine_major_strand_orientation(strand_array, len_array):
        '''
        Determines the main strand orientation of a chain according a strand orientation to hit length proportion
        '''
        numeric_strand_array = np.where(strand_array == '+', 1, -1)
        return sum(numeric_strand_array * len_array)
    
    def determine_strand_orientation(group, strand_column):
        '''
        Strand orientation determination of chains
        '''
        
        ###########################################################
        ## Strand orientation evaluation according to hit length ##
        ###########################################################
        strand_values = group[strand_column].to_numpy()
        
        if strand_column == 'q.strand':
            len_array = abs(group['q.start'].to_numpy()-group['q.end'].to_numpy())
        else:
            len_array = abs(group['s.start'].to_numpy()-group['s.end'].to_numpy())
        
        major_strand_orientation_value = determine_major_strand_orientation(strand_values, len_array)
        if major_strand_orientation_value >= 1:
            dominant_strand_orientation = True # Plus-strand case
            equal_strand_orientation_weight = False
        elif major_strand_orientation_value <= -1:
            dominant_strand_orientation = False # Minus-strand case
            equal_strand_orientation_weight = False
        elif major_strand_orientation_value == 0:
            dominant_strand_orientation = True # Plus / Minus positions are equal -> set equal_strand_orientation_weight to True
            strand_orientation_weight = 1
            equal_strand_orientation_weight = True
        return dominant_strand_orientation, equal_strand_orientation_weight

    def chain_hits_helper_function(hits_to_chain):
        '''
        Helper function to chain local alignment hits (per group via apply)
        '''
        q_start_min = np.min(hits_to_chain[['q.start', 'q.end']].values)
        q_end_max = np.max(hits_to_chain[['q.start', 'q.end']].values)
        s_start_min = np.min(hits_to_chain[['s.start', 's.end']].values)
        s_end_max = np.max(hits_to_chain[['s.start', 's.end']].values)
        mean_percent_identity = hits_to_chain['identity'].mean()
        joined_chain_indices = ','.join(hits_to_chain['indices'].unique())
        n_hits = len(hits_to_chain)
        q_strand_orientation, equal_strand_orientation_weight_query = determine_strand_orientation(hits_to_chain, 'q.strand')
        s_strand_orientation, equal_strand_orientation_weight_subject = determine_strand_orientation(hits_to_chain, 's.strand')
        
        if equal_strand_orientation_weight_query == True and equal_strand_orientation_weight_subject == True:
            q_check = hits_to_chain['q.strand'].to_numpy()
            s_check = hits_to_chain['s.strand'].to_numpy()
            if np.all(q_check == s_check) == False:
                q_strand_orientation = True
                s_strand_orientation = False
        elif equal_strand_orientation_weight_query == True and equal_strand_orientation_weight_subject == False:
            q_strand_orientation = s_strand_orientation
        elif equal_strand_orientation_weight_query == False and equal_strand_orientation_weight_subject == True:
            s_strand_orientation = q_strand_orientation

        local_alignment_contribution_query = calculate_local_alignment_contribution_in_chains(
            hits_to_chain, q_start_min if q_strand_orientation else q_end_max, q_end_max if q_strand_orientation else q_start_min
        )

        return pd.Series({
            'alignment_hits_indices': joined_chain_indices,
            'q.start': q_start_min if q_strand_orientation else q_end_max,
            'q.end': q_end_max if q_strand_orientation else q_start_min,
            's.start': s_start_min if s_strand_orientation else s_end_max,
            's.end': s_end_max if s_strand_orientation else s_start_min,
            'mean_percent_identity[%]': round(mean_percent_identity, 2),
            'q.strand': '+' if q_strand_orientation else '-',
            's.strand': '+' if s_strand_orientation else '-',
            'n_alignment_hits': n_hits,
            'alignment_hit_to_chain_contribution[%]': local_alignment_contribution_query
        })

    local_alignments_df['indices'] = local_alignments_df['indices'].astype(str)
    chained_df = local_alignments_df.groupby(label_column).apply(chain_hits_helper_function).reset_index(drop=True)
    return chained_df

def add_query_and_subject_length(chained_hits):
    '''
    Adds query and subject length to coordinate data
    '''
    chained_hits['q_length'] = abs(chained_hits['q.start'] - chained_hits['q.end'])
    chained_hits['s_length'] = abs(chained_hits['s.start'] - chained_hits['s.end'])
    return chained_hits