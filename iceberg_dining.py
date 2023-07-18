import csv
import os
import pandas as pd
from datetime import datetime, timedelta
import re
import requests

def process_csv_from_api(api_endpoint, output_file):
    qdf_total = 0
    bar_total_bill = 0
    tips_total = 0
    tips_bar = 0
    total_bill = 0
    qdf_bar = 0
    table_list = ['101', '203']

    now = datetime.now()

    if now.hour < 3:
        now = now - timedelta(days=1)

    start_date = now.replace(hour=3, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1)
    header = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": "Bearer eyJraWQiOiJoK3FlUnBNMWNrcFdXYW10UkJ0Q0ROMGt1bERQaFlUaEVSd3Q5Wmd4YXBRPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMjI2MWY0Zi1hZGU0LTQzZjItOTZhNy01ZTVkMGU0ZmM0YzQiLCJjb2duaXRvOmdyb3VwcyI6WyJRbHViQWRtaW4iXSwiZW1haWxfdmVyaWZpZWQiOnRydWUsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC5hcC1zb3V0aGVhc3QtMS5hbWF6b25hd3MuY29tXC9hcC1zb3V0aGVhc3QtMV9NY3BGem16cDMiLCJjb2duaXRvOnVzZXJuYW1lIjoiMzIyNjFmNGYtYWRlNC00M2YyLTk2YTctNWU1ZDBlNGZjNGM0Iiwib3JpZ2luX2p0aSI6IjE1MjM3N2YxLTBlNDUtNDQ1MS1hNWE5LTgwZjM2Y2FlZGFhNiIsImF1ZCI6IjRpNGhpNGFmYThnOXVkcmRkZXByMGxqYzR1IiwiZXZlbnRfaWQiOiI5NzNkOTA2Yi1kNTRlLTRlZjktYmMwMi1iYTJhYjM1MTZlZWYiLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTY4ODYyMTgxOSwiZXhwIjoxNjg5NzM4MzI1LCJpYXQiOjE2ODk2NTE5MjUsImp0aSI6ImNmNThkN2M3LTdiM2YtNDRjNC05YTRkLTdmOTRjMjY4ZTM5NSIsImVtYWlsIjoicHJlcml0aC5zdWJyYW1hbnlhQHFsdWIuaW8ifQ.lCsNK8g5fUZ77WJeFasiI6VB1FnYjEw78aoj6xVo-LVi8TrsZH7IP2xrrLEYAcnGxHAtlXCl1xJmllAo9EoHnMPw3XYVK40qsuHiXXoGpOdukNeI0imenhmLL_FRE9GtSBxQsABhXa6-3JQcBZfIYB4KVdV5IDrE14eyeYCtg2QccLaM_iVDexhSgppR6dts_zEwhedlKGsklDjsQTFGcbizhsFJdhGjp1M0qeEh9TUYgUTU255pT_GKGQc9LmgSGNlKOy8nZVFXVRo6J-TsXyw8wnl6MwgOdL6b6AoneawuHUV8OzaDg3T-nvwEuNZDAb1HXK4qoAQIDAe-MSuqKQ"
    }
    # Make API request to fetch CSV data
    response = requests.get(api_endpoint, headers=header)
    csv_data = response.content

    # Create a temporary file to store the CSV data
    with open('temp.csv', 'w') as temp_file:
        temp_file.write(csv_data)

    with open('temp.csv', 'r') as f:
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
            df = df.append(new_row, ignore_index=True)
        df.to_csv(output_file, index=False)
    else:
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["DATE", "Total BillAmount for Iceberg Dining", "Total Tips for Iceberg Dining",
                             "Total QlubDinerFee for Iceberg Dining", "Total BillAmount for Iceberg Bar",
                             "Total Tips for Iceberg Bar", "Total QlubDinerFee for Iceberg Bar"])
            writer.writerow([start_date_str, dining_total, dining_tips, dining_qdf, bar_total_bill, tips_bar, qdf_bar])

    # Remove the temporary file
    os.remove('temp.csv')

    return output_file

# Example usage

api_endpoint = "https://api-vendor.qlub.cloud/v1/vendor/order/download/3403?fileFormat=csv&startDate=2023-07-16T00:00:00.000Z&endDate=2023-07-16T23:59:59.999Z"
output_file = "15_iceberg_check.csv"
process_csv_from_api(api_endpoint, output_file)
