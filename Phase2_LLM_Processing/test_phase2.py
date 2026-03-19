import pytest
import pandas as pd
from phase2_llm_processing import sample_data, validate_llm_json, count_words, LLMValidationException

def test_count_words():
    assert count_words("Hello world this is a test") == 6
    assert count_words("") == 0
    assert count_words(None) == 0
    assert count_words("   Spaces   everywhere  ") == 2

def test_sample_data_limits_words():
    # Create fake dataframe that heavily exceeds the 9000 word limit
    # Each review text will have 100 words. Thus, total is 20,000 words.
    dummy_text = "word " * 100
    data = {"rating": [5] * 200, "text": [dummy_text.strip()] * 200, "date": ["2026-01-01"] * 200}
    df = pd.DataFrame(data)
    
    # 9000 words limit
    sampled = sample_data(df, max_words=9000)
    
    total_words = 0
    for _, row in sampled.iterrows():
        total_words += count_words(f"Rating: {row['rating']} - Review: {row['text']}")
        
    assert total_words <= 9000
    assert len(sampled) < 200 # It should naturally break way before parsing 200 records

def test_validate_llm_json_success():
    valid_data = {
        "themes": ["Theme1", "Theme2"],
        "top_3_themes": ["A", "B", "C"],
        "quotes": ["Q1", "Q2", "Q3"],
        "weekly_note": "This is a short note.",
        "action_ideas": ["I1", "I2", "I3"]
    }
    # If no exception is raised, test passes
    validate_llm_json(valid_data)

def test_validate_llm_json_too_many_themes():
    invalid_data = {
        "themes": ["1", "2", "3", "4", "5", "6"],
        "top_3_themes": ["A", "B", "C"],
        "quotes": ["Q1", "Q2", "Q3"],
        "weekly_note": "Note",
        "action_ideas": ["I1", "I2", "I3"]
    }
    with pytest.raises(LLMValidationException, match="themes must be a list of max 5 elements"):
        validate_llm_json(invalid_data)

def test_validate_llm_json_invalid_top_3():
    invalid_data = {
        "themes": ["1", "2"],
        "top_3_themes": ["A", "B"],
        "quotes": ["Q1", "Q2", "Q3"],
        "weekly_note": "Note",
        "action_ideas": ["I1", "I2", "I3"]
    }
    with pytest.raises(LLMValidationException, match="top_3_themes must be a list of exactly 3 elements"):
        validate_llm_json(invalid_data)

def test_validate_llm_json_long_note():
    # 251 words
    long_note = "word " * 251
    invalid_data = {
        "themes": ["1"],
        "top_3_themes": ["A", "B", "C"],
        "quotes": ["Q1", "Q2", "Q3"],
        "weekly_note": long_note.strip(),
        "action_ideas": ["I1", "I2", "I3"]
    }
    with pytest.raises(LLMValidationException, match="weekly_note exceeds 250 words limit"):
        validate_llm_json(invalid_data)
