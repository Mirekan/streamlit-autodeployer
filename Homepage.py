import streamlit as st
import connection as ssh
import ssh_command as sc

st.set_page_config(page_title="Laravel", page_icon=":computer:")

st.title("AutoDeploy APP")
st.sidebar.success("Select a page above.")

st.text("Laravel Requirements : \n 1. PHP 8.2 or higher \n 2. Composer \n 3. Node.js \n 4. NPM \n 5. MySQL or SQLite")