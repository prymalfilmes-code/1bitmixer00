import streamlit as st
import numpy as np
from PIL import Image
import random
import io
import zipfile

# --- 1bitmixer00 UI ---
st.set_page_config(page_title="1bitmixer00", layout="centered")
st.title("🕹️ 1bitmixer00")
st.caption("v1.0 | 1-bit Matrix Mixer for Pixel Artists")

# Initialize session state properly
if 'results' not in st.session_state:
    st.session_state.results = []
if 'zip_data' not in st.session_state:
    st.session_state.zip_data = None
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []

st.info("💡 This app runs entirely in your browser using stlite! No server needed.")

# 1. Upload Section
uploaded_files = st.file_uploader(
    "Upload 1-bit PNGs (at least 2)", 
    type=["png"], 
    accept_multiple_files=True
)

# Store uploaded files in session state
if uploaded_files:
    st.session_state.uploaded_files = uploaded_files
    st.success(f"✅ {len(uploaded_files)} images uploaded successfully!")

# 2. Mixing Logic
if st.button("GENERATE 10 MIXES", use_container_width=True):
    if len(st.session_state.uploaded_files) < 2:
        st.error("⚠️ Please upload at least 2 images first!")
    else:
        # Clear previous results
        st.session_state.results = []
        st.session_state.zip_data = None
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            for i in range(10):
                status_text.text(f"🔄 Mixing image {i+1}/10...")
                
                # Pick 2 random images
                f1, f2 = random.sample(st.session_state.uploaded_files, 2)
                
                # Reset file pointers
                f1.seek(0)
                f2.seek(0)
                
                # Open images and convert to 1-bit
                img1 = Image.open(f1).convert('1')
                img2 = Image.open(f2).convert('1')
                
                # Match sizes
                if img1.size != img2.size:
                    img2 = img2.resize(img1.size, Image.NEAREST)
                
                # Convert to numpy arrays
                arr1 = np.array(img1, dtype=bool)
                arr2 = np.array(img2, dtype=bool)
                
                # Perform logical AND (matrix mixing)
                mixed_arr = np.logical_and(arr1, arr2)
                
                # Convert back to image
                res_img = Image.fromarray(mixed_arr).convert('1')
                st.session_state.results.append(res_img)
                
                # Update progress
                progress_bar.progress((i + 1) / 10)
            
            status_text.text("✅ Mixing complete!")
            
            # Create ZIP file
            if st.session_state.results:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                    for idx, img in enumerate(st.session_state.results):
                        img_buffer = io.BytesIO()
                        img.save(img_buffer, format='PNG')
                        img_buffer.seek(0)
                        zip_file.writestr(f'mix_{idx+1:02d}.png', img_buffer.getvalue())
                
                zip_buffer.seek(0)
                st.session_state.zip_data = zip_buffer.getvalue()
                st.success("🎉 10 images mixed successfully! Scroll down to see results.")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Try uploading different PNG files (make sure they're valid 1-bit images)")

# 3. Display Results
if st.session_state.results:
    st.divider()
    st.subheader("🎨 Generated Mixes")
    
    # Display images in a grid
    cols = st.columns(2)
    for idx, img in enumerate(st.session_state.results):
        with cols[idx % 2]:
            st.image(img, caption=f"Mix {idx+1}", use_container_width=True)
    
    # Download buttons
    st.divider()
    
    # ZIP download
    if st.session_state.zip_data:
        st.download_button(
            label="📦 DOWNLOAD ALL AS ZIP",
            data=st.session_state.zip_data,
            file_name="1bitmixer00_results.zip",
            mime="application/zip",
            use_container_width=True
        )
    
    # Individual downloads
    with st.expander("📥 Download individual images"):
        st.write("Click any button to download a specific mix:")
        cols = st.columns(5)
        for idx, img in enumerate(st.session_state.results):
            col_idx = idx % 5
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            with cols[col_idx]:
                st.download_button(
                    label=f"Mix {idx+1}",
                    data=img_buffer,
                    file_name=f"mix_{idx+1:02d}.png",
                    mime="image/png",
                    key=f"dl_{idx}"
                )

# 4. Instructions and Tips
with st.expander("ℹ️ How to use"):
    st.markdown("""
    **1-bit Mixer00** creates artistic combinations of your pixel art!
    
    ### How it works:
    1. Upload at least 2 PNG images (1-bit/black & white recommended)
    2. Click "GENERATE 10 MIXES"
    3. The app randomly pairs images and performs a logical AND operation
    4. Download individual images or all as ZIP
    
    ### Tips:
    - Use 1-bit (black & white) images for best results
    - Images can be different sizes - they'll be automatically matched
    - Each mix is unique and randomly generated
    - Works entirely in your browser - no data is uploaded to any server
    """)

# Footer
st.divider()
st.caption("Made with ❤️ for pixel artists | Runs on stlite in your browser")