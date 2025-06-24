Here is your requested raw `README.md` file in markdown format:

````markdown
# Exploring the Potential of an LLM-Driven Opponent in DaMath

**Authors:** Gon Vincent Alicando, Ramel Cary Jamen, Edward Vincent Escasio  
**Supervisor:** Malikey M. Maulana  
**Department of Computer Science, MSU–Iligan Institute of Technology**  
**May 2025**

## Overview

This repository contains the code and documentation for our undergraduate thesis exploring the use of a Large Language Model (LLM) as a game-playing agent in the educational board game DaMath. We design, implement, and evaluate an LLM-driven opponent workflow that integrates prompt-to-code generation, tool calling, and metaprogramming within a Retrieval-Augmented Generation (RAG) framework.

### Key components include:

- **DaMath Game Engine**  
  A Python engine handling board state, piece movement, capturing, and scoring rules for DaMath.

- **LLM Agent**  
  A LangChain-based agent powered by LLaMA3 models running on Ollama; generates code to compute valid moves, selects best moves, and interacts with the game engine.

- **Baselines & Evaluation**  
  Comparison against a Random Choice Generator (RCG) AI and a Minimax AI with alpha-beta pruning over 50 simulated games each, plus runtime analysis.

- **Web Application Prototype**  
  A Flask-based back end and React front end providing an interactive UI for human vs. LLM and human vs. AI gameplay.

## Evaluation & Results

Results of our experiments—including LLM vs. RCG and LLM vs. Minimax over 50 games—can be found in the `results/` directory along with Jupyter notebooks for score analysis, runtime benchmarking, and hallucination assessment.

## Keywords

Artificial Intelligence, Large Language Models, Board Games, Damath, LLM Agent

## References

* Alicando, G. V., Jamen, R. C., & Escasio, E. V. “Exploring the Potential of LLM-Driven Opponent in DaMath.” MSU–Iligan Institute of Technology, May 2025.
* OpenAI et al., “GPT and Large Language Models.” 2023.
* Gallotta, F., et al. “Survey of LLMs in Games.” 2024.
* Dalidig, et al. “Game-Based Learning in Mathematics.” 2020.

---

# Installation & Setup

### Clone this repository:

```bash
git clone https://github.com/RCJamen/damathllm.git
cd damathllm
````
It is advisable to setup your own .env after cloning.

### Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies:

```bash
pip install -r requirements.txt
```

### Setup the database of the application

```bash
python3 setup_database.py
```

### [Install](https://github.com/ollama/ollama?tab=readme-ov-file#macos) ollama and pull models

Pulling the LLM that would be used:

```bash
ollama pull llama3.2:3b-instruct-q8_0
ollama pull gemma3:12b-it-q8_0
```

### Schema for testing endpoints

Import `rest-api.json` to your Postman or Insomnia Application

### Running the Flask App and LangChain App

```bash
chmod +x script.sh
./script.sh
```

