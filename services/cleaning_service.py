from services.file_parsing_service import validate_csv
import pandas as pd

def _date_normalization(csv_data):
    csv_data["date"] = pd.to_datetime(
        csv_data["date"],
        errors="coerce",
        dayfirst=True
    )

    csv_data["date"] = (
        csv_data["date"]
        .dt.strftime("%Y-%m-%d")
    )

    return csv_data

def _amount_normalization(csv_data):
    csv_data['amount'] = (
        csv_data['amount']
        .astype(str)
    )

    csv_data['amount'] = (
        csv_data['amount']
        .str.replace('$','',regex=False)
    )

    csv_data['amount'] = (
        csv_data['amount']
        .str.replace('₹','',regex=False)
    )

    csv_data['amount'] = (
        csv_data['amount']
        .str.strip()
    )

    csv_data['amount'] = pd.to_numeric(
        csv_data['amount'],
        errors='coerce'
    )

    return csv_data

def _currency_normalization(csv_data):
    csv_data['currency'] = (
        csv_data['currency']
        .fillna('')
        .str.strip()
        .str.upper()
    )

    return csv_data

def _category_normalization(csv_data):
    csv_data['category'] = (
        csv_data['category']
        .fillna('')
        .str.strip()
    )

    csv_data['category'] = (
        csv_data['category']
        .replace(r'^\s*$', None, regex=True)
    )

    return csv_data

def _status_normalization(csv_data):
    csv_data['status'] = (
        csv_data['status']
        .str.strip()
        .str.upper()
    )

    return csv_data

def cleaned_csv_data(filename,filepath):
    cleaned_data = validate_csv(filename,filepath)
    raw_count = len(cleaned_data)
    cleaned_data = _date_normalization(cleaned_data)
    cleaned_data = _amount_normalization(cleaned_data)
    cleaned_data = _currency_normalization(cleaned_data)
    cleaned_data = _status_normalization(cleaned_data)
    cleaned_data = _category_normalization(cleaned_data)
    cleaned_data = cleaned_data.drop_duplicates()
    clean_count = len(cleaned_data)

    return {
        'cleaned_csv': cleaned_data,
        'raw_count': raw_count,
        'clean_count': clean_count
    }
