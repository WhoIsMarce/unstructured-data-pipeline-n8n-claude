import os
import json
import pandas as pd
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/data-pipeline")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Sample unstructured dataset (Customer feedback)
SAMPLE_DATA = [
    {
        "id": "REV-001",
        "raw_text": "I ordered the Bluetooth headphones last Tuesday. Battery dies in 20 minutes! Needs replacement. Order #4421."
    },
    {
        "id": "REV-002",
        "raw_text": "Absolutely love the new UI update! The dark mode feature is super smooth and fast."
    },
    {
        "id": "REV-003",
        "raw_text": "Charged twice for my monthly subscription. Please refund the extra $15 immediately!"
    }
]


def process_feedback_item(item: dict) -> dict:
    """
    Sends raw text item to n8n webhook or formats payload for LLM processing.
    Falls back to local parser if webhook is unavailable.
    """
    payload = {
        "item_id": item["id"],
        "text": item["raw_text"]
    }
    
    try:
        response = requests.post(
            N8N_WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        else:
            return fallback_processing(item)
    except requests.exceptions.RequestException:
        # Webhook offline fallback mechanism
        return fallback_processing(item)


def fallback_processing(item: dict) -> dict:
    """
    Rule-based local parser executed when the webhook or LLM is offline.
    """
    text = item["raw_text"].lower()
    
    if "battery" in text or "crashing" in text or "hardware" in text:
        category = "Hardware / Bug"
        urgency = "High"
    elif "charged" in text or "refund" in text or "payment" in text:
        category = "Billing & Refund"
        urgency = "High"
    else:
        category = "General / Feature Request"
        urgency = "Low"
        
    sentiment = "Negative" if ("dies" in text or "refund" in text or "issue" in text) else "Positive"

    return {
        "id": item["id"],
        "raw_text": item["raw_text"],
        "category": category,
        "sentiment": sentiment,
        "urgency": urgency,
        "status": "Processed (Local Pipeline)"
    }


def main():
    print("=== Starting Unstructured Data Cleaning Pipeline ===")
    results = []

    for item in SAMPLE_DATA:
        print(f"Processing item {item['id']}...")
        processed_data = process_feedback_item(item)
        results.append(processed_data)

    # Convert results into a structured Pandas DataFrame
    df = pd.DataFrame(results)
    
    print("\n=== Cleaned & Structured Data Summary ===")
    print(df[["id", "category", "sentiment", "urgency", "status"]].to_string(index=False))

    # Export to CSV
    output_filename = "cleaned_data_output.csv"
    df.to_csv(output_filename, index=False)
    print(f"\n[SUCCESS] Cleaned dataset saved to '{output_filename}'")


if __name__ == "__main__":
    main()