import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime, timezone


# --------------------------------------------------
# SETUP
# --------------------------------------------------

load_dotenv()

evaluator_mode = os.getenv(
    "EVALUATOR_MODE",
    "mock"
).lower()

allowed_modes = [
    "mock",
    "live"
]

if evaluator_mode not in allowed_modes:
    raise ValueError(
        "EVALUATOR_MODE must be either 'mock' or 'live'."
    )

client = None

if evaluator_mode == "live":
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is required in live mode."
        )

    client = OpenAI(
        api_key=api_key
    )


# --------------------------------------------------
# LOAD PROJECT FILES
# --------------------------------------------------

with open("dataset/test_cases.json", "r") as file:
    test_cases = json.load(file)

with open("results/evaluation_results.json", "r") as file:
    evaluation_results = json.load(file)

with open("policies/support_policy.md", "r") as file:
    support_policy = file.read()

with open("rubrics/support_rubric.md", "r") as file:
    support_rubric = file.read()

with open("taxonomy/failure_taxonomy.md", "r") as file:
    failure_taxonomy = file.read()

with open("mocks/mock_judge_outputs.json", "r") as file:
    mock_evaluations = json.load(file)


# --------------------------------------------------
# FUNCTIONS
# --------------------------------------------------

def determine_result(total_score, max_score, critical_failure):
    if critical_failure:
        return "FAIL"
    elif total_score == max_score:
        return "PASS"
    else:
        return "FAIL"


def get_policy_section(policy_text, policy_reference):
    sections = policy_text.split("## ")

    for section in sections:
        if section.startswith(policy_reference):
            return "## " + section.strip()

    return None


def build_judge_prompt(
    test_case,
    policy_section,
    ai_response,
    rubric,
    taxonomy
):
    expected_behavior = "\n".join(
        f"- {item}" for item in test_case["expected_behavior"]
    )

    must_not = "\n".join(
        f"- {item}" for item in test_case["must_not"]
    )

    prompt = f"""
You are evaluating an AI customer-support response.

Use only the provided policy and evaluation requirements.
Do not use outside knowledge.

POLICY:
{policy_section}

CUSTOMER PROMPT:
{test_case["user_prompt"]}

EXPECTED BEHAVIOR:
{expected_behavior}

MUST NOT:
{must_not}

AI RESPONSE:
{ai_response}

EVALUATION RUBRIC:
{rubric}

FAILURE TAXONOMY:
{taxonomy}

Return your evaluation as JSON using this exact structure:

{{
  "scores": {{
    "correctness": 0,
    "completeness": 0,
    "groundedness": 0,
    "instruction_following": 0
  }},
  "critical_failure": true,
  "failure_type": "FM-01",
  "reason": "Brief explanation of the evaluation."
}}

For each score, use only 1 for PASS or 0 for FAIL.

If there is no failure type, return null.
"""

    return prompt


def validate_judge_result(judge_result):
    required_score_fields = [
        "correctness",
        "completeness",
        "groundedness",
        "instruction_following"
    ]
    if not isinstance(judge_result, dict):
        return False, "Judge result must be an object"

    if "scores" not in judge_result:
        return False, "Missing scores"

    if not isinstance(judge_result["scores"], dict):
        return False, "Scores must be an object"

    for field in required_score_fields:
        if field not in judge_result["scores"]:
            return False, f"Missing score: {field}"

        if judge_result["scores"][field] not in [0, 1]:
            return False, f"Invalid score for {field}"

    if "critical_failure" not in judge_result:
        return False, "Missing critical_failure"

    if not isinstance(judge_result["critical_failure"], bool):
        return False, "critical_failure must be true or false"

    if "failure_type" not in judge_result:
        return False, "Missing failure_type"

    allowed_failure_types = [
        "FM-01",
        "FM-02",
        "FM-03",
        None
    ]

    if judge_result["failure_type"] not in allowed_failure_types:
        return False, "Invalid failure_type"

    if (
    judge_result["critical_failure"]
    and judge_result["failure_type"] != "FM-01"
    ):
        return False, "Critical failure must be classified as FM-01"

    if (
    judge_result["failure_type"] == "FM-01"
    and not judge_result["critical_failure"]
    ):
        return False, "FM-01 must be marked as a critical failure"

    if judge_result["failure_type"] is None:
        scores = judge_result["scores"]

        if 0 in scores.values():
            return False, "Failed criteria must have a failure type"

    if "reason" not in judge_result:
        return False, "Missing reason"

    return True, "Valid judge result"


def process_judge_output(test_case, judge_output):
    try:
        judge_result = json.loads(judge_output)
    except json.JSONDecodeError:
        print(
            test_case["id"],
            "- INVALID JUDGE RESULT -",
            "Judge output is not valid JSON"
        )
        return None

    is_valid, validation_message = validate_judge_result(
        judge_result
    )

    if not is_valid:
        print(
            test_case["id"],
            "- INVALID JUDGE RESULT -",
            validation_message
        )
        return None

    scores = judge_result["scores"]
    total_score = sum(scores.values())
    max_score = len(scores)

    overall_result = determine_result(
        total_score,
        max_score,
        judge_result["critical_failure"]
    )

    evaluation = {
        "test_case_id": test_case["id"],
        "scores": scores,
        "total_score": total_score,
        "max_score": max_score,
        "critical_failure": judge_result["critical_failure"],
        "failure_type": judge_result["failure_type"],
        "overall_result": overall_result,
        "reason": judge_result["reason"]
    }

    return evaluation


# --------------------------------------------------
# MAIN PROGRAM
# --------------------------------------------------

def main():

    print(
    "Evaluator Mode:",
    evaluator_mode.upper()
    )

    # ----------------------------------------------
    # CHECK EXISTING MANUAL RESULTS
    # ----------------------------------------------

    for result in evaluation_results:
        scores = result["scores"]
        total_score = sum(scores.values())

        overall_result = determine_result(
            total_score,
            result["max_score"],
            result["critical_failure"]
        )

        stored_result = result["overall_result"]

        if stored_result == overall_result:
            status = "MATCH"
        else:
            status = "MISMATCH"

        print(
            result["test_case_id"],
            "-",
            total_score,
            "/",
            result["max_score"],
            "-",
            overall_result,
            "-",
            status
        )

    # ----------------------------------------------
    # RUN ALL TEST CASES
    # ----------------------------------------------

    automated_results = []

    for test_case in test_cases:
        test_case_id = test_case["id"]

        mock_data = mock_evaluations[test_case_id]

        ai_response = mock_data["ai_response"]
        judge_output = json.dumps(
        mock_data["judge_output"]
        )

        policy_section = get_policy_section(
            support_policy,
            test_case["policy_reference"]
        )

        judge_prompt = build_judge_prompt(
        test_case,
        policy_section,
        ai_response,
        support_rubric,
        failure_taxonomy
        )

        evaluation = process_judge_output(
            test_case,
            judge_output
        )

        if evaluation is not None:
            evaluation["ai_response"] = ai_response
            automated_results.append(evaluation)

    # ----------------------------------------------
    # DISPLAY RESULTS
    # ----------------------------------------------

    print("\nAUTOMATED EVALUATION RESULTS:")

    for evaluation in automated_results:
        print(
            evaluation["test_case_id"],
            "-",
            evaluation["total_score"],
            "/",
            evaluation["max_score"],
            "-",
            evaluation["overall_result"],
            "-",
            evaluation["failure_type"]
        )

    # ----------------------------------------------
    # CALCULATE SUMMARY METRICS
    # ----------------------------------------------

    total_tests = len(automated_results)

    passed_tests = sum(
        1
        for result in automated_results
        if result["overall_result"] == "PASS"
    )

    failed_tests = total_tests - passed_tests

    if total_tests > 0:
        pass_rate = (passed_tests / total_tests) * 100
    else:
        pass_rate = 0

    # ----------------------------------------------
    # CALCULATE CRITERION PASS RATES
    # ----------------------------------------------

    criteria = [
        "correctness",
        "completeness",
        "groundedness",
        "instruction_following"
    ]

    criterion_pass_rates = {}

    for criterion in criteria:
        passed = sum(
            result["scores"][criterion]
            for result in automated_results
        )

        if total_tests > 0:
            rate = (passed / total_tests) * 100
        else:
            rate = 0

        criterion_pass_rates[criterion] = rate

    # ----------------------------------------------
    # COUNT FAILURE TYPES
    # ----------------------------------------------

    failure_counts = {
        "FM-01": 0,
        "FM-02": 0,
        "FM-03": 0
    }

    for result in automated_results:
        failure_type = result["failure_type"]

        if failure_type in failure_counts:
            failure_counts[failure_type] += 1

    # ----------------------------------------------
    # DISPLAY SUMMARY
    # ----------------------------------------------

    print("\nEVALUATION SUMMARY")

    print("Total Test Cases:", total_tests)
    print("Passed:", passed_tests)
    print("Failed:", failed_tests)
    print(f"Pass Rate: {pass_rate:.1f}%")

    print("\nCriterion Pass Rates:")

    for criterion, rate in criterion_pass_rates.items():
        print(
            f"{criterion.replace('_', ' ').title()}: "
            f"{rate:.1f}%"
        )

    print("\nFailure Types:")

    for failure_type, count in failure_counts.items():
        print(f"{failure_type}: {count}")

    # ----------------------------------------------
    # BUILD EVALUATION REPORT
    # ----------------------------------------------

    evaluation_report = {
    "run_metadata": {
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "evaluator_mode": evaluator_mode,
        "test_case_count": total_tests
    },
    "summary": {
            "total_test_cases": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "pass_rate": round(pass_rate, 1),
            "criterion_pass_rates": {
                criterion: round(rate, 1)
                for criterion, rate
                in criterion_pass_rates.items()
            },
            "failure_type_counts": failure_counts
        },
        "results": automated_results
    }

    # ----------------------------------------------
    # SAVE EVALUATION REPORT
    # ----------------------------------------------

    with open(
        "results/automated_results.json",
        "w"
    ) as file:
        json.dump(
            evaluation_report,
            file,
            indent=2
        )

    print(
        "\nEvaluation report saved to "
        "results/automated_results.json"
    )


# --------------------------------------------------
# PROGRAM ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    main()