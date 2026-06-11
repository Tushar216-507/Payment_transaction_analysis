# Rule 1: Flag transactions where amount exceeds 3x the account's median
# Rule 2: Domestic merchant + USD
from services.cleaning_service import cleaned_csv_data

# ================================ RULE 1 FINISHED ===========================================
def _detect_statistical_outliers(cleaned_csv):
    account_median = (
        cleaned_csv
        .groupby('account_id')['amount']
        .median()
    )
    cleaned_csv['account_median'] = (
        cleaned_csv['account_id']
        .map(account_median)
    )
    anomaly = (
        cleaned_csv['amount'] > cleaned_csv['account_median'] * 3 
    )

    cleaned_csv.loc[
        anomaly,
        'is_anomaly'
    ] = True

    cleaned_csv.loc[
        anomaly,
        'anomaly_reason'
    ] = 'ACCOUNT_MEDIAN_OUTLIER'

    return cleaned_csv

# =============================== RULE 2 ===================================================
def _detect_domestic_usd(cleaned_csv):
    domestic_brand = [
        'SWIGGY',
        'OLA',
        'IRCTC',
        'ZOMATO',
        'JIO RECHARGE',
        'HDFC ATM'
    ]

    merchant_condition = (
        cleaned_csv['merchant']
        .str.upper()
        .isin(domestic_brand)
    )

    currency_condition = (
        cleaned_csv['currency'] == 'USD'
    )

    anomaly = (
        merchant_condition
        &
        currency_condition
    )

    cleaned_csv.loc[
        anomaly,
        'is_anomaly'
    ] = True

    cleaned_csv.loc[
        anomaly,
        'anomaly_reason'
    ] = (
        'DOMESTIC_MERCHANT_USD'
    )

    return cleaned_csv



#=========================== MAIN BLOCK =============================================  
def detect_anomalies(filename,filepath):
    csv_data = cleaned_csv_data(filename,filepath)
    cleaned_csv = csv_data[
        'cleaned_csv'
    ]
    cleaned_csv['is_anomaly'] = False
    cleaned_csv['anomaly_reason'] = None

    cleaned_csv = (
        _detect_statistical_outliers(
            cleaned_csv
        )
    )
    cleaned_csv = (
        _detect_domestic_usd(
            cleaned_csv
        )
    )

    cleaned_csv = cleaned_csv.drop(
        columns=['account_median']
    )

    return cleaned_csv

# =========================== TESTING BLOCK ========================================
if __name__ == "__main__":
    result = detect_anomalies(
        "transactions.csv",
        "uploads/transactions.csv"
    )

    import pandas as pd

    pd.set_option(
        'display.max_rows',
        None
    )

    pd.set_option(
        'display.max_columns',
        None
    )

    pd.set_option(
        'display.width',
        None
    )

    pd.set_option(
        'display.max_colwidth',
        None
    )
    # print(result)
    print(
    result[
        result['anomaly_reason']
            ==
            'DOMESTIC_MERCHANT_USD'
        ]
    )
    result.to_csv(
        "anomaly_output.csv",
        index=False
    )