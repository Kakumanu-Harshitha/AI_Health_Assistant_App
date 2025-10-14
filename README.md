# AI Health Assistant
This project is a comprehensive, multimodal AI Health Assistant designed to provide preliminary health guidance. Users can interact with the assistant using text, voice, or by uploading images, and receive safe, informative responses, including diet and lifestyle recommendations. The application features a secure user authentication system, a persistent conversation history, and a user-friendly dashboard.

# ✨ Features
**Multimodal Input:** Users can ask questions by typing text, recording their voice, or uploading an image, and provide all inputs together for a comprehensive query.

**AI-Powered Responses:** Utilizes a powerful Large Language Model (LLM) from Groq, configured with a detailed system prompt to act as a safe and empathetic health advisor.

**Secure Authentication:** A complete user signup and login system using JWT (JSON Web Tokens) to protect user data.

**Conversation Memory:** Chat history is stored securely in a MongoDB Atlas database, providing context for ongoing conversations.

**User Dashboard:** A dedicated page for users to review their entire conversation history.

**Fully Asynchronous Backend:** Built with FastAPI for high performance.

**Interactive Frontend:** A user-friendly and responsive interface built with Streamlit.

# 🛠️ Tech Stack
**Backend:**

Framework: FastAPI

LLM Service: Groq (for llama-3.1-8b-instant and whisper-large-v3 STT)

Authentication: python-jose for JWT, passlib for password hashing

**Frontend:**

Framework: Streamlit

Audio Recording: st-audiorec

**Databases:**

User Data: PostgreSQL

Conversation History: MongoDB Atlas

Deployment: Configured for cloud platforms like Railway or Render.

# 📁 Project Structure
Ai_health_assistant/

├── backend/

│   ├── auth.py             # Handles user signup, login, and JWT tokens

│   ├── dashboard_service.py # Powers the user dashboard

│   ├── llm_service.py      # The "brain" - communicates with the Groq LLM

│   ├── main.py             # Main FastAPI application entrypoint

│   ├── mongo_memory.py     # Manages conversation history in MongoDB

│   ├── query_service.py    # Handles all user queries (text, voice, image)

│   ├── speech_service.py   # Handles STT 

│   └── sql.py              # Manages PostgreSQL connection and user table

│

├── frontend/

│   └── app.py # The complete Streamlit frontend application

│

├── .env                    # Secret keys and configuration (MUST BE CREATED)

└── requirements.txt        # Python package dependencies

# Owner
[Harshitha-Kakumanu](https://github.com/Kakumanu-Harshitha)
