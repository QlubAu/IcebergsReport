import requests
import pandas as pd
from io import StringIO
from datetime import datetime
import streamlit as st
import re
from decimal import Decimal, InvalidOperation


def initialize_streamlit():
    """Initialize Streamlit interface by setting the title and instructions."""
    st.title("Icebergs Revenue Report")
    st.write("Select a date to see the revenue generated")


def get_start_date():
    """Prompt user to select a date using Streamlit and return selected date with specific time combined."""
    # Use current date as default
    current_date = datetime.now().date()

    # Select a date
    start_date = st.date_input("Select a date", current_date)
    selected_time = datetime.strptime("00:00:00", "%H:%M:%S").time()

    return datetime.combine(start_date, selected_time)


def get_end_date(dt_start):
    """Get end date which is one day ahead of the start date."""
    # Modify the time
    return dt_start.replace(hour=23, minute=59, second=59)


def convert_date_format(date_time, flag):
    """Convert date_time object to a specific string format."""
    return (
        date_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        if flag == "start"
        else date_time.strftime("%Y-%m-%dT%H:%M:%S" ".999Z")
    )


@st.cache_data(ttl=12 * 3600)
def get_token() -> str:
    """Get token from vendor panel login"""

    token_url = "https://api-vendor.qlub.cloud/v1/auth/login"
    header = {"Accept": "application/json"}
    data = {
        "email": st.secrets["email"],
        "password": st.secrets["password"],
        "type": "admin",
    }

    try:
        response = requests.post(token_url, headers=header, json=data)
        return f'Bearer {response.json()["data"]["cognitoUser"]["signInUserSession"]["idToken"]["jwtToken"]}'
    except Exception as e:
        raise e


def get_csv_from_api(start_date_time, end_date_time):
    """Make API request to fetch CSV data and return it as pandas DataFrame."""
    print(start_date_time, end_date_time)
    api_endpoint = (f"https://api-vendor.qlub.cloud/v1/vendor/transaction"
                    f"/download/3403?fileFormat=csv&startDate={start_date_time}&endDate={end_date_time}")
    header = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": get_token(),
    }

    try:
        response = requests.get(api_endpoint, headers=header)
        data = StringIO(response.text)
        if response.status_code == 200:
            print(response.status_code)
            return pd.read_csv(data, sep=",")
        else:
            print(response.status_code)
    except Exception as e:
        raise e


def process_csv_data(csv_df, start_date_time, end_date_time):
    """Process the CSV data and return the revenues, tips and surcharges."""
    qdf_total = Decimal('0')
    total_bill = Decimal('0')
    tips_total = Decimal('0')
    bill_3 = Decimal('0')  # bar_bill
    bill_4 = Decimal('0')  # bar_qdf
    bill_5 = Decimal('0')  # bar_tips
    table_list = [
        "100",
        "150",
        "200",
        "250",
        "300",
        "350",
        "400",
        "450",
        "500",
        "550",
        "600",
        "650",
        "700",
        "750",
        "800",
        "900",
        "1000",
        "1050",
        "2000",
        "2050",
        "4000",
        "4050",
        "5000",
        "5050",
        "6000",
        "6050",
        "7000",
        "7050",
        "B1",
        "B2",
        "B3",
        "POS-1",
        "POS-2",
        "POS-3",
    ]

    for index, row in csv_df.iterrows():
        try:
            row_date = datetime.strptime(str(row["DateTime"]), "%m/%d/%Y %H:%M %p")
        except ValueError:
            continue
        start_date = datetime.strptime(start_date_time, "%Y-%m-%dT%H:%M:%S.000Z")
        end_date = datetime.strptime(end_date_time, "%Y-%m-%dT%H:%M:%S.999Z")

        if start_date <= row_date < end_date:
            # print(f"Iteration {index}, total_bill: {total_bill}, qdf_total: {qdf_total}, tips_total: {tips_total}")
            for field in ["QlubDinerFee", "PaidAmount", "TipAmount"]:
                if pd.isna(row[field]):
                    value = Decimal('0')
                else:
                    try:
                        value = Decimal(str(row[field]))
                    except (InvalidOperation, ValueError):
                        value = Decimal('0')
                    if field == "QlubDinerFee":
                        qdf_total += value
                    elif field == "PaidAmount":
                        total_bill += value
                    elif field == "TipAmount":
                        tips_total += value

                table_number = re.findall(r"\d+|B\d+", str(row["Table"]))
                if table_number and table_number[0] in table_list:
                    print(table_number[0])
                    print(value if field == "PaidAmount" else Decimal('0'))
                    bill_3 += value if field == "PaidAmount" else Decimal('0')
                    bill_4 += value if field == "QlubDinerFee" else Decimal('0')
                    bill_5 += value if field == "TipAmount" else Decimal('0')
    return qdf_total, total_bill, tips_total, bill_3, bill_4, bill_5


def display_results(
        total_bill, tips_total, qdf_total, bill_3, bill_4, bill_5
):
    """Display the results in a table."""
    print(total_bill, bill_3)
    st.subheader("Revenue Summary")
    st.write("The revenue for the selected date is as follows:")
    bill_0 = "${0:.2f}".format(total_bill - bill_3)  # dining_bill
    bill_1 = "${0:.2f}".format(tips_total - bill_5)  # dining_tips
    bill_2 = "${0:.2f}".format(qdf_total - bill_4)  # dining_qdf
    bill_3 = "${0:.2f}".format(bill_3)  # bar_bill
    bill_4 = "${0:.2f}".format(bill_4)  # bar_qdf
    bill_5 = "${0:.2f}".format(bill_5)  # bar_tip
    # bill_6 = "${0:.2f}".format(refund_total - refund_bar)  # dining refund
    # bill_7 = "${0:.2f}".format(refund_bar)
    figure_list = [bill_0, bill_1, bill_2, bill_3, bill_5, bill_4]
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
    with st.spinner("Loading.."):
        csv_df = get_csv_from_api(start_date_time, end_date_time)
        print(csv_df.shape)
        if csv_df is not None:
            (
                qdf_total,
                total_bill,
                tips_total,
                bill_3,
                bill_4,
                bill_5,
            ) = process_csv_data(csv_df, start_date_time, end_date_time)
    if csv_df is not None:
        display_results(
            total_bill,
            tips_total,
            qdf_total,
            bill_3,
            bill_4,
            bill_5,
        )
    else:
        st.write("Unable to fetch data. Please check the date and try again.")


if __name__ == "__main__":
    main()
