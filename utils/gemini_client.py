import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def clean_json_text(text: str) -> str:
    """Remove markdown code fences or extra text from Gemini output."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def generate_topic_content(topic: str) -> dict:
    """
    Generate a well-structured presentation/document content for the given topic.
    Returns JSON-like structured data with slides, titles, and image prompts.
    """
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
    Generate a presentation content in strict JSON format for the topic: "{topic}".

    Structure it like this:
    {{
      "title": "Main title",
      "summary_points": ["Point 1", "Point 2", "Point 3"],
      "slides": [
        {{
          "slide_title": "Slide 1 Title",
          "main_content": "Bullet points or short explanation for slide 1.",
          "image_prompt": "Relevant image description (3–6 words)"
        }},
        {{
          "slide_title": "Slide 2 Title",
          "main_content": "Slide 2 content.",
          "image_prompt": "Image prompt"
        }}
      ]
    }}

    Rules:
    - Output only valid JSON.
    - No explanations, no markdown, just JSON.
    - Include 5–7 slides minimum.
    """

    try:
        response = model.generate_content(prompt)

        text_response = response.text.strip()
        cleaned = clean_json_text(text_response)

        # Try to parse JSON safely
        structured_data = json.loads(cleaned)

        return structured_data

    except json.JSONDecodeError:
        print(f"Gemini response was not valid JSON:\n{text_response}")
        return {"error": "Gemini returned invalid JSON format. Try rephrasing the topic."}
    except Exception as e:
        return {"error": f"Error generating content from Gemini: {e}"}
