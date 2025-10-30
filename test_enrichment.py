"""
Test LLM Text Enrichment for Audiobook Narration
"""
import os
from llm_enrich import enrich_text

# Check API keys
print("🔍 Checking API Keys...")
print(f"GOOGLE_API_KEY: {'✓ Set' if os.getenv('GOOGLE_API_KEY') else '✗ Not set'}")
print(f"OPENAI_API_KEY: {'✓ Set' if os.getenv('OPENAI_API_KEY') else '✗ Not set'}")
print()

# Test text with OCR errors and awkward phrasing
test_text = """
AI AudioBook Generator

This is an AI-powered audiobook generator that can convert any document into high-quality audio.
The system extracts text from PDFs images and DOCX files. Then it uses advanced text-to-speech technology to create natural sounding narration.

Key features include:
- Automatic text extraction
- Multiple TTS engines support
- High quality audio output
- Easy to use interface
"""

print("📝 Original Text:")
print("=" * 70)
print(test_text)
print("=" * 70)
print()

print("🤖 Enriching with LLM (Audiobook Mode)...")
enriched = enrich_text(test_text, audiobook_mode=True, provider="auto")

if enriched == test_text:
    print("⚠️ No enrichment applied - check API keys")
else:
    print("✅ Text Enriched!")
    print()
    print("📖 Enriched Text:")
    print("=" * 70)
    print(enriched)
    print("=" * 70)
    print()
    print(f"Original length: {len(test_text)} chars")
    print(f"Enriched length: {len(enriched)} chars")
