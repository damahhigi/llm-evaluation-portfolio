# LLM Evaluation Failure Taxonomy

This taxonomy defines the primary failure types used when evaluating customer-support AI responses.

## FM-01 — Hallucination / Unsupported Claim

The AI introduces information, rules, guarantees, or facts that are not supported by the provided company policy.

### Example

Policy:
Damaged orders require the customer to contact Customer Support with an order number and photo.

AI response:
"Damaged orders automatically receive a full refund within 3–5 business days."

### Classification Reason

The AI invented a refund guarantee and processing timeframe that are not contained in the policy.

---

## FM-02 — Missing-Information Assumption

The AI does not have all the information required to apply a policy rule but assumes the missing condition instead of asking for clarification.

### Example

Policy:
Orders may be cancelled before shipment but cannot be cancelled after shipment.

Customer:
"I placed my order yesterday."

AI response:
"You can cancel your order."

### Classification Reason

The AI does not know whether the order has shipped but assumes that it has not.

---

## FM-03 — Incomplete Rule Evaluation

The AI has the information required to evaluate a rule but ignores or fails to apply one or more conditions.

### Example

Policy:
Returns must be within 30 days, unused, and in their original packaging.

Customer:
"I received the item 10 days ago. It is unused, but I threw away the packaging."

AI response:
"You can return it because it is within 30 days and unused."

### Classification Reason

The AI had information about the packaging but failed to apply the original-packaging requirement.

---

## Classification Guidance

Use the most specific primary failure type.

- FM-01: The AI invents information that the policy does not contain.
- FM-02: Required information is missing, but the AI assumes it.
- FM-03: Required information is available, but the AI fails to apply it.

Additional failure types should only be added when a new failure pattern cannot be clearly classified using the existing taxonomy.