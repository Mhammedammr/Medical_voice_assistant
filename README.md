# AI Medical Voice Assistant

This project is an AI chat and voice assistant designed to help healthcare professionals by providing medical information and calculating medical scores. The assistant uses advanced AI models and prompt engineering to deliver accurate and contextually relevant responses.

### Key Features

* **Voice Interaction:** Uses the OpenAI **Whisper** model for accurate speech-to-text conversion.
* **Intelligent Responses:** Employs **prompt engineering** with state-of-the-art Large Language Models to generate conversational and informed answers.
* **Serverless LLMs:** Integrates with **DeepSeek-V3** and **Llama-4-Marvek** from **Fireworks AI** serverless services for powerful and scalable language processing.
* **Medical Score Calculation:** Supports **Function Calling** to compute specific medical scores based on user requests.

### Getting Started

To get the project up and running, follow the steps below.

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/AndreIglesias/AI-Medical-Voice-Assistant.git](https://github.com/AndreIglesias/AI-Medical-Voice-Assistant.git)
    cd AI-Medical-Voice-Assistant
    ```
2.  **Create a Virtual Environment and Install Dependencies:**
    It's recommended to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -e .
    ```
3.  **Configure API Keys:**
    Create a `.env` file in the root directory and add your API keys for the services used by the application.
    ```
    speech = fw_3ZfrrxLEQq441P9Jqw6kPLd1
    refine = fw_3ZURm9vXSrWS4nnPMo9K6CPG
    translation = fw_3ZPLkUDqtJnyXnM7Rn6KjUHg
    extraction = fw_3ZSDxLZKLtqAb1ctkWpffvaE
    ```
4.  **Run the Application:**
    Start the Flask application using the provided command.
    ```bash
    python flask_app.py
    ```
