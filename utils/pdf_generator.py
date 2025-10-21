from fpdf import FPDF
import os
import requests
from io import BytesIO
import re

FONT_PATH = r"D:\topic-generator-api\utils\fonts"

class CustomPDF(FPDF):
    """Custom FPDF class for formatted topic PDF generation."""

    def header(self):
        self.set_font('Helvetica', 'B', 15)
        self.cell(0, 10, '', 0, 1, 'C')
        self.ln(5)

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(0, 0, 128)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Helvetica', '', 11)
        lines = body.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith(('*', '-', '1.', '2.', '3.')):
                self.set_font('ZapfDingbats', '', 11)
                self.cell(5, 6, chr(108), 0, 0, 'L')
                self.set_font('Helvetica', '', 11)
                self.multi_cell(0, 6, line.lstrip('*-1234567890. '), 0, 'L')
            else:
                self.multi_cell(0, 6, line, 0, 'L')
        self.ln(4)

def sanitize_text(text):
    """
    Removes or replaces characters that are not supported by Latin-1 (like emojis).
    """
    # Replace emojis and unsupported chars with '(Idea)' or blank
    text = re.sub(r'[^\x00-\xFF]', '(Idea)', text)
    return text

def save_as_pdf(data: dict, output_folder="output"):
    """
    Save structured topic data as a PDF with proper formatting, bullets, and optional images.
    """
    if "error" in data:
        raise ValueError(f"Cannot create PDF: {data['error']}")

    topic = sanitize_text(data.get("title", "Generated_Topic"))
    os.makedirs(output_folder, exist_ok=True)
    safe_topic = topic.replace(' ', '_').replace('/', '_').replace(':', '')

    pdf_path = os.path.join(output_folder, f"{safe_topic}.pdf")

    pdf = CustomPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)

    # ✅ Add your custom fonts
    pdf.add_font('Helvetica', '', os.path.join(FONT_PATH, 'Helvetica.ttf'), uni=True)
    pdf.add_font('Helvetica', 'B', os.path.join(FONT_PATH, 'Helvetica-Bold.ttf'), uni=True)

    pdf.add_page()

    # ✅ Title
    pdf.set_font("Helvetica", "B", 20)
    pdf.multi_cell(0, 15, sanitize_text(topic), 0, 'C')
    pdf.ln(10)

    # ✅ Summary
    pdf.chapter_title("Key Takeaways / Summary")
    for point in data.get("summary_points", []):
        pdf.set_font('ZapfDingbats', '', 11)
        pdf.cell(5, 6, chr(108), 0, 0, 'L')
        pdf.set_font('Helvetica', '', 11)
        pdf.multi_cell(0, 6, sanitize_text(point), 0, 'L')
    pdf.ln(5)

    # ✅ Slides / Sections
    for section in data.get("slides", []):
        pdf.chapter_title(sanitize_text(section.get("slide_title", "Section")))
        pdf.chapter_body(sanitize_text(section.get("main_content", "No content provided.")))

        # ✅ Image (optional)
        image_url = section.get("image_url")
        if image_url:
            try:
                img_data = requests.get(image_url, timeout=10).content
                pdf.image(BytesIO(img_data), w=100)
                pdf.ln(10)
            except Exception as e:
                pdf.set_font('Helvetica', 'I', 8)
                pdf.cell(0, 5, f"[Image failed: {e}]", 0, 1, 'L')
        else:
            pdf.set_font('Helvetica', 'I', 8)
            # ✅ Replace 💡 with "(Idea)" text
            suggestion = sanitize_text("💡 Image Suggestion: " + section.get("image_prompt", "No image prompt"))
            pdf.cell(0, 5, suggestion, 0, 1, 'L')

    pdf.output(pdf_path)
    return pdf_path

# ✅ Test Example
if __name__ == "__main__":
    sample_data = {
        "title": "Artificial Intelligence Overview",
        "summary_points": [
            "AI simulates human intelligence processes by machines.",
            "It is widely used in healthcare, finance, and robotics.",
            "Key subsets include ML, DL, and NLP."
        ],
        "slides": [
            {
                "slide_title": "Introduction to AI",
                "main_content": "Artificial Intelligence (AI) is the science of making machines intelligent.\n* Mimics human decision-making.\n* Enables automation in multiple sectors.",
                "image_prompt": "Illustration of AI concept."
            },
            {
                "slide_title": "Applications of AI",
                "main_content": "AI applications are everywhere:\n1. Self-driving cars\n2. Chatbots\n3. Fraud detection",
                "image_prompt": "Image showing real-world AI use cases."
            }
        ]
    }

    pdf_file = save_as_pdf(sample_data)
    print(f"✅ PDF successfully generated at: {pdf_file}")
