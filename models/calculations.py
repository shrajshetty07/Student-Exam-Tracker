"""
calculations.py
----------------
Business logic for automatic result calculation: total marks,
percentage, letter grade, GPA points and pass/fail status.

Marks breakdown per subject (out of 130):
    Assignment 20 + Quiz 10 + Lab 20 + Internal 20 + Project 10 + Final Exam 50
"""

MAX_TOTAL = 130
PASS_THRESHOLD_PERCENT = 40
PASS_MIN_FINAL_EXAM = 15  # must clear the final exam component itself

GRADE_TABLE = [
    (90, "A+", 10.0),
    (80, "A", 9.0),
    (70, "B+", 8.0),
    (60, "B", 7.0),
    (50, "C", 6.0),
    (40, "D", 5.0),
    (0, "F", 0.0),
]


def compute_total(assignment, quiz, lab, internal, project, final_exam) -> float:
    return round(
        float(assignment) + float(quiz) + float(lab) + float(internal) +
        float(project) + float(final_exam), 2
    )


def compute_percentage(total: float) -> float:
    return round(total / MAX_TOTAL * 100, 2)


def compute_grade(percentage: float) -> str:
    for threshold, grade, _ in GRADE_TABLE:
        if percentage >= threshold:
            return grade
    return "F"


def compute_gpa_point(percentage: float) -> float:
    for threshold, _, gpa in GRADE_TABLE:
        if percentage >= threshold:
            return gpa
    return 0.0


def compute_pass_fail(percentage: float, final_exam_marks: float) -> str:
    if percentage >= PASS_THRESHOLD_PERCENT and final_exam_marks >= PASS_MIN_FINAL_EXAM:
        return "Pass"
    return "Fail"


def compute_full_result(assignment, quiz, lab, internal, project, final_exam) -> dict:
    """Single entry point used by the marks routes to compute everything at once."""
    total = compute_total(assignment, quiz, lab, internal, project, final_exam)
    percentage = compute_percentage(total)
    grade = compute_grade(percentage)
    gpa = compute_gpa_point(percentage)
    pass_fail = compute_pass_fail(percentage, float(final_exam))
    return {
        "total": total,
        "percentage": percentage,
        "grade": grade,
        "gpa": gpa,
        "pass_fail": pass_fail,
    }


def compute_ranks(students_with_percentage: list) -> list:
    """
    Given a list of dicts each containing a 'percentage' key, return the
    same list with a 'rank' key added (1 = highest percentage). Ties share
    the same rank (standard competition ranking).
    """
    ranked = sorted(students_with_percentage, key=lambda s: s["percentage"], reverse=True)
    rank = 0
    last_pct = None
    for i, row in enumerate(ranked, start=1):
        if row["percentage"] != last_pct:
            rank = i
            last_pct = row["percentage"]
        row["rank"] = rank
    return ranked
