# LLM Evaluation Harness

A Python-based evaluation framework for testing AI-generated customer-support responses against defined business policies.

The project demonstrates how traditional software QA practices can be adapted to evaluate non-deterministic AI systems using structured test cases, evaluation rubrics, failure taxonomies, deterministic scoring, and automated validation.

## Project Goals

This project was designed to explore how AI responses can be evaluated when exact-output assertions are not appropriate.

The harness evaluates responses across four criteria:

- Correctness
- Completeness
- Groundedness
- Instruction Following

It also classifies failures using a defined taxonomy and identifies critical hallucination failures.

## Current Evaluation Coverage

The evaluation dataset currently contains five customer-support scenarios covering:

- Order cancellation
- Product returns
- Damaged orders
- Late deliveries
- Unsupported or hallucinated policy claims

The current mock evaluation suite intentionally contains both passing and failing responses so that scoring and failure-classification behavior can be demonstrated.

## Failure Taxonomy

| Code | Failure Type | Description |
|---|---|---|
| FM-01 | Hallucination / Unsupported Claim | Introduces company-policy information not supported by the provided policy |
| FM-02 | Missing-Information Assumption | Assumes information required to make a decision instead of requesting clarification |
| FM-03 | Incomplete Rule Evaluation | Fails to apply one or more relevant policy conditions when the required information is available |

FM-01 is treated as a critical failure.

## Evaluation Architecture

The harness follows a structured evaluation pipeline:

```text
Test Case
   ↓
Relevant Policy Section
   ↓
Candidate AI Response
   ↓
Evaluation Rubric + Failure Taxonomy
   ↓
Judge Evaluation
   ↓
Output Validation
   ↓
Deterministic Scoring
   ↓
Failure Classification
   ↓
Aggregate Metrics
   ↓
JSON Evaluation Report
```

The judge is responsible for evaluating qualitative criteria, while Python handles deterministic operations such as score calculation, PASS/FAIL determination, validation, aggregation, and report generation.

## Project Structure

```text
llm-evaluation-portfolio/
├── dataset/
│   └── test_cases.json
├── mocks/
│   └── mock_judge_outputs.json
├── policies/
│   └── support_policy.md
├── results/
│   ├── automated_results.json
│   └── evaluation_results.json
├── rubrics/
│   └── support_rubric.md
├── taxonomy/
│   └── failure_taxonomy.md
├── tests/
│   └── test_evaluator.py
├── .env.example
├── .gitignore
├── evaluate.py
├── README.md
└── requirements.txt
```

## Evaluation Logic

Each AI response receives a binary score for four criteria:

| Criterion | Evaluation Question |
|---|---|
| Correctness | Does the response correctly apply the relevant policy? |
| Completeness | Does it include the information necessary to address the scenario? |
| Groundedness | Are its claims supported by the provided policy? |
| Instruction Following | Does it follow the defined response constraints? |

Each criterion receives either `1` (pass) or `0` (fail), for a maximum score of 4.

The current evaluation rule requires all four criteria to pass:

```text
4/4 → PASS
Less than 4/4 → FAIL
```

An FM-01 hallucination or unsupported company-policy claim is classified as a critical failure and results in `FAIL` regardless of the numeric score.

## Judge Output Validation

Judge output is validated before scoring. The harness checks for:

- Valid JSON
- Required score fields
- Binary score values
- Valid failure-type classifications
- Boolean critical-failure values
- Consistency between FM-01 and critical-failure status
- Failure classification when one or more criteria fail

Malformed or logically inconsistent judge output is rejected rather than silently scored.

## Automated Harness Tests

The evaluator itself is tested using `pytest`.

Current automated tests cover:

- Full-score PASS behavior
- Incomplete-score FAIL behavior
- Critical-failure override
- Valid judge output
- Invalid score rejection
- Missing failure classification
- Malformed JSON
- Invalid judge-result structure
- Invalid score structure
- FM-01 critical-failure consistency

Current test suite:

```text
11 passed
```

## Running the Project

### 1. Clone the repository

```bash
git clone <repository-url>
cd llm-evaluation-portfolio
```

### 2. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 3. Configure the environment

Copy the example environment file:

```bash
cp .env.example .env
```

For the current mock evaluation:

```text
EVALUATOR_MODE=mock
```

An API key is not required in mock mode.

### 4. Run the evaluation

```bash
python3 evaluate.py
```

The harness evaluates all configured test cases, calculates aggregate metrics, and writes the evaluation report to:

```text
results/automated_results.json
```

### 5. Run the evaluator test suite

```bash
python3 -m pytest tests/test_evaluator.py -v
```

## Mock and Live Evaluation Modes

The project supports two evaluator modes:

### Mock Mode

```text
EVALUATOR_MODE=mock
```

Mock mode uses predefined judge outputs from:

```text
mocks/mock_judge_outputs.json
```

This makes the evaluation pipeline reproducible and allows the framework to be demonstrated without external API calls or API costs.

### Live Mode

```text
EVALUATOR_MODE=live
```

Live mode is reserved for evaluation using an external LLM judge and requires an API key.

The current portfolio implementation demonstrates the complete evaluation pipeline using mock judge outputs. Live LLM judge invocation is not yet implemented.

## Example Evaluation Results

The current five-case mock evaluation produces:

| Metric | Result |
|---|---:|
| Total Test Cases | 5 |
| Passed | 1 |
| Failed | 4 |
| Pass Rate | 20.0% |
| FM-01 | 1 |
| FM-02 | 2 |
| FM-03 | 1 |

The low pass rate is intentional. The mock dataset contains deliberately incorrect responses designed to exercise the scoring logic and each failure category.

The generated JSON report also records:

- Evaluation timestamp
- Evaluator mode
- Test-case count
- Criterion-level pass rates
- Failure-type counts
- Individual evaluation results
- Candidate AI responses
- Evaluation reasons

## Design Decisions

### Policy-grounded evaluation

Responses are evaluated against provided company policy rather than general model knowledge.

### Relevant policy retrieval

Each test case references the policy section required for that scenario instead of treating the entire policy document as the expected answer.

### Qualitative evaluation with deterministic scoring

The judge handles qualitative assessment, while Python calculates scores, PASS/FAIL results, failure counts, and aggregate metrics deterministically.

### Explicit failure taxonomy

Failures are classified separately from numeric scores so that evaluation results show not only whether a response failed, but the type of failure observed.

### Evaluator validation

Judge output is treated as untrusted input and validated before being accepted by the scoring pipeline.

### Separation of evaluation data and logic

Policies, test cases, rubrics, failure definitions, and mock judge outputs are stored separately from the Python evaluation logic.

## Current Limitations

This is a portfolio evaluation harness rather than a production AI evaluation platform.

Current limitations include:

- Live LLM judge invocation is not yet implemented.
- Judge outputs currently use predefined mock data.
- The dataset contains five scenarios and is intentionally small.
- Scoring uses binary criterion values rather than graded scales.
- The project does not yet measure judge-to-human agreement.
- Repeated LLM evaluation stability has not yet been measured.
- Prompt-injection resilience is not yet tested.
- The project does not currently compare multiple models or prompt versions.

## Future Improvements

Planned extensions include:

- Connect a live LLM judge
- Use structured model outputs
- Expand the evaluation dataset
- Add human-labelled reference evaluations
- Measure judge/human agreement
- Measure repeated-run evaluation consistency
- Add prompt-injection and adversarial cases
- Compare model and prompt versions
- Add historical run comparison
- Add richer evaluation metrics and reporting

## Skills Demonstrated

This project demonstrates practical application of:

- AI / LLM quality evaluation
- Test-case design
- Evaluation rubric design
- Failure taxonomy development
- Policy-grounded testing
- Python
- JSON processing
- Input validation
- Error handling
- Automated testing with pytest
- Evaluation reporting
- QA thinking applied to non-deterministic AI systems