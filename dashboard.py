import streamlit as st
import subprocess

# Instalar paquetes desde requirements.txt
try:
    print(['pip', 'install', '-r', 'requirements.txt'])
    subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True)
except Exception as e: 
    print('installing requirements',e)

try:
    import plotly.express as px
    import pandas as pd
    import os
    import warnings
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import numpy as np
except Exception as e: 
    print(e)


warnings.filterwarnings('ignore')

st.set_page_config(page_title='DataCo Supply Chain Data Analysis Dashboard', page_icon=':bar_chart:', layout='wide')

st.title(" :bar_chart: DataCo Supply Chain Data Analysis Dashboard")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# f1 = st.file_uploader(":file_folder: Upload a file", type=(['csv']))
# if f1 is not None:
#     filename = f1.name
#     st.write(filename)
#     df=pd.read_csv(filename)
# else:
    # os.chdir(r'X:\Plaksha_term_4\Python for DS\Group Project\data_archive')
df = pd.read_csv("supply_data_final.csv", encoding='utf-8')

col1, col2 = st.columns((2))
df['shipping date (DateOrders)'] = pd.to_datetime(df['shipping date (DateOrders)'], format="%d-%m-%Y %H:%M")

startDate = pd.to_datetime(df['shipping date (DateOrders)']).min()
endDate = pd.to_datetime(df['shipping date (DateOrders)']).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df['shipping date (DateOrders)'] >= date1) & (df['shipping date (DateOrders)'] <= date2)].copy()

st.sidebar.header("Choose your filter: ")

# Create for Region
region = st.sidebar.multiselect("Pick a Region", df['Order Region'].unique())

if not region:
    df2 = df.copy()
else:
    df2 = df[df["Order Region"].isin(region)]

# Create for Country
country = st.sidebar.multiselect("Pick a Country", df2['Order Country'].unique())

if not country:
    df3 = df2.copy()
else:
    df3 = df2[df2["Order Country"].isin(country)]

# Create for State
state = st.sidebar.multiselect("Pick a State", df3['Order State'].unique())

if not state:
    df4 = df3.copy()
else:
    df4 = df3[df3["Order State"].isin(state)]

if not region and not country and not state:
    filtered_df = df
elif not country and not state:
    filtered_df = df[df['Order Region'].isin(region)]
elif not region and not state:
    filtered_df = df[df['Order Region'].isin(country)]
elif not region and not country:
    filtered_df = df[df['Order Region'].isin(state)]
elif country and state:
    filtered_df = df[(df['Order Country'].isin(country)) & (df['Order State'].isin(state))]
elif region and state:
    filtered_df = df[(df['Order Region'].isin(region)) & (df['Order State'].isin(state))]
elif region and country:
    filtered_df = df[(df['Order Region'].isin(region)) & (df['Order Country'].isin(country))]
elif state:
    filtered_df = df[df['Order State'].isin(state)]
else:
    filtered_df = df[(df['Order Region'].isin(region)) & (df['Order Country'].isin(country)) & (df['Order State'].isin(state))]


department_df = filtered_df.groupby(by=["Department Name"], as_index=False)[['Order Item Total', 'Order Profit Per Order']].sum()
ordered_departments = department_df.sort_values(by='Order Item Total', ascending=False)['Department Name']
tot_sales = filtered_df['Order Item Total'].sum()
tot_profit = filtered_df['Order Profit Per Order'].sum()
tot_orders = filtered_df['Order Id'].nunique()
avg_profit = filtered_df['Order Profit Per Order'].mean()
avg_sales = filtered_df['Order Item Total'].mean()

## SALES INSIGHTS -----------------------------------------------------------------------------------------------------------------------------------------------------------
st.markdown("<h1 style='text-align: center;'>SALES INSIGHTS</h1>", unsafe_allow_html=True)

col3, col4 = st.columns(2)
with col3:   
    st.subheader(f":chart: Total Sales: ${tot_sales:.2f}")
    st.subheader(f":package: Total Orders: {tot_orders}")
    st.subheader(f":heavy_dollar_sign: Average Sales: ${avg_sales:.2f}")
with col4:
    st.subheader(f":moneybag: Total Profit: ${tot_profit:.2f}")
    st.subheader(f":coin: Profit Margin: {(tot_profit/tot_sales)*100:.2f}%")
    st.subheader(f":eight_spoked_asterisk: Average Profit: ${avg_profit:.2f}")
st.markdown("---")

col5, col6 = st.columns(2)
with col5:
    st.subheader(f"Department wise Sales")
    fig = px.bar(department_df, x="Department Name", y="Order Item Total", text = ['${:,.2f}'.format(x) for x in department_df['Order Item Total']],
                 template = "seaborn",
                 category_orders={'Department Name': ordered_departments})
    st.plotly_chart(fig, use_container_width=True, height=200)

    st.subheader("Segment wise Sales")
    fig = px.pie(filtered_df, values="Order Item Total", names="Customer Segment", hole=0.5)
    fig.update_traces(text=filtered_df['Customer Segment'], textposition = "outside")
    st.plotly_chart(fig, use_container_width=True)

ordered_departments = department_df.sort_values(by='Order Profit Per Order', ascending=False)['Department Name']
with col6:
    st.subheader(f"Department wise Profits")
    fig = px.bar(department_df, x="Department Name", y="Order Profit Per Order", text = ['${:,.2f}'.format(x) for x in department_df['Order Profit Per Order']],
                 template = "seaborn",
                 category_orders={'Department Name': ordered_departments})
    st.plotly_chart(fig, use_container_width=True, height=200)

    st.subheader("Segment wise Profits")
    fig = px.pie(filtered_df, values="Order Profit Per Order", names="Customer Segment", hole=0.5)
    fig.update_traces(text=filtered_df['Customer Segment'], textposition = "outside")
    st.plotly_chart(fig, use_container_width=True)

## Code perfect till here.
product_df = filtered_df.groupby(by=["Product Name"], as_index=False).agg({
    'Order Item Total': 'sum',
    'Order Profit Per Order': 'sum',
    'Order Item Discount Rate': 'mean',
    'Order Item Quantity': "sum"
})

top_products = product_df.sort_values(by='Order Profit Per Order', ascending=False)
top_products = top_products.head(10)
low_products = product_df.sort_values(by='Order Profit Per Order', ascending=True)
low_products = low_products.head(10)

st.markdown("<h1 style='text-align: center;'>PRODUCT AND BRAND INSIGHTS</h1>", unsafe_allow_html=True)
st.markdown("---")
## TOP PRODUCTS-----------------------------------------------------------------------------------------------------------------------------------------------------------
st.markdown("<h3 style='text-align: center;'>Highest Benefit Products</h3>", unsafe_allow_html=True)
# Create a figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add Total Benefit to the chart
fig.add_trace(
    go.Bar(x=top_products['Product Name'], y=top_products['Order Item Total'], name='Sales', offsetgroup=1),
    secondary_y=False,
)

# Add Total Benefit to the chart
fig.add_trace(
    go.Bar(x=top_products['Product Name'], y=top_products['Order Profit Per Order'], name='Profit', offsetgroup=2),
    secondary_y=False,
)

# Add Average Discount Rate to the chart
fig.add_trace(
    go.Scatter(x=top_products['Product Name'], y=top_products['Order Item Discount Rate'], name='Average Discount Rate', mode='lines'),
    secondary_y=True,
)

# Add titles and labels
fig.update_layout(
    title_text='Total Benefit and Average Discount Rate by Product',
    xaxis_title='Product Name'
)
fig.update_yaxes(title_text='Total Benefit', secondary_y=False)
fig.update_yaxes(title_text='Average Discount Rate (%)', secondary_y=True)
fig.update_layout(height=600)  # Set the height of the chart)
st.plotly_chart(fig, use_container_width=True)

## LOW PRODUCTS-----------------------------------------------------------------------------------------------------------------------------------------------------------
st.markdown("---")
st.markdown("<h3 style='text-align: center;'>Lowest Benefit Products</h3>", unsafe_allow_html=True)
# Create a figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add Total Benefit to the chart
fig.add_trace(
    go.Bar(x=low_products['Product Name'], y=low_products['Order Item Total'], name='Sales', offsetgroup=1),
    secondary_y=False,
)

# Add Total Benefit to the chart
fig.add_trace(
    go.Bar(x=low_products['Product Name'], y=low_products['Order Profit Per Order'], name='Profit', offsetgroup=2),
    secondary_y=False,
)

# Add Average Discount Rate to the chart
fig.add_trace(
    go.Scatter(x=low_products['Product Name'], y=low_products['Order Item Discount Rate'], name='Average Discount Rate', mode='lines'),
    secondary_y=True,
)

# Add titles and labels
fig.update_layout(
    title_text='Total Benefit and Average Discount Rate by Product',
    xaxis_title='Product Name'
)
fig.update_yaxes(title_text='Total Benefit', secondary_y=False)
fig.update_yaxes(title_text='Average Discount Rate (%)', secondary_y=True)
fig.update_layout(height=600)  # Set the height of the chart)
st.plotly_chart(fig, use_container_width=True)

## BRAND WISE TOP BRANDS --------------------------------------------------------------------------------------------------------------------------------------------------
brand_df = filtered_df.groupby(by=["Brand"], as_index=False).agg({
    'Order Item Total': 'sum',
    'Order Profit Per Order': 'sum',
    'Order Item Discount Rate': 'mean',
    'Order Item Quantity': "sum"
})

topbrand_df = brand_df.sort_values(by='Order Profit Per Order', ascending=False)
topbrand_df = topbrand_df.head(7)
lowbrand_df = brand_df.sort_values(by='Order Profit Per Order', ascending=True)
lowbrand_df = lowbrand_df.head(7)
st.markdown("---")
## TOP BRANDS-----------------------------------------------------------------------------------------------------------------------------------------------------------
st.markdown("<h3 style='text-align: center;'>Highest Benefit Brands</h3>", unsafe_allow_html=True)
# Create a figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add Total Benefit to the chart
fig.add_trace(
    go.Bar(x=topbrand_df['Brand'], y=topbrand_df['Order Item Total'], name='Sales', offsetgroup=1),
    secondary_y=False,
)

# Add Total Benefit to the chart
fig.add_trace(
    go.Bar(x=topbrand_df['Brand'], y=topbrand_df['Order Profit Per Order'], name='Profit', offsetgroup=2),
    secondary_y=False,
)

# Add Average Discount Rate to the chart
fig.add_trace(
    go.Scatter(x=topbrand_df['Brand'], y=topbrand_df['Order Item Discount Rate'], name='Average Discount Rate', mode='lines'),
    secondary_y=True,
)

# Add titles and labels
fig.update_layout(
    title_text='Highest Benefit and Average Discount Rate by Brands',
    xaxis_title='Brand'
)
fig.update_yaxes(title_text='Total Benefit', secondary_y=False)
fig.update_yaxes(title_text='Average Discount Rate (%)', secondary_y=True)
fig.update_layout(height=600)  # Set the height of the chart)
st.plotly_chart(fig, use_container_width=True)

## LOW BRANDS-----------------------------------------------------------------------------------------------------------------------------------------------------------
st.markdown("---")
st.markdown("<h3 style='text-align: center;'>Lowest Benefit Brands</h3>", unsafe_allow_html=True)
# Create a figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add Total Benefit to the chart
fig.add_trace(
    go.Bar(x=lowbrand_df['Brand'], y=lowbrand_df['Order Item Total'], name='Sales', offsetgroup=1),
    secondary_y=False,
)

# Add Total Benefit to the chart
fig.add_trace(
    go.Bar(x=lowbrand_df['Brand'], y=lowbrand_df['Order Profit Per Order'], name='Profit', offsetgroup=2),
    secondary_y=False,
)

# Add Average Discount Rate to the chart
fig.add_trace(
    go.Scatter(x=lowbrand_df['Brand'], y=lowbrand_df['Order Item Discount Rate'], name='Average Discount Rate', mode='lines'),
    secondary_y=True,
)

# Add titles and labels
fig.update_layout(
    title_text='Lowest Benefit and Average Discount Rate by Brands',
    xaxis_title='Brand'
)
fig.update_yaxes(title_text='Total Benefit', secondary_y=False)
fig.update_yaxes(title_text='Average Discount Rate (%)', secondary_y=True)
fig.update_layout(height=600)  # Set the height of the chart)
st.plotly_chart(fig, use_container_width=True)
# col7, col8 = st.columns(2)
# with col7:

##CUSTOMER DATA-------------------
#for top customers
filtered_df['Customer Full Name'] = filtered_df['Customer Fname'] + " " + filtered_df['Customer Lname']
df_corporate = filtered_df[filtered_df['Customer Segment'] == 'Corporate']
df_consumer = filtered_df[filtered_df['Customer Segment'] == 'Consumer']
df_homeoffice = filtered_df[filtered_df['Customer Segment'] == 'Home Office']

#FOR TOP CUSTOMERS
#customer summary for whole dataset
customer_summary = filtered_df.groupby('Customer Id').agg({
    'Order Item Total': 'sum',
    'Order Profit Per Order': 'sum',
    'Customer Full Name': 'first',
    "Order Item Quantity": 'sum'
}).reset_index()

#customer summary for corporate customers dataset
customer_summary_corp = df_corporate.groupby('Customer Id').agg({
    'Order Item Total': 'sum',
    'Order Profit Per Order': 'sum',
    'Customer Full Name': 'first',
    "Order Item Quantity": 'sum'
}).reset_index()

#customer summary for corporate customers dataset
customer_summary_consumer = df_consumer.groupby('Customer Id').agg({
    'Order Item Total': 'sum',
    'Order Profit Per Order': 'sum',
    'Customer Full Name': 'first',
    "Order Item Quantity": 'sum'
}).reset_index()

#customer summary for corporate customers dataset
customer_summary_home = df_homeoffice.groupby('Customer Id').agg({
    'Order Item Total': 'sum',
    'Order Profit Per Order': 'sum',
    'Customer Full Name': 'first',
    "Order Item Quantity": 'sum'
}).reset_index()

corpconsum_profit = customer_summary_corp.sort_values(by='Order Profit Per Order', ascending=False)
corpconsum_profit = corpconsum_profit.head(5)
corpconsum_quantity = customer_summary_corp.sort_values(by='Order Item Quantity', ascending=False)
corpconsum_quantity = corpconsum_quantity.head(5)

custconsum_profit = customer_summary_consumer.sort_values(by='Order Profit Per Order', ascending=False)
custconsum_profit = custconsum_profit.head(5)
custconsum_quantity = customer_summary_consumer.sort_values(by='Order Item Quantity', ascending=False)
custconsum_quantity = custconsum_quantity.head(5)

homeconsum_profit = customer_summary_home.sort_values(by='Order Profit Per Order', ascending=False)
homeconsum_profit = homeconsum_profit.head(5)
homeconsum_quantity = customer_summary_home.sort_values(by='Order Item Quantity', ascending=False)
homeconsum_quantity = homeconsum_quantity.head(5)

st.markdown("---")
st.markdown("<h1 style='text-align: center;'>Customer Segmentation</h1>", unsafe_allow_html=True)
st.subheader(":office: Corporate Consumers")
st.markdown("---")

col7, col8 = st.columns(2)
with col7:
    st.subheader(f":dollar: Top Consumers by Profit") 
    fig = make_subplots(specs=[[{"secondary_y": True}]])   
    # Add Total Benefit to the chart
    fig.add_trace(
        go.Bar(x=corpconsum_profit['Customer Full Name'], y=corpconsum_profit['Order Item Total'], name='Sales', offsetgroup=1),
        secondary_y=False,
    )

    # Add Total Benefit to the chart
    fig.add_trace(
        go.Bar(x=corpconsum_profit['Customer Full Name'], y=corpconsum_profit['Order Profit Per Order'], name='Profit', offsetgroup=2),
        secondary_y=False,
    )

    # Add Average Discount Rate to the chart
    fig.add_trace(
        go.Bar(x=corpconsum_profit['Customer Full Name'], y=corpconsum_profit['Order Item Quantity'], name='Quantity', offsetgroup=3),
        secondary_y=True,
    )

    # Add titles and labels
    fig.update_layout(
        title_text='Top Consumers by Profit',
        xaxis_title='Customer Full Name'
    )
    fig.update_yaxes(title_text='Amount (in $)', secondary_y=False)
    fig.update_yaxes(title_text='Quantity Ordered', secondary_y=True)
    st.plotly_chart(fig, use_container_width=True, height=200)

with col8:
    st.subheader(f":package: Top Consumers by Quantity Ordered") 
    fig = make_subplots(specs=[[{"secondary_y": True}]])   
    # Add Total Benefit to the chart
    fig.add_trace(
        go.Bar(x=corpconsum_quantity['Customer Full Name'], y=corpconsum_quantity['Order Item Total'], name='Sales', offsetgroup=1),
        secondary_y=False,
    )

    # Add Total Benefit to the chart
    fig.add_trace(
        go.Bar(x=corpconsum_quantity['Customer Full Name'], y=corpconsum_quantity['Order Profit Per Order'], name='Profit', offsetgroup=2),
        secondary_y=False,
    )

    # Add Average Discount Rate to the chart
    fig.add_trace(
        go.Bar(x=corpconsum_quantity['Customer Full Name'], y=corpconsum_quantity['Order Item Quantity'], name='Quantity', offsetgroup=3),
        secondary_y=True,
    )

    # Add titles and labels
    fig.update_layout(
        title_text='Top Consumers by Quantity Ordered',
        xaxis_title='Customer Full Name'
    )
    fig.update_yaxes(title_text='Amount (in $)', secondary_y=False)
    fig.update_yaxes(title_text='Quantity Ordered', secondary_y=True)
    st.plotly_chart(fig, use_container_width=True, height=200)

##### MAP DATA ####
# # Plotting the data
# fig = px.scatter_geo(filtered_df, lat='Latitude', lon='Longitude', text='Department Name')

# # Show the figure
# st.plotly_chart(fig, use_container_width=True)
st.subheader(":male-office-worker: Customer Consumers")
st.markdown("---")

col9, col10 = st.columns(2)
with col9:
    st.subheader(f":dollar: Top Consumers by Profit") 
    fig = make_subplots(specs=[[{"secondary_y": True}]])   
    # Add Total Benefit to the chart
    fig.add_trace(
        go.Bar(x=custconsum_profit['Customer Full Name'], y=custconsum_profit['Order Item Total'], name='Sales', offsetgroup=1),
        secondary_y=False,
    )

    # Add Total Benefit to the chart
    fig.add_trace(
        go.Bar(x=custconsum_profit['Customer Full Name'], y=custconsum_profit['Order Profit Per Order'], name='Profit', offsetgroup=2),
        secondary_y=False,
    )

    # Add Average Discount Rate to the chart
    fig.add_trace(
        go.Bar(x=custconsum_profit['Customer Full Name'], y=custconsum_profit['Order Item Quantity'], name='Quantity', offsetgroup=3),
        secondary_y=True,
    )

    # Add titles and labels
    fig.update_layout(
        title_text='Top Consumers by Profit',
        xaxis_title='Customer Full Name'
    )
    fig.update_yaxes(title_text='Amount (in $)', secondary_y=False)
    fig.update_yaxes(title_text='Quantity Ordered', secondary_y=True)
    st.plotly_chart(fig, use_container_width=True, height=200)

with col10:
    st.subheader(f":package: Top Consumers by Quantity Ordered") 
    fig = make_subplots(specs=[[{"secondary_y": True}]])   
    # Add Total Benefit to the chart
    fig.add_trace(
        go.Bar(x=custconsum_quantity['Customer Full Name'], y=custconsum_quantity['Order Item Total'], name='Sales', offsetgroup=1),
        secondary_y=False,
    )

    # Add Total Benefit to the chart
    fig.add_trace(
        go.Bar(x=custconsum_quantity['Customer Full Name'], y=custconsum_quantity['Order Profit Per Order'], name='Profit', offsetgroup=2),
        secondary_y=False,
    )

    # Add Average Discount Rate to the chart
    fig.add_trace(
        go.Bar(x=custconsum_quantity['Customer Full Name'], y=custconsum_quantity['Order Item Quantity'], name='Quantity', offsetgroup=3),
        secondary_y=True,
    )

    # Add titles and labels
    fig.update_layout(
        title_text='Top Consumers by Quantity Ordered',
        xaxis_title='Customer Full Name'
    )
    fig.update_yaxes(title_text='Amount (in $)', secondary_y=False)
    fig.update_yaxes(title_text='Quantity Ordered', secondary_y=True)
    st.plotly_chart(fig, use_container_width=True, height=200)

st.subheader(":derelict_house_building: Home Office Consumers")
st.markdown("---")

col11, col12 = st.columns(2)
with col11:
    st.subheader(f":dollar: Top Consumers by Profit") 
    fig = make_subplots(specs=[[{"secondary_y": True}]])   
    # Add Total Benefit to the chart
    fig.add_trace(
        go.Bar(x=homeconsum_profit['Customer Full Name'], y=homeconsum_profit['Order Item Total'], name='Sales', offsetgroup=1),
        secondary_y=False,
    )

    # Add Total Benefit to the chart
    fig.add_trace(
        go.Bar(x=homeconsum_profit['Customer Full Name'], y=homeconsum_profit['Order Profit Per Order'], name='Profit', offsetgroup=2),
        secondary_y=False,
    )

    # Add Average Discount Rate to the chart
    fig.add_trace(
        go.Bar(x=homeconsum_profit['Customer Full Name'], y=homeconsum_profit['Order Item Quantity'], name='Quantity', offsetgroup=3),
        secondary_y=True,
    )

    # Add titles and labels
    fig.update_layout(
        title_text='Top Consumers by Profit',
        xaxis_title='Customer Full Name'
    )
    fig.update_yaxes(title_text='Amount (in $)', secondary_y=False)
    fig.update_yaxes(title_text='Quantity Ordered', secondary_y=True)
    st.plotly_chart(fig, use_container_width=True, height=200)

with col12:
    st.subheader(f":package: Top Consumers by Quantity Ordered") 
    fig = make_subplots(specs=[[{"secondary_y": True}]])   
    # Add Total Benefit to the chart
    fig.add_trace(
        go.Bar(x=homeconsum_quantity['Customer Full Name'], y=homeconsum_quantity['Order Item Total'], name='Sales', offsetgroup=1),
        secondary_y=False,
    )

    # Add Total Benefit to the chart
    fig.add_trace(
        go.Bar(x=homeconsum_quantity['Customer Full Name'], y=homeconsum_quantity['Order Profit Per Order'], name='Profit', offsetgroup=2),
        secondary_y=False,
    )

    # Add Average Discount Rate to the chart
    fig.add_trace(
        go.Bar(x=homeconsum_quantity['Customer Full Name'], y=homeconsum_quantity['Order Item Quantity'], name='Quantity', offsetgroup=3),
        secondary_y=True,
    )

    # Add titles and labels
    fig.update_layout(
        title_text='Top Consumers by Quantity Ordered',
        xaxis_title='Customer Full Name'
    )
    fig.update_yaxes(title_text='Amount (in $)', secondary_y=False)
    fig.update_yaxes(title_text='Quantity Ordered', secondary_y=True)
    st.plotly_chart(fig, use_container_width=True, height=200)

##################LOGISTICS#######################################################################################
st.markdown("---")
st.markdown("<h1 style='text-align: center;'>LOGISTICS DATA</h1>", unsafe_allow_html=True)
shipping_mode_counts = filtered_df['Shipping Mode'].value_counts().reset_index()
shipping_mode_counts.columns = ['Shipping Mode', 'count']
shipping_mode_late_counts = filtered_df[filtered_df['Delivery Status']=="Late delivery"]['Shipping Mode'].value_counts().reset_index()
shipping_mode_late_counts.columns = ['Shipping Mode', 'count']

col13, col14=st.columns(2)

with col13:
    # Now create the pie chart
    fig = px.pie(shipping_mode_counts, values='count', names='Shipping Mode', 
                title='Class Contribution in Total Orders', 
                hole=0.5, # If you want a donut chart, set a value between 0 and 1
                color_discrete_sequence=px.colors.qualitative.Set1) # This sets the color sequence

    # Optional: Customize the layout
    fig.update_traces(textinfo='percent+label', pull=[0.1, 0, 0, 0])  # 'pull' pulls slices from the center

    st.plotly_chart(fig, use_container_width=True, height=200)

with col14:
    # Now create the pie chart
    fig = px.pie(shipping_mode_late_counts, values='count', names='Shipping Mode', 
                title='Class Contribution in Late Orders', 
                hole=0.5, # If you want a donut chart, set a value between 0 and 1
                color_discrete_sequence=px.colors.qualitative.Set1) # This sets the color sequence

    # Optional: Customize the layout
    fig.update_traces(textinfo='percent+label', pull=[0.1, 0, 0, 0])  # 'pull' pulls slices from the center

    st.plotly_chart(fig, use_container_width=True, height=200)

st.subheader("Within-Class Late Delivery")

std_shipdata = filtered_df[filtered_df['Shipping Mode']=="Standard Class"]
std_shipdata = std_shipdata.groupby("Delivery Status")['Type'].count()
std_shipdata_df = pd.DataFrame()
std_shipdata_df['Delivery Status'] = std_shipdata.index
std_shipdata_df['Count'] = std_shipdata.values

fcshipdata = filtered_df[filtered_df['Shipping Mode']=="First Class"]
fcshipdata = fcshipdata.groupby("Delivery Status")['Type'].count()
fcshipdata_df = pd.DataFrame()
fcshipdata_df['Delivery Status'] = fcshipdata.index
fcshipdata_df['Count'] = fcshipdata.values

scshipdata = filtered_df[filtered_df['Shipping Mode']=="Second Class"]
scshipdata = scshipdata.groupby("Delivery Status")['Type'].count()
scshipdata_df = pd.DataFrame()
scshipdata_df['Delivery Status'] = scshipdata.index
scshipdata_df['Count'] = scshipdata.values

sdshipdata = filtered_df[filtered_df['Shipping Mode']=="Same Day"]
sdshipdata = sdshipdata.groupby("Delivery Status")['Type'].count()
sdshipdata_df = pd.DataFrame()
sdshipdata_df['Delivery Status'] = sdshipdata.index
sdshipdata_df['Count'] = sdshipdata.values

col15, col16 = st.columns(2)
with col15:
    st.subheader("Standard Shipping")
    fig = px.pie(std_shipdata_df, values='Count', names='Delivery Status')
    st.plotly_chart(fig, use_container_width=True, height=500)

    st.subheader("First Class Shipping")
    fig = px.pie(fcshipdata_df, values='Count', names='Delivery Status')
    st.plotly_chart(fig, use_container_width=True, height=500)

with col16:
    st.subheader("Second Class Shipping")
    fig = px.pie(scshipdata_df, values='Count', names='Delivery Status')
    st.plotly_chart(fig, use_container_width=True, height=500)

    st.subheader("Same Day Shipping")
    fig = px.pie(sdshipdata_df, values='Count', names='Delivery Status')
    st.plotly_chart(fig, use_container_width=True, height=500)
##################################################################################################################
st.subheader("Mean and Median for late data by Delivery Modes")
latedata = filtered_df[filtered_df['Delivery Status']=="Late delivery"]
median_latedata = latedata.groupby("Shipping Mode")['Days for shipping (real)'].median()
mean_latedata = latedata.groupby("Shipping Mode")['Days for shipping (real)'].mean()
# fig = px.bar(median_latedata, x=median_latedata.index, y=median_latedata.values, offset=0)
fig = make_subplots()

# Add Total Benefit to the chart
fig.add_trace(
    go.Bar(x=median_latedata.index, y=median_latedata.values, name="Median Late Data", offsetgroup=0)
)

# Add Total Benefit to the chart
fig.add_trace(
    go.Bar(x=mean_latedata.index, y=mean_latedata.values, name="Mean Late Data",offsetgroup=1)
)
# Show the plot
st.plotly_chart(fig, use_container_width=True, height=300)
##################################################################################################################
st.markdown("---")
filtered_df['shipping date (DateOrders)'] = pd.to_datetime(filtered_df['shipping date (DateOrders)'], format="%d-%m-%Y %H:%M")
filtered_df['order date (DateOrders)'] = pd.to_datetime(filtered_df['order date (DateOrders)'], format="%d-%m-%Y %H:%M")
filtered_df['ordtoship time']=(filtered_df['shipping date (DateOrders)'] - filtered_df['order date (DateOrders)']).dt.total_seconds()/3600
filtered_df['ordtoship time']=filtered_df['ordtoship time'].astype('int')

def ord_to_ship_hours(x):
    if x<=12:
        return 12
    elif x>12 and x<=48:
        return 48
    elif x>48 and x<=72:
        return 72
    elif x>72 and x<=96:
        return 96
    elif x>96 and x<=120:
        return 120
    else:
        return 144
    
filtered_df['ordtoship time'] = filtered_df['ordtoship time'].apply(ord_to_ship_hours)
unique_ordtoshiptime = filtered_df['ordtoship time'].unique()

st.subheader("Order to Shipment Time")
col17, col18 = st.columns(2)
with col17:
    total_orders=filtered_df.groupby(['ordtoship time','Shipping Mode'])['Order Id'].nunique().reset_index(name='count')
    fig = px.bar(total_orders, x='ordtoship time', y='count', color='Shipping Mode', 
                title='Distribution of total orders for Order time to Shipping time hours')

    st.plotly_chart(fig, use_container_width=True, height=200)

with col18:
    late_orders=filtered_df[filtered_df['Delivery Status']=='Late delivery'].groupby(['ordtoship time','Shipping Mode'])['Order Id'].nunique().reset_index(name='count')
    fig = px.bar(late_orders, x='ordtoship time', y='count', color='Shipping Mode', 
                title='Distribution of Late Orders for Order time to Shipping time hours')

    st.plotly_chart(fig, use_container_width=True, height=200)

#### Order Late by Hours#######################################################################################################
# Group and sum the data
st.subheader("Risk of Late Delivery by Order Placed Time")
filtered_df['Order Hour']=filtered_df['order date (DateOrders)'].dt.hour
grouped_data = filtered_df.groupby('Order Hour')['Late_delivery_risk'].sum()

# Calculate the mean
mean_late_delivery_risk = grouped_data.mean()

# Create a line chart
line_chart = go.Scatter(x=grouped_data.index, y=grouped_data.values, mode='lines')

# Create a layout, including a horizontal line for the mean
layout = go.Layout(
    title='Late Delivery Risk vs Order Hour',
    xaxis=dict(title='Order Hour'),
    yaxis=dict(title='Number of Late Delivery Risk'),
    shapes=[
        # Line Horizontal Mean Line
        {
            'type': 'line',
            'x0': min(grouped_data.index),
            'x1': max(grouped_data.index),
            'y0': mean_late_delivery_risk,
            'y1': mean_late_delivery_risk,
            'line': {
                'color': 'red',
                'width': 2,
                'dash': 'dash',
            },
        }
    ]
)

# Create the figure and plot it
fig = go.Figure(data=[line_chart], layout=layout)
st.plotly_chart(fig, use_container_width=True, height=200)

################################################################################################################################
#Probability of late or delivery cancelled by Brands
prob=[]
names=[]
for i in filtered_df['Brand'].value_counts().index:
    df_prod=filtered_df[filtered_df['Brand']==i]
    vc=df_prod['Delivery Status'].value_counts()
    n=vc.index
    v=vc.values
    s=0
    names.append(i)
    for j,k in zip(n,v):
        if j in ['Late delivery','Shipping canceled']:
            s=s+k
    # print(f"{i} : {s/sum(v)}")
    prob.append(s/sum(v))
pr=pd.DataFrame()
pr['Brand']=names
pr['Probability of Late Delivery/ Shipping Cancelled']=prob
pr=pr.sort_values(by=['Probability of Late Delivery/ Shipping Cancelled'],ascending=False)
top5 = pr.nlargest(10, 'Probability of Late Delivery/ Shipping Cancelled')
# Get the bottom 5 values
# bottom5 = pr.nsmallest(5, 'Probability of Late Delivery/ Shipping Cancelled')
# Concatenate the two DataFrames
# pr_new = pd.concat([top5, bottom5])

col19, col20 = st.columns(2)
with col19:
    st.subheader(f"Brand Wise Probabilities of Late Delivery")
    fig = px.bar(top5, x="Brand", y="Probability of Late Delivery/ Shipping Cancelled", text = ['{:,.2f}'.format(x) for x in top5['Probability of Late Delivery/ Shipping Cancelled']],
                 template = "seaborn",)
    st.plotly_chart(fig, use_container_width=True, height=200)

#Probability of late or delivery cancelled by Brands
prob=[]
names=[]
for i in filtered_df['Product Name'].value_counts().index:
    df_prod=filtered_df[filtered_df['Product Name']==i]
    vc=df_prod['Delivery Status'].value_counts()
    n=vc.index
    v=vc.values
    s=0
    names.append(i)
    for j,k in zip(n,v):
        if j in ['Late delivery','Shipping canceled']:
            s=s+k
    # print(f"{i} : {s/sum(v)}")
    prob.append(s/sum(v))
pr=pd.DataFrame()
pr['Product Name']=names
pr['Probability of Late Delivery/ Shipping Cancelled']=prob
pr=pr.sort_values(by=['Probability of Late Delivery/ Shipping Cancelled'],ascending=False)
top5 = pr.nlargest(10, 'Probability of Late Delivery/ Shipping Cancelled')
# Get the bottom 5 values
# bottom5 = pr.nsmallest(5, 'Probability of Late Delivery/ Shipping Cancelled')
# Concatenate the two DataFrames
# pr_new = pd.concat([top5, bottom5])

with col20:
    st.subheader(f"Product Wise Probabilities of Late Delivery")
    fig = px.bar(top5, x="Product Name", y="Probability of Late Delivery/ Shipping Cancelled", text = ['{:,.2f}'.format(x) for x in top5['Probability of Late Delivery/ Shipping Cancelled']],
                 template = "seaborn",)
    st.plotly_chart(fig, use_container_width=True, height=200)
