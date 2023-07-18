import requests
import pandas as pd
import datetime as dt_
from io import StringIO
from datetime import datetime, timedelta
import streamlit as st
import re


def initialize_streamlit():
    """Initialize Streamlit interface by setting the title and instructions."""
    st.title("Icebergs Revenue Report")
    st.write("Select a date to see the revenue generated")


def get_start_date():
    """Prompt user to select a date using Streamlit and return selected date with specific time combined."""
    # Select a date range
    start_date = st.date_input("Select a date", dt_.date(2023, 7, 18))
    selected_time = datetime.strptime("03:00:00", "%H:%M:%S").time()

    return datetime.combine(start_date, selected_time)


def get_end_date(dt_start):
    """Get end date which is one day ahead of the start date."""
    return dt_start + timedelta(days=1)


def convert_date_format(date_time, flag):
    """Convert date_time object to a specific string format."""
    return (
        date_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        if flag == "start"
        else date_time.strftime("%Y-%m-%dT%H:%M:%S" ".999Z")
    )


def get_csv_from_api(start_date_time, end_date_time):
    """Make API request to fetch CSV data and return it as pandas DataFrame."""
    api_endpoint = f"https://api-vendor.qlub.cloud/v1/vendor/order/download/3403?fileFormat=csv&startDate={start_date_time}&endDate={end_date_time}"
    header = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": "Bearer eyJraWQiOiJoK3FlUnBNMWNrcFdXYW10UkJ0Q0ROMGt1bERQaFlUaEVSd3Q5Wmd4YXBRPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIzMjI2MWY0Zi1hZGU0LTQzZjItOTZhNy01ZTVkMGU0ZmM0YzQiLCJjb2duaXRvOmdyb3VwcyI6WyJRbHViQWRtaW4iXSwiZW1haWxfdmVyaWZpZWQiOnRydWUsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC5hcC1zb3V0aGVhc3QtMS5hbWF6b25hd3MuY29tXC9hcC1zb3V0aGVhc3QtMV9NY3BGem16cDMiLCJjb2duaXRvOnVzZXJuYW1lIjoiMzIyNjFmNGYtYWRlNC00M2YyLTk2YTctNWU1ZDBlNGZjNGM0Iiwib3JpZ2luX2p0aSI6IjE1MjM3N2YxLTBlNDUtNDQ1MS1hNWE5LTgwZjM2Y2FlZGFhNiIsImF1ZCI6IjRpNGhpNGFmYThnOXVkcmRkZXByMGxqYzR1IiwiZXZlbnRfaWQiOiI5NzNkOTA2Yi1kNTRlLTRlZjktYmMwMi1iYTJhYjM1MTZlZWYiLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTY4ODYyMTgxOSwiZXhwIjoxNjg5NzM4MzI1LCJpYXQiOjE2ODk2NTE5MjUsImp0aSI6ImNmNThkN2M3LTdiM2YtNDRjNC05YTRkLTdmOTRjMjY4ZTM5NSIsImVtYWlsIjoicHJlcml0aC5zdWJyYW1hbnlhQHFsdWIuaW8ifQ.lCsNK8g5fUZ77WJeFasiI6VB1FnYjEw78aoj6xVo-LVi8TrsZH7IP2xrrLEYAcnGxHAtlXCl1xJmllAo9EoHnMPw3XYVK40qsuHiXXoGpOdukNeI0imenhmLL_FRE9GtSBxQsABhXa6-3JQcBZfIYB4KVdV5IDrE14eyeYCtg2QccLaM_iVDexhSgppR6dts_zEwhedlKGsklDjsQTFGcbizhsFJdhGjp1M0qeEh9TUYgUTU255pT_GKGQc9LmgSGNlKOy8nZVFXVRo6J-TsXyw8wnl6MwgOdL6b6AoneawuHUV8OzaDg3T-nvwEuNZDAb1HXK4qoAQIDAe-MSuqKQ",
    }

    response = requests.get(api_endpoint, headers=header)
    data = StringIO(response.text)
    return pd.read_csv(data, sep=",") if response.status_code == 200 else None


def process_csv_data(csv_df, start_date_time, end_date_time):
    """Process the CSV data and return the revenues, tips and surcharges."""
    qdf_total = 0
    bill_3 = 0
    tips_total = 0
    bill_5 = 0
    total_bill = 0
    bill_4 = 0
    table_list = [
        100,
        150,
        200,
        250,
        300,
        350,
        400,
        450,
        500,
        550,
        600,
        650,
        700,
        750,
        800,
        900,
        1000,
        1050,
        2000,
        2050,
        4000,
        4050,
        5000,
        5050,
        6000,
        6050,
        7000,
        7050,
        "B1",
        "B2",
        "B3",
    ]

    for index, row in csv_df.iterrows():
        try:
            row_date = datetime.strptime(str(row["DateTime"]), "%m/%d/%Y %H:%M %p")
        except ValueError:
            continue
        start_date = datetime.strptime(start_date_time, "%Y-%m-%dT%H:%M:%S.000Z")
        end_date = datetime.strptime(end_date_time, "%Y-%m-%dT%H:%M:%S.999Z")

        if start_date <= row_date < end_date:
            qdf_total += float(row["QlubDinerFee"])
            total_bill += float(row["PaidAmount"])
            tips_total += float(row["TipAmount"])
            table_number = re.findall(r"\d+|B\d+", str(row["TableID"]))
            if table_number and table_number[0] in table_list:
                bill_3 += float(row["PaidAmount"])  # bar_bill
                bill_4 += float(row["QlubDinerFee"])  # bar_qdf
                bill_5 += float(row["TipAmount"])  # bar_tips

    return qdf_total, total_bill, tips_total, bill_3, bill_4, bill_5


def display_results(total_bill, tips_total, qdf_total, bill_3, bill_4, bill_5):
    """Display the results in a table."""
    st.subheader("Revenue Summary")
    st.write("The revenue for the selected date is as follows:")
    bill_0 = "${0:.2f}".format(total_bill - bill_3)  # dining_bill
    bill_1 = "${0:.2f}".format(tips_total - bill_5)  # dining_tips
    bill_2 = "${0:.2f}".format(qdf_total - bill_4)  # dining_qdf
    bill_3 = "${0:.2f}".format(bill_3)  # bar_bill
    bill_4 = "${0:.2f}".format(bill_4)  # bar_qdf
    bill_5 = "${0:.2f}".format(bill_5)  # bar_tip

    figure_list = [bill_0, bill_1, bill_2, bill_3, bill_4, bill_5]
    st.table(
        pd.DataFrame(
            [figure_list],
            columns=[
                "Dining Revenue",
                "Dining Tips",
                "Dining Surcharge",
                "Bar Revenue",
                "Bar Tips",
                "Bar Surcharge",
            ],
        )
    )


def main():
    """Main function to run the revenue report generator."""
    initialize_streamlit()
    dt_start = get_start_date()
    dt_end = get_end_date(dt_start)

    start_date_time = convert_date_format(dt_start, "start")
    end_date_time = convert_date_format(dt_end, "end")

    csv_df = get_csv_from_api(start_date_time, end_date_time)
    if csv_df is not None:
        qdf_total, total_bill, tips_total, bill_3, bill_4, bill_5 = process_csv_data(
            csv_df, start_date_time, end_date_time
        )
        display_results(total_bill, tips_total, qdf_total, bill_3, bill_4, bill_5)
    else:
        st.write("Unable to fetch data. Please check the date and try again.")


if __name__ == "__main__":
    main()
