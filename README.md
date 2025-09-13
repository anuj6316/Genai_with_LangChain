# Genai_with_LangChain
Learning LangChain with CampusX

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/anuj6316/Genai_with_LangChain.git
cd Genai_with_LangChain
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
1. Copy the example environment file:
   ```bash
   copy env.example .env
   ```

2. Edit `.env` file and add your API keys:
   ```
   HUGGINGFACEHUB_API_KEY=your_huggingface_token_here
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   ```

### 5. Get API Keys
- **Hugging Face**: https://huggingface.co/settings/tokens
- **OpenAI**: https://platform.openai.com/api-keys
- **Google**: https://makersuite.google.com/app/apikey

## Project Structure
```
V03_Langchains_Models/
├── 01LLMs/           # Large Language Models
├── 02Chat_Models/    # Chat Models
└── 03Embedding_Models/ # Embedding Models
```

## Usage
Run any of the model examples:
```bash
python V03_Langchains_Models/01LLMs/OpenAI.py
python V03_Langchains_Models/02Chat_Models/Gemini_Chat_Model.py
python V03_Langchains_Models/02Chat_Models/huggingface_api_model.py
```

## Security Note
- Never commit your `.env` file to version control
- The `.env` file is already in `.gitignore`
- Use `env.example` as a template for required environment variables
