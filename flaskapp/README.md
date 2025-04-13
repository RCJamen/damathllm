# Flask Server RAG with Ollama & PgVector

### 1. [Install](https://github.com/ollama/ollama?tab=readme-ov-file#macos) ollama and pull models

Pull the LLM you'd like to use:

```shell
ollama pull phi3

ollama pull llama3.1
```

Pull the Embeddings model:

```shell
ollama pull nomic-embed-text
```

### 2. Create a virtual environment

```shell
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install libraries

```shell
pip install -r requirements.txt
npm install -g promptfoo
```

### 4. Run PgVector

> Install [docker desktop](https://docs.docker.com/desktop/install/mac-install/) first.

- Run using a helper script

```shell
sudo ./run_pgvector.sh
```

### 5. Set .env and .flaskenv

```shell
cp env-example .env
cp flaskenv-example .flaskenv
```
and add details configuration.

### 6. Schema for testing endpoints 
- Import "postman-damath-collection.json" to your Postman Application

### 7. Run Flask RAG App

```shell
flask run
```

### 8. Debugging Commands

```shell
DOCKER
sudo docker stop "name-of-img"
sudo docker rm "name-of-img"
sudo docker stats "name-of-img"
sudo docker exec -it "name-of-img" /bin/bash
```

- Add websites or PDFs and ask question.
- Example PDF: https://phi-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf
- Example Websites:
  - https://techcrunch.com/2024/04/18/meta-releases-llama-3-claims-its-among-the-best-open-models-available/?guccounter=1
  - https://www.theverge.com/2024/4/23/24137534/microsoft-phi-3-launch-small-ai-language-model


<!-- 
  steps to run:

start pgvector docker: sudo docker start pgvector
next: flask run before postman initialize
next: intialize postman
next: start kubi -->
  