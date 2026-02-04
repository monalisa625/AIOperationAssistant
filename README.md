# 🤖 AI Operations Assistant

A production-quality, multi-agent AI Operations Assistant that accepts natural language tasks, plans tool executions, and verifies results using real third-party APIs. Built for GenAI internship assignments with a clean, modular architecture.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)](https://openai.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [API Reference](#api-reference)
- [Error Handling](#error-handling)
- [Example Output](#example-output)
- [Troubleshooting](#troubleshooting)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

The **AI Operations Assistant** is a multi-agent system that:

- ✅ Accepts **natural language tasks** from users
- ✅ Uses an **LLM-powered Planner** to break tasks into structured execution steps
- ✅ Executes steps using **real third-party APIs** (GitHub, Weather)
- ✅ Verifies results with an **LLM-powered Verifier** that can request retries
- ✅ Returns **structured JSON responses** with complete execution traces

### Key Highlights

- **Multi-Agent Architecture**: Separate Planner, Executor, and Verifier agents with distinct responsibilities
- **Real API Integration**: Uses actual GitHub REST API and OpenWeatherMap API (no mocks)
- **Production-Ready**: Error handling, retry logic, and fail-fast configuration
- **Flexible Runtime**: Supports both CLI and FastAPI server modes
- **Clean Code**: Well-structured, commented, and follows Python best practices

---

## ✨ Features

- 🔍 **Intelligent Planning**: LLM converts natural language into structured execution plans
- 🔄 **Automatic Retry**: Failed steps can be automatically re-executed based on verifier feedback
- 🌐 **Real API Integration**: 
  - GitHub repository search (public API, optional token for rate limits)
  - Current weather data (OpenWeatherMap)
- ✅ **Result Verification**: LLM-powered verification ensures data quality and completeness
- 📊 **Structured Output**: Consistent JSON responses with execution traces
- 🚀 **Dual Runtime**: CLI for quick tasks, FastAPI for integration

---

## 🏗️ Architecture

### Multi-Agent System

```
┌─────────────────────────────────────────────────────────────┐
│                    User Input (CLI/API)                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Planner Agent                            │
│  • Receives natural language task                           │
│  • Uses LLM to create structured JSON plan                  │
│  • Validates plan with Pydantic models                      │
│  • Output: Ordered list of tool steps                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Executor Agent                            │
│  • Iterates through plan steps                              │
│  • Calls appropriate tools (GitHub, Weather)                 │
│  • Handles retries (once per step)                         │
│  • Captures errors and partial failures                     │
│  • Output: Raw execution results                            │
└──────────────┬──────────────────────────┬──────────────────┘
               │                          │
               ▼                          ▼
    ┌──────────────────┐      ┌──────────────────┐
    │   GitHub Tool    │      │  Weather Tool    │
    │  (REST API)      │      │  (OpenWeather)   │
    └──────────────────┘      └──────────────────┘
               │                          │
               └──────────┬───────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Verifier Agent                            │
│  • Analyzes execution results using LLM                     │
│  • Detects missing/empty/erroneous data                    │
│  • Can request re-execution of specific steps               │
│  • Produces final structured output                        │
│  • Output: Verification result + summary                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Final Structured Response                       │
│  • Task, Plan, Execution, Verification                     │
│  • User-friendly summary                                   │
│  • Machine-readable structured_output                      │
└─────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities

| Agent | Responsibility | Technology |
|-------|---------------|------------|
| **Planner** | Converts natural language → structured JSON plan | LLM (OpenAI) + Pydantic |
| **Executor** | Executes plan steps, calls tools, handles retries | Python async + Requests |
| **Verifier** | Validates results, requests retries, formats output | LLM (OpenAI) + Pydantic |

---

## 📦 Prerequisites

- **Python 3.8+** (tested with Python 3.10+)
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))
- **OpenWeatherMap API Key** ([Get one here](https://openweathermap.org/api))
- **GitHub Token** (optional, for higher rate limits)

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/monalisa625/AIOperationAssistant.git
cd AIOperationAssistant
```

### 2. Create Virtual Environment

**Windows:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
cd ai_ops_assistant
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
GITHUB_TOKEN=your-github-token-here  # Optional
OPENWEATHER_API_KEY=your-openweather-api-key-here
```

**⚠️ Important**: Never commit `.env` to version control. It's already in `.gitignore`.

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | ✅ Yes | Your OpenAI API key | - |
| `OPENAI_MODEL` | ❌ No | Model to use (e.g., `gpt-4o-mini`, `gpt-4-turbo`) | `gpt-4o-mini` |
| `GITHUB_TOKEN` | ❌ No | GitHub personal access token (increases rate limits) | - |
| `OPENWEATHER_API_KEY` | ✅ Yes | OpenWeatherMap API key | - |

### Getting API Keys

1. **OpenAI API Key**:
   - Visit https://platform.openai.com/api-keys
   - Sign up/login and create a new API key
   - Copy the key (starts with `sk-`)

2. **OpenWeatherMap API Key**:
   - Visit https://openweathermap.org/api
   - Sign up for a free account
   - Navigate to API keys section
   - Copy your API key

3. **GitHub Token** (Optional):
   - Visit https://github.com/settings/tokens
   - Generate a new token (no scopes needed for public repos)
   - Copy the token

---

## 💻 Usage

### CLI Mode (Recommended for Testing)

Run a task directly from the command line:

```bash
python main.py "Find 3 popular GitHub repositories related to AI agents and tell me the current weather in London."
```

**Output**: Pretty-printed JSON with task, plan, execution results, and verification.

### FastAPI Server Mode

Start the API server:

```bash
python main.py "ignored" --mode api --host 0.0.0.0 --port 8000
```

Then call the API endpoint:

**Using curl:**
```bash
curl -X POST "http://localhost:8000/run" \
  -H "Content-Type: application/json" \
  -d '{"task": "Find 3 popular GitHub repositories related to AI agents and tell me the current weather in London."}'
```

**Using Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/run",
    json={"task": "Find 3 popular GitHub repositories related to AI agents and tell me the current weather in London."}
)
print(response.json())
```

**Using JavaScript (fetch):**
```javascript
fetch('http://localhost:8000/run', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    task: "Find 3 popular GitHub repositories related to AI agents and tell me the current weather in London."
  })
})
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## 📁 Project Structure

```
ai_ops_assistant/
│
├── agents/                    # Multi-agent system
│   ├── planner.py            # PlannerAgent: Converts tasks → plans
│   ├── executor.py           # ExecutorAgent: Executes plan steps
│   ├── verifier.py           # VerifierAgent: Validates & formats results
│   └── __init__.py
│
├── tools/                     # Third-party API integrations
│   ├── github_tool.py        # GitHub REST API wrapper
│   ├── weather_tool.py       # OpenWeatherMap API wrapper
│   └── __init__.py
│
├── llm/                       # LLM client & prompts
│   ├── client.py             # Centralized OpenAI Async client
│   ├── prompts.py            # Planner & Verifier prompt templates
│   └── __init__.py
│
├── main.py                   # CLI & FastAPI entrypoints
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
└── README.md                 # This file
```

---

## 🔄 How It Works

### Step-by-Step Execution Flow

1. **User submits task** (e.g., "Find 3 popular AI agent repos and London weather")

2. **Planner Agent**:
   - Receives natural language task
   - Uses LLM with strict JSON-only prompt
   - Generates structured plan:
     ```json
     {
       "steps": [
         {
           "id": 1,
           "action": "search_github",
           "tool": "github",
           "input": {"query": "AI agents", "per_page": 3}
         },
         {
           "id": 2,
           "action": "get_weather",
           "tool": "weather",
           "input": {"city": "London", "units": "metric"}
         }
       ]
     }
     ```
   - Validates plan with Pydantic models

3. **Executor Agent**:
   - Iterates through plan steps sequentially
   - Calls `github_tool.search_repositories()` for step 1
   - Calls `weather_tool.get_current_weather()` for step 2
   - Retries each step once on failure
   - Collects raw outputs

4. **Verifier Agent**:
   - Analyzes execution results using LLM
   - Checks for missing data, errors, empty responses
   - Decides if results are sufficient (`status: "ok"` or `"retry"`)
   - If `retry`, specifies which `step_ids` to re-execute
   - Produces final summary and structured output

5. **Orchestrator (main.py)**:
   - If verifier requests retry, re-runs only those steps
   - Merges results and re-verifies
   - Returns complete response with task, plan, execution, and verification

---

## 📡 API Reference

### FastAPI Endpoint

**POST** `/run`

**Request Body:**
```json
{
  "task": "Your natural language task here"
}
```

**Response:**
```json
{
  "task": "Original task",
  "plan": {
    "steps": [...]
  },
  "execution": {
    "steps": [...]
  },
  "verification": {
    "status": "ok",
    "retry_step_ids": [],
    "summary": "User-friendly summary",
    "structured_output": {...},
    "steps": [...]
  }
}
```

---

## 🛡️ Error Handling

### Planner Errors

- **Invalid JSON**: Retries up to 2 times, then raises
- **Validation Errors**: Pydantic validation catches malformed plans
- **Missing API Key**: Fails fast with clear error message

### Executor Errors

- **Network Failures**: Retries once per step
- **API Errors**: Captured as `{"error": "..."}` in output
- **Missing Tool**: Returns error object, doesn't crash

### Verifier Errors

- **Invalid JSON Response**: Falls back to wrapping raw text
- **Missing Data**: Sets `status: "retry"` with `retry_step_ids`
- **Empty Results**: Requests re-execution of affected steps

### Tool-Specific Errors

- **GitHub API**: Handles rate limits, network timeouts (10s)
- **Weather API**: Returns structured error if API key missing
- **All Tools**: Return error objects instead of raising exceptions

---

## 📊 Example Output

### Successful Execution

```json
{
  "task": "Find 3 popular GitHub repositories related to AI agents and tell me the current weather in London.",
  "plan": {
    "steps": [
      {
        "id": 1,
        "action": "search_github",
        "tool": "github",
        "input": {
          "query": "AI agents",
          "per_page": 3
        }
      },
      {
        "id": 2,
        "action": "get_weather",
        "tool": "weather",
        "input": {
          "city": "London",
          "units": "metric"
        }
      }
    ]
  },
  "execution": {
    "steps": [
      {
        "step_id": 1,
        "tool": "github",
        "action": "search_github",
        "input": {"query": "AI agents", "per_page": 3},
        "success": true,
        "output": {
          "query": "AI agents",
          "total_count": 12345,
          "items": [
            {
              "full_name": "langchain-ai/langchain",
              "html_url": "https://github.com/langchain-ai/langchain",
              "stargazers_count": 75000,
              "description": "Building applications with LLMs through composability",
              "language": "Python"
            }
            // ... 2 more repos
          ]
        }
      },
      {
        "step_id": 2,
        "tool": "weather",
        "action": "get_weather",
        "input": {"city": "London", "units": "metric"},
        "success": true,
        "output": {
          "city": "London",
          "temperature": 19.2,
          "feels_like": 18.5,
          "humidity": 65,
          "description": "light rain"
        }
      }
    ]
  },
  "verification": {
    "status": "ok",
    "retry_step_ids": [],
    "summary": "Found 3 popular AI agent repositories: langchain-ai/langchain (75K stars), ... Current weather in London: 19.2°C, light rain.",
    "structured_output": {
      "github": {
        "repositories": [
          {
            "name": "langchain-ai/langchain",
            "stars": 75000,
            "description": "Building applications with LLMs through composability"
          }
          // ... 2 more
        ]
      },
      "weather": {
        "city": "London",
        "temperature": 19.2,
        "description": "light rain"
      }
    },
    "steps": [
      {"step_id": 1, "ok": true, "issues": []},
      {"step_id": 2, "ok": true, "issues": []}
    ]
  }
}
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. `OPENAI_API_KEY is missing`

**Solution**: Ensure `.env` file exists and contains `OPENAI_API_KEY=sk-...`

#### 2. `ModuleNotFoundError: No module named 'openai'`

**Solution**: Install dependencies: `pip install -r requirements.txt`

#### 3. Weather API returns error

**Solution**: 
- Verify `OPENWEATHER_API_KEY` is set in `.env`
- Check API key is valid at https://openweathermap.org/api

#### 4. GitHub API rate limit exceeded

**Solution**: Add `GITHUB_TOKEN` to `.env` (optional but recommended)

#### 5. `python-dotenv` not found

**Solution**: `pip install python-dotenv`

### Debug Mode

To see more detailed error messages, check the terminal output. All errors are captured in the execution results.

---

## 🚀 Future Improvements

- [ ] **More Tools**: Add integrations for incident management, logging, metrics
- [ ] **Persistent Memory**: Store past runs and allow planner to reuse results
- [ ] **Observability**: Structured logging, trace IDs, timing metrics
- [ ] **Streaming**: Stream partial results back to clients
- [ ] **Advanced Verification**: Cross-check APIs, historical comparisons
- [ ] **Configurable Policies**: Max tools, latency budgets, retry strategies
- [ ] **Web UI**: Browser-based interface for task submission
- [ ] **Tool Plugins**: Plugin system for adding custom tools

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests (if available)
pytest

# Format code
black ai_ops_assistant/
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI** for GPT models
- **OpenWeatherMap** for weather data API
- **GitHub** for repository search API
- **FastAPI** for the excellent web framework

---

## 📧 Contact

For questions or issues, please open an issue on GitHub or contact the maintainer.

---

**Made with ❤️ for GenAI internship assignments**
