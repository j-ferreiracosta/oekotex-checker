==========================================
Chatbot Interface Project
==========================================

Overview:
---------
This project is a Python-based chatbot that provides an interactive interface using Gradio. It connects to available language models via the OpenAI library. To function correctly, you must have either Ollama or LM Studio installed on your computer with an available model.

Installation & Setup:
---------------------
1. Ensure you have Python installed.
2. Install the required dependencies using pip. For example:
   
   pip install -r requirements.txt

3. Install either Ollama or LM Studio on your computer, and ensure at least one model is available.
4. Update the URL in the file `openai_cli/cli_openai.py` to point to your model’s endpoint.

Project Structure:
------------------
- **openai_cli/cli_openai.py**: Contains the code to connect to the language model. (Remember to update the URL.)
- **chat.py** (or similar): Launches the Gradio interface for the chatbot.
- **files/**: Folder with example of Products and Scope files.
- **readme.txt**: This file.

User Interface:
---------------
The Gradio interface features a central chatbot area and three option tabs on the left:

1. **Option 1 – Inference Parameters:**
   - Choose the desired model.
   - Adjust inference parameters (e.g., temperature).
   - Define the system role for the chatbot.

2. **Option 2 – Scope Checker:**
   - Provides three text boxes to input:
     - Rules
     - Product
     - Scope
   - The AI evaluates whether the defined Product is within the provided Scope.

3. **Option 3 – Bulk Validation:**
   - Contains a Rules textbox.
   - Includes two buttons to load files:
     - One for Products.
     - One for Scopes.
   - The AI returns a JSON-formatted response indicating if each Product is defined within the corresponding Scope.

Usage:
------
1. Launch the project (e.g., by running `python chat.py`).
2. Interact with the chatbot through the Gradio interface.
3. Use the tabs to adjust parameters or validate products against scopes.
4. Make sure the URL in `openai_cli/cli_openai.py` is updated to match your model’s endpoint before running the project.

Notes:
------
- This project requires external tools (Ollama or LM Studio) to be installed with a valid model.
- Customization of the interface (such as modifying CSS or button colors) can be done within the Gradio Blocks setup in your Python code.

Enjoy using the Chatbot Interface!
