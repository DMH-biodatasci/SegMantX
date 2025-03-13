---
id: linux
---

# Installation on linux

## Prerequisites
Before getting started, ensure you have Miniconda installed on your machine (i.e., using your terminal conda should be available).
If your (older) conda version doesn't support the parameter '--platform', try the [platform independent installation](https://dmh-biodatasci.github.io/SegMantX/installation/independent.html).

```bash
# Clone the repository
git clone https://github.com/DMH-biodatasci/SegMantX.git
cd SegMantX

# Create and activate a new conda environment from the provided .yml file
conda env create -f SegMantX.yml --platform linux-64
# Alternatively: conda env create -f SegMantX.yml --platform linux-aarch64
conda activate SegMantX

#Ensure running these commands to make SegMantX globally callable
cp SegMantX $CONDA_PREFIX/bin
cp -r modules $CONDA_PREFIX/bin
cp app.py $CONDA_PREFIX/bin
```

Note, we also provide a solution using SegMantX and its app via [Docker](https://dmh-biodatasci.github.io/SegMantX/docker.html). However, it is less recommended as the syntax for running SegMantX changes and it may be less user-friendly.

