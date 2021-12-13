"""
Name: Shikhali Alizada
Date: Monday, December 13, 2021
Description: page that allows for graphing based on user input using matplotlib
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
    data_copy.drop(["OFFENSE_CODE_GROUP", "UCR_PART", "SHOOTING"], 1, inplace=True)
    data_copy['STREET'] = data_copy['STREET'].str.split(' MA ').str[0]
    crime_list = ["Larceny", "Drugs", "Threats", "Vandalism", "Graffiti", "Assault", "Auto theft", "Missing person", "Fraud",
                  "Towed", "Trespassing", "Violation", "Burglary", "Harassment", "Fire", "Dispute", "Stolen", "Sick assist",
                  "Investigate", "Robbery"]
    day_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dict_months = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June"}

    months = ['January', 'February', 'March', 'April', 'May', 'June']

    # the code below is a list comprehension, but it doesn't fully covert the numbered month to words for some reason
    # months_list = [str(x) for x in data_copy["MONTH"]]
    # month_series = pd.Series(months_list)

    month_series = data_copy.loc[:, "MONTH"]

    def replace(dicts, series):
        for key, value in dicts.items():
            series = series.replace(key, value)
        return series

    month_series = replace(dict_months, month_series)

    data_copy.drop(['MONTH'], axis=1, inplace=True)
    data_copy["MONTH"] = month_series

    # sort date values for the graphs
    data_copy['DAY_OF_WEEK'] = pd.Categorical(data_copy['DAY_OF_WEEK'], categories=day_of_week, ordered=True)
    data_copy['MONTH'] = pd.Categorical(data_copy['MONTH'], categories=months, ordered=True)
    data_copy = data_copy.sort_values('DAY_OF_WEEK')
    data_copy = data_copy.sort_values('MONTH')

    dict_chart = {
        'Line Plot': 'line',
        'Bar Chart': 'bar',
        'Box Plot': 'box',
        'Area Plot': 'area',
    }

    def offense_type(row):
        for crime in crime_list:
            if crime.upper() in row['OFFENSE_DESCRIPTION']:
                return crime
    data_copy['Crime_Type'] = data_copy.apply(offense_type, axis=1)
    data_copy = data_copy[data_copy['Crime_Type'].notna()]
    data_copy.reset_index(drop=True, inplace=True)
    df_second_filter = data_copy.copy()
    column_list = [col for col in data_copy]
    html = '''<div style="background-color:rgb(0, 131, 182);border:1px solid black;">
        <p style="text-align:center;font-size:25px;font-weight:bold;font-family:copperplate">Instructions</p>
        <p style="text-align:left;font-size:15px;font-weight:bold;font-family:Monaco">Select a basic filter using the radio buttons.
        If you would like to add more filters, select the "Add more filters?" checkbox. When graphing, it is recommended that you use 
        line and area charts exclusively for time values as the x-axis.</p>
        </div>'''
    st.markdown(html, unsafe_allow_html=True)
    st.write(data_copy)

    # depending on the user input, the values are inverted.
    def user_inputs(second_filter=None, filter_value=None, filter_choice=None):
        filter_checkbox = st.sidebar.checkbox("Add more filters?")
        if filter_checkbox:
            filter_choice = st.sidebar.selectbox("Filter by Time or Names", ['Time', 'Name'])
            if filter_choice == "Name":
                first_filter = st.sidebar.radio("Choose a filter", ["DISTRICT", "STREET", 'OFFENSE_DESCRIPTION', 'Crime_Type'])
                for column in column_list:
                    if first_filter == column:
                        filter_list = data_copy[column].unique()
                        filter_list = pd.DataFrame(filter_list)
                        filter_list.dropna(inplace=True)
                        st.sidebar.write(f'Valid {column.lower()} for graph')
                        st.sidebar.write(filter_list)
                        # default value to first column value
                        filter_value = (st.sidebar.text_input(column, data_copy[column].iloc[0])).upper()
                        # if statement because crimes are capitalized in the list, not upper case
                        if column == "Crime_Type":
                            filter_value = filter_value.capitalize()
                second_filter = st.sidebar.radio("Choose another filter", ['MONTH', 'DAY_OF_WEEK', 'HOUR'])
            else:
                first_filter = st.sidebar.radio("Choose a filter", ['MONTH', 'DAY_OF_WEEK', 'HOUR'])
                if first_filter == "MONTH":
                    filter_value = st.sidebar.selectbox('Choose a Month', data_copy["MONTH"].unique())
                elif first_filter == "DAY_OF_WEEK":
                    filter_value = st.sidebar.selectbox("Choose the Day of the Week", data_copy["DAY_OF_WEEK"].unique())
                elif first_filter == "HOUR":
                    filter_value = int(st.sidebar.number_input('Choose the hour', min_value=0, max_value=23, value=10, step=1))
                second_filter = st.sidebar.radio("Choose another filter", ["DISTRICT", "STREET", 'OFFENSE_DESCRIPTION', 'Crime_Type'])

        else:
            first_filter = st.sidebar.radio("Choose a filter", ["DISTRICT", "STREET", 'OFFENSE_DESCRIPTION', 'Crime_Type', 'MONTH', 'DAY_OF_WEEK', 'HOUR'])

        return first_filter, filter_checkbox, second_filter, filter_value, filter_choice

    first_filter, filter_checkbox, second_filter, filter_value, filter_choice = user_inputs()

    # creates total column for crime frequency depending on the filter
    data_copy["Total"] = 0
    data_copy = data_copy.groupby([first_filter], sort=True)["Total"].count()

    # filters for frequencies above 30 to avoid clustering in the graphs
    data_copy = data_copy[data_copy > 30]

    # if "Add more filters?" checkbox is active
    if filter_checkbox:
        data_copy = df_second_filter
        data_copy["Total"] = 0
        data_copy = data_copy[(data_copy[first_filter] == filter_value)]
        if filter_choice == "Name":
            data_copy = data_copy.groupby([second_filter], sort=True)["Total"].count()
        elif filter_choice == "Time":
            data_copy = data_copy.groupby([second_filter], sort=True)["Total"].count()
            data_copy = data_copy[data_copy > 5]
            # > 5 because there are too many streets with 1-5 total crimes, avoids clustering

    # list comprehension and dict method
    list_keys = [key for key in dict_chart.keys()]
    chart_select = st.sidebar.selectbox(
        label="Select the chart type",
        options=list_keys
    )
    color = st.sidebar.color_picker('Pick A Color', '#00f900')
    button = st.sidebar.button("Graph Chart")
    if button:
        fig3, ax3 = plt.subplots(figsize=(10, 5))
        data_copy.plot(kind=str(dict_chart[chart_select]), color=color)

        if filter_checkbox:
            plt.title(f'Number of Crimes: {str(filter_value).capitalize()}')
            plt.xlabel(second_filter)
        else:
            plt.title(f'Number of Crimes by {str(first_filter).capitalize()}')
            plt.xlabel(first_filter)
        plt.xticks(rotation='vertical')
        plt.xticks(fontsize=7)
        plt.ylabel('Number of Crimes')
        st.pyplot(fig3)




