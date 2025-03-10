---
id: app
---
# SegMantX as app
Run the SegMantX app with the following command:
```bash
streamlit run app.py
```

Briefly, the app provides a graphical user interface to SegMantX's main modules. Each page contains a brief description to support the user selecting the correct input data and parameters.

1. **Landing page**: Contains a brief description of the SegMantX app. 
2. **Generate alignments**: Graphical user interface to apply [generate_alignments](https://dmh-biodatasci.github.io/SegMantX/command_line_manual/generate_alignments.html)
3. **Self-alignment chaining**: Graphical user interface to apply [chain_self_alignments](https://dmh-biodatasci.github.io/SegMantX/command_line_manual/chain_self_alignments.html) 
4. **Alignment chaining**: Graphical users interface to apply [chain_alignments](https://dmh-biodatasci.github.io/SegMantX/command_line_manual/chain_alignments.html) 
5. **Visualize chains**: Graphical user interface to apply [visualize_chains](https://dmh-biodatasci.github.io/SegMantX/command_line_manual/visualize_chains.html) 
6. **Fetch chains**: Graphical user interface to apply [fetch_nucleotide_chains](https://dmh-biodatasci.github.io/SegMantX/command_line_manual/fetch_nucleotide_chains.html) 


Alternatviely, the app can also be started by building a Docker container.
```bash
# Go to to your SegMantX directory e.g.,
cd SegMantX

docker build -f Dockerfile_SegMantX_App -t segmantx_app .
docker run -p 8501:8501 segmantx_app
# Open a browser and navigate to: http://localhost:8501
```
