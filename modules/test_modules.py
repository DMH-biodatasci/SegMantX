#!/usr/bin/env python3
from Bio import Entrez, SeqIO
import argparse
import sys
from subprocess import run
import os


def check_output(file_path):
    if os.path.exists(file_path):
        print(f"{file_path} ok.")
        return True, f"{file_path} ok."
    else:
        print(f"Warning: {file_path} does not exist.")
        return False, f"Warning: {file_path} does not exist."

    
def fetch_fasta(accession_number):
    if not os.path.exists('tests'):
        os.makedirs('tests')
    try:
        with Entrez.efetch(db="nucleotide", id=accession_number, rettype="fasta", retmode="text") as handle:
            record = handle.read()
            with open('tests/{0}.fasta'.format(accession_number), "w") as f:
                f.write(record)
    except Exception as e:
        print(f"Error fetching sequence: {e}")
        
def fetch_genbank(accession_number):
    try:
        with Entrez.efetch(db="nucleotide", id=accession_number, rettype="gb", retmode="text") as handle:
            data = handle.read()
            with open('tests/{}.gbk'.format(accession_number), "w") as f:
                f.write(data)
    except Exception as e:
        print(f"Error fetching GenBank file: {e}")


def main():   
    fasta_test_data = ["NZ_CP051709.1", "NZ_AP022172.1", "NC_018218.1", "NZ_CP018634.1", "NZ_CP022004.1"]  # Internal IDs: 4029, 461, ztritici, 10635, 10567
    #response = input("Do you want to download the test data? Please enter 'yes' or 'no': ").strip().lower()
    #response == 'yes'
    #if response == 'yes':               
    for accession in fasta_test_data:              
        fetch_fasta(accession)
        if accession == "NZ_AP022172.1":
            fetch_genbank(accession)
                
    with open("test_commands.txt", "r") as f:
        cmd_lines = f.readlines()
    for line in cmd_lines:
        if line.startswith('python3'):
            line = line.rstrip()
            run(line, shell=True, check=True)
    
    print("Checking alignment coordinates files ...")
    c1, p1 = check_output('tests/NZ_CP051709.1.alignment_coordinates.tsv')
    c2, p2 = check_output('tests/NZ_AP022172.1.alignment_coordinates.tsv')
    c3, p3 = check_output('tests/NC_018218.1.alignment_coordinates.tsv')
    c4, p4 = check_output('tests/NZ_CP018634.1_vs_NZ_CP022004.1.alignment_coordinates.tsv')
    print("\n")
    print("Checking chained alignments files ...")
    c5, p5 = check_output('tests/NZ_CP051709.1.chains.tsv')
    c6, p6 = check_output('tests/NZ_AP022172.1.chains.tsv')
    c7, p7 = check_output('tests/NC_018218.1.chains.tsv')
    c8, p8 = check_output('tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.tsv')
    print("\n")
    print("Checking chained alignments fasta files ...")
    c9, p9 = check_output('tests/NZ_CP051709.1.chains.fasta')
    c10, p10 = check_output('tests/NZ_AP022172.1.chains.fasta')
    c11, p11 = check_output('tests/NC_018218.1.chains.fasta')
    c12, p12 = check_output('tests/NZ_CP018634.1_vs_NZ_CP022004.1.chains.fasta')
    print("\n")
    print("Checking plot files ...")
    c13, p13 = check_output('tests/NZ_CP051709.1.html')
    c14, p14 = check_output('tests/NZ_AP022172.1.html')
    c15, p15 = check_output('tests/NC_018218.1.html')
    c16, p16 = check_output('tests/NZ_CP018634.1_vs_NZ_CP022004.1.html')
    check_list = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16]
    error_print_reports = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16]
    
    if all(check_list):
        print("\n")
        print("All modules are fine using the test data.")
    else:
        print("\n")
        print("At least one module encountered an error. Please check the stdout or error_report.txt file.")
        print("Please report any unsolved bugs to the GitHub page of SegMantX.")
        with open('error_report.txt', 'w') as file:
            for line in error_print_reports:
                file.write(line + '\n')
    
    return 

if __name__ == "__main__":
    main()
    