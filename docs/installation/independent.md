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

#Ensure running these commands to make SegMantX globally callable
cp SegMantX $CONDA_PREFIX/bin
cp -r modules $CONDA_PREFIX/bin
cp app.py $CONDA_PREFIX/bin
```