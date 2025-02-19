import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import time

st.set_page_config(page_title="🚀 DataSwift", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style> 
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;600&display=swap');
    * { font-family: 'Poppins', sans-serif; }
    body { background: linear-gradient(135deg, #2b5876, #4e4376); color: #ffffff; }
    .main { background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 10px; backdrop-filter: blur(10px); box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.2); }
    h1, h2, h3 { text-align: center; color: #00d2ff; }
    .stButton > button, .stDownloadButton > button { 
        color: white !important; 
        transition: all 0.3s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover { 
        transform: scale(1.05); 
        color: white !important;
    }
    .sidebar .sidebar-content { background: rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px; }
    .stProgress > div > div > div { background-color: #00d2ff; }
</style>
""", unsafe_allow_html=True)

st.title("🚀 DataSwift - The Ultimate Data Playground!")

st.sidebar.title("⚙️ Settings")
st.sidebar.write("📥 **Upload CSV / Excel Files Below:**")
uploaded_files = st.sidebar.file_uploader("📂 Upload Files", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[1].lower()

        with st.spinner(f"⏳ Processing `{file.name}`... Please wait..."):
            time.sleep(2)

        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"❌ Unsupported file type: {file_ext}")
            continue

        st.subheader(f"📄 File: `{file.name}` ({file.size / 1024:.2f} KB)")

        with st.expander("📜 **Quick Preview of Data**"):
            st.write("📝 **First 5 Rows of Data:**")
            st.dataframe(df.head())
            st.write("📊 **Column Overview:**", df.describe().T.style.set_properties(**{"background-color": "#222", "color": "white"}))

        with st.expander("🧹 **Data Cleaning & Processing**"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"🗑 Remove Duplicates ({file.name})"):
                    df.drop_duplicates(inplace=True)
                    st.success("✅ Duplicates Removed!")

                drop_cols = st.multiselect("📌 Drop Columns", df.columns)
                if drop_cols:
                    df.drop(columns=drop_cols, inplace=True)
                    st.success(f"✅ Dropped Columns: {drop_cols}")

            with col2:
                if st.button(f"📌 Fill Missing Values ({file.name})"):
                    numeric_cols = df.select_dtypes(include=["number"]).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.success("✅ Missing Values Filled with Mean!")

                fill_value = st.text_input("✏️ Fill Missing Values with Custom Value:")
                if fill_value:
                    df.fillna(fill_value, inplace=True)
                    st.success(f"✅ Missing values replaced with `{fill_value}`")

        with st.expander("🔍 **Search & Filter Data**"):
            search_col = st.selectbox("🔎 Choose column to search", df.columns)
            search_val = st.text_input(f"🔎 Search {search_col}")
            if search_val:
                df = df[df[search_col].astype(str).str.contains(search_val, case=False)]
                st.dataframe(df)

        with st.expander("📊 **Advanced Data Visualization**"):
            numeric_cols = df.select_dtypes(include="number").columns
            if len(numeric_cols) > 0:
                chart_type = st.selectbox("📊 Choose Chart Type", [
                    "Bar Chart", "Scatter Plot", "Histogram", "Line Chart", "Box Plot", "Pie Chart", "Area Chart"
                ])

                x_axis = st.selectbox("📌 Select X-Axis", numeric_cols)
                y_axis = st.selectbox("📌 Select Y-Axis", numeric_cols) if len(numeric_cols) > 1 else x_axis

                if chart_type == "Bar Chart":
                    fig = px.bar(df, x=x_axis, y=y_axis)
                elif chart_type == "Scatter Plot":
                    fig = px.scatter(df, x=x_axis, y=y_axis)
                elif chart_type == "Histogram":
                    fig = px.histogram(df, x=x_axis)
                elif chart_type == "Line Chart":
                    fig = px.line(df, x=x_axis, y=y_axis)
                elif chart_type == "Box Plot":
                    fig = px.box(df, x=x_axis, y=y_axis)
                elif chart_type == "Pie Chart":
                    fig = px.pie(df, names=x_axis, values=y_axis)
                elif chart_type == "Area Chart":
                    fig = px.area(df, x=x_axis, y=y_axis)

                st.plotly_chart(fig)
            else:
                st.error("⚠️ No numeric columns available for visualization.")

        with st.expander("🔄 **Convert & Download File**"):
            conversion_type = st.radio(f"🎯 Convert `{file.name}` to:", ["CSV", "Excel", "JSON"], key=file.name)

            if st.button(f"💾 Convert `{file.name}`"):
                buffer = BytesIO()
                new_file_name = file.name.replace(file_ext, f".{conversion_type.lower()}")

                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    mime_type = "text/csv"
                    conversion_success = True
                elif conversion_type == "Excel":
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                        df.to_excel(writer, index=False, sheet_name="Sheet1")
                    buffer.seek(0)

                    new_file_name = file.name.replace(file_ext, ".xlsx")
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    conversion_success = True
                elif conversion_type == "JSON":
                    buffer.write(df.to_json(orient="records").encode("utf-8"))
                    mime_type = "application/json"
                    conversion_success = True

                buffer.seek(0)

                st.download_button(label=f"⬇️ Download `{new_file_name}`", data=buffer, file_name=new_file_name, mime=mime_type)

                if conversion_success:
                    st.success("✅ **File conversion completed successfully!** 🎉")
