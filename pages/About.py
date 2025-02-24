import streamlit as st
import connection as ssh
import ssh_command as sc

st.title("About This App")


st.text("This app is a Streamlit app that can be used to deploy a Laravel application to a server. It uses SSH to connect to the server and execute commands. The app is built using Python and Streamlit. The app is designed to be user-friendly and easy to use. The app is open-source and can be found on GitHub at ")
st.markdown("""
[![GitHub](https://img.shields.io/github/stars/Mirekan/streamlit-autodeployer?style=social)](https://github.com/Mirekan/streamlit-autodeployer)
""")
