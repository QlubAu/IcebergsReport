# Icebergs Revenue Report Generator

This Python script generates a revenue report for the Icebergs, making use of data fetched from an API and processed through pandas DataFrame.

## Prerequisites

The script requires the following libraries to be installed:

- `requests`
- `pandas`
- `datetime`
- `streamlit`
- `re`

## How to Run

You can run this script by navigating to the script's directory and executing the command:

```bash
streamlit run main.py
```

## Features

- User-friendly interface to select a date to see the revenue generated for that date.
- API request to fetch CSV data from a specific URL.
- Processes CSV data into pandas DataFrame.
- Calculates the total bill, total QDF (QlubDinerFee), total tips, and also segregates the details for bar and dining revenue.
- Displays the results in a user-friendly format using Streamlit.
