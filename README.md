# Exploring the Potential of an LLM-Driven Opponent in DaMath

**Authors:** Gon Vincent Alicando, Ramel Cary Jamen, Edward Vincent Escasio  
**Supervised by:** Malikey M. Maulana  
**Department of Computer Science, MSU–Iligan Institute of Technology**

May 2025

---

## Abstract

This undergraduate thesis investigates the application of **Large Language Models (LLMs)** as an opponent in the board game **Damath**. The research proposes an **LLM Agent** whose knowledge is based on embedded Damath information, mechanics, and representations stored in a vector database, with its output evaluated through test-driven prompt engineering. A **Damath Game Engine** will be developed to facilitate interaction between the user and the LLM Agent, managing inputs/outputs and updating the game state. Additionally, a web application will be created to provide a user interface for the Damath game, connecting the user to the game engine and the LLM Agent.

## Background of the Study

The paper highlights the increasing prevalence of LLMs and their advancements in AI, including their use in gaming for NPC behavior, game design, and playing games. While AI has been widely applied to board games like Chess and Go, the use of LLMs as game-playing agents in lesser-known board games like Damath is a growing area. Damath, an educational board game combining checkers with mathematical operations, has shown potential in improving math students' understanding. This research explores the novel application of an **LLM-Driven opponent** in Damath. Existing AI applications in Damath are limited, especially concerning LLMs, with no known prior studies on their usage in this game.

## Objectives

The main objective of this study is to **explore the potential of a Damath opponent that utilizes a Large Language Model capable of playing against real players**.

The specific objectives include:

- To develop a **board structure and piece movement representation of Damath** to serve as an input to the LLM Agent.
- To create an **LLM Agent** designed to specifically play Damath that utilizes an instruct-based Large Language Model, embedded with the Portable Document Format of Damath information, mechanics, and its representations stored in the vector database, which will serve as the core knowledge base of the LLM agent.
- To create the **game engine** that is responsible for the input and output of user and LLM Agent, and vice versa.
- To create an **architectural design and prototype of the Damath game system**, incorporating a user interface, game engine, game storage, and an integrated LLM Agent within a cohesive game client and game server framework.

## Methodology

The research methodology involves several key stages:

- **Creating Game Representations:** Developing representations for the Damath board and piece movements (normal and capture) that can be understood by the LLM Agent. This includes a **one-dimensional array representation of the board** converted into **JSON format**. **Movement notations** in JSON format will also be defined for normal moves and captures.
- **Developing the LLM Agent:** Utilizing an open-source framework and employing **LLaMA3.1 with 8B parameters** as the instruct-based language model. **Retrieval-Augmented Generation (RAG)** will be used, embedding Damath game mechanics (in PDF format) and representations into the agent's knowledge base using **nomic-embed-text embedding** and **Ollama**. The agent's output (moves in JSON format) will be tested using **promptfoo**.
- **Developing the Damath Game Engine:** Creating a game engine responsible for processing inputs and outputs between the player and the LLM Agent. This includes functions for determining valid moves, validating moves, handling piece captures based on Damath mechanics, and converting game states into formats understandable by the LLM Agent.
- **Constructing System Architecture:** Designing a system architecture that includes the **Player (Game Client)**, **Game Engine (Game Server)**, and **LLM Agent (Game Server)**, with data exchange primarily in **JSON format**.
- **Developing the Damath Application Prototype:** Building a web application for the Damath game using the **Python Flask framework** to provide a user interface and integrate the game engine and LLM Agent.

## Key Components

The system will consist of the following main components:

- **LLM Agent:** An AI agent powered by LLaMA3.1, trained on Damath rules and mechanics, capable of playing the game.
- **Damath Game Engine:** The core logic of the Damath game, responsible for managing the game state, rules, and interactions between the player and the LLM Agent.
- **Web Application:** A user interface built with Flask, allowing users to play Damath against the LLM Agent and potentially access a helper chat powered by the same LLM.

## Significance and Contribution

This research is significant in the field of **Game Design and Development** by exploring the use of LLMs as game opponents for Damath. It aims to assess the model's ability to learn game mechanics and make informed decisions as an AI opponent. This study could potentially set a standard for **AI applications in less common board games** and provide valuable insights for future integration of LLMs as game opponents. Furthermore, it explores the synergy between **AI and educational games** like Damath to potentially enhance learning outcomes.


## Keywords

Artificial Intelligence, Large Language Models, Board Games, Damath, LLM Agent


# Setting Up Local DaMath LLM (Ollama, Flask, and Langchain)

### 1. [Install](https://github.com/ollama/ollama?tab=readme-ov-file#macos) ollama and pull models

Pulling the LLM that would be used:

```shell
ollama pull llama3.2:3b-instruct-q8_0

ollama pull gemma3:12b-it-q8_0
```

### 2. Create a virtual environment

```shell
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install libraries

```shell
pip install -r requirements.txt
```

### 4. Schema for testing endpoints 
- Import "rest-api.json" to your Postman or Insomnia Application

### 5. Running the Flask App and Lanchain App

```shell
chmod +x script.sh
./script.sh
```



