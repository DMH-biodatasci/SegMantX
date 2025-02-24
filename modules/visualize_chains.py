#!/usr/bin/env python3
import argparse
import sys
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
from Bio import SeqIO
from modules.common_functions import get_sequence_length
import time


def get_features_from_genbank(genbank_file, sequence_length=None, for_internal_processing=False):
    '''
    Function to extract features from genbank file.
    Returns a dataframe containing features.
    '''
    genbank_data = SeqIO.read(genbank_file, "genbank")
    features_list = []
    for feature in genbank_data.features:
        if feature.type == "CDS":
            features_list.append({
                'start': feature.location.start,
                'end': feature.location.end,
                'strand': feature.location.strand,
                'type': feature.type,
                'protein_id': feature.qualifiers.get('protein_id', [''])[0],
                'pseudo': 'pseudo' in feature.qualifiers,
                'product': feature.qualifiers.get('product', [''])[0],
                'translation': feature.qualifiers.get('translation', [''])[0]
            })
    
    features_df = pd.DataFrame(features_list)
    if 'pseudo' not in features_df.columns:
        features_df['pseudo'] = False
    features_df['start'] = pd.to_numeric(features_df['start'], errors='coerce')
    features_df['end'] = pd.to_numeric(features_df['end'], errors='coerce')
    features_df['width'] = features_df['end'] - features_df['start']
    features_df['strand'] = features_df['strand'].astype(str)
    features_df['type'] = features_df['type'].astype(str)
    features_df['protein_id'] = features_df['protein_id'].astype(str)
    features_df['pseudo'] = features_df['pseudo'].astype(bool)
    features_df['product'] = features_df['product'].astype(str)
    features_df['translation'] = features_df['translation'].astype(str)

    if sequence_length is not None:
        features_df['width'] = features_df['end'] - features_df['start']
        features_exceed_linear_sequence = features_df[features_df['start'] > features_df['end']].copy()
        features_df = features_df[features_df['start'] <= features_df['end']].copy()
        if not features_exceed_linear_sequence.empty:
            features_exceed_linear_sequence['start'] = 1
            features_exceed_linear_sequence['end'] = sequence_length
            features_df = pd.concat([features_df, features_exceed_linear_sequence], ignore_index=True)
    
    features_df['ID'] = range(1, len(features_df) + 1)
    if not for_internal_processing:
        return features_df.tail(-4)
    else:
        return features_df


def scaled_feature_rectangle_positions(seq_len, scale, factor=10000):
    '''
    Helper function to scale the positioning of genbank features (y0, y1)
    '''
    if scale == 'kbp':
        factor = 10000
    elif scale == 'bp':
        factor = 10
    elif scale == 'mbp':
        factor = 10000000
    else:
        factor = 10
    return (seq_len/factor)

def set_y_values(row, scaled_value):
    '''
    Helper function to vary the positioning of genbank features on plus/minus strand
    '''
    if row['strand'] == '+' and not row['pseudo']:
        return (-scaled_value/2), -1  
    elif row['strand'] == '-' and not row['pseudo']:
        return (-scaled_value/2), -scaled_value
    if row['pseudo']:
        return -scaled_value, (-scaled_value-(scaled_value/2))
    else:
        return 0, 0  
    
def choose_scaling_value(scale):
    '''
    Helper function to pick scaling values and x/y-axis titles.
    '''
    if scale == 'kbp':
        return 1000, 'Query sequence [kbp]', 'Subject sequence [kbp]'
    elif scale == 'bp':
        return 1, 'Query sequence [bp]', 'Subject sequence [bp]'
    elif scale == 'mbp':
        return 1000000, 'Query sequence [mbp]', 'Subject sequence [mbp]'
    else:
        return 1, 'Query sequence [bp]', 'Subject sequence [bp]'

def create_segmentplot_for_chains(chained_hits, genbank_df=pd.DataFrame(), scale='kbp', seq_len_query=None, seq_len_subject=None, fasta_file_query=None, fasta_file_subject=None, query_is_subject=False):
    '''
    Main function for creating the segmentation plot as interactive plot
    '''

    scaling_value, xaxis_title, yaxis_title = choose_scaling_value(scale) 
    chained_hits[['q.start', 'q.end', 's.start', 's.end']] /= scaling_value
    seq_len_query /= scaling_value
    seq_len_subject /= scaling_value

    fig = go.Figure()
    chained_hits['q_mean'] = (chained_hits['q.start'] + chained_hits['q.end'])/2
    chained_hits['s_mean'] = (chained_hits['s.start'] + chained_hits['s.end'])/2
    fig = px.scatter(
        chained_hits,
        x='q_mean',
        y='s_mean',
        color='mean_percent_identity[%]',  
        color_continuous_scale='Viridis_r',  
        range_color=[0, 100],  
        labels={'mean_percent_identity[%]': 'mean_percent_identity[%]'},
        width=800,
        height=600,
        opacity=0,
        hover_data={
            'ID': True,
            'q.start': True,  
            'q.end': True,    
            's.start': True,  
            's.end': True,    
            'mean_percent_identity[%]': True,  
            'n_alignment_hits': True,
            'alignment_hit_to_chain_contribution[%]': True,
            'q.strand': True,
            's.strand': True,
            'chain_topology_query': True, 
            'chain_topology_subject': True
        }
    )
    
    for _, row in chained_hits.iterrows():
        fig.add_scatter(
            x=[row['q.start'], row['q.end']],
            y=[row['s.start'], row['s.end']],
            mode='lines',
            line=dict(color=row['color'], width=2),
            hoverinfo='skip'
        )

    y_zero_value = 0
    if not genbank_df.empty:
        genbank_df[['start', 'end']] /= scaling_value
        y_zero_value = -scaled_feature_rectangle_positions(seq_len_query, scale) * scaling_value
        # Creation of rectangle shapes
        rect_shapes = [
            dict(
                type="rect",
                x0=start,
                y0=y0,
                x1=end,
                y1=y1,
                line = dict(color="DarkGray", width=2) if pseudo else (dict(color="RoyalBlue", width=2) if strand == '+' else dict(color="Crimson", width=2)),
                fillcolor = "Gray" if pseudo else ("LightSkyBlue" if strand == '+' else "LightSalmon"),
                opacity=0.6
            )
            for start, end, y0, y1, strand, pseudo in zip(genbank_df['start'], genbank_df['end'], genbank_df['y0'], genbank_df['y1'], genbank_df['strand'], genbank_df['pseudo'])
        ]
        
        # Add horizontal line if features are added
        rect_shapes.append({'type':'line', 'x0':0, 'x1':seq_len_query,'y0':0, 'y1':0, 'line': {'color': 'black', 'width': 2}})

        fig.update_layout(shapes=rect_shapes)

        # Creation of hover text
        genbank_df['hover_text'] = (
            "Start: " + genbank_df['start'].astype(str) + "<br>" +
            "End: " + genbank_df['end'].astype(str) + "<br>" +
            "Strand: " + genbank_df['strand'].astype(str) + "<br>" +
            "Pseudo: " + genbank_df['pseudo'].astype(str) + "<br>" +
            "Product: " + genbank_df['product'].astype(str)
        )

        # Adding hover data points (midpoints of rectangles) as a scatter plot with invisible markers
        hover_data_points = go.Scatter(
            x=(genbank_df['start'] + genbank_df['end']) / 2,  # X midpoint
            y=(genbank_df['y0'] + genbank_df['y1']) / 2,      # Y midpoint
            mode='markers',
            marker=dict(size=0, color='rgba(0,0,0,0)'),       # Invisible markers
            hoverinfo='text',
            hovertext=genbank_df['hover_text'],               # Use the hover text
            showlegend=False
        )
        fig.add_trace(hover_data_points)
       
    if genbank_df.empty:
        min_yaxis_value = 0
    else:
        min_yaxis_value = min(genbank_df['y0']+genbank_df['y1'])

    fig.update_layout(
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        coloraxis_colorbar=dict(
            title='Mean sequence\nidentity [%]',
            tickvals=[0, 25, 50, 75, 100],
            ticktext=['0', '25', '50', '75', '100']
        ),
        showlegend=False,
        plot_bgcolor='white',  
        paper_bgcolor='white',  
        xaxis=dict(range=[0, seq_len_query], showgrid=False, gridcolor='lightgrey'),  
        yaxis=dict(range=[min_yaxis_value, seq_len_subject], showgrid=False, gridcolor='lightgrey'),
        width=1400,  
        height=800,
        template='simple_white'
    )
    return fig

def ensure_presence_of_seq_len_values(chained_hits, seq_len_query=None, seq_len_subject=None, fasta_file_query=None, fasta_file_subject=None, query_is_subject=False):
    '''
    Checks the presence of provided sequence length and returns the sequence length
    or max. value in chained hits data for visualization purposes.
    '''
    if query_is_subject:
        seq_len_subject = seq_len_query
    if seq_len_query == None and not fasta_file_query == None:
        seq_len_query = get_sequence_length(fasta_file_query)
    if seq_len_subject == None and not fasta_file_subject == None:
        seq_len_subject = get_sequence_length(fasta_file_subject)
    if seq_len_query == None:
        seq_len_query = max(chained_hits["q.start"].to_list()+chained_hits["q.end"].to_list())
    if seq_len_subject==None:
        seq_len_subject = max(chained_hits["s.start"].to_list()+chained_hits["s.end"].to_list())
    return seq_len_query, seq_len_subject

def segmentplot_of_chains(chained_hits, seq_len_query=None, seq_len_subject=None, genbank=None, scale='kbp', output_file='', fasta_file_query=None, fasta_file_subject=None, query_is_subject=False):
    '''
    Visualizes chained hits by creating a dotplot like interactive graph.
    '''
    if isinstance(chained_hits, pd.DataFrame):
        chained_hits = chained_hits
    else:
        chained_hits = pd.read_csv(chained_hits, sep='\t')
    chained_hits = chained_hits.copy()
    seq_len_query, seq_len_subject = ensure_presence_of_seq_len_values(chained_hits, seq_len_query, seq_len_subject, fasta_file_query, fasta_file_subject, query_is_subject)

    if isinstance(genbank, str):
        genbank_df = get_features_from_genbank(genbank)
        genbank_df = genbank_df.copy()
        genbank_df['strand'] = genbank_df['strand'].apply(lambda x: '+' if x == '1' else '-' if x == '-1' else x)
        genbank_df[['y0', 'y1']] = genbank_df.apply(lambda row: set_y_values(row, scaled_feature_rectangle_positions(seq_len_query, scale)), axis=1, result_type='expand')
    else:
        genbank_df = pd.DataFrame()

    color_scale = px.colors.sequential.Viridis_r    
    chained_hits['color'] = chained_hits['mean_percent_identity[%]'].apply(
        lambda x: color_scale[int(x / 100 * (len(color_scale) - 1))]
    )

    plt = create_segmentplot_for_chains(chained_hits, genbank_df, scale, seq_len_query, seq_len_subject, fasta_file_query, fasta_file_subject)

    if not output_file == '':
        plt.write_html(output_file)

    return plt


def main():
    parser = argparse.ArgumentParser(description="Generates a dotplot to visualize yielded chains for a sequence.")
    
    parser.add_argument("module", type=str, help="Name of the module being executed.")
    parser.add_argument("-i", "--input_file", type=str, required=True, help="Output file from chaining results as input.")    
    parser.add_argument("-LQ", "--sequence_length_query", type=int, default=None, help="Size of the query sequence (is required with circular sequence topology). Otherwise, provide fasta file (i.e., using --fasta_file_query) (Default: None).")
    parser.add_argument("-LS", "--sequence_length_subject", type=int, default=None, help="Size of the subject sequence (is required with circular sequence topology). Otherwise, provide fasta file (i.e., using --fasta_file_subject) (Default: None).")
    parser.add_argument("-gf", "--genbank_file", type=str, default=pd.DataFrame(), help="Genbank file to visualize features.")
    parser.add_argument("-o", "--output_file", type=str, default='plot.html', help="Output file: Interactive plot (i.e., html file).")
    parser.add_argument("-S", "--scale", type=str, default='kbp', help="Scaling the plot to bp, kbp (default), or mbp options:[bp, kbp, mbp].")
    parser.add_argument("-fq", "--fasta_file_query", type=str, help="Fasta file to read out the sequence length.")
    parser.add_argument("-fs", "--fasta_file_subject", type=str, help="Fasta file to read out the sequence length.")
    parser.add_argument("-QIS", "--query_is_subject", action="store_true", help="Specify this flag if the query sequence is identical to the subject sequence (i.e., chaining result from self-alignment).")
    
    args = parser.parse_args()
      
    start = time.time()
    print("Starting to create interactive plot ...")
    print("\n")
    print("Module {} will use the following parameters:".format(args.module))
    print("Input alignments coordinates file: {}".format(args.input_file))
    print("Genbank file: {}".format(args.genbank_file))
    print("Scale for plot axes: {}".format(args.scale))
    print("FASTA file (query): {}".format(args.fasta_file_query))
    print("Sequence length (query): {}".format(args.sequence_length_query))
    print("FASTA file (subject): {}".format(args.fasta_file_subject))
    print("Sequence length (subject): {}".format(args.sequence_length_subject))
    print("Query and subject are identical: {}".format(args.query_is_subject))
    print("Output filename: {}".format(args.output_file))
    print("\n")
    
    segmentplot_of_chains(
        chained_hits=args.input_file,
        seq_len_query=args.sequence_length_query,
        seq_len_subject=args.sequence_length_subject,
        output_file=args.output_file,
        scale=args.scale,
        fasta_file_query=args.fasta_file_query,
        fasta_file_subject=args.fasta_file_subject,
        query_is_subject=args.query_is_subject,
        genbank=args.genbank_file
    )
    
    print("Time to create plot: {}".format(time.time()-start))
    print("\n")
    print("Warning: Chains originating from sequences that are characterized by a circular sequence topology may appear with a steep slope. These chains may look abnormal by visual inspection.")
    return 

if __name__ == "__main__":
    main()

