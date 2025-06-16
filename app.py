import streamlit as st
import pandas as pd
import os
from io import StringIO

# Set tab title and layout
st.set_page_config(page_title="Domain List Cleaner", layout="centered")

# App title
st.title("🧹 Domain List Cleaner")

# App description
st.markdown("""
Upload your daily CSV file with company domain data. This app will:
1. Identify the column named `Company Website`
2. Clean and extract valid domains
3. Split the list into separate files of 500 rows max
4. Rename the files based on your uploaded filename
5. Provide separate download links for each file
""")

# Helpers
def extract_filename_parts(filename):
    """Extract prefix and date from filename like 'd3 16.6.csv'"""
    name = os.path.splitext(filename)[0]
    parts = name.split()
    if len(parts) != 2:
        st.error("Filename format should be like 'd3 16.6.csv'")
        return None, None
    return parts[0], parts[1]

def split_dataframe(df, chunk_size):
    return [df.iloc[i:i + chunk_size].reset_index(drop=True) for i in range(0, len(df), chunk_size)]

# Upload CSV
uploaded_file = st.file_uploader("Upload your raw CSV file", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        # Check for the expected column
        if "Company Website" not in df.columns:
            st.error("No column named 'Company Website' found in the file.")
        else:
            # Extract and clean the target column
            domain_series = df["Company Website"].dropna().astype(str).str.strip()
            domain_df = pd.DataFrame(domain_series)
            domain_df.columns = ["Company Website"]

            # Split into chunks of 500
            chunks = split_dataframe(domain_df, 500)

            # Naming based on original file
            prefix, date_part = extract_filename_parts(uploaded_file.name)
            if prefix and date_part:
                if len(chunks) == 1:
                    output_name = f"{prefix} {date_part} clean.csv"
                    st.download_button(
                        label=f"Download cleaned file ({len(domain_df)} rows)",
                        data=chunks[0].to_csv(index=False, header=False),
                        file_name=output_name,
                        mime="text/csv"
                    )
                else:
                    for i, chunk in enumerate(chunks):
                        numbered_name = f"{prefix}.{i+1} {date_part} clean.csv"
                        st.download_button(
                            label=f"Download {numbered_name} ({len(chunk)} rows)",
                            data=chunk.to_csv(index=False, header=False),
                            file_name=numbered_name,
                            mime="text/csv"
                        )
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
