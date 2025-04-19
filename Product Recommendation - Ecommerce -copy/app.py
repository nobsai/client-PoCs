import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv("fictitious_dataset.csv")
    df['time_stamp'] = pd.to_datetime(df['time_stamp'])
    return df

df = load_data()

# Process the data
NOW = df['time_stamp'].max()
rfmTable = df.groupby('card_name').agg({
    'time_stamp': lambda x: (NOW - x.max()).days,
    'product_id': lambda x: len(x),
    'price': lambda x: x.sum()
})
rfmTable['time_stamp'] = rfmTable['time_stamp'].astype(int)
rfmTable.rename(columns={'time_stamp': 'recency', 
                         'product_id': 'frequency',
                         'price': 'monetary_value'}, inplace=True)

rfmTable['r_quartile'] = pd.qcut(rfmTable['recency'], q=4, labels=range(1, 5), duplicates='raise')
rfmTable['f_quartile'] = pd.qcut(rfmTable['frequency'], q=4, labels=range(1, 5), duplicates='drop')
rfmTable['m_quartile'] = pd.qcut(rfmTable['monetary_value'], q=4, labels=range(1, 5), duplicates='drop')
rfm_data = rfmTable.reset_index()

rfm_data['r_quartile'] = rfm_data['r_quartile'].astype(str)
rfm_data['f_quartile'] = rfm_data['f_quartile'].astype(str)
rfm_data['m_quartile'] = rfm_data['m_quartile'].astype(str)
rfm_data['RFM_score'] = rfm_data['r_quartile'] + rfm_data['f_quartile'] + rfm_data['m_quartile']

# Assign customer segments
rfm_data['customer_segment'] = 'Other'
rfm_data.loc[rfm_data['RFM_score'].isin(['334', '443', '444', '344', '434', '433', '343', '333']), 'customer_segment'] = 'Premium Customer'
rfm_data.loc[rfm_data['RFM_score'].isin(['244', '234', '232', '332', '143', '233', '243']), 'customer_segment'] = 'Repeat Customer'
rfm_data.loc[rfm_data['RFM_score'].isin(['424', '414', '144', '314', '324', '124', '224', '423', '413', '133', '323', '313', '134']), 'customer_segment'] = 'Top Spender'
rfm_data.loc[rfm_data['RFM_score'].isin(['422', '223', '212', '122', '222', '132', '322', '312', '412', '123', '214']), 'customer_segment'] = 'At Risk Customer'
rfm_data.loc[rfm_data['RFM_score'].isin(['411', '111', '113', '114', '112', '211', '311']), 'customer_segment'] = 'Inactive Customer'

# Merge customer segments with the main dataset
df = pd.merge(df, rfm_data[['card_name', 'customer_segment']], on='card_name', how='left')

# Get all unique customer names
customer_names = df['card_name'].unique().tolist()

# Recommendation Function
def generate_recommendations(target_customer, cohort, num_recommendations=5):
    user_item_matrix = cohort.groupby('card_name')['product'].apply(lambda x: ', '.join(x)).reset_index()
    user_item_matrix['product_descriptions'] = cohort.groupby('card_name')['product_description'].apply(lambda x: ', '.join(x)).reset_index()['product_description']
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(user_item_matrix['product_descriptions'])
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    target_customer_index = user_item_matrix[user_item_matrix['card_name'] == target_customer].index[0]
    similar_customers = similarity_matrix[target_customer_index].argsort()[::-1][1:num_recommendations+1]
    target_customer_purchases = set(user_item_matrix[user_item_matrix['card_name'] == target_customer]['product'].iloc[0].split(', '))

    recommendations = []
    for customer_index in similar_customers:
        customer_purchases = set(user_item_matrix.iloc[customer_index]['product'].split(', '))
        new_items = customer_purchases.difference(target_customer_purchases)
        recommendations.extend(new_items)
    
    return list(set(recommendations))[:num_recommendations]

# Streamlit Interface
st.title("Customer Recommendation System with Segmentation")

# Display first few rows of the dataset
st.subheader("Dataset Preview")
st.write("First few rows of the dataset:")
st.dataframe(df.head())

# Run button to trigger chart and recommendations
if st.button("Run Analysis"):
    # Display customer segment distribution chart
    st.subheader("Customer Segment Distribution")
    segment_counts = df['customer_segment'].value_counts()
    plt.figure(figsize=(10, 6))
    segment_counts.plot(kind='bar')
    plt.title('Customer Segment Distribution')
    plt.xlabel('Customer Segment')
    plt.ylabel('Number of Customers')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('segment_distribution.png')
    st.image('segment_distribution.png')

    # Dropdown to select customer
    st.subheader("Customer Recommendations")
    st.write("Select a Customer to view their segment and product recommendations.")
    selected_customer = st.selectbox("Select a Customer", customer_names)

    if selected_customer:
        # Display customer segment
        customer_segment = df[df['card_name'] == selected_customer]['customer_segment'].iloc[0]
        st.subheader(f"Customer Segment for {selected_customer}: {customer_segment}")

        # Generate recommendations
        recommendations = generate_recommendations(selected_customer, df, num_recommendations=3)
        
        st.subheader(f"Product Recommendations for {selected_customer}:")
        if recommendations:
            for product in recommendations:
                product_data = df[df['product'] == product].iloc[0]
                st.write(f"**Product Name:** {product_data['product']}")
                st.write(f"**Description:** {product_data['product_description']}")
                st.write(f"**Price:** ${product_data['price']}")
                st.markdown("---")
        else:
            st.write("No recommendations available.")