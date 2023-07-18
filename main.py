from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from pathlib import Path
import csv
import re
from datetime import datetime, timedelta
import os
import pandas as pd
import plotly.express as px
import streamlit as st


def process_file(file_name):
    qdf_total = 0
    bar_total_bill = 0
    tips_total = 0
    tips_bar = 0
    total_bill = 0
    qdf_bar = 0
    table_list = ['101', '203']

    #now = datetime.now()
    now = datetime(year=2023, month=7, day=14,hour=23,minute=23,second=12)

    if now.hour < 3:
        now = now - timedelta(days=1)

    start_date = now.replace(hour=3, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1)

    with open(file_name, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row_date = datetime.strptime(row['DateTime'], '%m/%d/%Y %H:%M %p')
            except ValueError:
                continue

            if start_date <= row_date < end_date:
                qdf_total += float(row['QlubDinerFee'])
                total_bill += float(row['PaidAmount'])
                tips_total += float(row['TipAmount'])

                table_number = re.findall(r'\d+|B\d+', row['TableID'])
                if table_number and table_number[0] in table_list:
                    bar_total_bill += float(row['PaidAmount'])
                    qdf_bar += float(row['QlubDinerFee'])
                    tips_bar += float(row['TipAmount'])

    dining_total = total_bill - bar_total_bill
    dining_tips = tips_total - tips_bar
    dining_qdf = qdf_total - qdf_bar
    start_date_str = start_date.strftime('%d/%m/%Y')

    output_file = '15_iceberg_check.csv'
    file_exists = os.path.isfile(output_file)
    if file_exists:
        df = pd.read_csv(output_file)
        if start_date_str in df['DATE'].values:
            df.loc[df['DATE'] == start_date_str, 'Total BillAmount for Iceberg Dining'] = dining_total
            df.loc[df['DATE'] == start_date_str, 'Total Tips for Iceberg Dining'] = dining_tips
            df.loc[df['DATE'] == start_date_str, 'Total QlubDinerFee for Iceberg Dining'] = dining_qdf
            df.loc[df['DATE'] == start_date_str, 'Total BillAmount for Iceberg Bar'] = bar_total_bill
            df.loc[df['DATE'] == start_date_str, 'Total Tips for Iceberg Bar'] = tips_bar
            df.loc[df['DATE'] == start_date_str, 'Total QlubDinerFee for Iceberg Bar'] = qdf_bar
        else:
            new_row = {'DATE': start_date_str,
                       'Total BillAmount for Iceberg Dining': dining_total,
                       'Total Tips for Iceberg Dining': dining_tips,
                       'Total QlubDinerFee for Iceberg Dining': dining_qdf,
                       'Total BillAmount for Iceberg Bar': bar_total_bill, 'Total Tips for Iceberg Bar': tips_bar,
                       'Total QlubDinerFee for Iceberg Bar': qdf_bar}
            df = df._append(new_row, ignore_index=True)
        df.to_csv(output_file, index=False)
    else:
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["DATE", "Total BillAmount for Iceberg Dining", "Total Tips for Iceberg Dining",
                             "Total QlubDinerFee for Iceberg Dining", "Total BillAmount for Iceberg Bar",
                             "Total Tips for Iceberg Bar", "Total QlubDinerFee for Iceberg Bar"])
            writer.writerow([start_date_str, dining_total, dining_tips, dining_qdf, bar_total_bill, tips_bar, qdf_bar])
    return output_file
def web_scraper():
    # Define the path for ChromeDriver
    chrome_options = Options()

    # Set up ChromeDriver
    webdriver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    wait = WebDriverWait(driver, 10)
    # Navigate to the login page
    driver.get("https://vendor.qlub.cloud/orders/")
    time.sleep(2)

    # Enter login credentials
    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[2]/div/div[2]/div/div/form/div/div[1]/div/div/input"))).send_keys("stefano@idrb.com")
    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[2]/div/div[2]/div/div/form/div/div[2]/div/div/input"))).send_keys("Qlub!2023")


    # Click on the checkbox and login
    #driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']").click()
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    time.sleep(5)

    # Navigate to dropdown menu and select an option
    dropdown_menu = driver.find_element(By.ID, "select-restaurant-autocomplete")
    dropdown_menu.click()

    time.sleep(5)

    # Select the option
    #option = driver.find_element(By.XPATH, "//li[text()='Iceberg Dining']")
    #option.click()
    # Select the option
    dropdown_menu = wait.until(EC.presence_of_element_located((By.ID, "select-restaurant-autocomplete")))
    dropdown_menu.click()
    input_box = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[2]/div/div[2]/div/div/form/div/div[1]/div/div/div/input")))
    input_box.send_keys("Iceberg Dining")
    time.sleep(2)

    input_box.send_keys(Keys.ARROW_DOWN)  # Send the 'down arrow' key press

    # After the down arrow key press, you may want to press 'Enter' to select the option
    input_box.send_keys(Keys.ENTER)

    # At this point, if there's an autocomplete option for "Iceberg Dining", it should appear. You can then select it by clicking on it.
    #option = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div[2]/div[2]/div/div[2]/div/div[2]/div/div/form/div/div[1]/div/div/div/div/button[2]")))
    #option = driver.find_element(By.XPATH,"/html/body/div/div/div[2]/div[2]/div/div[2]/div/div[2]/div/div/form/div/div[1]/div/div/div/div/button[2]")
    #option.click()
    print("bob")
    time.sleep(3)


    # Click on the select button
    #select_button = driver.find_element(By.ID, "select-res-btn")
    #select_button.click()
    select_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "select-res-btn")))
    select_button.click()

    time.sleep(12)

    # Navigate to the specific webpage
    driver.get("https://vendor.qlub.cloud/orders/")

    time.sleep(5)

    # Click on the Export button
    driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div[2]/div[1]/div/div/button").click()

    time.sleep(5)

    # Click on the radio button 'All' in the popup
    driver.find_element(By.XPATH, "//span[normalize-space()='All']").click()

    # Click on the Export button in the popup
    driver.find_element(By.ID, "action-btn").click()

    time.sleep(5)

    # Define Downloads folder
    downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')

    # Check if the Downloads directory exists
    if not os.path.isdir(downloads_dir):
        print("Downloads directory does not exist.")
    else:
        try:
            # Get list of files sorted by modified time
            files = Path(downloads_dir).glob('*.*')
            files_by_date = sorted(files, key=os.path.getmtime, reverse=True)

            # Check if the Downloads directory is empty
            if not files_by_date:
                print("Downloads directory is empty.")
            else:
                # Get latest downloaded file path
                latest_download = files_by_date[0]
                print(f"The most recently downloaded file is: {latest_download}")

        except Exception as e:
            print(f"An error occurred: {e}")

    # Close the browser
    driver.quit()
    return latest_download


def load_data(file_name):
    return pd.read_csv(file_name, parse_dates=['DATE'],dayfirst=True)


def streamlit_p(csv_file):
    # Set title
    st.title("Iceberg Check Data Analysis")

    # Load data
    data = load_data(csv_file)

    # Set pandas option to display large numbers
    pd.options.display.float_format = '{:,.2f}'.format

    # Display raw data
    if st.button('Display Raw Data'):
        st.subheader('Raw Data')
        st.dataframe(data)

    st.subheader('Visual Analysis')

    # Plot for restaurant revenue
    st.subheader('Restaurant Revenue Analysis')
    fig1 = px.line(data, x='DATE', y='Total BillAmount for Iceberg Dining',
                   title='Time Series Plot of Total BillAmount for Iceberg Dining')
    st.plotly_chart(fig1)

    # Plot for bar revenue
    st.subheader('Bar Revenue Analysis')
    fig2 = px.line(data, x='DATE', y='Total BillAmount for Iceberg Bar',
                   title='Time Series Plot of Total BillAmount for Iceberg Bar')
    st.plotly_chart(fig2)


# Call the function
csv_name = web_scraper()
output = process_file(csv_name)
streamlit_p(output)

