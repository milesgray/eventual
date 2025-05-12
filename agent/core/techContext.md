## Technology Stack

Main language: Python

Virtual Environment: source env/bin/activate

Packages:
- pytest
- spacy
- scikit-learn
- baml-py
- pydantic

### TESTING

**pytest**

<Overview>
    Use `pytest` always.  Any tests that exist that are not pytest should be converted to pytest.
</Overview>

Always activate the venv when initiating a test.

Example:

```bash
source /home/user/eventual/env/bin/activate && pytest tests/test_basic_chat_flow.py
```

### NLP

**spaCy**, **Sci-kit Learn**

### LLM

**BAML**

<Overview>
  BAML (Basically, A Made-Up Language) is a domain-specific language for building LLM prompts as functions.
  You can build an agentic workflow with BAML.
</Overview>