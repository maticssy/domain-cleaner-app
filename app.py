import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import StringIO

def extract_filename_parts(filename):
    """Extract prefix and date from filename like 'd3 16.6.csv'"""
    name = os.path.splitext(filename)[0]  # remove .csv
    parts = name.split()
    if len(parts) != 2:
        st.error("Filename format should be like 'd3 16.6.csv'")
        return None, None
    return parts[0], parts[1]

def split_dataframe(df, chunk_size):
    """Split DataFrame into list of DataFrames with chunk_size rows each"""
    return [df.iloc[i:i + chunk_size].reset_index(drop=True) for i in range(0, len(df), chunk_size)]

st.title("🧹 Domain List Cleaner")

uploaded_file = st.file_uploader("Upload your raw CSV file", type=["csv"])

if uploaded_file:
    try:
        # Load with headers
        df = pd.read_csv(uploaded_file)

        # Identify domain column
        if "Company Website" not in df.columns:
            st.error("No column named 'Company Website' found in the file.")
        else:
            # Extract and clean domain column
            domain_series = df["Company Website"].dropna().astype(str).str.strip()
            domain_df = pd.DataFrame(domain_series)
            domain_df.columns = ["Company Website"]  # Ensure column name

            # Split into chunks of 500
            chunks = split_dataframe(domain_df, 500)

            # File naming
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
