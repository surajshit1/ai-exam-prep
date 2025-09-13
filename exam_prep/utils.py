# exam_prep/utils.py
import os
import re
from datetime import datetime, timedelta
from typing import Optional


def validate_inputs(
    exam_type: str,
    subjects: str,
    days_until_exam: int,
    study_hours: int,
    level: str = "Intermediate",
    pyq_folder: Optional[str] = None,
):
    """Validate and sanitize user inputs for exam prep system."""
    validated = {}

    exam_type = (exam_type or "").strip()
    if not exam_type:
        raise ValueError("Exam type cannot be empty")
    validated["exam_type"] = exam_type.upper()

    subjects = (subjects or "").strip()
    if not subjects:
        raise ValueError("Subjects cannot be empty")
    validated["subjects"] = [s.strip() for s in subjects.split(",") if s.strip()]
    if not validated["subjects"]:
        raise ValueError("Please provide at least one subject")

    if not isinstance(days_until_exam, int) or days_until_exam <= 0 or days_until_exam > 365:
        raise ValueError("Days until exam must be between 1 and 365")
    validated["days_until_exam"] = days_until_exam

    if not isinstance(study_hours, int) or study_hours <= 0 or study_hours > 24:
        raise ValueError("Study hours must be between 1 and 24")
    validated["study_hours"] = study_hours

    level = (level or "Intermediate").strip().capitalize()
    if level not in ["Beginner", "Intermediate", "Advanced"]:
        raise ValueError("Level must be Beginner, Intermediate, or Advanced")
    validated["level"] = level

    # Optional previous-year-questions folder check
    if pyq_folder:
        pyq_folder = os.path.abspath(pyq_folder)
        if not os.path.exists(pyq_folder) or not os.path.isdir(pyq_folder):
            raise ValueError("pyq_folder does not exist or is not a directory")
        validated["pyq_folder"] = pyq_folder
    else:
        validated["pyq_folder"] = None

    exam_date = datetime.now() + timedelta(days=days_until_exam)
    validated["exam_date"] = exam_date.strftime("%Y-%m-%d")
    validated["exam_date_readable"] = exam_date.strftime("%B %d, %Y")

    validated["total_study_hours"] = days_until_exam * study_hours

    return validated


def create_output_directory(base_dir: str = "output"):
    """Create output directory if it doesn't exist."""
    os.makedirs(base_dir, exist_ok=True)
    return base_dir


def safe_filename(name: str) -> str:
    """Return a filesystem-safe filename component."""
    return re.sub(r"[^\w\d-]+", "_", name).strip("_")[:120]
