import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
import base64
from PIL import Image
import io
import random

def get_avatar_emoji():
    """Get a random luxury/fashion related emoji for profile avatars"""
    emojis = ["👑", "💎", "🕶️", "👔", "👗", "👜", "👞", "⌚", "🧣", "🧥", "🌟", "✨", "💫", "🔱", "📱"]
    return random.choice(emojis)

def get_luxury_color():
    """Get a random luxury-palette color for UI elements"""
    colors = [
        "#F8F9FA",  # White Smoke
        "#E6E6FA",  # Lavender
        "#F0F8FF",  # Alice Blue
        "#FFFAF0",  # Floral White
        "#F5F5DC",  # Beige
        "#FFDAB9",  # Peach
    ]
    return random.choice(colors)

def generate_wordcloud(keywords):
    """Generate a word cloud from keywords"""
    if not keywords:
        return None
        
    # Count keyword frequencies
    word_freq = {}
    for word in keywords:
        if word.lower() in ['the', 'and', 'of', 'a', 'an']:
            continue
        word_freq[word] = word_freq.get(word, 0) + 1
    
    if not word_freq:
        return None
    
    # Generate wordcloud with luxury colors
    luxury_colormap = plt.cm.RdYlBu
    
    # Fix: Create a color function that returns integers, not floats
    def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        return plt.cm.Paired(random.randint(0, 9))
    
    wc = WordCloud(
        background_color=get_luxury_color(),
        max_words=30,
        width=400,
        height=200,
        contour_width=1,
        contour_color='#E0E0E0',
        colormap='Pastel1',
        prefer_horizontal=0.9,
        font_path=None,  # Use default font
        max_font_size=None,
        min_font_size=10,
        relative_scaling=0.5
    ).generate_from_frequencies(word_freq)
    
    # Convert to image
    fig, ax = plt.subplots(figsize=(5, 2))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    plt.tight_layout()
    
    # Convert to bytes
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', dpi=300, bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    img_buf.seek(0)
    
    return img_buf

def render_profile_card(profile):
    """Render a customer profile card in Streamlit"""
    # Card layout
    col1, col2 = st.columns([1, 3])
    
    # Avatar and basic info
    with col1:
        st.markdown(f"<h1 style='text-align: center; font-size: 48px; margin-bottom: 10px;'>{get_avatar_emoji()}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; margin-top: 0;'>{profile['customer_id']}</h3>", unsafe_allow_html=True)
        
        # Stats with gold accent
        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 20px;">
                <p style="margin: 8px 0;"><b>Orders:</b> <span class="gold-accent">{profile['order_count']}</span></p>
                <p style="margin: 8px 0;"><b>Spent:</b> <span class="gold-accent">${profile['total_spent']:,.2f}</span></p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Brand tags
        st.markdown("<p style='text-align: center; font-size: 0.9em; color: #666;'><b>Top Brands</b></p>", unsafe_allow_html=True)
        for brand in profile['favorite_brands'][:2]:
            st.markdown(
                f"""
                <div style='text-align: center; margin: 5px 0;'>
                    <span style='background-color: #F8F9FA; padding: 3px 8px; border-radius: 12px; font-size: 0.8em;'>
                        {brand}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # Main profile content
    with col2:
        # Archetype
        st.markdown(f"### {profile['archetype']}")
        
        # Persona summary
        st.markdown(f"> {profile['persona']}")
        
        # Expandable sections
        with st.expander("Style Analysis"):
            st.markdown(profile['style_analysis'])
        
        with st.expander("Lifestyle Traits"):
            st.markdown(profile['lifestyle_analysis'])
        
        with st.expander("Purchase Preferences"):
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("#### Color Palette")
                for color in profile['favorite_colors'][:3]:
                    st.markdown(f"- {color}")
            
            with col_b:
                st.markdown("#### Categories")
                for category in profile['favorite_categories'][:3]:
                    st.markdown(f"- {category}")
        
        # Word cloud from purchase keywords
        if 'product_keywords' in profile and profile['product_keywords']:
            try:
                with st.expander("Purchase Keywords"):
                    wordcloud_img = generate_wordcloud(profile['product_keywords'])
                    if wordcloud_img:
                        st.image(wordcloud_img)
            except Exception as e:
                st.warning(f"Could not generate wordcloud: {e}")

def render_filter_sidebar():
    """Render the filter sidebar for customer profiles"""
    # Expandable filter sections
    with st.expander("By Style", expanded=False):
        style_filters = {
            "Minimalist": st.checkbox("Minimalist"),
            "Luxury": st.checkbox("Luxury"),
            "Casual": st.checkbox("Casual"),
            "Streetwear": st.checkbox("Streetwear"),
            "Classic": st.checkbox("Classic")
        }
    
    with st.expander("By Category", expanded=False):
        category_filters = {
            "Footwear": st.checkbox("Footwear"),
            "Apparel": st.checkbox("Apparel"),
            "Accessories": st.checkbox("Accessories"),
            "Automotive Gear": st.checkbox("Automotive Gear")
        }
    
    with st.expander("By Price Range", expanded=False):
        price_range = st.slider("Total Spend ($)", 0, 10000, (0, 10000))
    
    # Filter actions
    col1, col2 = st.columns(2)
    with col1:
        apply_button = st.button("Apply Filters")
    with col2:
        reset_button = st.button("Reset")
    
    return {
        "styles": {k: v for k, v in style_filters.items() if v},
        "categories": {k: v for k, v in category_filters.items() if v},
        "price_range": price_range,
        "apply": apply_button,
        "reset": reset_button
    } 