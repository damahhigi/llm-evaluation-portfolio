from evaluate import (
    determine_result,
    process_judge_output,
    validate_judge_result
)

def test_full_score_passes():
    result = determine_result(
        total_score=4,
        max_score=4,
        critical_failure=False
    )

    assert result == "PASS"


def test_incomplete_score_fails():
    result = determine_result(
        total_score=3,
        max_score=4,
        critical_failure=False
    )

    assert result == "FAIL"


def test_critical_failure_fails():
    result = determine_result(
        total_score=4,
        max_score=4,
        critical_failure=True
    )

    assert result == "FAIL"

def test_valid_judge_result():
    judge_result = {
        "scores": {
            "correctness": 1,
            "completeness": 1,
            "groundedness": 1,
            "instruction_following": 1
        },
        "critical_failure": False,
        "failure_type": None,
        "reason": "The response meets all evaluation criteria."
    }

    is_valid, message = validate_judge_result(judge_result)

    assert is_valid is True
    assert message == "Valid judge result"


def test_invalid_score_is_rejected():
    judge_result = {
        "scores": {
            "correctness": 7,
            "completeness": 1,
            "groundedness": 1,
            "instruction_following": 1
        },
        "critical_failure": False,
        "failure_type": None,
        "reason": "Invalid score test."
    }

    is_valid, message = validate_judge_result(judge_result)

    assert is_valid is False
    assert message == "Invalid score for correctness"


def test_failed_score_requires_failure_type():
    judge_result = {
        "scores": {
            "correctness": 0,
            "completeness": 1,
            "groundedness": 1,
            "instruction_following": 1
        },
        "critical_failure": False,
        "failure_type": None,
        "reason": "Failure type is missing."
    }

    is_valid, message = validate_judge_result(judge_result)

    assert is_valid is False
    assert message == "Failed criteria must have a failure type"

def test_malformed_json_is_rejected():
    test_case = {
        "id": "TC-TEST"
    }

    malformed_output = """
    {
        "scores": invalid
    }
    """

    result = process_judge_output(
        test_case,
        malformed_output
    )

    assert result is None

def test_judge_result_must_be_object():
    judge_result = [
        "not",
        "an",
        "object"
    ]

    is_valid, message = validate_judge_result(
        judge_result
    )

    assert is_valid is False
    assert message == "Judge result must be an object"


def test_scores_must_be_object():
    judge_result = {
        "scores": "perfect"
    }

    is_valid, message = validate_judge_result(
        judge_result
    )

    assert is_valid is False
    assert message == "Scores must be an object"

def test_fm01_must_be_critical():
    judge_result = {
        "scores": {
            "correctness": 0,
            "completeness": 0,
            "groundedness": 0,
            "instruction_following": 0
        },
        "critical_failure": False,
        "failure_type": "FM-01",
        "reason": "Unsupported company-policy claim."
    }

    is_valid, message = validate_judge_result(
        judge_result
    )

    assert is_valid is False
    assert message == "FM-01 must be marked as a critical failure"


def test_critical_failure_must_be_fm01():
    judge_result = {
        "scores": {
            "correctness": 0,
            "completeness": 0,
            "groundedness": 0,
            "instruction_following": 0
        },
        "critical_failure": True,
        "failure_type": "FM-02",
        "reason": "Incorrect critical classification."
    }

    is_valid, message = validate_judge_result(
        judge_result
    )

    assert is_valid is False
    assert message == "Critical failure must be classified as FM-01"