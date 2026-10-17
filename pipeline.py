import os
import asyncio
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

USE_MOCK = os.getenv("USE_MOCK_AI", "true").lower() == "true"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

class UnstructuredDataPipeline:
    def __init__(self):
        self.use_mock = USE_MOCK or not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "your_anthropic_api_key_here"
        if self.use_mock:
            logger.info("Initializing Pipeline in MOCK MODE (Zero cost, local simulation active).")
        else:
            logger.info("Initializing Pipeline with LIVE Anthropic Claude API.")

    async def sanitize_payload(self, raw_text: str) -> str:
        """Validates and sanitizes incoming unstructured text."""
        if not raw_text or not isinstance(raw_text, str):
            raise ValueError("Invalid or empty input payload.")
        # Basic sanitization / stripping excess spaces
        sanitized = " ".join(raw_text.split())
        logger.info("Payload successfully sanitized.")
        return sanitized

    async def call_claude_or_mock(self, sanitized_text: str) -> Dict[str, Any]:
        """Routes execution to real API or local mock engine."""
        if self.use_mock:
            # Simulate async processing delay
            await asyncio.sleep(0.8)
            return {
                "status": "success",
                "mode": "mock_simulation",
                "processed_length": len(sanitized_text),
                "extracted_insights": {
                    "summary": f"Mock processed: {sanitized_text[:60]}...",
                    "entities": ["unstructured_doc", "local_pipeline", "n8n_mock"],
                    "confidence_score": 0.98
                }
            }
        else:
            # Placeholder for real Anthropic API call integration
            logger.info("Executing real Anthropic API request...")
            # (Real API integration logic would go here)
            pass

    async def run_pipeline(self, raw_input: str) -> Dict[str, Any]:
        try:
            logger.info("Starting pipeline execution...")
            clean_text = await self.sanitize_payload(raw_input)
            result = await self.call_claude_or_mock(clean_text)
            logger.info("Pipeline execution completed successfully.")
            return result
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            return {"status": "error", "message": str(e)}

# Execution test block
if __name__ == "__main__":
    sample_text = "Report: Unstructured quarterly feedback data received from multiple client communication channels..."
    pipeline = UnstructuredDataPipeline()
    output = asyncio.run(pipeline.run_pipeline(sample_text))
    print("\n--- Pipeline Execution Output ---")
    print(output)