from database.db import (
    init_database,
    create_job,
    save_transactions,
    save_summary,
    update_job_status
)

from services.cleaning_service import (
    cleaned_csv_data
)

from services.anomaly_service import (
    detect_anomalies
)

from services.llm_service import (
    _classify_missing_categories,
    _generate_narrative_summary
)

def process_transaction_file():
    job_id = None

    filename = 'transactions.csv'
    filepath = 'uploads/transactions.csv'

    try:

        init_database()

        raw_data = cleaned_csv_data(
            filename,
            filepath
        )

        raw_count = raw_data[
            'raw_count'
        ]

        clean_count = raw_data[
            'clean_count'
        ]

        job_id = create_job(
            filename,
            filepath,
            raw_count,
            clean_count
        )

        cleaned_csv = (
            detect_anomalies(
                filename,
                filepath
            )
        )

        classified_csv = (
            _classify_missing_categories(
                cleaned_csv
            )
        )

        summary = (
            _generate_narrative_summary(
                classified_csv
            )
        )

        save_transactions(
            job_id,
            classified_csv
        )

        save_summary(
            job_id,
            summary
        )

        update_job_status(
            job_id,
            'completed'
        )

        print(
            'Pipeline completed successfully'
        )

    except Exception as e:
        if job_id:
            update_job_status(
                job_id,
                'failed',
                str(e)
            )

        print(
            f'Pipeline failed: {e}'
        )


if __name__ == '__main__':
    process_transaction_file()