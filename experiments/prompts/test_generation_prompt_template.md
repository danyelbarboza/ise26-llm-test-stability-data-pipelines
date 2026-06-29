# Test Generation Prompt Template

Generate a `pytest` test suite for the Python function described below.

Requirements:

- Import the function only from `ise26.targets`.
- Use `pytest`.
- Do not modify or wrap the original implementation.
- Cover common scenarios and edge cases.
- When applicable, consider null values, duplicates, dates, schema validation, and business rules.
- Write assertions that verify behavior through returned values.
- Return only Python test code.
- Do not include Markdown fences.
- Do not include explanations outside the test code.

Function metadata:

- Function ID: `{function_id}`
- Function name: `{function_name}`
- Description: `{function_description}`

Expected behavior:

`{expected_behavior}`

Function code:

```python
{function_code}
```
