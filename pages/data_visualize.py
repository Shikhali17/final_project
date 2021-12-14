"""
Name: Shikhali Alizada
Date: Monday, December 13, 2021
Description: page for mapping crime location based on a district and additional filters
"""
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static
import folium
from folium.plugins import MarkerCluster



def app():
    df = pd.read_csv('/Users/shikhalializada/PycharmProjects/pythonProject/Final_Project/bostoncrime2021_7000_sample.csv')
    df_district = pd.read_csv('/Users/shikhalializada/PycharmProjects/pythonProject/Final_Project/BostonPoliceDistricts.csv')
    data_copy = df[(df.Lat != 0) & (df.Long != 0)]
    data_copy['OCCURRED_ON_DATE'] = pd.to_datetime(data_copy['OCCURRED_ON_DATE'])
    data_copy['DATE'] = data_copy['OCCURRED_ON_DATE'].dt.strftime('%d/%m/%Y')
    data_copy['TIME'] = data_copy['OCCURRED_ON_DATE'].dt.strftime('%H:%M:%S')
    data_copy.drop(["OFFENSE_CODE_GROUP", "UCR_PART", "SHOOTING"], 1, inplace=True)
    # some streets contain extra info, so I split them at MA and took the first index value using str[0]
    data_copy['STREET'] = data_copy['STREET'].str.split(' MA ').str[0]
    data_copy.dropna(inplace=True)
    crime_list = ["LARCENY", "DRUGS", "THREATS", "VANDALISM", "GRAFFITI", "ASSAULT", "THEFT", "MISSING PERSON", "FRAUD",
                  "TOWED", "TRESPASSING", "VIOLATION", "BURGLARY", "HARASSMENT", "FIRE", "DISPUTE", "STOLEN"]
    dict_months = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June"}
    district_list = list(zip(df_district["District"], df_district["District Name"]))
    district_dict = {}
    for k, v in district_list:
        district_dict[k] = v
    month_series = data_copy.loc[:, "MONTH"]
    district_series = data_copy.loc[:, "DISTRICT"]

    def replace(dicts, series):
        for key, value in dicts.items():
            series = series.replace(key, value)
        return series

    month_series = replace(dict_months, month_series)
    district_series = replace(district_dict, district_series)

    data_copy.drop(['MONTH', "DISTRICT"], axis=1, inplace=True)
    data_copy["MONTH"] = month_series
    data_copy["DISTRICT"] = district_series
    district_count = data_copy["DISTRICT"].rename("Frequency").value_counts()
    district_count.dropna(inplace=True)
    st.sidebar.subheader("Valid districts for map:")
    st.sidebar.write(district_count)

    def user_inputs(month="January", weekday="Monday"):
        district = st.sidebar.text_input("Choose a district", data_copy["DISTRICT"].iloc[0])
        highlight = st.sidebar.selectbox('Choose a crime to highlight', crime_list)
        filter_checkbox = st.sidebar.checkbox("Add more filters?")
        if filter_checkbox:
            month = st.sidebar.selectbox('Choose a Month', data_copy["MONTH"].unique())
            weekday = st.sidebar.selectbox("Choose the Day of the Week", data_copy["DAY_OF_WEEK"].unique())
        cluster = st.sidebar.checkbox("Add clusters to map?")
        button = st.sidebar.button("Produce Map")
        return district, button, month, weekday, highlight, cluster, filter_checkbox

    district, button, month, weekday, highlight, cluster, filter_checkbox = user_inputs()
    districts = data_copy["DISTRICT"].value_counts()
    if district in districts:
        st.sidebar.success("Valid District")
        if filter_checkbox:
            crimes_in_district = data_copy[(data_copy.DISTRICT == district) & (data_copy.MONTH == month) & (data_copy.DAY_OF_WEEK == weekday)].sort_values(by="DATE", ascending=False)
        else:
            crimes_in_district = data_copy[(data_copy.DISTRICT == district)].sort_values(by="DATE", ascending=False)
        st.write(f"Crimes in {district}")
        st.write(crimes_in_district[['STREET', 'INCIDENT_NUMBER', 'OFFENSE_DESCRIPTION', 'DATE']])
    elif district not in districts:
            st.sidebar.error("Invalid District. Try Again")


    if button:
        line = '<hr style="height:3px;border:none;color:rgb(0, 131, 182);background-color:rgb(0, 131, 182);" />'
        st.markdown(line, unsafe_allow_html=True)
        text = '<p style="color:White; font-size: 15px;text-align:left">The map below shows the location of crimes in your ' \
            'chosen filters and colors the specific crime that you selected. You can also cluster the markers.</p>'
        st.markdown(text, unsafe_allow_html=True)
        districtdf = data_copy.copy()

        districtdf = crimes_in_district

        st.subheader(f'Location of Crimes in District {district}')
        # function to create a new column, "color"
        # returns color red if selected crime is in the column value
        def select_marker_color(row):
            if highlight in row['OFFENSE_DESCRIPTION']:
                return 'red'
            return 'blue'
        districtdf['color'] = districtdf.apply(select_marker_color, axis=1)

        my_map = folium.Map(
            location=[districtdf["Lat"].mean(), districtdf["Long"].mean()],
            zoom_start=14,
            tiles='Stamen Terrain'
        )
        marker_cluster = MarkerCluster().add_to(my_map)
        for _, crime in districtdf.iterrows():
            html = '''<div style="background-color:rgb(0, 131, 182);border:1px solid black;">
            <p style="text-align:center;font-size:25px;font-weight:bold;font-family:copperplate">Crime Information</p>
            <p style="text-align:left;font-size:15px;font-weight:bold;font-family:copperplate">Date:</p>
            <p>''' + str(crime["DATE"]) + '</p> <p style="text-align:left;font-size:15px;font-weight:bold;font-family:copperplate">Street:</p><p>'\
                    + str(crime["STREET"]) + '</p> <p style="text-align:left;font-size:15px;font-weight:bold;font-family:copperplate">Number:</p><p>'\
                    + str(crime["INCIDENT_NUMBER"]) + '</p></div>'

            iframe = folium.IFrame(html, width=200, height=310)
            popup = folium.Popup(iframe, parse_html=True)
            # if "Add clusters to map?" is active, add crime marker to cluster
            if cluster:
                folium.Marker(
                    location=[crime['Lat'], crime['Long']],
                    popup=popup,
                    tooltip=crime["OFFENSE_DESCRIPTION"],
                    icon=folium.Icon(color=crime['color'], prefix='fa', icon='circle')
                ).add_to(my_map).add_to(marker_cluster)
            else:
                folium.Marker(
                    location=[crime['Lat'], crime['Long']],
                    popup=popup,
                    tooltip=crime["OFFENSE_DESCRIPTION"],
                    icon=folium.Icon(color=crime['color'], prefix='fa', icon='circle')
                ).add_to(my_map)
        folium_static(my_map)


