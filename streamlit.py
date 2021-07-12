
from simple_salesforce import Salesforce
import requests
import csv
import pandas as pd
from io import StringIO
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')
import os
import glob
import numpy as np
import time
import streamlit as st

pwd = st.sidebar.text_input("Password:", value="", type="password")

    
if pwd != 'AllenDeary':
    st.error('Enter Password')
    

else:
    
    rad = st.sidebar.radio('Navigation', ['About', 'Melterizer', 'Archive'])




    if rad == 'About':
        st.header('This is a beta version of Melterizer')


    if rad == 'Melterizer':
        st.title('Melterizer')


        time_now = time.time()
        full_now = datetime.datetime.fromtimestamp(time_now).strftime('%Y-%m-%d %H:%M:%S')
        st.subheader('Net Bookings change as of {}'.format(full_now))

        left_column, right_column = st.beta_columns(2)

        sf = Salesforce(username='sfapi@openexc.com', password='Welcome#0E', security_token='J4HtMUWKvLCUFPDw36V4WPtQ')

            # Basic report URL structure:
        orgParams = 'https://openexchange.lightning.force.com/' # you can see this in your Salesforce URL
        exportParams = '?isdtp=p1&export=1&enc=UTF-8&xf=csv'

            # Download Orders/Bookings report:
        reportId = '00O1L000007mjecUAA' # You find this in the URL of the report in question between "Report/" and "/view"
        reportUrl = orgParams + reportId + exportParams
        reportReq = requests.get(reportUrl, headers=sf.headers, cookies={'sid': sf.session_id})
        reportData = reportReq.content.decode('utf-8')
        active_report = pd.read_csv(StringIO(reportData))
        active_report = active_report[active_report['Status'] != 'Cancelled']

        active_report['Business Line'] = np.where(active_report['Business Line'] == 'Corporate StreamLinks', 'Subscription', active_report['Business Line'])
        active_report['Business Line'] = np.where(active_report['Business Line'] == 'Knovio', 'Subscription', active_report['Business Line'])

            #Static Report
        list_of_files = glob.glob('/Users/seanmullins/Desktop/Booking_Static/*') # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        static_report = pd.read_excel(latest_file)
        static_report = static_report[static_report['Status'] != 'Cancelled']
        static_report['Business Line'] = np.where(static_report['Business Line'] == 'Corporate StreamLinks', 'Subscription', static_report['Business Line'])
        static_report['Business Line'] = np.where(static_report['Business Line'] == 'Knovio', 'Subscription', static_report['Business Line'])


         #GET PIVOTS

        active_report_pivot = active_report.pivot_table(values='Order Amount (converted)', index=['Region'], \
                                 columns=['Business Line'], aggfunc=np.sum, margins=True).fillna(0)

        static_report_pivot = static_report.pivot_table(values='Order Amount (converted)', index=['Region'], \
                                 columns=['Business Line'], aggfunc=np.sum, margins=True).fillna(0)

        final_pivot = active_report_pivot - static_report_pivot
        final_pivot = final_pivot.style.format('$ {:,.1f}')
        st.dataframe(data=final_pivot, width=None, height=None)

        st.markdown('##')

        #Changes Made
        st.subheader('Big Adjustments')

        static_filtered = static_report.filter(items=['Order Number', 'Order Amount (converted)'])
        s1 = pd.merge(active_report, static_filtered, how='left', on=['Order Number'])




        s1['change'] = s1['Order Amount (converted)_x'] - s1['Order Amount (converted)_y']
        s1 = s1.fillna(0)

        s1_changes = s1[((s1['change'] != 0) & (s1['change'] > 3000)) | ((s1['change'] != 0) & (s1['change'] < -3000))]



        s1_changes = s1_changes.filter(items=['Order Number','Account Name', 'Event Name', 'Region', 'change'])
        s1_changes = s1_changes.sort_values(by=['change'], ascending=False)


        def format(x):
            return "${:.1f}K".format(x/1000)


        s1_changes['change'] = s1_changes['change'].apply(format)
        s1_changes = s1_changes.set_index('Order Number')
        st.table(data=s1_changes)

        st.markdown('##')

        st.subheader('Big New Bookings')


        active_index = active_report.set_index('Order Number')
        static_index = static_report.set_index('Order Number')
        s3 = active_index[~active_index.isin(static_index)].dropna()
        s3 = s3.filter(items=['Order Number','Account Name', 'Event Name', 'Region', 'Order Amount (converted)'])
        s3 = s3[s3['Order Amount (converted)'] > 3000]
        s3['Order Amount (converted)'] = s3['Order Amount (converted)'].apply(format)
        st.table(data=s3)

        st.markdown('##')

        st.text('Updating...')
        progress = st.progress(0)
        for i in range(100):
            time.sleep(1)
            progress.progress(i+1)


        st.experimental_rerun()


    if rad == 'Archive':
        st.title('This is where the melt archives will go for historical reference')

   

