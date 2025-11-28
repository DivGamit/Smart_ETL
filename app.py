
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO


def perform_etl(file_name, file_bytes):
    
    if file_name.endswith('.csv'):
        df = pd.read_csv(BytesIO(file_bytes))
    else:
        df = pd.read_excel(BytesIO(file_bytes))

    original_rows = len(df)

    
    df.columns = df.columns.str.strip()
    df.drop_duplicates(inplace=True)

    
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            df[col].fillna(df[col].mean(), inplace=True)
        else:
            mode_val = df[col].mode()
            df[col].fillna(mode_val[0] if not mode_val.empty else "Unknown", inplace=True)

    
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    summary = {
        "Original rows": original_rows,
        "Final rows": len(df),
        "Duplicates removed": original_rows - len(df),
    }
    return df, output, summary


st.set_page_config(page_title="Smart ETL")
st.title("Smart Data Cleaner")
st.caption("Upload CSV/Excel → Get perfectly cleaned file instantly")

uploaded_file = st.file_uploader("Drop your file here", type=["csv", "xlsx", "xls"])

if uploaded_file:
    if st.button("Clean My Data", type="primary", use_container_width=True):
        with st.spinner("Working..."):
            clean_df, excel_file, summary = perform_etl(uploaded_file.name, uploaded_file.getvalue())

        st.success("Cleaned successfully!")
        col1, col2 = st.columns(2)
        col1.metric("Original rows", summary["Original rows"])
        col2.metric("Final rows", summary["Final rows"])
        st.write(f"Duplicates rows removed: {summary['Duplicates removed']}")
        missing_count = clean_df.isnull().sum().sum()
        if missing_count == 0:
            st.success("All missing values successfully filled!")
        else:
            st.error(f"{missing_count} missing values could not be filled")

        st.download_button(
            label="Download Cleaned Excel",
            data=excel_file,
            file_name="CLEANED-" + uploaded_file.name.rsplit('.', 1)[0] + ".xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        with st.expander("Preview first 50 rows"):
            st.dataframe(clean_df.head(50))