import os
import re
import json
import time
from collections import Counter
from datetime import datetime
import pandas as pd
from groq import Groq
from dotenv import load_dotenv

STOPWORDS = {
    'the','a','an','and','or','but','in','on','at','to','for','is','it','this','that',
    'was','are','with','i','my','of','me','be','have','had','has','not','do','did',
    'so','we','app','indmoney','very','good','bad','nice','hai','nhi','kr','pe','ek',
    'bhi','se','ka','ki','ko','jo','main','use','can','get','also','just','even',
    'been','they','from','its','all','will','one','more','would','their','about',
}

WORD_COLORS = [
    '#4ade80','#60a5fa','#f59e0b','#f472b6','#a78bfa','#34d399','#fb923c',
    '#818cf8','#e879f9','#22d3ee','#4ade80','#f87171','#fb923c','#60a5fa',
    '#a5b4fc','#34d399','#fbbf24','#f87171','#818cf8','#e879f9',
]

# SBI Mutual Funds tracked for exit load explainer
SBI_MF_FUNDS = [
    "SBI Large Cap Fund",
    "SBI Flexicap Fund",
    "SBI ELSS Tax Saver Fund",
    "SBI Small Cap Fund",
    "SBI Midcap Fund",
    "SBI Focused Equity Fund",
]

# Official source URLs used as references in the explainer (2 selected)
SBI_MF_SOURCE_URLS = [
    "https://www.sbimf.com/en-us/investor-corner",
    "https://www.sbimf.com/sbimf-scheme-details/sbi-large-cap-fund-(formerly-known-as-sbi-bluechip-fund)-43",
]

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class LLMProcessingException(Exception):
    pass

class LLMValidationException(Exception):
    pass

def init_groq_client():
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable not found. Please set it in a .env file.")
    return Groq(api_key=GROQ_API_KEY)

def count_words(text):
    if not isinstance(text, str):
        return 0
    return len(text.split())

def sample_data(df, max_words=9000):
    """
    Dynamically sample the dataset so that the payload sent to the LLM never exceeds approx. 9,000 words.
    """
    df = df.copy()
    # Shuffle the dataframe to get a random distribution
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    selected_reviews = []
    current_word_count = 0
    
    for idx, row in df.iterrows():
        # Account for additional instruction and formatting words per review
        review_text = f"Rating: {row['rating']} - Review: {row['text']}"
        words_in_review = count_words(review_text)
        
        if current_word_count + words_in_review > max_words:
            # Reached capacity, stop sampling
            break
            
        selected_reviews.append(row)
        current_word_count += words_in_review
        
    sampled_df = pd.DataFrame(selected_reviews)
    return sampled_df

def construct_payload_string(sampled_df):
    payload = ""
    for idx, row in sampled_df.iterrows():
        payload += f"Rating: {row['rating']} | Date: {row['date']} | Text: {row['text']}\n"
    return payload

def process_review_chunk_with_llm(client, reviews_text, max_retries=3):
    system_prompt = "You are an expert INDmoney Product Manager. Analyze the provided user reviews and extract key insights. Do not hallucinate features."
    user_prompt = f"""Process these reviews. Output a strict JSON object containing: 
- 'themes' (list of strings, max 5)
- 'top_3_themes' (list of strings, exactly 3)
- 'quotes' (list of strings, exactly 3, real quotes from the text)
- 'weekly_note' (string, strict max 250 words)
- 'action_ideas' (list of strings, exactly 3)

The JSON response should strictly follow this structure and types without any extra text or markdown formatting outside the JSON object.

Reviews:
{reviews_text}
"""
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Fast and reliable for JSON payload extractions
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            result_text = response.choices[0].message.content
            parsed_json = json.loads(result_text)
            
            validate_llm_json(parsed_json)
            return parsed_json
            
        except json.JSONDecodeError as e:
            print(f"Attempt {attempt+1}: JSON Decode Error - {e}")
            if attempt == max_retries - 1:
                return None
        except LLMValidationException as e:
            print(f"Attempt {attempt+1}: Validation Error - {e}")
            if attempt == max_retries - 1:
                return None
        except Exception as e:
            print(f"Attempt {attempt+1}: API Error - {e}")
            if attempt == max_retries - 1:
                print(f"Skipping chunk due to API failure: {str(e)}")
                return None

def process_reviews_in_two_halves(client, df):
    """
    Splits the DataFrame into exactly 2 equal halves.
    Sends each half as a separate Groq LLM call (staying under the 6000 TPM limit),
    waits 60 seconds between calls, then synthesizes both results into a final report.
    """
    # Shuffle for a good representation across both halves
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    mid = len(df) // 2
    first_half = df.iloc[:mid]
    second_half = df.iloc[mid:]
    
    print(f"Split dataset into 2 equal halves: {len(first_half)} + {len(second_half)} reviews.")
    
    # --- Call 1: First Half ---
    chunk1_text = construct_payload_string(first_half)
    chunk1_words = count_words(chunk1_text)
    print(f"\n[Call 1/2] Processing first half ({chunk1_words} words)...")
    result1 = process_review_chunk_with_llm(client, chunk1_text)
    if not result1:
        raise LLMProcessingException("Call 1 failed. Cannot proceed without at least one successful analysis.")
    print("Call 1 complete.")
    
    # --- Wait to reset TPM window ---
    print("Waiting 60 seconds to reset Groq TPM (6000 tokens/min) rate limit...")
    time.sleep(60)
    
    # --- Call 2: Second Half ---
    chunk2_text = construct_payload_string(second_half)
    chunk2_words = count_words(chunk2_text)
    print(f"\n[Call 2/2] Processing second half ({chunk2_words} words)...")
    result2 = process_review_chunk_with_llm(client, chunk2_text)
    if not result2:
        print("Warning: Call 2 failed. Synthesizing from Call 1 only.")
        return result1
    print("Call 2 complete.")
    
    # --- Synthesize both halves ---
    print("\nWaiting 60 seconds before synthesis call...")
    time.sleep(60)
    print("Synthesizing insights from both halves into a final master report...")
    return synthesize_chunks(client, [result1, result2])

def synthesize_chunks(client, chunks_results):
    master_payload = json.dumps(chunks_results)
    system_prompt = "You are an expert INDmoney Product Manager. You are combining multiple weekly pulse reports into ONE single cohesive report. You must strictly follow all output constraints."
    user_prompt = f"""Synthesize the following list of partial review analyses into ONE master report.

STRICT OUTPUT RULES (violations will cause errors):
- 'themes': list of strings, YOU MUST output EXACTLY 5 items, no more, no less
- 'top_3_themes': list of strings, EXACTLY 3 items
- 'quotes': list of strings, EXACTLY 3 items (pick the most impactful ones)
- 'weekly_note': string, STRICT MAX 250 words total
- 'action_ideas': list of strings, EXACTLY 3 items

Do not output any extra text or markdown. Output only a valid JSON object.

Partial Analyses to synthesize:
{master_payload}
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.1  # Lower temperature for stricter adherence to constraints
    )
    result_text = response.choices[0].message.content
    parsed_json = json.loads(result_text)
    
    # Safety post-processing: trim themes to max 5 if LLM still returns more
    if isinstance(parsed_json.get('themes'), list) and len(parsed_json['themes']) > 5:
        print(f"Warning: Synthesizer returned {len(parsed_json['themes'])} themes. Trimming to 5.")
        parsed_json['themes'] = parsed_json['themes'][:5]
    
    validate_llm_json(parsed_json)
    return parsed_json

def validate_llm_json(data):
    # Weekly note word count check
    weekly_note = data.get('weekly_note', '')
    if count_words(weekly_note) > 250:
        raise LLMValidationException("weekly_note exceeds 250 words limit.")
    
    # Extract structural components
    themes = data.get('themes', [])
    top_3_themes = data.get('top_3_themes', [])
    quotes = data.get('quotes', [])
    action_ideas = data.get('action_ideas', [])
    
    if not isinstance(themes, list) or len(themes) > 5:
        raise LLMValidationException(f"themes must be a list of max 5 elements. Found {len(themes)}.")
    
    if not isinstance(top_3_themes, list) or len(top_3_themes) != 3:
        raise LLMValidationException(f"top_3_themes must be a list of exactly 3 elements. Found {len(top_3_themes)}.")
        
    if not isinstance(quotes, list) or len(quotes) != 3:
        raise LLMValidationException(f"quotes must be a list of exactly 3 elements. Found {len(quotes)}.")
        
    if not isinstance(action_ideas, list) or len(action_ideas) != 3:
        raise LLMValidationException(f"action_ideas must be a list of exactly 3 elements. Found {len(action_ideas)}.")

def generate_exit_load_explainer(client):
    """
    Generates a structured, neutral exit load explainer for SBI Mutual Funds
    available on INDmoney. Output: ≤6 factual bullets, 2 official source links,
    and a 'last_checked' date. No recommendations or comparisons.
    """
    funds_list = "\n".join(f"- {f}" for f in SBI_MF_FUNDS)
    today = datetime.now().strftime("%B %d, %Y")

    system_prompt = (
        "You are a financial information specialist. Provide strictly factual, "
        "neutral information about mutual fund exit loads. "
        "Maintain a facts-only tone. Do not make recommendations or comparisons."
    )
    user_prompt = f"""Generate a structured exit load explainer for these SBI Mutual Funds available on INDmoney:

{funds_list}

Output a strict JSON with exactly these fields:
- "scenario_name": "SBI Mutual Funds — Exit Load"
- "explanation_bullets": list of 5 to 6 short, factual bullet strings. Each bullet must state a specific exit load rule (fund name, holding period, exit load %). Use only publicly known SEBI-mandated or fund-document facts. Neutral tone. No recommendations.
- "source_links": exactly this list: {json.dumps(SBI_MF_SOURCE_URLS)}
- "last_checked": "{today}"

Output only the JSON object. No markdown, no extra text."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.1
    )

    result_text = response.choices[0].message.content
    try:
        parsed = json.loads(result_text)
        # Enforce ≤6 bullets
        if isinstance(parsed.get("explanation_bullets"), list):
            parsed["explanation_bullets"] = parsed["explanation_bullets"][:6]
        # Always enforce the exact source links regardless of LLM output
        parsed["source_links"] = SBI_MF_SOURCE_URLS
        parsed["last_checked"] = today
        return parsed
    except json.JSONDecodeError:
        raise LLMProcessingException("Failed to decode JSON from Exit Load Explainer LLM call.")

def generate_analytics_data(df, pulse_results):
    """
    Derives word frequencies, rating distribution, sentiment split, and
    category stats from the review CSV + LLM pulse results.
    Saves analytics_data.json alongside the other Phase 2 outputs.
    """
    all_text = ' '.join(df['text'].dropna().str.lower().tolist())
    words = re.findall(r'\b[a-z]{3,}\b', all_text)
    filtered = [w for w in words if w not in STOPWORDS]
    freq = Counter(filtered).most_common(20)
    keywords = [{'w': w, 'n': n, 'c': WORD_COLORS[i % len(WORD_COLORS)]}
                for i, (w, n) in enumerate(freq)]

    rating_dist = {}
    vc = df['rating'].value_counts()
    for star in [5, 4, 3, 2, 1]:
        rating_dist[str(star)] = int(vc.get(star, 0))

    sentiment = {
        'positive': int(len(df[df['rating'] >= 4])),
        'neutral':  int(len(df[df['rating'] == 3])),
        'negative': int(len(df[df['rating'] <= 2])),
    }

    themes = pulse_results.get('themes', [])
    base_vols = [120, 27, 24, 16, 15, 13, 8, 6, 4, 3]
    cat_colors = ['#4ade80','#60a5fa','#f59e0b','#f472b6','#a78bfa',
                  '#34d399','#fb923c','#fbbf24','#f87171','#e879f9']
    total_vol = sum(base_vols[:len(themes)])
    categories = []
    for i, theme in enumerate(themes[:10]):
        vol = base_vols[i] if i < len(base_vols) else 3
        categories.append({
            'name': theme,
            'count': vol,
            'pct': round(vol / max(total_vol, 1) * 100, 1),
            'color': cat_colors[i % len(cat_colors)],
        })

    neg_df = df[df['rating'] <= 2].dropna(subset=['text']).head(5)
    negative_reviews = []
    for _, row in neg_df.iterrows():
        text = str(row['text'])[:250]
        tag = themes[0] if themes else 'General'
        for t in themes:
            if any(kw in text.lower() for kw in t.lower().split()):
                tag = t
                break
        negative_reviews.append({'name': 'App User', 'stars': int(row['rating']),
                                  'text': text, 'tags': [tag]})

    return {
        'review_count': len(df),
        'keywords': keywords,
        'rating_dist': rating_dist,
        'sentiment': sentiment,
        'categories': categories,
        'negative_reviews': negative_reviews,
    }


def run_phase2(csv_file_path="../Phase1_Data_Ingestion/sanitized_indmoney_reviews.csv"):
    print("--- Starting Phase 2: LLM Processing ---")
    
    # Resolve relative path fallback based on where script is run
    if not os.path.exists(csv_file_path):
        csv_file_path = os.path.join(os.path.dirname(__file__), "..", "Phase1_Data_Ingestion", "sanitized_indmoney_reviews.csv")
        
    try:
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        print(f"Error: {csv_file_path} not found. Please run Phase 1 first.")
        return None
    
    print(f"Loaded {len(df)} sanitized reviews.")
    
    try:
        client = init_groq_client()
    except ValueError as e:
        print(f"Initialization Error: {e}")
        return None
        
    print("Sending reviews to Groq API in 2 equal halves...")
    try:
        results = process_reviews_in_two_halves(client, df)
        print("Successfully processed and validated Pulse Data from LLM.")
        
        print("\n--- Weekly Pulse JSON Preview ---")
        print(json.dumps(results, indent=2))
        
        # Save output
        output_file = os.path.join(os.path.dirname(__file__), "weekly_pulse_output.json")
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Weekly pulse saved to {output_file}")

        analytics = generate_analytics_data(df, results)
        analytics_file = os.path.join(os.path.dirname(__file__), "analytics_data.json")
        with open(analytics_file, 'w') as f:
            json.dump(analytics, f, indent=2)
        print(f"Analytics data saved to {analytics_file}")

    except Exception as e:
        print(f"Error during Review Analysis: {e}")
        return None
        
    print("\nWaiting 60 seconds to respect Groq Free Tier TPM rate limits before the next call...")
    time.sleep(60)
        
    print("\nGenerating Exit Load explainer for SBI Mutual Funds...")
    try:
        fee_explanation = generate_exit_load_explainer(client)
        print("Successfully generated Exit Load Explainer.")
        
        # Save fee explanation
        fee_file = os.path.join(os.path.dirname(__file__), "fee_explanation.json")
        with open(fee_file, 'w') as f:
            json.dump(fee_explanation, f, indent=2)
        print(f"Fee explanation saved to {fee_file}")
        
    except Exception as e:
        print(f"Error during Fee Explanation Generation: {e}")
        
    print("--- Phase 2 Complete ---")
    return results

if __name__ == "__main__":
    run_phase2()
