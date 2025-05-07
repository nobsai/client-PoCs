import os
import pandas as pd
import numpy as np
from openai import OpenAI
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
from dotenv import load_dotenv
import plotly.express as px

# Set page configuration
st.set_page_config(
    page_title="Retail Customer Segmentation",
    page_icon="🛍️",
    layout="wide"
)

# Apply custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2563EB;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .cluster-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #3B82F6;
    }
    .insights-box {
        background-color: #F0F9FF;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
        margin-bottom: 1rem;
    }
    .recommendations-box {
        background-color: #ECFDF5;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #10B981;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to create customer profile text
def create_customer_profile(row):
    return (
        f"Customer ID: {row['Customer_ID']}. "
        f"A {row['Age']}-year-old {row['Gender']} with an annual income of ${row['Annual_Income']}. "
        f"Total spent: ${row['Total_Spent']} over {row['Num_Purchases']} purchases (avg: ${row['Avg_Purchase_Value']}). "
        f"Preferred style: {row['Preferred_Style']}, favorite color: {row['Preferred_Color']}. "
        f"Loyalty member: {row['Loyalty_Program_Member']}. Shops mostly on: {row['Preferred_Shopping_Day']}. "
        f"Prefers: {row['Online_vs_InStore']} shopping. Coupon usage: {row['Coupon_Usage_Frequency']}. "
        f"Last purchased {row['Last_Purchase_Category']} {row['Time_Since_Last_Purchase_Days']} days ago. "
        f"Loyalty points: {row['Loyalty_Points_Accumulated']}, store visits/month: {row['Store_Visits_Per_Month']}. "
        f"Customer since {row['Customer_Since']}."
    )

# Generate embeddings
def get_embeddings(texts):
    embeddings = []
    for text in tqdm(texts, desc="Generating embeddings"):
        try:
            response = client.embeddings.create(input=text, model="text-embedding-3-small")
            embeddings.append(response.data[0].embedding)
        except Exception as e:
            print(f"Embedding error for text: {text}\n{e}")
            embeddings.append([0]*1536)
    return embeddings

# Load and process data
@st.cache_data
def load_data(csv_file):
    df = pd.read_csv(csv_file)
    df['Profile'] = df.apply(create_customer_profile, axis=1)
    df['Embedding'] = get_embeddings(df['Profile'].tolist())
    return df

# Clustering
def perform_clustering(df, n_clusters=5):  # Fixed to 5 clusters
    embedding_matrix = np.array(df['Embedding'].tolist())
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df['Cluster'] = kmeans.fit_predict(embedding_matrix)
    return df, kmeans

# Dimensionality reduction
def reduce_dimensions(embedding_matrix):
    pca = PCA(n_components=2)
    return pca.fit_transform(embedding_matrix)

# Analyze clusters
def analyze_clusters(df):
    cluster_insights = df.groupby('Cluster').agg({
        'Age': 'mean',
        'Annual_Income': 'mean',
        'Total_Spent': 'mean',
        'Num_Purchases': 'mean',
        'Avg_Purchase_Value': 'mean',
        'Loyalty_Points_Accumulated': 'mean',
        'Store_Visits_Per_Month': 'mean',
        'Preferred_Style': lambda x: x.mode()[0],
        'Preferred_Color': lambda x: x.mode()[0],
        'Online_vs_InStore': lambda x: x.mode()[0],
        'Coupon_Usage_Frequency': lambda x: x.mode()[0],
        'Preferred_Shopping_Day': lambda x: x.mode()[0],
        'Loyalty_Program_Member': lambda x: x.mode()[0],
        'Last_Purchase_Category': lambda x: x.mode()[0],
    }).reset_index()
    return cluster_insights

# Generate summaries using GPT
def generate_cluster_summaries(cluster_insights):
    summaries = []
    for _, row in cluster_insights.iterrows():
        prompt = (
            f"Provide a concise, professional summary for a customer cluster with the following characteristics:\n\n"
            f"- Average Age: {row['Age']:.1f}\n"
            f"- Average Income: ${row['Annual_Income']:.2f}\n"
            f"- Average Total Spent: ${row['Total_Spent']:.2f}\n"
            f"- Average Purchases: {row['Num_Purchases']:.2f} times\n"
            f"- Avg Purchase Value: ${row['Avg_Purchase_Value']:.2f}\n"
            f"- Loyalty Points: {row['Loyalty_Points_Accumulated']:.1f}\n"
            f"- Visits per Month: {row['Store_Visits_Per_Month']:.1f}\n"
            f"- Most Preferred Style: {row['Preferred_Style']}\n"
            f"- Favorite Color: {row['Preferred_Color']}\n"
            f"- Most Used Channel: {row['Online_vs_InStore']}\n"
            f"- Coupon Usage: {row['Coupon_Usage_Frequency']}\n"
            f"- Shopping Day: {row['Preferred_Shopping_Day']}\n"
            f"- Loyalty Program Member: {row['Loyalty_Program_Member']}\n"
            f"- Recent Purchase Category: {row['Last_Purchase_Category']}\n\n"
            f"Write the summary as bullet points with insights and strategic recommendations for marketing and product teams."
            f"Show avg cluster values in format with Demographics & Income, Spending & Purchasing Behavior, Shopping Preferences, Loyalty & Engagement, Recent Purchase Trends as headers."
            f"Add an insights section and recommendations section in bullet points below."
        )
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a data analyst summarizing customer clusters for leadership."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            summaries.append(response.choices[0].message.content)
        except Exception as e:
            print(f"Summary error: {e}")
            summaries.append("Failed to generate summary.")
    return summaries

# Function to create a radar chart for cluster comparison
def create_radar_chart(cluster_insights, cluster_num):
    # Select the cluster
    cluster_data = cluster_insights[cluster_insights['Cluster'] == cluster_num].iloc[0]
    
    # Select numerical columns for the radar chart
    radar_features = ['Age', 'Annual_Income', 'Total_Spent', 'Num_Purchases', 
                      'Avg_Purchase_Value', 'Loyalty_Points_Accumulated', 'Store_Visits_Per_Month']
    
    # Normalize the data for better visualization
    all_values = cluster_insights[radar_features].values.flatten()
    max_values = cluster_insights[radar_features].max()
    
    # Prepare data for radar chart
    fig = px.line_polar(
        r=[cluster_data[feature]/max_values[feature] for feature in radar_features],
        theta=radar_features,
        line_close=True,
    )
    fig.update_traces(fill='toself')
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1])
        ),
        showlegend=False,
        title=f"Cluster {cluster_num} Profile"
    )
    return fig

# Create a simple pie chart for categorical data
def create_pie_chart(df, cluster_num, column):
    cluster_df = df[df['Cluster'] == cluster_num]
    value_counts = cluster_df[column].value_counts().reset_index()
    value_counts.columns = [column, 'Count']
    
    fig = px.pie(value_counts, values='Count', names=column, title=f"{column} Distribution in Cluster {cluster_num}")
    return fig

# Streamlit app
def main():
    st.markdown('<div class="main-header">🛍️ Retail Customer Segmentation with GPT & KMeans</div>', unsafe_allow_html=True)
    st.write("Upload customer data and receive cluster-based insights using AI embeddings and clustering.")
    
    # Fixed number of clusters
    n_clusters = 5
    
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    if uploaded_file:
        # Show a spinner while processing
        with st.spinner("Processing data and generating insights..."):
            df = load_data(uploaded_file)

            # Data preview in an expander
            with st.expander("📋 Data Preview", expanded=False):
                st.dataframe(df.head(10))

            st.markdown('<div class="sub-header">📊 Customer Clusters</div>', unsafe_allow_html=True)
            df, kmeans = perform_clustering(df, n_clusters=n_clusters)

            embedding_matrix = np.array(df['Embedding'].tolist())
            reduced_embeddings = reduce_dimensions(embedding_matrix)
            df['PCA1'] = reduced_embeddings[:, 0]
            df['PCA2'] = reduced_embeddings[:, 1]

            # Cluster visualization using Plotly for interactivity
            # Convert cluster to string for better legend display
            df['Cluster_Label'] = 'Cluster ' + df['Cluster'].astype(str)
            
            fig = px.scatter(
                df, x='PCA1', y='PCA2', 
                color='Cluster_Label',  # Use labeled clusters
                title="Customer Clusters (PCA Reduced)",
                color_discrete_sequence=px.colors.qualitative.Set2,  # Use discrete colors for categorical data
                hover_data=['Customer_ID', 'Age', 'Annual_Income', 'Total_Spent'],
                template="simple_white"
            )
            fig.update_layout(
                height=600,
                legend_title_text='Customer Segments',
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="right",
                    x=0.99,
                    bgcolor="rgba(255, 255, 255, 0.8)",
                    bordercolor="lightgrey",
                    borderwidth=1
                )
            )
            st.plotly_chart(fig, use_container_width=True)

            # Generate all cluster insights and summaries upfront
            cluster_insights = analyze_clusters(df)
            summaries = generate_cluster_summaries(cluster_insights)
            
            # Creating tabs - reversed order as requested
            tab1, tab2 = st.tabs(["Comparative Analysis", "Cluster Details"])
            
            with tab1:
                st.markdown('<div class="sub-header">📊 Comparative Analysis</div>', unsafe_allow_html=True)
                
                # Display all cluster metrics in a table for comparison
                st.dataframe(cluster_insights.style.background_gradient(cmap='Blues'))
                
                # Select columns for comparison
                comparison_cols = st.multiselect(
                    "Select metrics to compare across clusters:", 
                    options=['Age', 'Annual_Income', 'Total_Spent', 'Num_Purchases', 
                             'Avg_Purchase_Value', 'Loyalty_Points_Accumulated', 'Store_Visits_Per_Month'],
                    default=['Annual_Income', 'Total_Spent']
                )
                
                if comparison_cols:
                    # Create bar charts for selected columns
                    for col in comparison_cols:
                        fig = px.bar(
                            cluster_insights, 
                            x='Cluster', 
                            y=col,
                            title=f"{col} by Cluster",
                            color='Cluster',
                            color_continuous_scale=px.colors.qualitative.Set2
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                st.markdown('<div class="sub-header">🧠 Cluster Details</div>', unsafe_allow_html=True)
                
                # Create a selectbox for clusters
                clusters = sorted(df['Cluster'].unique())
                selected_cluster = st.selectbox("Select a cluster to view details:", clusters)
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Show radar chart for the selected cluster
                    radar_fig = create_radar_chart(cluster_insights, selected_cluster)
                    st.plotly_chart(radar_fig, use_container_width=True)
                    
                    # Show key metrics
                    cluster_metrics = cluster_insights[cluster_insights['Cluster'] == selected_cluster].iloc[0]
                    st.metric("Average Age", f"{cluster_metrics['Age']:.1f}")
                    st.metric("Average Income", f"${cluster_metrics['Annual_Income']:.2f}")
                    st.metric("Average Total Spent", f"${cluster_metrics['Total_Spent']:.2f}")
                
                with col2:
                    # Display the summary for the selected cluster with improved formatting
                    summary = summaries[selected_cluster]
                    st.markdown(summary)
                
                # Show some pie charts in expandable sections
                with st.expander("Categorical Distributions", expanded=False):
                    cat_col1, cat_col2 = st.columns(2)
                    with cat_col1:
                        pie1 = create_pie_chart(df, selected_cluster, 'Preferred_Style')
                        st.plotly_chart(pie1, use_container_width=True)
                    with cat_col2:
                        pie2 = create_pie_chart(df, selected_cluster, 'Online_vs_InStore')
                        st.plotly_chart(pie2, use_container_width=True)
                
                # Customer sample from this cluster
                with st.expander("Customer Samples", expanded=False):
                    sample_customers = df[df['Cluster'] == selected_cluster].sample(min(5, len(df[df['Cluster'] == selected_cluster])))
                    st.dataframe(sample_customers[['Customer_ID', 'Age', 'Gender', 'Annual_Income', 'Total_Spent', 'Preferred_Style', 'Last_Purchase_Category']])

if __name__ == "__main__":
    main()