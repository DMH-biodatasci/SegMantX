#!/usr/bin/env python3
from pandas import read_csv, DataFrame
from pandas.errors import EmptyDataError
import argparse
import sys
from Bio.SeqIO import parse as seqioparse, write as seqiowrite
from io import StringIO
import time
from subprocess import run
import os

############################
## 0. BLAST (if required) ##
############################

def safe_remove(file_pattern):
    '''
    Removes files matching a pattern (Windows-safe).
    '''
    for file in os.listdir():
        if file.startswith(file_pattern):
            try:
                os.remove(file)
            except FileNotFoundError:
                pass

def blastn_self_sequence_alignment(query, blast_output='blast_output.txt', alignments_output='alignment_hits.tsv', is_circular=False, evalue=1e-9, min_identity_percentage=60, threads=1, word_size=11):
    '''
    Performs BLASTn self-sequence alignment and generates output files.
    '''
    if is_circular:
        with open("tmp.fasta", "w") as tmp:
            for record in seqioparse(query, "fasta"):
                seqiowrite(record, tmp, "fasta")
                tmp.write(str(record.seq))
        query = 'tmp.fasta'
        
    cmd_blastdb = 'makeblastdb -in {0} -title "{0}" -dbtype nucl'.format(query)
    cmd_blastn = 'blastn -query {0} -db {0} -num_threads {4} -outfmt 7 -evalue {2} -perc_identity {3} -word_size {5} -dust no -soft_masking F -out {1}'.format(query, blast_output, evalue, min_identity_percentage, threads, word_size)
    print("Starting makeblastdb ...")
    start = time.time()
    run(cmd_blastdb, shell=True, check=True)
    end = time.time()
    print("Time for performing makeblastdb: {}".format(round(end-start, 2)))
    print("Starting blastn ...")
    start = time.time()
    run(cmd_blastn, shell=True, check=True)
    end = time.time()
    print("Time for performing blastn: {}".format(round(end-start, 2)))
    
    safe_remove(query)  # Remove intermediate files
    if is_circular:
        safe_remove("tmp.fasta")
    alignment_data = read_csv(blast_output, sep='\t', comment='#', header=None)#[[6,7,8,9,2]]
    alignment_data[[6,7,8,9,2]].to_csv(alignments_output, sep='\t', header=None, index=None)
    return alignment_data[[6,7,8,9,2]]

def blastn_sequence_alignment(query, subject, blast_output='blast_output.txt', alignments_output='alignment_hits.tsv', is_query_circular=False, is_subject_circular=False, evalue=1e-9, min_identity_percentage=60, threads=1, word_size=11):
    '''
    Performs BLASTn sequence alignment between a query and a subject sequence and generates output files.
    '''
    tmp_files = []  # Track temporary files for later removal

    if is_query_circular and is_subject_circular:
        with open("tmp_query.fasta", "w") as tmp:
            for record in seqioparse(query, "fasta"):
                seqiowrite(record, tmp, "fasta")
                tmp.write(str(record.seq))
        with open("tmp_subject.fasta", "w") as tmp:
            for record in seqioparse(subject, "fasta"):
                seqiowrite(record, tmp, "fasta")
                tmp.write(str(record.seq))
        query, subject = 'tmp_query.fasta', 'tmp_subject.fasta'
        tmp_files.extend(['tmp_query.fasta', 'tmp_subject.fasta'])
        
    elif is_query_circular and not is_subject_circular:
        with open("tmp_query.fasta", "w") as tmp:
            for record in seqioparse(query, "fasta"):
                seqiowrite(record, tmp, "fasta")
                tmp.write(str(record.seq))
        query = 'tmp_query.fasta'
        tmp_files.append('tmp_query.fasta')
        
    elif not is_query_circular and is_subject_circular:
        with open("tmp_subject.fasta", "w") as tmp:
            for record in seqioparse(subject, "fasta"):
                seqiowrite(record, tmp, "fasta")
                tmp.write(str(record.seq))
        subject = 'tmp_subject.fasta'
        tmp_files.append('tmp_subject.fasta')
        
    cmd_blastdb = 'makeblastdb -in {0} -title "{0}" -dbtype nucl'.format(subject)
    cmd_blastn = 'blastn -query {0} -db {1} -num_threads {5} -outfmt 7 -evalue {3} -perc_identity {4} -word_size {6} -dust no -soft_masking F -out {2}'.format(query, subject, blast_output, evalue, min_identity_percentage, threads, word_size)
    print("Starting makeblastdb ...") 
    run(cmd_blastdb, shell=True, check=True)
    print("Starting blastn ...")
    print(cmd_blastn)
    start = time.time()
    run(cmd_blastn, shell=True, check=True)
    end = time.time()
    print("Time for performing blastn: {}".format(round(end-start, 2)))
    
    for file in tmp_files:
        safe_remove(file)
    
    try:
        alignment_data = read_csv(blast_output, sep='\t', comment='#', header=None)#[[6,7,8,9,2]]
        alignment_data[[6,7,8,9,2]].to_csv(alignments_output, sep='\t', header=None, index=None)
        return  alignment_data[[6,7,8,9,2]]
    except EmptyDataError:
        empty_df = DataFrame()
        empty_df.to_csv(alignments_output, sep='\t', header=None, index=None)
        return empty_df


def main():
    parser = argparse.ArgumentParser(description="Computes alignments for chaining modules.")
    
    parser.add_argument("module", type=str, help="Name of the module being executed.")
    parser.add_argument("-q", "--query_file", required=True, type=str, help="Path to the query nucleotide FASTA file (required). ")
    parser.add_argument("-s", "--subject_file", type=str, default='', help="Path to the subject nucleotide FASTA file (required for sequence comparison).")
    parser.add_argument("-b", "--blast_output_file", type=str, default='blast_output.txt', help="Path to the output file for BLASTn results (Default: blast_output.txt).")
    parser.add_argument("-a", "--alignment_hits_file", type=str, default='alignment_hits.tsv', help="Path to the output file containing (main) alignment hit data for the chaining process (Default: alignment_hits.tsv).")
    parser.add_argument("-Q", "--is_query_circular", action="store_true", help="Indicates if the query sequence is circular (Default: False).")
    parser.add_argument("-S", "--is_subject_circular", action="store_true", help="Indicates if the subject sequence is circular (Default: False).")
    parser.add_argument("-SA", "--self_sequence_alignment", action="store_true", default=False, help="Indicates to perform a self-sequence alignment (Default: False).")
    parser.add_argument("-e", "--evalue", type=float, default=1e-9, help="E-value threshold for BLASTn (Default: 1e-9).")
    parser.add_argument("-i", "--min_identity_percentage", type=int, default=60, help="Minimum percentage identity for BLASTn matches (Default: 60).")
    parser.add_argument("-T", "--number_of_threads", type=int, default=1, help="Number of threads for BLASTn search (Default: 1).")
    parser.add_argument("-W", "--word_size", type=int, default=11, help="Word size for BLASTn search (increase it for large genomes) (Default: 11).")

    args = parser.parse_args()
    
    if args.self_sequence_alignment:
        start = time.time()
        print("Starting to compute alignments for duplication detection ...")
        print("\n")
        print("Module {} will use the following parameters:".format(args.module))
        print("Input (query): {}".format(args.query_file))
        print("Circular sequence topology (query): {}".format(args.is_query_circular))
        print("Perc. identity: {}".format(args.min_identity_percentage))
        print("E-value: {}".format(args.evalue))
        print("Threads: {}".format(args.number_of_threads))
        print("Word size: {}".format(args.word_size))
        print("Output - alignment coordinates table: {}".format(args.alignment_hits_file))
        print("Output - BLAST output format 7: {}".format(args.blast_output_file))
        print("\n")
        
        blastn_self_sequence_alignment(
            query=args.query_file,
            blast_output=args.blast_output_file,
            alignments_output=args.alignment_hits_file,
            is_circular=args.is_query_circular,
            evalue=args.evalue,
            min_identity_percentage=args.min_identity_percentage,
            threads=args.number_of_threads,
            word_size = args.word_size
        )
    if not args.self_sequence_alignment:
        start = time.time()
        print("Starting to compute alignments for sequence comparison detection ...")
        print("\n")
        print("Module {} will use the following parameters:".format(args.module))
        print("Input (query): {}".format(args.query_file))
        print("Input (subject): {}".format(args.subject_file))
        print("Circular sequence topology (query): {}".format(args.is_query_circular))
        print("Circular sequence topology (subject): {}".format(args.is_subject_circular))
        print("Perc. identity: {}".format(args.min_identity_percentage))
        print("E-value: {}".format(args.evalue))
        print("Threads: {}".format(args.number_of_threads))
        print("Word size: {}".format(args.word_size))
        print("Alignment coordinates table (output): {}".format(args.alignment_hits_file))
        print("BLAST output format 7: {}".format(args.blast_output_file))
        print("\n")
        
        blastn_sequence_alignment(
            query=args.query_file, 
            subject=args.subject_file, 
            blast_output=args.blast_output_file, 
            alignments_output=args.alignment_hits_file,
            is_query_circular=args.is_query_circular,
            is_subject_circular=args.is_subject_circular,
            evalue=args.evalue,
            min_identity_percentage=args.min_identity_percentage,
            threads=args.number_of_threads,
            word_size = args.word_size
        )
    
    print("Total time to run module generate_alignments.py: {}".format(round(time.time()-start, 2)))    
    
    return 

if __name__ == "__main__":
    main()
    