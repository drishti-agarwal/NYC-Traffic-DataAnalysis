
import streamlit as st
import numpy as np
import pandas as pd
import pydeck as pdk
import plotly.express as px
from PIL import Image
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

###TITLE AND SIDEBAR###


st.title("NYC Motor Vehicles Collisions Analysis")
st.sidebar.title("CONTROLLER")

###INTRODUCTION###
st.markdown("## **Introduction**")
img = Image.open('new-york-traffic1.jpg')
st.image(img,use_column_width=True)
st.write("*New York State is the fourth largest state in the United States of America based on our latest projections." 
"New York State has an overall population density of 421 people per square mile, with an area of 47,126 square miles." 
"When most people think of New York, they immediately think of New York City, the largest city in the US."
"New York City is also the most densely populated major city in the country." 
"Nearly 43 percent of New York state's population live in the 305 square miles that comprise New York City." 
"The next largest city in the state of New York is Buffalo, with just over 250,000 residents." 
"This means New York City is over 33 times larger than the second largest city in New York." 
"New York's state capital Albany is home to just under 100 thousand residents."
"The most populated counties in New York are Kings County (2,648,771), Queens County (2,358,582), and New York County (1,664,727).*")
st.markdown("## **About**")
st.write("*The website aims at providing you an insight about new york's traffic and the motor vehicle collision accidents " 
        "through a map overview*") 

###LOADING DATASET###
@st.cache(persist=True)
def load_data():
    data = pd.read_csv("dataset1.csv",parse_dates=['crash_date_crash_time'])
    
    return data

dataset_old1=load_data()
dataset_old=pd.DataFrame(dataset_old1.iloc[:,1:22])

###Adding the Category column###


dat_cat = pd.DataFrame(dataset_old.iloc[:,10:16].idxmax(axis=1,skipna=True),columns=['category'])
col = [dataset_old,dat_cat]
dataset = pd.concat(col,axis=1)


### Display Dataset###
if st.sidebar.checkbox("Show Dataset",False,key=5):
    st.markdown("## **The NYC Dataset**")
    st.write(dataset)

########################################################################################################

st.markdown("## **The Visual Data Analysis**")
st.write("*Road safety is by any means a critical issue,"
 "and is relevant to everybody's daily life. It's inevitable, and more often" 
 "than not, a life-or-death situation indeed. Therefore, it is very important"
 "to look at the past collision history data and see what we can learn from the data"
 "to help better prevent and/or avoid collisions in the future.*")

###RAW DATA MAP PLOT###

if st.sidebar.checkbox("Geographical Data-Plot",False,key=1):
    st.markdown("### ➡ Maximum Number of Injuries Geographically") 
    st.write("*To help easily visualize and explore the spatial details of the collision data," 
    "a comprehensive and flexible interactive map tool*")
    injured_people = st.slider("number of person",0,20,key=1)
    mapdata = pd.DataFrame(data=dataset)
    mapdata.dropna(subset=['injured_persons'],inplace=True)
    
    fig = px.scatter_mapbox(mapdata.query("injured_persons >= @injured_people"), lat="latitude", lon="longitude", hover_name="borough", hover_data=["on_street_name"],
                        color_discrete_sequence=["red"], zoom=7, height=200)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(height=600,margin={"r":0,"t":0,"l":0,"b":0})
    st.write(fig)

###COLLISIONS PER HOUR TABULAR DATA###

if st.sidebar.checkbox("Collisions per hour",False,key=2):
    st.markdown("### ➡ Tabular Data-Collison per Hour ") 
    hour = st.slider("Hour to look at", 0, 23,key=2)
    datahrs_T=dataset[dataset['crash_date_crash_time'].dt.hour == hour]
    st.markdown("### ➡ Raw data by minute between %i:00 and %i:00" % (hour, (hour + 1)))
    st.write(datahrs_T)

###GEGORAPHICAL TIME WISE PLOT####

if st.sidebar.checkbox("Gegraphical Time-wise Plot",False,key=3):
    st.markdown("### ➡ Geographical Data-Collison per Hour ") 
    st.write("*This plot will help you analyse the hours of day with maximum injuries geographically." 
    "Thus,we can use this map to learn about the most lethal hours of the day for a particular area*")
    hour = st.slider("Hour to look at", 0, 23,key=4)
    datahrs_M=dataset[dataset['crash_date_crash_time'].dt.hour == hour]
    midpoint = np.average(dataset["latitude"]), np.average(dataset["longitude"])
    st.markdown("### ➡ Raw data by minute between %i:00 and %i:00" % (hour, (hour + 1)))
    st.write(pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v10",
        initial_view_state={
            "latitude": midpoint[0],
            "longitude": midpoint[1],
            "zoom": 11,
            "pitch": 50,
        },
        layers=[
            pdk.Layer(
            "HexagonLayer",
            data=datahrs_M[['crash_date_crash_time', 'latitude', 'longitude']],
            get_position=["longitude", "latitude"],
            auto_highlight=True,
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0, 1000],
            ),
        ],
    ))

### BARGRAPH PLOT FOR HOURLY ANALYSIS ###
if st.sidebar.checkbox("Hourly Analysis",False,key=4):
    st.markdown("### ➡Data Analysis by Bargraph ") 
    st.write("*The bargraph data will help you analyse the no. of accidents" 
    "hourly for the entire dataset of the new york thus providing minute wise analysis*")
    hour = st.slider("Hour to look at", 0, 23,key=5)
    filtered = dataset[
        (dataset['crash_date_crash_time'].dt.hour>=(hour%12)) & (dataset['crash_date_crash_time'].dt.hour<((hour+1)%12))
        ]
    st.write(filtered)
    
    hist = np.histogram(filtered['crash_date_crash_time'].dt.minute, bins=60, range=(0, 60))[0]
    
    data_b = pd.DataFrame({"minute": range(60), "crashes": hist})
    fig = px.bar(data_b, x="minute", y="crashes", height=500,width=800,hover_data=['minute', 'crashes'],color=hist)
    st.markdown("### ➡ Raw data by minute between %i:00 and %i:00" % (hour, (hour + 1)))
    st.write(fig)

#### PIE GRAPH FOR BOROUGH AND CATEGORY ####
if st.sidebar.checkbox("Area/Category wise Analysis",False,key=7):
    st.markdown("### ➡Data Analysis by Piegraph ") 
    st.write("*This section will help you understand the specific areas of NYC with" 
    "the most number of accidents in the entire dataset along with category wise distribution.*")
    pidata1 = dataset['borough'].value_counts()
    pie_frame1 = pd.Series.to_frame(pidata1)
    pie_frame1['Name'] = list(pie_frame1.index)
    #st.write(pie_frame1)
    fig = px.pie(pie_frame1, values="borough",names="Name", title="Long-Form Input")
    #st.write(fig)
    pidata2 =dataset['category'].value_counts()
    pie_frame2 =pd.Series.to_frame(pidata2)
    pie_frame2['Name']=list(pie_frame2.index)
    #st.write(pie_frame2)
    fig = go.Figure()
    fig = make_subplots(rows=1, cols=3, specs=[[{'type':'domain'}, {'type':'domain'},  {'type':'domain'}]],
            subplot_titles=['Area Wise Count',' ','Category Wise Count'])

    fig.add_trace(go.Pie(labels=pie_frame1['Name'], values=pie_frame1['borough'], name="Area Wise Count",showlegend=False,
            textinfo='label+percent',insidetextorientation='radial',
            marker=dict(colors=[ 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink'])),1, 1)

    fig.add_trace(go.Pie(labels=pie_frame2['Name'], values=pie_frame2['category'], name="Category Wise Count",
            showlegend=False,textinfo='label+percent',insidetextorientation='radial',
            marker=dict(colors=['mediumseagreen','mediumslateblue', 'mediumspringgreen',
                'mediumturquoise', 'mediumvioletred',' midnightblue'])),1, 3)

    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    fig.update_traces(hole=.4, hoverinfo="label+percent+name")
    fig.update_layout(
    autosize=False,
    width=850,
    height=400,
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=0,
       
    ))
    st.write(fig)

### BAR GRAPH FOR DANGEORUS STREETS ###
    
if st.sidebar.checkbox("Top 20 dangerous Streets",False,key=6):
    st.markdown("### ➡Data Analysis by Bargraph ")
    st.write("*Now,let us figure out the top 20 streets which had the most accidents in NYC.*")
    street_count=dataset["on_street_name"].value_counts()
    street_datafrm=pd.Series.to_frame(street_count) 
    street_datafrm['id']=list(street_datafrm.index)
    fig = px.histogram(street_datafrm.iloc[0:20,:],x="id",y="on_street_name",range_y=[100,300],height=500,width=900,
            color=['purple', 'red','palevioletred','lightpink','rosybrown','orchid', 'lawngreen', 'orange', 'orangered'
               ,'palegoldenrod', 'palegreen', 'paleturquoise',
                'papayawhip', 'peachpuff','peru', 'pink',
                'plum', 'powderblue',  
                'royalblue', 'saddlebrown'], color_discrete_map="identity")
    st.write(fig)
    

    st.write("*This is my work over data visualization, Thanks for visiting!*")
    st.markdown("created by Drishti Agarwal 😀")
   



