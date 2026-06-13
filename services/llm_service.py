from groq import Groq
from config import Config
import pandas as pd
import json
from services.cleaning_service import cleaned_csv_data
from services.anomaly_service import (
    detect_anomalies
)

client = Groq(api_key=Config.GROQ_API_KEY)

def _build_system_prompt(category_data):
    base = f"""
        YOU ARE AN ANALYSIS AI AGENT, YOUR JOB IS TO CLASSIFY PAYMENT TRANSACTIONS THAT HAVE MISSING CATEGORIES.
                                        
        ALLOWED CATEGORIES:
        FOOD
        TRAVEL
        TRANSPORT
        UTILITIES
        CASH WITHDRAWAL
        ENTERTAINMENT
        SHOPPING
        OTHER

        RULES:
        1.
        SWIGGY/ZOMATO -> FOOD
        OLA -> TRANSPORT
        IRCTC -> TRAVEL
        HDFC ATM -> CASH WITHDRAWAL
        JIO RECHARGE → Utilities
        AMAZON → Shopping
        FLIPKART → Shopping
        BOOKMYSHOW → Entertainment
        MAKEMYTRIP → Travel.
        2.IF UNSURE CLASSIFY THE TRANSACTION AS OTHER
        3.ONLY USE THE ALLOWED CATEGORIES .
        4.NEVER INVENT NEW CATEGORIES BY YOURSELF, STRICTLY FOLLOW THE ALLOWED CATEGORIES.
        5.DONT INCLUDE ANY EXPLANATION ONLY RETURN JSON AS SAID STRICTLY .
        6.DONT INCLUDE MARKDOWN FOR CLASSIFICATION.
        7.RETURN CLASSIFICATION FOR EVERY TRANSACTION.
        8.RETURN ONLY VALID JSON AS SAID BELOW.

        CLASSIFY THIS TRANSACTION:
        {category_data}

        return only valid JSON:
        [
            {{
                "txn_id": "TXN1001",
                "category": "Food"
            }}
        ]
    """
    return base

def _classify_missing_categories(cleaned_csv):
    missing_rows = cleaned_csv[
        cleaned_csv['category'].isna()
    ]

    missing_rows = missing_rows[
        [
            'txn_id',
            'merchant',
            'amount',
            'currency',
            'notes'
        ]
    ]

    if missing_rows.empty:
        return cleaned_csv

    category_data = (
        missing_rows
        .to_dict(
            orient='records'
        )
    )

    prompt = (
        _build_system_prompt(
            category_data
        )
    )

    response = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[
            {
                'role': 'system',
                'content': prompt
            }
        ],
        temperature=0
    )

    llm_output = (
        response
        .choices[0]
        .message.content
    )

    classified_categories = (
        pd.DataFrame(
            json.loads(
                llm_output
            )
        )
    )

    classified_categories = (
        classified_categories[
            classified_categories[
                'txn_id'
            ]
            .notna()
        ]
    )

    classified_categories = (
        classified_categories[
            classified_categories[
                'txn_id'
            ] != 'null'
        ]
    )

    classified_categories[
        'category'
    ] = (
        classified_categories[
            'category'
        ]
        .str.title()
    )

    category_mapping = dict(
        zip(
            classified_categories[
                'txn_id'
            ],
            classified_categories[
                'category'
            ]
        )
    )

    mask = (
        cleaned_csv['category']
        .isna()
    )

    cleaned_csv.loc[
        mask,
        'category'
    ] = (
        cleaned_csv.loc[
            mask,
            'txn_id'
        ]
        .map(category_mapping)
    )

    cleaned_csv['category'] = (
        cleaned_csv['category']
        .fillna('OTHER')
    )

    return cleaned_csv

def _build_summary_prompt(
    summary_data
):
    base = f"""
YOU ARE A FINANCIAL ANALYSIS AI.

Analyze the payment transaction data and return ONLY VALID JSON.

Required JSON format:

{{
    "total_spend_by_currency": {{
        "INR": 0,
        "USD": 0
    }},
    "top_3_merchants": [],
    "anomaly_count": 0,
    "spending_narrative": "",
    "risk_level": "low"
}}

Rules:
1. risk_level must only be:
low, medium, high

2. spending_narrative should be 2-3 sentences.

3. Return ONLY valid JSON.
4. Do not include markdown.
5. Do not include explanations.
6. Do not write text before or after JSON.
7. Output must start with {{
8. Output must end with }}

Transaction Data:
{summary_data}
"""
    return base

def _generate_narrative_summary(
    cleaned_csv
):
    summary_data = (
        cleaned_csv[
            [
                'merchant',
                'amount',
                'currency',
                'category',
                'is_anomaly'
            ]
        ]
        .to_dict(
            orient='records'
        )
    )

    prompt = (
        _build_summary_prompt(
            summary_data
        )
    )

    response = (
        client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[
                {
                    'role': 'system',
                    'content': prompt
                }
            ],
            temperature=0
        )
    )

    llm_output = (
        response
        .choices[0]
        .message.content
    )

    llm_output = (
        llm_output
        .replace(
            '```json',
            ''
        )
        .replace(
            '```',
            ''
        )
        .strip()
    )

    summary_json = (
        json.loads(
            llm_output
        )
    )

    summary_json[
        'risk_level'
    ] = (
        summary_json[
            'risk_level'
        ]
        .lower()
    )

    return summary_json
#================================== TESTING BLOCK =================================================
if __name__ == '__main__':
    cleaned_csv = (
        detect_anomalies(
            'transactions.csv',
            'uploads/transactions.csv'
        )
    )

    result = (
        _classify_missing_categories(
            cleaned_csv
        )
    )

    summary = (
        _generate_narrative_summary(
            result
        )
    )

    print(summary)

    print(
        result[
            [
                'txn_id',
                'merchant',
                'category'
            ]
        ]
    )