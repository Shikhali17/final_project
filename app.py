"""
Name: Shikhali Alizada
Date: Monday, December 13, 2021
Description: an application for crime data analysis with queries using pandas
"""


from PIL import Image
import streamlit as st
import numpy as np

# Custom imports
from multipage import MultiPage
from pages import metadata, data_visualize, graph, home



app = MultiPage()

display = Image.open('logo.png')
display = np.array(display)
_, col1, col2, _,  = st.columns([0.5, 2, 2, 0.75])
col1.image(display, width=260)
with col2:
    original_title = '<p style="font-family:copperplate;font-weight:bold; color:White; font-size: 40px;text-align:center">Crime Data Analysis of Greater Boston</p>'
    st.markdown(original_title, unsafe_allow_html=True)




app.add_page("Home", home.app)
app.add_page("Top Data", metadata.app)
app.add_page("Mapping", data_visualize.app)
app.add_page("Graphing", graph.app)



app.run()
