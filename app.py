from flask import Flask, request, jsonify
from utils.gemini_client import generate_topic_content
from utils.pdf_generator import save_as_pdf
from utils.ppt_generator import save_as_ppt
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Welcome to the Topic Research Generator API",
        "endpoints": {
            "POST /generate": "Generate research content on a topic and export as PDF/PPT"
        }
    })

@app.route('/generate', methods=['POST'])
def generate_content_route():
    data = request.get_json()
    topic = data.get('topic')
    output_format = data.get('format', 'ppt') # 'ppt' or 'pdf'

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    # Step 1: Generate structured content
    content_data = generate_topic_content(topic) # <-- Now returns a dict

    if "error" in content_data:
        return jsonify(content_data), 500

    # Step 2: Generate File
    try:
        if output_format.lower() == 'ppt':
            file_path = save_as_ppt(content_data) # <-- Pass dict
        elif output_format.lower() == 'pdf':
            file_path = save_as_pdf(content_data) # <-- Pass dict
        else:
            return jsonify({"error": "Invalid format. Use 'ppt' or 'pdf'."}), 400

        # Note: You'll need to use Flask's send_file/send_from_directory 
        # to return the actual file, not just the path.
        return jsonify({"message": f"File generated successfully at {file_path}", "file_path": file_path})
    
    except Exception as e:
        return jsonify({"error": f"File generation failed: {str(e)}"}), 500

if __name__ == "__main__":
    os.makedirs("utils/output", exist_ok=True)
    app.run(debug=True)
