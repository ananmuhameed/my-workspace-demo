# My Workspace — Public Demo

Streamlit demo with **synthetic records only**. UI is English; imported Excel/CSV headers remain Arabic.

## Publish to Streamlit Community Cloud
1. Create a new GitHub repository and upload **the contents of this folder** (including `app.py`, `pages/`, `demo_store.py`, `requirements.txt`, and `.streamlit/`). Do not upload real records or `.db` files.
2. Open https://share.streamlit.io and sign in with GitHub.
3. Select the repository, branch `main`, and entrypoint `app.py`, then deploy.
4. Share the resulting `*.streamlit.app` link.

## Local run
`pip install -r requirements.txt` then `streamlit run app.py`.

## Important
- Demo records are fictional; data is stored in temporary session-specific SQLite files, not permanent storage.
- Data can be lost on app restarts and temporary files can remain on the server until cleanup. **Do not upload sensitive information.**
- This is a demo, not a production multi-user data platform. No authentication is included.
- Duplicate check matches all five fields exactly.
- Word Generator supports `.xlsx` and `.docx` templates; it generates up to 100 files per batch.
