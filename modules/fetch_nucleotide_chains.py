#!/usr/bin/env python3
import argparse
import sys
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO
import pandas as pd
import numpy as np
import time

def retrieve_unique_chaining_coordinates(chained_hits):
    '''
    Identifies and removes redundant chaining coordinates in case of self-alignment chaining for duplication detection.
    '''
    chained_hits["sorted_coords"] = chained_hits.apply(lambda row: tuple(sorted([row["q.start"], row["q.end"], row["s.start"], row["s.end"]])), axis=1)
    chained_hits = chained_hits.drop_duplicates(subset=["sorted_coords"])
    chained_hits = chained_hits.drop(columns="sorted_coords")
    sub_df_query = chained_hits[["ID", "q.start", "q.end", "q.strand", "chain_topology_query", "alignment_hits_indices"]]
    sub_df_subject = chained_hits[["ID", "s.start", "s.end", "s.strand", "chain_topology_subject", "alignment_hits_indices"]]
    sub_df_query = sub_df_query.rename(columns={"q.start": "start", "q.end": "end", "q.strand": "strand", "chain_topology_query": "segment_type"})
    sub_df_subject = sub_df_subject.rename(columns={"s.start": "start", "s.end": "end", "s.strand": "strand", "chain_topology_subject": "segment_type"})
    sub_df_query["query_subject"] = 'query'
    sub_df_subject["query_subject"] = 'subject'
    concatenated_df = pd.concat([sub_df_query, sub_df_subject], axis=0)
    unique_coords_df = concatenated_df.drop_duplicates(subset=["start", "end", "strand"])
    unique_coords_df.loc[:, 'segment_type'] = np.where(unique_coords_df['segment_type'] == 'segment', False, True)
    unique_coords_df.columns = ["ID", "start", "end", "strand", "chain_exceeds_seq", "alignment_hits_indices", "query_subject"]
    return unique_coords_df

def get_nucleotide_chain(row, sequences, seq_id_origin):
    '''
    Extracts the chain as nucleotide sequence from a given fasta file and returns the record.
    '''
    seq_id = '{0}_{1}'.format(row['ID'], row['query_subject'])
    start = row['start']
    end = row['end']
    plus_strand = row['strand'] == '+'
    chain_exceeds_seq = row['chain_exceeds_seq']
    
    full_sequence = sequences.seq

    if plus_strand and not chain_exceeds_seq:
        chain_seq = full_sequence[start:end]
    if not plus_strand and not chain_exceeds_seq: 
        chain_seq = full_sequence[end:start]
        chain_seq = chain_seq.reverse_complement()
    if chain_exceeds_seq:
        if plus_strand:
            chain_subseq1 = full_sequence[start:len(full_sequence)]
            chain_subseq2 = full_sequence[0:end]
            chain_seq = chain_subseq1 + chain_subseq2
        if not plus_strand:
            chain_subseq1 = full_sequence[end:len(full_sequence)]
            chain_subseq2 = full_sequence[0:start]
            chain_seq = chain_subseq1 + chain_subseq2
            chain_seq = chain_seq.reverse_complement()
    if plus_strand:
        record = SeqRecord(Seq(str(chain_seq)),
                           id=seq_id,
                           description=f"{seq_id_origin}:{start}-{end} (+)")
    else:
        record = SeqRecord(Seq(str(chain_seq)),
                           id=seq_id,
                           description=f"{seq_id_origin}:{start}-{end} (-)")
    return record

def return_first_sequence(fasta_file):
    '''
    Returns first sequence in a fasta file
    '''
    return next(SeqIO.parse(fasta_file, "fasta"))

def get_chained_sequences(chained_hits, fasta_file, output_fasta):
    '''
    Fetches chains as nucleotide sequences using the chaining output and fasta file and write result to fasta file.
    '''
    if isinstance(chained_hits, pd.DataFrame):
        pass
    else:
        try:
            chained_hits = pd.read_csv(chained_hits, sep='\t')
        except pd.errors.EmptyDataError:
            return print("No chains available!")
    unique_chaining_coordinates_df = retrieve_unique_chaining_coordinates(chained_hits)
    sequences = return_first_sequence(fasta_file)
    unique_chaining_coordinates_df['subsequence_record'] = unique_chaining_coordinates_df.apply(get_nucleotide_chain, axis=1, sequences=sequences, seq_id_origin = sequences.id)   
    chain_seq_records = unique_chaining_coordinates_df['subsequence_record'].tolist()
    with open(output_fasta, "w") as output_handle:
        SeqIO.write(chain_seq_records, output_handle, "fasta")
    return output_fasta
        
def split_query_subject_coordinate_dataframes(chained_hits):
    '''
    Splits segmentation coordinate data into query and subject dataframes for sequence extraction.
    '''
    sub_df_query = chained_hits[["ID", "q.start", "q.end", "q.strand", "chain_topology_query", "alignment_hits_indices"]]
    sub_df_subject = chained_hits[["ID", "s.start", "s.end", "s.strand", "chain_topology_subject", "alignment_hits_indices"]]
    sub_df_query = sub_df_query.rename(columns={"q.start": "start", "q.end": "end", "q.strand": "strand", "chain_topology_query": "topology_type"})
    sub_df_subject = sub_df_subject.rename(columns={"s.start": "start", "s.end": "end", "s.strand": "strand", "chain_topology_subject": "topology_type"})
    sub_df_query["query_subject"] = 'query'
    sub_df_subject["query_subject"] = 'subject'

    sub_df_query.loc[:, 'topology_type'] = np.where(sub_df_query['topology_type'] == 'segment', False, True)
    sub_df_query.columns = ["ID", "start", "end", "strand", "chain_exceeds_seq", "alignment_hits_indices", "query_subject"]
    
    sub_df_subject.loc[:, 'topology_type'] = np.where(sub_df_subject['topology_type'] == 'segment', False, True)
    sub_df_subject.columns = ["ID", "start", "end", "strand", "chain_exceeds_seq", "alignment_hits_indices", "query_subject"]
    
    return sub_df_query, sub_df_subject
        
def get_chained_sequences_from_two_sequences(chained_hits, fasta_file_query, fasta_file_subject, output_fasta):
    '''
    Fetches chains as nucleotide sequences using the chaining output and fasta files and write result to fasta file.
    '''
    try:
        chained_hits = pd.read_csv(chained_hits, sep='\t')
    except pd.errors.EmptyDataError:
        return print("No chains available!")
            
    sub_df_query, sub_df_subject = split_query_subject_coordinate_dataframes(chained_hits)
    
    query_sequence = return_first_sequence(fasta_file_query)
    subject_sequence = return_first_sequence(fasta_file_subject)
 
    sub_df_query['subsequence_record'] = sub_df_query.apply(get_nucleotide_chain, axis=1, sequences=query_sequence, seq_id_origin = query_sequence.id)
    chain_seq_records_query = sub_df_query['subsequence_record'].tolist()
    
    sub_df_subject['subsequence_record'] = sub_df_subject.apply(get_nucleotide_chain, axis=1, sequences=subject_sequence, seq_id_origin = subject_sequence.id)
    chain_seq_records_subject = sub_df_subject['subsequence_record'].tolist()
    
    chain_seq_records = chain_seq_records_query + chain_seq_records_subject
    with open(output_fasta, "w") as output_handle:
        SeqIO.write(chain_seq_records, output_handle, "fasta")
    return output_fasta


def main():
    parser = argparse.ArgumentParser(description="Extracts nucleotide sequences from chained alignments (FASTA format).")
    
    parser.add_argument("module", type=str, help="Name of the module being executed.")
    parser.add_argument("-i", "--input_file", type=str, required = True, help="Output file from chaining results as input.")
    parser.add_argument("-fq", "--fasta_file_query", type=str, help="Fasta file to read out the sequence length.")
    parser.add_argument("-o", "--output_file", type=str, default='chains.fasta', help="Output file: Fasta file containing nucleotide chains.")
    parser.add_argument("-fs", "--fasta_file_subject", type=str, help="Fasta file to read out the sequence length.")
    
    args = parser.parse_args()
    
    if isinstance(args.fasta_file_query, str) and not isinstance(args.fasta_file_subject, str):
        check = True
    elif isinstance(args.fasta_file_subject, str) and not isinstance(args.fasta_file_query, str):
        args.fasta_file_query = args.fasta_file_subject
        check = True
    elif isinstance(args.fasta_file_query, str) and isinstance(args.fasta_file_subject, str) and args.fasta_file_subject == args.fasta_file_query:
        check =True
    else:
        check = False
    
    if check:
        start = time.time()
        print("Starting to extract chained alignments as nucleotide sequences from one fasta file ...")
        print("\n")
        print("Module {} will use the following parameters:".format(args.module))
        print("Input chained alignments file: {}".format(args.input_file))
        print("Input FASTA file: {}".format(args.fasta_file_query))
        print("Output FASTA file: {}".format(args.output_file))
        
        get_chained_sequences(
            chained_hits=args.input_file,
            fasta_file=args.fasta_file_query,
            output_fasta=args.output_file
        )
        
    elif isinstance(args.fasta_file_query, str) and isinstance(args.fasta_file_subject, str):
        start = time.time()
        print("Starting to extract chained alignments as nucleotide sequences from two fasta files ...")
        print("\n")
        print("Module {} will use the following parameters:".format(args.module))
        print("Input chained alignments file: {}".format(args.input_file))
        print("Input FASTA file (query): {}".format(args.fasta_file_query))
        print("Input FASTA file (subject): {}".format(args.fasta_file_subject))
        print("Output FASTA file: {}".format(args.output_file))
        
        get_chained_sequences_from_two_sequences(
            chained_hits=args.input_file,
            fasta_file_query=args.fasta_file_query,
            fasta_file_subject=args.fasta_file_subject,
            output_fasta=args.output_file
        )
    else:
        print("Provide only one fasta file (--fasta_file_query or --fasta_file_subject) if the chains as nucleotide sequences should be feteched from one sequence.")
        print("Alternatively, indicate the fasta files for the query (--fasta_file_query) and subject (--fasta_file_subject) sequences.")
        print("For help type: python3 segmentation.py fetch_nucleotide_chains --help")

    print("Total time to fetch chains as nucleotide sequences: {}".format(time.time()-start))
    return 

if __name__ == "__main__":
    main()
    