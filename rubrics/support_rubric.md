# Customer Support AI Evaluation Rubric

This rubric is used to evaluate AI-generated responses against the Customer Support Policy.

## Scoring Criteria

Each criterion is worth 1 point.

### 1. Correctness

The response must provide information that is correct according to the company policy.

- PASS = Information provided is correct.
- FAIL = The response contains incorrect information.

### 2. Completeness

The response must address the important information needed to answer the customer's question.

- PASS = All important policy requirements and conditions are addressed.
- FAIL = Important information, conditions, or required actions are missing.

### 3. Groundedness

Claims made by the AI must be supported by the provided company policy.

- PASS = Claims are supported by the policy.
- FAIL = The response includes unsupported claims or information.

### 4. Instruction Following

The AI must use only the company information provided and must not invent missing information.

- PASS = The response follows the instructions.
- FAIL = The response ignores the instructions or invents information.

## Score

Maximum score: 4 points.

- Correctness: 1 point
- Completeness: 1 point
- Groundedness: 1 point
- Instruction Following: 1 point

## Critical Failure Rule

An unsupported or invented company-policy claim is considered a critical failure.

If a response contains a hallucinated company-policy claim:

**Overall Result = FAIL**

This applies regardless of the total numeric score.