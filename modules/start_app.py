#!/usr/bin/env python3
import subprocess

def main():
    subprocess.run('streamlit run app.py', shell=True, check=True)
    return 

if __name__ == "__main__":
    main()
    