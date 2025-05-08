---
id: docker
---

## SegMantX via Docker

Using Docker to install SegMantX ensures platform-independent availability. However, this method is less recommended because it alters the syntax for running SegMantX and may be less user-friendly.

Hint: Running SegMantX with Docker requires some prior knowledge of Docker commands and container management.

## Running SegMantX as a Command-Line Tool via Docker

### 1. Build the Docker image
```bash
# Clone the repository
git clone https://github.com/DMH-biodatasci/SegMantX.git
cd SegMantX #Navigate to the SegMantX directory

# Build the Docker image
docker build -f Dockerfile_SegMantX -t segmantx .
```

### 2. Running SegMantX commands
Use the following syntax to run SegMantX commands inside the container:
```bash
docker run -it --rm segmantx test_modules
# Instead of: python3 SegMantX test_modules
```

### 3. Saving output files to the host
To save output files to your local machine, mount a directory using the -v flag:
```bash
docker run -it --rm -v /path/to/host:/data segmantx generate_alignments \
  --query_file /path/to/host/query_file \
  --blast_output_file /path/to/host/blast_output_file \
  --alignment_hits_file /path/to/host/alignment_hits_output_file \
  --is_query_circular \
  --self_sequence_alignment
```

This replaces the standard Python command:
```bash
SegMantX generate_alignments --query_file /path/to/host/query_file \
  --blast_output_file /path/to/host/blast_output_file \
  --alignment_hits_file /path/to/host/alignment_hits_output_file \
  --is_query_circular \
  --self_sequence_alignment
```

## Running SegMantX as a web application via Docker
If you want to use SegMantX as a web-based app, follow these steps:

### 1. Build the app container
```bash
# Clone the repository
git clone https://github.com/DMH-biodatasci/SegMantX.git
cd SegMantX #Navigate to the SegMantX directory

# Build the Docker image for the app
docker build -f Dockerfile_SegMantX_App -t segmantx_app .
docker run -p 8501:8501 segmantx_app
# Open a browser and navigate to: http://localhost:8501
```

### 2. Run the app
```bash
docker run -p 8501:8501 segmantx_app 
# Note, that nothing will be displayed on the terminal screen
```

### 3. Access the web interface
Open a browser and navigate to:
- http://localhost:8501
