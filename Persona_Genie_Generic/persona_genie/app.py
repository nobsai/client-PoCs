import streamlit as st
import pandas as pd
import os
import time
import io
import concurrent.futures
import threading
import base64
from PIL import Image
from dotenv import load_dotenv

# Load local modules
from utils.data_generator import generate_sample_dataset
from utils.data_processor import load_data, group_by_customer, get_customer_stats, export_profiles
from agents.crew import CustomerProfilerCrew
from components.profile_card import render_profile_card, render_filter_sidebar

# Set a timeout for profile generation (seconds)
PROFILE_TIMEOUT = 120

# Function to load and encode images
def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Logo path
#logo_path = os.path.join(os.path.dirname(__file__), "images", "LOGO-AFHQ-4.png")

# Page configuration
st.set_page_config(
    page_title="Customer Persona Genie",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for luxury aesthetics with enhanced design
st.markdown(f"""
<style>
    /* Main background with subtle texture */
    .stApp {{
        background-color: #FFFFFF;
        background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23f0f0f0' fill-opacity='0.2' fill-rule='evenodd'/%3E%3C/svg%3E");
    }}
    
    /* Header with logo styling */
    .header-container {{
        display: flex;
        align-items: center;
        padding: 1rem 0;
        border-bottom: 1px solid #F0F0F0;
        margin-bottom: 2rem;
        background-color: #FFFFFF;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }}
    
    .logo-container {{
        margin-right: 20px;
    }}
    
    .logo-container img {{
        height: 60px;
    }}
    
    .header-text {{
        flex-grow: 1;
    }}
    
    /* Headers */
    h1, h2, h3 {{
        font-family: 'Playfair Display', serif;
        color: #1E293B;
        letter-spacing: 0.5px;
    }}
    
    h1 {{
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #1E293B, #4F6C92);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    h2 {{
        font-size: 1.8rem;
        margin-top: 2rem;
        position: relative;
        padding-bottom: 0.5rem;
    }}
    
    h2:after {{
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 40px;
        height: 3px;
        background: #D4AF37;
    }}
    
    /* Text */
    p, li {{
        font-family: 'Roboto', sans-serif;
        color: #333333;
        line-height: 1.6;
    }}
    
    /* Quote blocks */
    blockquote {{
        border-left: 4px solid #D4AF37 !important;
        background-color: #FFFBF2;
        padding: 15px;
        font-style: italic;
        color: #3A3A3A;
        margin: 1.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    
    /* Dividers */
    hr {{
        border: none;
        height: 1px;
        background: linear-gradient(to right, rgba(212, 175, 55, 0.1), rgba(212, 175, 55, 0.5), rgba(212, 175, 55, 0.1));
        margin: 2.5rem 0;
    }}
    
    /* Buttons */
    .stButton>button {{
        background-color: #FFFFFF;
        color: #1E293B;
        border: 1px solid #D4AF37;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-family: 'Roboto', sans-serif;
        font-weight: 500;
        transition: all 0.3s ease;
    }}
    
    .stButton>button:hover {{
        background-color: #FFFBF2;
        border: 1px solid #B8860B;
        transform: translateY(-1px);
        box-shadow: 0 2px 5px rgba(184, 134, 11, 0.1);
    }}
    
    /* Cards with soft shadows and rounded corners */
    .profile-card {{
        background-color: white;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid #F0F0F0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    
    .profile-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    }}
    
    /* Sidebar */
    .css-1d391kg, .css-1cypcdb {{
        background-color: #FAFAFA;
    }}
    
    /* Expander styling */
    .streamlit-expanderHeader {{
        font-family: 'Roboto', sans-serif;
        font-weight: 500;
        color: #1E293B !important;
        background-color: #F8F9FA;
        border-radius: 4px;
    }}
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        padding: 10px 20px;
        border-radius: 4px 4px 0 0;
    }}
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {{
        background-color: #D4AF37;
    }}
    
    /* Alert and info boxes */
    .stAlert {{
        border-radius: 4px;
        border-width: 1px;
    }}
    
    /* Luxury gold accents */
    .gold-accent {{
        color: #D4AF37;
        font-weight: 500;
    }}
    
    /* Data preview table styling */
    .dataframe {{
        font-family: 'Roboto', sans-serif;
        font-size: 0.9rem;
        border-collapse: collapse;
    }}
    
    .dataframe th {{
        background-color: #F8F9FA;
        color: #1E293B;
        font-weight: 500;
        padding: 8px;
        text-align: left;
        border-bottom: 2px solid #E0E0E0;
    }}
    
    .dataframe td {{
        padding: 8px;
        border-bottom: 1px solid #F0F0F0;
    }}
    
    /* File uploader styling */
    .uploadedFile {{
        border: 1px solid #E0E0E0;
        border-radius: 4px;
        padding: 5px;
    }}
    
    /* Custom checkbox styling */
    .stCheckbox {{
        color: #1E293B;
    }}
    
    /* Tooltip styling */
    .stTooltip {{
        font-family: 'Roboto', sans-serif;
        color: #333333;
    }}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'profiles' not in st.session_state:
    st.session_state.profiles = []

if 'data' not in st.session_state:
    st.session_state.data = None

if 'file_uploaded' not in st.session_state:
    st.session_state.file_uploaded = False

if 'profile_timeout' not in st.session_state:
    st.session_state.profile_timeout = PROFILE_TIMEOUT

if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = ""

# Function to generate a profile with timeout
def generate_profile_with_timeout(profiler, customer_id, orders, timeout=None):
    """Generate a customer profile with a timeout"""
    if timeout is None:
        timeout = st.session_state.profile_timeout
        
    result = None
    error = None
    
    # Define the target function to run with timeout
    def target():
        nonlocal result, error
        try:
            result = profiler.get_customer_profile(customer_id, orders)
        except Exception as e:
            error = str(e)
            # Check specifically for OpenAI API key errors
            if "openai_api_key" in str(e).lower() or "api key" in str(e).lower():
                error = f"OpenAI API key error: {e}"
    
    # Start thread
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    
    # Wait for timeout
    thread.join(timeout)
    
    # Check if thread is still alive (timeout occurred)
    if thread.is_alive():
        return None, f"Timeout generating profile for {customer_id} after {timeout} seconds"
    
    if error:
        # If it's an API key error, provide more helpful message
        if "api key" in error.lower():
            return None, f"API key error when generating profile for {customer_id}. Please check your OpenAI API key."
        return None, f"Error generating profile for {customer_id}: {error}"
    
    return result, None

# Function to process a batch of customers
def process_customer_batch(profiler, customer_groups, start_idx, end_idx, progress_callback=None):
    """Process a batch of customers and return their profiles"""
    batch_profiles = []
    
    # Get a slice of customers to process
    batch_items = list(customer_groups.items())[start_idx:end_idx]
    
    for i, (customer_id, orders) in enumerate(batch_items):
        # Update progress
        if progress_callback:
            progress_callback(i, len(batch_items), customer_id)
        
        # Generate profile with timeout
        profile, error = generate_profile_with_timeout(profiler, customer_id, orders)
        
        if error:
            st.warning(error)
        
        if profile:
            # Get statistics
            stats = get_customer_stats(orders)
            
            # Add product keywords for wordcloud
            profile['product_keywords'] = stats.get('product_keywords', [])
            
            # Add to profiles list
            batch_profiles.append(profile)
    
    return batch_profiles

# Custom header with logo
def render_header():
    """Render the app header with AlFahim logo"""
    try:
        # Check if logo exists
        logo_path = os.path.join(os.path.dirname(__file__), "images", "LOGO-AFHQ-4.png")
        if os.path.exists(logo_path):
            # Render header container
            st.markdown(
                f"""
                <div class="header-container">
                    <div class="logo-container">
                        <img src="data:image/png;base64,{get_base64_encoded_image(logo_path)}" alt="AlFahim HQ Logo">
                    </div>
                    <div class="header-text">
                        <h1>Customer Persona Genie</h1>
                        <p>Intelligent Customer Profiling Solution</p>
                    </div>
                </div>
                """, 
                unsafe_allow_html=True
            )
        else:
            # Fallback to text-only header
            st.title("💎 Customer Persona Genie")
            st.markdown("### Intelligent Customer Profiling")
    except Exception as e:
        # Fallback in case of any errors
        st.title("💎 Customer Persona Genie")
        st.markdown("### Intelligent Customer Profiling")

# Render header
render_header()
st.markdown("---")

# Sidebar for API key, data loading and filtering
with st.sidebar:
    st.markdown("## API Configuration")
    
    # Add OpenAI API key input
    openai_api_key = st.text_input(
        "OpenAI API Key",
        value=st.session_state.openai_api_key,
        type="password",
        help="Enter your OpenAI API key to enable AI-powered profile generation"
    )
    
    # Save API key to session state only
    if openai_api_key:
        st.session_state.openai_api_key = openai_api_key
        st.success("✅ API key saved")
    
    st.markdown("---")
    st.markdown("## Data Source")
    
    # Option to upload or generate data
    data_option = st.radio(
        "Choose data source:",
        ["Upload Customer Data", "Generate Sample Data"]
    )
    
    if data_option == "Upload Customer Data":
        uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx", "xls"])
        
        if uploaded_file is not None:
            try:
                file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                
                if file_ext == '.csv':
                    data = pd.read_csv(uploaded_file)
                elif file_ext in ['.xlsx', '.xls']:
                    data = pd.read_excel(uploaded_file)
                
                st.session_state.data = data
                st.session_state.file_uploaded = True
                st.success(f"File uploaded successfully! {len(data)} rows loaded.")
            except Exception as e:
                st.error(f"Error: {e}")
    
    elif data_option == "Generate Sample Data":
        st.markdown("#### Sample Data Parameters")
        
        n_customers = st.slider("Number of Customers", 5, 100, 50)
        n_orders = st.slider("Number of Orders", 50, 300, 200)
        
        if st.button("Generate Sample Data"):
            with st.spinner("Generating sample data..."):
                data = generate_sample_dataset(n_customers, n_orders)
                st.session_state.data = data
                st.success(f"Sample data generated! {len(data)} rows created.")
    
    # Render filters
    if st.session_state.data is not None:
        st.markdown("---")
        st.markdown("## Filters")
        filters = render_filter_sidebar()
        
        # Add batch size and performance options
        st.markdown("---")
        st.markdown("## Performance Settings")
        batch_size = st.slider("Customers per batch", 1, 10, 5, 
                              help="Process customers in smaller batches to avoid timeouts")
        
        timeout_seconds = st.slider("Profile timeout (seconds)", 30, 300, st.session_state.profile_timeout,
                                   help="Maximum time allowed for analyzing each customer")
        
        # Apply performance settings
        if st.button("Apply Settings"):
            st.session_state.profile_timeout = timeout_seconds
            st.success(f"Settings applied: {batch_size} customers per batch, {timeout_seconds}s timeout")

# Main content area
if st.session_state.file_uploaded or (st.session_state.data is not None):
    # Create tabs for different sections
    tab1, tab2 = st.tabs(["Data & Generation", "Customer Profiles"])
    
    with tab1:
        # Data preview section
        st.subheader("Data Preview")
        st.dataframe(st.session_state.data.head(10), use_container_width=True)
        
        # Data statistics
        if st.session_state.data is not None:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Orders", len(st.session_state.data))
            with col2:
                st.metric("Unique Customers", st.session_state.data['CustomerID'].nunique())
            with col3:
                st.metric("Total Revenue", f"${st.session_state.data['Price'].sum():.2f}")
        
        st.markdown("---")
        
        # Check if API key is provided
        if not st.session_state.openai_api_key:
            st.warning("⚠️ Please enter your OpenAI API key in the sidebar to generate profiles")
        else:
            # Generate profiles button with enhanced styling
            st.markdown("<h2>Generate Customer Profiles</h2>", unsafe_allow_html=True)
            st.markdown(
                """
                Click the button below to analyze customer data and generate intelligent persona profiles.
                This process uses AI agents to derive insights about style preferences, lifestyle traits, and purchasing patterns.
                """
            )
            
            if st.button("Generate Customer Profiles", key="generate_profiles_btn"):
                # Verify API key format
                if not st.session_state.openai_api_key.startswith(('sk-', 'org-')):
                    st.error("❌ The API key provided doesn't appear to be valid. Please check your OpenAI API key.")
                else:
                    # Group data by customer
                    customer_groups = group_by_customer(st.session_state.data)
                    
                    # Initialize profiler crew with API key
                    profiler = CustomerProfilerCrew(verbose=False, api_key=st.session_state.openai_api_key)
                    
                    # Set up progress tracking with enhanced styling
                    progress_container = st.container()
                    with progress_container:
                        st.markdown("<h3>Analysis Progress</h3>", unsafe_allow_html=True)
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        result_area = st.empty()
                    
                    # Function to update progress
                    def update_progress(i, total, customer_id):
                        status_text.markdown(f"Analyzing customer **{i+1}/{total}**: `{customer_id}`")
                        progress_bar.progress((i + 1) / total)
                    
                    # Process customers in batches
                    profiles = []
                    total_customers = len(customer_groups)
                    api_key_error_count = 0
                    
                    # Get batch size from sidebar or default
                    if 'batch_size' not in locals():
                        batch_size = 5
                    
                    # Determine number of batches
                    num_batches = (total_customers + batch_size - 1) // batch_size
                    
                    for batch_idx in range(num_batches):
                        start_idx = batch_idx * batch_size
                        end_idx = min(start_idx + batch_size, total_customers)
                        
                        result_area.info(f"Processing batch {batch_idx+1}/{num_batches} (customers {start_idx+1}-{end_idx})")
                        
                        # Process this batch
                        batch_profiles = process_customer_batch(
                            profiler,
                            customer_groups,
                            start_idx,
                            end_idx,
                            lambda i, t, cid: update_progress(start_idx + i, total_customers, cid)
                        )
                        
                        # Check for consistent API key errors
                        if batch_idx == 0 and len(batch_profiles) == 0:
                            api_key_error_msg = st.error("❌ No profiles were generated in the first batch. This is likely due to API key issues. Please check your OpenAI API key and try again.")
                            break
                        
                        # Add to overall profiles
                        profiles.extend(batch_profiles)
                        
                        # Update overall progress
                        progress_bar.progress(end_idx / total_customers)
                        
                        # Show interim results
                        result_area.success(f"Batch {batch_idx+1} complete: Generated {len(batch_profiles)} profiles")
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Save to session state
                    st.session_state.profiles = profiles
                    
                    if not profiles:
                        result_area.error("❌ No profiles were generated. Please check your OpenAI API key and try again.")
                    else:
                        # Final success message with enhanced styling
                        result_area.markdown(
                            f"""
                            <div style="padding: 1rem; background-color: #F0FFF4; border-left: 4px solid #38A169; border-radius: 4px;">
                                <h3 style="margin-top: 0; color: #38A169;">Analysis Complete!</h3>
                                <p>Successfully generated <span class="gold-accent">{len(profiles)}</span> customer profiles out of {total_customers} customers.</p>
                                <p>Switch to the <b>Customer Profiles</b> tab to view detailed personas.</p>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
    
    with tab2:
        # Display profiles
        if st.session_state.profiles:
            # Export button
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("Export Profiles to CSV"):
                    # Export profiles to CSV
                    output_path = os.path.join("data", "customer_profiles.csv")
                    export_path = export_profiles(st.session_state.profiles, output_path)
                    st.success(f"Profiles exported to {export_path}")
            
            # Profile summary
            st.markdown(
                f"""
                <h2>Customer Profiles</h2>
                <p>Showing <span class="gold-accent">{len(st.session_state.profiles)}</span> personalized customer profiles generated through AI analysis.</p>
                """,
                unsafe_allow_html=True
            )
            
            # Display profile cards with enhanced styling
            for profile in st.session_state.profiles:
                with st.container():
                    st.markdown('<div class="profile-card">', unsafe_allow_html=True)
                    render_profile_card(profile)
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No profiles generated yet. Go to the 'Data & Generation' tab and click 'Generate Customer Profiles'.")

else:
    # Welcome message when no data is loaded
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 1rem;">
            <h2>Welcome to Customer Persona Genie</h2>
            <p style="font-size: 1.1rem; margin-bottom: 2rem;">
                Discover deeper insights into your customers through AI-powered profile analysis.
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # API key input in main area as well
    if not st.session_state.openai_api_key:
        st.warning("⚠️ To get started, please enter your OpenAI API key in the sidebar")
    
    # Feature overview with columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            """
            <div style="text-align: center; padding: 1rem;">
                <h3>💾 Data Handling</h3>
                <p>Upload your customer data or generate synthetic luxury retail data instantly.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            """
            <div style="text-align: center; padding: 1rem;">
                <h3>🧠 AI Analysis</h3>
                <p>Leverage specialized AI agents to uncover style preferences, brand affinities, and lifestyle traits.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            """
            <div style="text-align: center; padding: 1rem;">
                <h3>📊 Rich Insights</h3>
                <p>View elegant customer archetypes and narratives that reveal the essence of each customer.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # Getting started section
    st.markdown(
        """
        <h2>Getting Started</h2>
        <ol>
            <li><b>Enter your OpenAI API key</b> - Provide your API key in the sidebar to enable AI analysis</li>
            <li><b>Select data source</b> - Upload your CSV/Excel file or generate sample data using the sidebar</li>
            <li><b>Generate profiles</b> - Analyze customer data to create detailed persona profiles</li>
            <li><b>Explore insights</b> - Browse customer archetypes, style preferences, and narrative descriptions</li>
            <li><b>Export results</b> - Save generated profiles for presentations or further analysis</li>
        </ol>
        """, 
        unsafe_allow_html=True
    )
    
    # Sample image with caption
    st.image("https://images.unsplash.com/photo-1541597455068-49e3562bdfa4?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80", 
             caption="Luxury retail analytics powered by AI")

if __name__ == "__main__":
    # Run the app
    pass 
