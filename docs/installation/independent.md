---
id: independent
---

# Platform-independent installation

## Prerequisites
Before getting started, ensure you have Miniconda installed on your machine (i.e., using your terminal conda should be available).

Warning: This installation procedure may cause issues during the installation on some platforms due to package availability on some operating systems and chip architectures.
However, this installation may be necessary using (older) conda versions that don't support the parameter '--platform'.

```bash
# Clone the repository
git clone https://github.com/DMH-biodatasci/SegMantX.git
cd SegMantX

# Create and activate a new conda environment from the provided .yml file
conda env create -f SegMantX.yml
conda activate SegMantX

#Ensure running the post_install.sh script to make SegMantX globally callable
./post_install.sh
```

Note, we also provide a solution using SegMantX and its app via [Docker](https://dmh-biodatasci.github.io/SegMantX/docker.html). However, it is less recommended as the syntax for running SegMantX changes and it may be less user-friendly.