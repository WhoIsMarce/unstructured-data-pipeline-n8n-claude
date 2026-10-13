# Unstructured Data Classification & Cleaning Pipeline Using Python, n8n & Claude AI

## Executive Summary

This project demonstrates an end-to-end automated pipeline designed to ingest, clean, categorize, and structure noisy, unstructured text data (such as customer support tickets, product reviews, and feedback forms).

By orchestrating **Python**, **n8n automation workflows**, and **Anthropic's Claude 3.5 Sonnet LLM**, this pipeline transforms unstructured text into normalized, actionable JSON and CSV records.

---

## System Architecture

[ Unstructured Text Data (CSV / JSON) ]
│
▼
[ Python Preprocessing (main.py) ]
│ (HTTP POST Payload)
▼
[ n8n Webhook / Workflow ]
│ (Prompt Assembly)
▼
[ Anthropic Claude 3.5 Sonnet ]
│ (Structured JSON Response)
▼
[ Cleaned & Categorized Dataset (CSV / DB) ]

### Key Capabilities

- **Automated Text Normalization**: Cleans whitespace, handles special characters, and validates payload structures.
- **AI-Powered Entity & Sentiment Extraction**: Leverages Claude 3.5 Sonnet to categorize feedback, determine sentiment (Positive, Negative, Neutral), and evaluate urgency (High, Medium, Low).
- **Rule-Based Fallback Engine**: Ensures high availability by applying local regex and keyword parsing if the API or webhook is unreachable.
- **n8n Workflow Integration**: Connects disparate data ingestion channels directly to LLM processing nodes.

---

## Tech Stack

- **Language**: Python 3.10+ (`pandas`, `requests`, `python-dotenv`)
- **Orchestration**: n8n (Workflow Automation Engine)
- **AI Engine**: Anthropic Claude 3.5 Sonnet API
- **Document Format**: Markdown, JSON, CSV

---

## Installation & Setup

### Prerequisites

1. Python 3.10 or higher installed.
2. Git installed.
3. An active Anthropic API key (optional for local fallback mode).

### 1. Clone the Repository

```bash
git clone [https://github.com/YOUR_USERNAME/unstructured-data-pipeline-n8n-claude.git](https://github.com/YOUR_USERNAME/unstructured-data-pipeline-n8n-claude.git)
cd unstructured-data-pipeline-n8n-claude
2. Configure Virtual Environment & Dependencies
Bash
# Create virtual environment
py -m venv venv

# Activate virtual environment (Git Bash)
source venv/Scripts/activate

# Install required Python packages
pip install requests pandas python-dotenv anthropic
3. Environment Variables
Create a .env file in the project root folder:

Fragmento de código
ANTHROPIC_API_KEY=your_actual_api_key_here
N8N_WEBHOOK_URL=http://localhost:5678/webhook/data-pipeline
Usage Guide
Running the Python Processing Pipeline
Execute main.py in your terminal to process the sample dataset:

Bash
python main.py
Importing the n8n Workflow
Open your n8n instance dashboard.

Select Workflows > Import from File.

Choose workflow.json from this repository.

Activate the webhook node.

Sample Data Transformation
Raw Input (Unstructured)
JSON
{
  "id": "REV-001",
  "raw_text": "I ordered the Bluetooth headphones last Tuesday. Battery dies in 20 minutes! Needs replacement immediately. Order #4421."
}
Structured Output (Cleaned)
JSON
{
  "id": "REV-001",
  "category": "Hardware / Battery Defect",
  "sentiment": "Negative",
  "urgency": "High",
  "status": "Processed"
}
License
Distributed under the MIT License. Free for commercial and open-source use.


---

### Archivo 3: `main.py`
**Nombre exacto:** `main.py`  
*(El código ejecutable en Python. Lee datos de muestra, se conecta al webhook o usa un analizador local si no está conectado, procesa todo con Pandas y guarda el resultado en un archivo CSV).*

```python
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
