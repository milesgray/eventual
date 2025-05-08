import pytest
from eventual.context.context_injector import ContextInjector

def test_context_injector_initialization():
    injector = ContextInjector()
    assert isinstance(injector, ContextInjector)

def test_inject_context_with_knowledge():
    injector = ContextInjector()
    # Represent knowledge_context as parts to avoid multi-line string literal issue
    knowledge_context_parts = [
        "Concepts: apple, banana.",
        "Relevant Events:",
        "Event 1: ..."
    ]
    knowledge_context = "".join(knowledge_context_parts) # Join for actual injection

    user_query = "What about oranges?"
    full_context = injector.inject_context(knowledge_context, user_query)

    # Check for the presence of key substrings and structure
    for part in knowledge_context_parts:
        assert part in full_context
    assert user_query in full_context
    assert f"User Query: {user_query}" in full_context # Check for the separator and query

def test_inject_context_without_knowledge():
    injector = ContextInjector()
    knowledge_context = ""
    user_query = "Hello, how are you?"
    full_context = injector.inject_context(knowledge_context, user_query)

    # Check that only the user query is in the output
    assert full_context == user_query

    # Check that the separator is not present
    assert "User Query:" not in full_context

# Add more tests for different formatting scenarios or edge cases if needed
