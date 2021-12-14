"""
Name: Shikhali Alizada
Date: Monday, December 13, 2021
Description: page for quick analysis of top crime values based on filter
"""


import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st



def app():
    df = pd.read_csv('/Users/shikhalializada/PycharmProjects/pythonProject/Final_Project/bostoncrime2021_7000_sample.csv')
    data_copy = df[(df.Lat != 0) & (df.Long != 0)]
    data_copy['OCCURRED_ON_DATE'] = pd.to_datetime(data_copy['OCCURRED_ON_DATE'])
    data_copy['DATE'] = data_copy['OCCURRED_ON_DATE'].dt.strftime('%d/%m/%Y')
    data_copy['TIME'] = data_copy['OCCURRED_ON_DATE'].dt.strftime('%H:%M:%S')
    data_copy.drop(["OFFENSE_CODE_GROUP", "SHOOTING", "YEAR", "UCR_PART"], 1, inplace=True)
    data_copy['STREET'] = data_copy['STREET'].str.split(' MA ').str[0]
    st.text = ""
    title = '<p style="color:White; font-size: 25px;text-align:center">Top Crimes in Greater Boston During 2021</p>'
    st.markdown(title, unsafe_allow_html=True)

    if st.sidebar.checkbox("Show Top Crimes during 2021"):
        df_b = data_copy[["INCIDENT_NUMBER", "OFFENSE_DESCRIPTION", "STREET", "DATE", "TIME"]]
        user_choice = st.sidebar.selectbox("OFFENSE_DESCRIPTION", list(df_b.columns)[1:])
        user_inp = int(st.sidebar.number_input('Number to Filter By', min_value=1, max_value=50, value=10, step=1))
        # .head() obtains top values, but requires sorting. nlargest does both.
        df_b["Total"] = 0
        df_b = pd.DataFrame(df_b.groupby([user_choice], sort=True)["Total"].count().nlargest(user_inp))
        st.subheader(f'Top {user_inp} Crimes')
        st.write(df_b)
        line = '<hr style="height:3px;border:none;color:rgb(0, 131, 182);background-color:rgb(0, 131, 182);" />'
        st.markdown(line, unsafe_allow_html=True)
        text = '<p style="color:White; font-size: 15px;text-align:left">The graph below shows the top values based on your filters.</p>'
        st.markdown(text, unsafe_allow_html=True)
        crime_type = pd.Series(df_b.index[:])
        crime_frequency = df_b["Total"].tolist()
        fig, ax = plt.subplots(figsize=(10, 5))
        plt.bar(crime_type, crime_frequency, width=0.5, color=('r', 'b'))
        plt.title(f'Top Crimes by {user_choice.capitalize()}')
        plt.xlabel(user_choice)
        plt.ylabel("Crime Frequency")
        plt.xticks(rotation='vertical')
        plt.xticks(fontsize=7)
        st.pyplot(fig)





