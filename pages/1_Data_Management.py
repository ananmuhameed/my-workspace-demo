import io
import sqlite3
from datetime import date, datetime
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Data Management | My Workspace",page_icon="📊",layout="wide")
st.title("📊 Data Management")
st.caption("Import and manage records using the fixed five-column XLSX or CSV template")
HEADERS=["اسم الجهة","اسم رئيس الجهة","من","الي","نبذة عن السبب"]
LABELS={"entity":"Entity","leader":"Leader (column B)","date_from":"From (column C)","date_to":"To (column D)","reason":"Reason"}
from demo_store import connect, banner
banner()

def load():
    with connect() as con:
        df=pd.read_sql_query("SELECT id,entity,leader,date_from,date_to,reason FROM records ORDER BY id DESC",con)
    for c in ["date_from","date_to"]: df[c]=pd.to_datetime(df[c],errors="coerce").dt.date
    return df

def parse_date(v):
    if pd.isna(v) or str(v).strip()=="": return None
    if isinstance(v,(datetime,date,pd.Timestamp)): return pd.Timestamp(v).date().isoformat()
    if isinstance(v,(int,float)) and not isinstance(v,bool):
        if 1<=v<=2958465: return (pd.Timestamp("1899-12-30")+pd.to_timedelta(v,unit="D")).date().isoformat()
    s=str(v).strip()
    for dayfirst in (True,False):
        try: return pd.to_datetime(s,dayfirst=dayfirst,errors="raise").date().isoformat()
        except (ValueError,TypeError,OverflowError): pass
    raise ValueError(f"Invalid date: {s}")

def filter_data(df,prefix):
    if df.empty: return df
    q=st.text_input("Search all text fields",key=prefix+"search")
    leaders=sorted(x for x in df.leader.dropna().unique().tolist() if x)
    selected=st.multiselect("Leader (column B)",leaders,key=prefix+"leader")
    left,right=st.columns(2)
    with left: start=st.date_input("From date — on or after (column C)",value=None,key=prefix+"from")
    with right: end=st.date_input("To date — on or before (column D)",value=None,key=prefix+"to")
    if q:
        fields=df[["entity","leader","reason"]].fillna("")
        df=df[fields.astype(str).apply(lambda s:s.str.contains(q,case=False,regex=False)).any(axis=1)]
    if selected: df=df[df.leader.isin(selected)]
    if start: df=df[df.date_from.notna() & (df.date_from>=start)]
    if end: df=df[df.date_to.notna() & (df.date_to<=end)]
    return df

def display(df):
    return df.rename(columns=LABELS).copy()

upload,browse,analysis=st.tabs(["📤 Import Data","🔎 Records & Filters","📈 Analysis"])
with upload:
    st.write("Required file headers (in this exact order):")
    st.code(" | ".join(HEADERS))
    f=st.file_uploader("Choose an Excel or CSV file (.xlsx, .csv)",type=["xlsx","csv"],key="data_upload")
    if f:
        if len(f.getvalue()) > 5 * 1024 * 1024:
            st.error("Demo uploads must be 5 MB or smaller.")
            st.stop()
        try:
            if f.name.lower().endswith(".csv"):
                raw=f.getvalue()
                incoming=None
                for encoding in ("utf-8-sig", "utf-16", "cp1256"):
                    try:
                        incoming=pd.read_csv(io.BytesIO(raw),dtype=object,encoding=encoding,sep=None,engine="python")
                        break
                    except (UnicodeError, UnicodeDecodeError):
                        continue
                if incoming is None:
                    raise ValueError("CSV encoding is not supported. Save as UTF-8 CSV and try again.")
            else:
                incoming=pd.read_excel(f,dtype=object)
            if len(incoming) > 2000:
                raise ValueError("Demo limit: 2,000 rows per file.")
            incoming.columns=[str(c).strip() for c in incoming.columns]
            if list(incoming.columns)!=HEADERS:
                st.error("The file columns do not match the required five-column template.")
            else:
                incoming=incoming.dropna(how="all")
                rows=[]; errors=[]
                for excel_row,values in enumerate(incoming.itertuples(index=False,name=None),start=2):
                    entity,leader,from_raw,to_raw,reason=values
                    entity="" if pd.isna(entity) else str(entity).strip()
                    leader="" if pd.isna(leader) else str(leader).strip()
                    reason="" if pd.isna(reason) else str(reason).strip()
                    if not entity:
                        errors.append(f"Row {excel_row}: Entity is required."); continue
                    try:
                        a,b=parse_date(from_raw),parse_date(to_raw)
                        if a and b and a>b: raise ValueError("From date is later than To date")
                        rows.append((entity,leader,a,b,reason))
                    except ValueError as exc: errors.append(f"Row {excel_row}: {exc}")
                if errors:
                    st.error("Fix the following rows before importing:")
                    for msg in errors[:25]: st.write(msg)
                else:
                    preview=pd.DataFrame(rows,columns=["Entity","Leader","From","To","Reason"])
                    st.dataframe(preview,use_container_width=True,hide_index=True)
                    if st.button("Import records",type="primary",disabled=not rows):
                        added=0
                        with connect() as con:
                            for row in rows:
                                exists=con.execute("""SELECT 1 FROM records WHERE entity=? AND leader=?
                                    AND COALESCE(date_from,'')=COALESCE(?,'') AND COALESCE(date_to,'')=COALESCE(?,'')
                                    AND reason=? LIMIT 1""",row).fetchone()
                                if not exists:
                                    con.execute("INSERT INTO records(entity,leader,date_from,date_to,reason) VALUES(?,?,?,?,?)",row)
                                    added+=1
                        st.success(f"Imported {added} new records; skipped {len(rows)-added} duplicates.")
        except Exception as exc: st.error(f"Could not process the uploaded file: {exc}")
with browse:
    full=load()
    filtered=filter_data(full,"browse_")
    st.metric("Matching records",len(filtered))
    st.dataframe(display(filtered),hide_index=True,use_container_width=True)
    output=io.BytesIO()
    export_columns = {"entity": "اسم الجهة", "leader": "اسم رئيس الجهة", "date_from": "من", "date_to": "الي", "reason": "نبذة عن السبب"}
    export_df = filtered[list(export_columns)].rename(columns=export_columns).copy()
    export_df.to_excel(output, index=False, sheet_name="Data")
    st.download_button("Download filtered Excel",output.getvalue(),"filtered_records.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    if not full.empty:
        st.divider();st.subheader("Edit or delete a record")
        chosen=st.selectbox("Select record",full.id.tolist(),format_func=lambda i:f"#{i} — {full.loc[full.id==i,'entity'].iloc[0]}")
        original=full.loc[full.id==chosen].iloc[0]
        with st.form("edit_form"):
            entity=st.text_input("Entity",value=original.entity)
            leader=st.text_input("Leader",value=original.leader)
            a=st.date_input("From",value=original.date_from if pd.notna(original.date_from) else None)
            b=st.date_input("To",value=original.date_to if pd.notna(original.date_to) else None)
            reason=st.text_area("Reason",value=original.reason)
            if st.form_submit_button("Save changes",type="primary"):
                if not entity.strip(): st.error("Entity is required.")
                elif a and b and a>b: st.error("From date cannot be after To date.")
                else:
                    with connect() as con:
                        con.execute("UPDATE records SET entity=?,leader=?,date_from=?,date_to=?,reason=? WHERE id=?",(entity.strip(),leader.strip(),a.isoformat() if a else None,b.isoformat() if b else None,reason.strip(),int(chosen)))
                    st.success("Record updated.");st.rerun()
        confirmed=st.checkbox("I confirm I want to delete this record")
        if st.button("Delete record",disabled=not confirmed):
            with connect() as con: con.execute("DELETE FROM records WHERE id=?",(int(chosen),))
            st.success("Record deleted.");st.rerun()
with analysis:
    st.caption("Charts update with the filters below.")
    filtered=filter_data(load(),"analysis_")
    total=len(filtered)
    a,b,c,d=st.columns(4)
    a.metric("Total records",total)
    b.metric("Unique entities",filtered.entity.nunique())
    c.metric("Unique leaders",filtered.leader.replace("",pd.NA).nunique())
    valid=filtered.dropna(subset=["date_from","date_to"]).copy()
    if not valid.empty:
        valid["duration_days"]=[(end-start).days+1 for start,end in zip(valid.date_from,valid.date_to)]
    d.metric("Avg. duration (days)",f"{valid.duration_days.mean():.1f}" if not valid.empty else "—")
    if total:
        left,right=st.columns(2)
        with left:
            st.subheader("Top entities")
            st.bar_chart(filtered.entity.value_counts().head(12),horizontal=True)
        with right:
            st.subheader("Records by leader")
            st.bar_chart(filtered.leader.replace("","Unspecified").value_counts().head(12),horizontal=True)
        dated=filtered.dropna(subset=["date_from"]).copy()
        if not dated.empty:
            st.subheader("Records by start month")
            dated["month"]=pd.to_datetime(dated.date_from).dt.to_period("M").astype(str)
            st.line_chart(dated.groupby("month").size().rename("Records"))
        if not valid.empty:
            st.subheader("Duration distribution (days, inclusive)")
            st.bar_chart(valid.duration_days.value_counts().sort_index().rename("Records"))
        st.subheader("Date completeness")
        st.write(f"{len(valid)} of {total} records have both From and To dates.")
    else: st.info("No matching records yet. Import an Excel file or adjust the filters.")
