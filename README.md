Python AI Toolkit



An AI-powered application built using Python and Ollama. It includes a command-line interface (CLI) and a Flask-based web chat application.



FEATURES



CLI Features:

- Text Summarization

- Text Translation

- Sentiment Analysis

- AI Chat Mode

- Save Chat History

- View Previous Conversations



Web Application Features:

- User Registration and Login

- AI Chat with Streaming Responses

- Individual Chat History for Each User

- Create and Delete Chats

- Search Chat History

- Export Conversations

- Stop AI Generation

- Light and Dark Themes

- Markdown and Code Formatting



TECHNOLOGIES USED



- Python

- Flask

- Flask-Login

- Flask-SQLAlchemy

- Ollama

- Qwen 2.5 3B

- HTTPX

- Rich

- HTML, CSS and JavaScript

- SQLite



REQUIREMENTS



- Python 3.10 or later

- Ollama

- Git



INSTALLATION



1\. Clone the repository.

2\. Create a virtual environment:

   python -m venv venv

3\. Activate the environment:

   .\venv\Scripts\Activate.ps1

4\. Install dependencies:

   pip install -r requirements.txt

5\. Download the AI model:

   ollama pull qwen2.5:3b

6\. Make sure Ollama is running.



RUN CLI APPLICATION



python main.py



RUN WEB APPLICATION



python web/app.py



Open http://127.0.0.1:5000 in your browser.



RUN TESTS



pytest



AI MODEL



This project uses the Qwen 2.5 3B model through Ollama to provide local AI-powered responses.
