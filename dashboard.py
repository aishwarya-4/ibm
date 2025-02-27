import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scispacy
import spacy
from scispacy.linking import EntityLinker

# Load ScispaCy model and UMLS linker
@st.cache_resource
def load_model():
    nlp = spacy.load("en_core_sci_md")
    linker = EntityLinker(resolve_abbreviations=True, name="umls")
    nlp.add_pipe(linker)
    return nlp, linker

nlp, linker = load_model()

# Medical term extractor using ScispaCy
def extract_medical_terms(text):
    doc = nlp(text)
    medical_terms = []
    for entity in doc.ents:
        for umls_ent in entity._.umls_ents:
            concept_id, _ = umls_ent
            preferred_name = linker.kb.cui_to_entity[concept_id].canonical_name
            medical_terms.append(preferred_name)
    return ", ".join(set(medical_terms)) if medical_terms else "No medical terms found"

# Data cleaning function
def clean_data(df):
    df["SUGGESTED_DIAGNOSIS"] = df["TEXT"].apply(extract_medical_terms)
    return df

# Streamlit app layout
st.title("🩺 Automated Healthcare Data Cleaning Dashboard")

# Upload dataset
uploaded_file = st.file_uploader(r"C:\Users\PAVANI\OneDrive\Desktop\IBM Project\dataset\health prescription data.csv", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Show raw data
    st.subheader("📊 Raw Data Preview")
    st.write(df.head())

    # Clean the data
    if st.button("🧹 Clean Data with ScispaCy"):
        df_cleaned = clean_data(df)

        # Display cleaned data
        st.subheader("✅ Cleaned Data Preview")
        st.write(df_cleaned.head())

        # Download cleaned data
        csv = df_cleaned.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Cleaned Data", csv, "cleaned_healthcare_data.csv", "text/csv")

        # Diagnosis distribution
        st.subheader("📈 Diagnosis Distribution")
        if "DIAGNOSIS" in df.columns:
            plt.figure(figsize=(10, 5))
            sns.countplot(y=df["DIAGNOSIS"], order=df["DIAGNOSIS"].value_counts().index, palette="viridis")
            st.pyplot(plt)

        # Anomaly detection insight
        st.subheader("📌 Suggested Diagnoses")
        st.write(df_cleaned[["TEXT", "SUGGESTED_DIAGNOSIS"]].head(10))

# Instructions
st.sidebar.header("🛠️ Instructions")
st.sidebar.info(
    """
1. Upload your healthcare dataset (CSV).  
2. Click 'Clean Data' to process using **ScispaCy**.  
3. Download the cleaned dataset.  
4. View diagnosis insights & anomalies.  
"""
)
