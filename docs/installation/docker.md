---
id: docker
---

# Docker

This proposed installation via Docker ensures a platform-independent availability of SegMantX.
However, it is less recommended as the syntax for running SegMantX changes and it may be less user-friendly. 
Hint: Running SegMantX using Docker may require some 'profound' knowledge about Docker.

```bash
# Clone the repository
git clone https://github.com/DMH-biodatasci/SegMantX.git
cd SegMantX
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

