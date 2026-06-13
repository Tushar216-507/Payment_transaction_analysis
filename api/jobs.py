from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
)

import shutil
import os

from database.db import (
    create_job,
    get_job_by_id,
    get_all_jobs,
    get_job_results,
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

from database.db import (
    save_transactions,
    save_summary
)

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)

UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

@router.post("/upload")
def upload_csv(
    file: UploadFile = File(...)
):

    if not file.filename.endswith(
        ".csv"
    ):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files allowed"
        )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(
        file_path,
        "wb"
    ) as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    cleaned_data = (
        cleaned_csv_data(
            file.filename,
            file_path
        )
    )

    job_id = create_job(
        file.filename,
        file_path,
        cleaned_data[
            "raw_count"
        ],
        cleaned_data[
            "clean_count"
        ]
    )

    try:

        result = detect_anomalies(
            file.filename,
            file_path
        )

        classified_csv = (
            _classify_missing_categories(
                result
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
            "completed"
        )

    except Exception as e:

        update_job_status(
            job_id,
            "failed",
            str(e)
        )

    return {
        "job_id": job_id,
        "status": "processing"
    }

@router.get("/{job_id}/status")
def get_status(job_id):

    job = get_job_by_id(
        job_id
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job

@router.get("/{job_id}/results")
def get_results(job_id):

    return get_job_results(
        job_id
    )

@router.get("")
def list_jobs():

    return get_all_jobs()