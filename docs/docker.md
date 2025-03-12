---
id: docker
---

## SegMantX via Docker

This proposed installation by building a Docker container ensures a platform-independent availability of SegMantX.
However, it is less recommended as the syntax for running SegMantX changes and it may be less user-friendly.

Hint: Running SegMantX using Docker may require some profound knowledge about Docker.

## Docker container for SegMantX as command-line tool

```bash
# Clone the repository
git clone https://github.com/DMH-biodatasci/SegMantX.git
cd SegMantX #Navigate to the SegMantX directory 
docker build -f Dockerfile_SegMantX -t segmantx .
```

Modify the syntax using SegMantX via, for example:
```bash
docker run -it --rm segmantx test_modules
# Instead of: python3 SegMantX test_modules
```

To save output files to localhost, modify your commands such as:
```bash
docker run -it --rm -v /path/to/host:/data segmantx generate_alignments \
  --query_file /path/to/host/query_file \
  --blast_output_file /path/to/host/blast_output_file \
  --alignment_hits_file /path/to/host/alignment_hits_output_file \
  --is_query_circular \
  --self_sequence_alignment
  
#Instead of: python3 SegMantX generate_alignments --query_file /path/to/host/query_file --blast_output_file /path/to/host/blast_output_file --alignment_hits_file /path/to/host/alignment_hits_output_file --is_query_circular --self_sequence_alignment
```

## Docker container for SegMantX as app

```bash
# Go to to your SegMantX directory e.g.,
cd SegMantX

docker build -f Dockerfile_SegMantX_App -t segmantx_app .
docker run -p 8501:8501 segmantx_app
# Open a browser and navigate to: http://localhost:8501
```
