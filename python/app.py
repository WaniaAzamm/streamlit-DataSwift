import streamlit as st
import pandas as pd
import os
from io import BytesIO

st.set_page_config(page_title="📊 Swift Data", layout="wide")
st.markdown("""
    <style>
        .main {
            background-color: #f4f4f4;
        }
        h1 {
            color: #007bff;
            text-align: center;
        }
        .stButton > button {
            background-color: #28a745;
            color: white;
            border-radius: 10px;
            width: 100%;
        }
        .stDownloadButton > button {
            background-color: #007bff;
            color: white;
            border-radius: 10px;
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Swift Data")
st.write("🔄 Convert CSV and Excel files with built-in **data cleaning**, **renaming**, and **visualization**!")

uploaded_files = st.file_uploader("📥 Upload your files", type=['csv', 'xlsx'], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[1].lower()

        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"❌ Unsupported file type: {file_ext}")
            continue

        st.write(f"**📄 File Name:** `{file.name}`")
        st.write(f"**📏 File Size:** `{file.size / 1024:.2f} KB`")

        st.write("### 🔍 Data Preview")
        st.dataframe(df.head())

        st.write("### 📈 Summary Statistics")
        st.write(df.describe())

        st.subheader("🛠️ Data Cleaning Options")
        if st.checkbox(f"⚡ Clean Data for `{file.name}`"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"🗑 Remove Duplicates ({file.name})"):
                    df.drop_duplicates(inplace=True)
                    st.write("✅ **Duplicates Removed!**")

                drop_cols = st.multiselect("📌 Drop Columns", df.columns)
                if drop_cols:
                    df.drop(columns=drop_cols, inplace=True)
                    st.write("✅ **Selected Columns Dropped!**")

            with col2:
                if st.button(f"📌 Fill Missing Values ({file.name})"):
                    numeric_cols = df.select_dtypes(include=["number"]).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("✅ **Missing Values Filled!**")

                fill_value = st.text_input("✏️ Fill Missing Values with:")
                if fill_value:
                    df.fillna(fill_value, inplace=True)
                    st.write(f"✅ **Missing values replaced with `{fill_value}`**")

        st.subheader("✏️ Rename Columns")
        new_column_names = {}
        for col in df.columns:
            new_name = st.text_input(f"Rename `{col}`", value=col)
            new_column_names[col] = new_name
        df.rename(columns=new_column_names, inplace=True)

        st.subheader("🎯 Select Columns for Conversion")
        selected_columns = st.multiselect(f"📌 Choose Columns for `{file.name}`", df.columns, default=df.columns)
        df = df[selected_columns]

        st.subheader("📊 Data Visualization")
        if st.checkbox(f"📉 Show Chart for `{file.name}`"):
            numeric_cols = df.select_dtypes(include="number")
            if not numeric_cols.empty:
                chart_type = st.selectbox("📊 Choose Chart Type", ["Bar Chart", "Scatter Plot", "Histogram"])
                if chart_type == "Bar Chart":
                    st.bar_chart(numeric_cols.iloc[:, :2])
                elif chart_type == "Scatter Plot":
                    st.scatter_chart(numeric_cols)
                elif chart_type == "Histogram":
                    st.write("### 📊 Histogram")
                    st.bar_chart(numeric_cols.iloc[:, :1])
            else:
                st.error("⚠️ No numeric columns available for visualization.")

        st.subheader("🔄 Convert & Download File")
        conversion_type = st.radio(f"🎯 Convert `{file.name}` to:", ["CSV", "Excel", "JSON"], key=file.name)

        if st.button(f"💾 Convert `{file.name}`"):
            buffer = BytesIO()
            new_file_name = file.name.replace(file_ext, f".{conversion_type.lower()}")

            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                mime_type = "text/csv"

            if conversion_type == "Excel":
                buffer = BytesIO()  # Ensure a fresh buffer
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Sheet1")
                buffer.seek(0)

                new_file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"



            elif conversion_type == "JSON":
                buffer.write(df.to_json(orient="records").encode("utf-8"))
                mime_type = "application/json"

            buffer.seek(0)

            st.download_button(
                label=f"⬇️ Download `{new_file_name}`",
                data=buffer,
                file_name=new_file_name,
                mime=mime_type
            )

            st.success("✅ **File conversion completed successfully!** 🎉")
