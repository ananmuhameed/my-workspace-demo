import io
import re
import zipfile
from pathlib import Path
import pandas as pd
import streamlit as st
from docxtpl import DocxTemplate

st.set_page_config(page_title="Word Generator | My Workspace",page_icon="📄",layout="wide")
from demo_store import banner
banner()
st.title("📄 Word Generator")
st.write("Upload an Excel file and a Word template (.docx). Each Excel row generates one Word document.")
st.info("Use column names as template variables in {{ double braces }}. Spaces in headers become underscores.")
excel=st.file_uploader("Excel data file",type=["xlsx"],key="word_excel")
word=st.file_uploader("Word template",type=["docx"],key="word_template")
if excel and word:
    try:
        if len(excel.getvalue()) > 5 * 1024 * 1024 or len(word.getvalue()) > 5 * 1024 * 1024:
            raise ValueError("Demo files must be 5 MB or smaller.")
        df=pd.read_excel(excel,dtype=str).fillna("")
        if len(df)>100:
            raise ValueError("Demo limit: 100 Word documents per batch.")
        df.columns=[re.sub(r"\W+","_",str(c).strip(),flags=re.UNICODE).strip("_") for c in df.columns]
        if len(set(df.columns))!=len(df.columns):
            st.error("Column names must be unique after normalization.")
            st.stop()
        st.write("Available Word variables:")
        st.code("  ".join("{{ "+col+" }}" for col in df.columns))
        st.dataframe(df.head(10),hide_index=True,use_container_width=True)
        if st.button("Generate Word files",type="primary"):
            if df.empty:
                st.warning("The Excel file contains no data rows.")
            else:
                output=io.BytesIO()
                with zipfile.ZipFile(output,"w",zipfile.ZIP_DEFLATED) as archive:
                    for i, row in df.iterrows():
                        doc=DocxTemplate(io.BytesIO(word.getvalue()))
                        doc.render({k:str(v) for k,v in row.to_dict().items()})
                        result=io.BytesIO()
                        doc.save(result)
                        archive.writestr(f"document_{i+1:03d}.docx",result.getvalue())
                st.download_button("⬇️ Download Word files (ZIP)",output.getvalue(),"generated_documents.zip",mime="application/zip")
                st.success(f"Generated {len(df)} Word documents.")
    except Exception as exc:
        st.error(f"Could not process the files: {exc}")
