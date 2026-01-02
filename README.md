# AI Recruiter Agency 🤖💼

An AI-powered recruitment automation system that uses specialized LLM agents to process resumes, analyze candidate profiles, match them with job descriptions, and provide hiring recommendations.

## 🌟 Features

- **Multi-Agent Orchestration**: Specialized agents for extraction, analysis, matching, screening, and recommendation.
- **Local LLM Integration**: Powered by **Ollama** (default: `llama3.2`) for privacy and cost-efficiency.
- **Streamlit Dashboard**: A user-friendly web interface to upload resumes and visualize recruitment insights.
- **Automated PDF Parsing**: Extracts text and structured data from PDF resumes using `pdfminer.six`.
- **Intelligent Matching**: Ranks candidates against job requirements with detailed reasoning.

## 🏗️ Architecture

The system follows an agentic workflow managed by an **Orchestrator**:

1.  **Extractor Agent**: Parses PDF resumes into structured JSON data.
2.  **Analyzer Agent**: Performs deep-dive analysis of technical skills and experience.
3.  **Matcher Agent**: Matches candidates against a pool of available job positions.
4.  **Screener Agent**: Evaluates cultural fit, qualifications, and potential red flags.
5.  **Recommender Agent**: Synthesizes all data to provide a final hiring recommendation.

## 🚀 Getting Started

### Prerequisites

- [Ollama](https://ollama.com/) installed and running.
- Python 3.10+
- The `llama3.2` model downloaded (`ollama pull llama3.2`).

### Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd AI-Recruiter-Agency
    ```

2.  **Set up a virtual environment**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    # source venv/bin/activate  # macOS/Linux
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 🛠️ Usage

### Running the Web App

Launch the Streamlit interface:
```bash
streamlit run app.py
```
Then, open your browser to the URL provided (usually `http://localhost:8501`).

### Running the Test Workflow

To test the backend logic via the console:
```bash
python test_workflow.py
```

## 📁 Project Structure

- `agents/`: Contains the logic for specialized AI agents.
- `app.py`: The Streamlit web application.
- `test_workflow.py`: A script to verify the agent workflow.
- `uploads/`: Temporary storage for uploaded resumes.
- `requirements.txt`: Project dependencies.

## ⚖️ License

MIT License
