"""
Name: Shikhali Alizada
Date: Monday, December 13, 2021
Description: home page allows for incident search and quick filtering
"""
import pandas as pd
import streamlit as st
import datetime
from datetime import date
import pydeck as pdk

def app():
    df_district = pd.read_csv('BostonPoliceDistricts.csv')
    df = pd.read_csv('bostoncrime2021_7000_sample.csv')
    # list of the days of the week and months for pandas categorical sort
    day_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    months = ['January', 'February', 'March', 'April', 'May', 'June']
    # list of crimes used as a new column in the dataframe
    crime_list = ["Larceny", "Drugs", "Threats", "Vandalism", "Graffiti", "Assault", "Auto Theft", "Missing Person", "Fraud",
                  "Towed", "Trespassing", "Violation", "Burglary", "Harassment", "Fire", "Dispute", "Stolen", "Sick Assist",
                  "Investigate", "Robbery"]
    # dictionary of keys to convert the integer Month values to word form
    dict_months = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June"}
    district_list = list(zip(df_district["District"], df_district["District Name"]))
    district_dict = {}
    for k, v in district_list:
        district_dict[k] = v
    st.text = ""
    title = '<p style="color:White; font-size: 25px;text-align:center">Raw Crime Data for 2021</p>'
    st.markdown(title, unsafe_allow_html=True)

    data_copy = df[(df.Lat != 0) & (df.Long != 0)]
    data_copy['OCCURRED_ON_DATE'] = pd.to_datetime(data_copy['OCCURRED_ON_DATE'])
    # convert date column to two separate columns with proper formatting
    data_copy['DATE'] = data_copy['OCCURRED_ON_DATE'].dt.strftime('%d/%m/%y')
    data_copy['TIME'] = data_copy['OCCURRED_ON_DATE'].dt.strftime('%H:%M:%S')
    data_copy.drop(["OCCURRED_ON_DATE", "OFFENSE_CODE_GROUP",
                    'UCR_PART', "YEAR", "SHOOTING", "Location", "HOUR", "OFFENSE_CODE"], 1, inplace=True)
    data_copy['STREET'] = data_copy['STREET'].str.split(' MA ').str[0]
    data_copy.dropna(inplace=True)
    district_series = data_copy.loc[:, "DISTRICT"]
    month_series = data_copy.loc[:, "MONTH"]
    # two parameter function, uses for loop and dict method "items"

    def replace(dicts, series):
        for key, value in dicts.items():
            series = series.replace(key, value)
        return series

    month_series = replace(dict_months, month_series)
    district_series = replace(district_dict, district_series)

    data_copy.drop(['MONTH', "DISTRICT"], axis=1, inplace=True)
    data_copy["MONTH"] = month_series
    data_copy["DISTRICT"] = district_series

    # checks if the crimes in crime_list is in the column rows
    # applies function to a new column showing the crime type
    def offense_type(row):
        for crime in crime_list:
            if crime.upper() in row['OFFENSE_DESCRIPTION']:
                return crime
    data_copy['Type'] = data_copy.apply(offense_type, axis=1)
    df_unique = data_copy[data_copy['Type'].notna()]
    df_unique = df_unique[["INCIDENT_NUMBER", "Type", "OFFENSE_DESCRIPTION", "DISTRICT",
                          "REPORTING_AREA", "STREET", "MONTH", "DAY_OF_WEEK", "DATE", "TIME", "Lat", "Long"]]
    st.write(df_unique)

    search = st.sidebar.text_input("Search an incident")
    line = '<hr style="height:3px;border:none;color:rgb(0, 131, 182);background-color:rgb(0, 131, 182);" />'
    # if/else statement to check if incident number is valid


    if search:
        if search in df_unique.INCIDENT_NUMBER.values:
            st.sidebar.success(f'{search} is a valid number')
            current_selection = df_unique[(df_unique.INCIDENT_NUMBER == search)]
            text = '<p style="color:White; font-size: 15px;text-align:left">The dataframe below shows information about the selected incident.</p>'
            st.markdown(line, unsafe_allow_html=True)
            st.markdown(text, unsafe_allow_html=True)
            st.write(current_selection)
            summary = st.expander("Obtain Summary")
            # converts new df to datetime format to select the specific year, month, and day of incident
            with summary:
                current_selection["DATE"] = pd.to_datetime(current_selection['DATE'])
                year = current_selection["DATE"].dt.year
                month = current_selection["DATE"].dt.month
                day = current_selection["DATE"].dt.day
                # changes formatting of string, makes it more legible
                current_date = date(day=day, month=month, year=year).strftime('%A, %B %d, %Y')
                crime = current_selection["Type"].item()
                current_selection['TIME'] = pd.to_datetime(current_selection['TIME'])
                current_selection['TIME'] = current_selection['TIME'].dt.strftime('%H:%M')
                crime_time = current_selection["TIME"].item()
                street = current_selection["STREET"].item()
                district = current_selection["DISTRICT"].item()
                lat = current_selection["Lat"].item()
                lon = current_selection["Long"].item()
                st.write(f"""
                The incident, **{crime.lower()}**, occurred on **{current_date}**. The time was **{crime_time}** and the location was **{street}** at district **{district}**.
                """)
                current_selection.rename(columns={'Lat': 'lat', 'Long': 'lon'}, inplace=True)
                # I used pydeck for the adjustable zoom; folium's html is static and doesn't fit into expander.
                st.pydeck_chart(pdk.Deck(
                    map_style='mapbox://styles/mapbox/light-v9',
                    initial_view_state=pdk.ViewState(
                        latitude=lat,
                        longitude=lon,
                        zoom=17,
                        pitch=50,
                    ),
                    ), use_container_width=False)
        else:
            st.sidebar.error(f'{search} is an invalid number')

    expand = st.sidebar.expander("Filter Table by Criteria")
    # expands sidebar for filters
    with expand:
        st.header("Please Filter Here:")
        crime_choice = st.selectbox('Select the crime:', crime_list)
        start_date = st.date_input("Start date", datetime.date(2021, 1, 1),
                                   datetime.date(2021, 1, 1), datetime.date(2021, 5, 31))
        end_date = st.date_input('End date', datetime.date(2021, 5, 31), datetime.date(2021, 1, 1), datetime.date(2021, 5, 31))
        if start_date < end_date:
            st.success('Start date: `%s`\n\nEnd date: `%s`' % (start_date, end_date))
        else:
            st.error('Error: End date must fall after start date.')
        # converted the input to datetime to compare with columns. Gives error otherwise.
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        # filters df by chosen crime, date
        df_unique = df_unique[(df_unique.Type == crime_choice)]
        df_unique["DATE"] = pd.to_datetime(df_unique['DATE'])
        date_range = (df_unique['DATE'] >= start_date) & (df_unique['DATE'] <= end_date)
        df_unique = df_unique.loc[date_range]
        df_unique['DATE'] = df_unique['DATE'].dt.strftime('%d/%m/%y')
        sort_list = [col for col in df_unique]
        sort_choice = st.multiselect("Select sort order:", sort_list)
        df_unique['DAY_OF_WEEK'] = pd.Categorical(df_unique['DAY_OF_WEEK'], categories=day_of_week, ordered=True)
        df_unique['MONTH'] = pd.Categorical(df_unique['MONTH'], categories=months, ordered=True)
        # pandas categorical sort using lists with predefined order
        df_unique = df_unique.sort_values(sort_choice, ascending=True)
        button = st.button('Make Table')
    if button:
        st.markdown(line, unsafe_allow_html=True)
        text_2 = '<p style="color:White; font-size: 15px;text-align:left">This is the dataframe created based on your filters.</p>'
        st.markdown(text_2, unsafe_allow_html=True)
        df_unique.reset_index(drop=True, inplace= True)
        st.write(df_unique)















