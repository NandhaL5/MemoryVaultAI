\# MemoryVault AI



AI-Powered Personal Memory Management System

Built with FastAPI, SQLite, JavaScript, and Google Gemini AI.

Version 1.0.0



MemoryVault AI is an AI-powered personal memory management system.



It allows users to securely store, manage, search, edit, delete,

and favorite their personal memories.



It also provides an AI assistant that can answer questions

using the user's saved memories.



\## Features



\- User Registration and Login

\- JWT Authentication

\- Add Memories

\- View Memories

\- Edit Memories

\- Delete Memories

\- Favorite Memories

\- Search Memories

\- Favorites List

\- Dashboard

\- Ask AI

\- Password Reset



\## Technologies Used



\### Backend

\- Python

\- FastAPI

\- SQLite

\- Pydantic

\- JWT

\- Passlib

\- bcrypt

\- Google Gemini API



\### Frontend

\- HTML

\- CSS

\- JavaScript



\### Other

\- Uvicorn

\- python-dotenv



\## Project Structure



MemoryVauLtAI/

│

├── backend/

│   ├── main.py

│   ├── database.py

│   ├── memoryvault.db

│   ├── .env

│   └── venv/

│

├── frontend/

│   └── index.html

│

├── database/

├── docs/

├── uploads/

│

├── memoryvault.db

└── README.md



\## How to Run



\### 1. Start Backend



Open PowerShell and run:



cd C:\\Users\\nandh\\Desktop\\MemoryVauLtAI\\backend



.\\venv\\Scripts\\Activate.ps1



python -m uvicorn main:app --reload --port 8001



Backend URL:



http://127.0.0.1:8001





\### 2. Start Frontend



Open another PowerShell window and run:

cd C:\\Users\\nandh\\Desktop\\MemoryVauLtAI\\frontend

python -m http.server 5500



Frontend URL:

http://127.0.0.1:5500



\## API Endpoints



GET    /                 - Check backend status

POST   /register         - Register a new user

POST   /login            - Login user

POST   /forgot-password  - Verify email

POST   /reset-password   - Reset password



POST   /memory           - Add a memory

GET    /memories         - Get user's memories

PUT    /memory/{id}      - Edit a memory

DELETE /memory/{id}      - Delete a memory



GET    /favorites        - Get favorite memories

GET    /search           - Search memories

GET    /profile          - Get user profile

GET    /dashboard        - Get dashboard statistics



POST   /ask-ai           - Ask MemoryVault AI



\## Security



MemoryVault AI uses JWT authentication to protect user data.

Passwords are securely hashed using bcrypt.

Each user can access only their own memories.

The Gemini API key is stored in the backend .env file

and should never be exposed in the frontend or shared publicly.



\## Project Status



MemoryVault AI core features are completed and tested.



Completed features:

\- Login ✅

\- Register ✅

\- Add Memory ✅

\- View Memories ✅

\- Edit Memory ✅

\- Delete Memory ✅

\- Favorite Memory ✅

\- Favorites List ✅

\- Search Memories ✅

\- Dashboard ✅

\- Ask AI ✅

\- Password Reset ✅



\## System Architecture



User

&#x20; |

&#x20; v

Frontend (HTML + CSS + JavaScript)

&#x20; |

&#x20; v

FastAPI Backend

&#x20; |

&#x20; +-------------------+

&#x20; |                   |

&#x20; v                   v

SQLite Database     Google Gemini AI

&#x20; |

&#x20; v

User Memories





\## Requirements



Before running MemoryVault AI, make sure the following are installed:

\- Python 3.14 or later

\- FastAPI

\- Uvicorn

\- SQLite

\- Google Gemini API Key

\- Modern Web Browser





\## Environment Configuration



Create a `.env` file inside the `backend` folder.

Add your Gemini API key:

GEMINI\_API\_KEY=your\_gemini\_api\_key

Never share the `.env` file or your API key publicly.





\## Database



MemoryVault AI uses SQLite for data storage.



The database stores:

\- User accounts

\- Password hashes

\- User memories

\- Favorite status

\- Memory creation dates



The database file is:

memoryvault.db





\## Authentication



MemoryVault AI uses JWT-based authentication.



When a user logs in:

1\. The backend verifies the email and password.

2\. A JWT access token is generated.

3\. The token is stored in the browser.

4\. The token is used to access protected memory APIs.

5\. Each user can access only their own memories.





\## Main Features



\### User Management

\- User Registration

\- User Login

\- JWT Authentication

\- Forgot Password

\- Reset Password

\- User Profile



\### Memory Management

\- Add Memories

\- View Memories

\- Edit Memories

\- Delete Memories

\- Search Memories

\- Mark Memories as Favorites

\- View Favorite Memories



\### AI Assistant

\- Ask questions about saved memories

\- Uses Google Gemini AI

\- Provides answers based on the user's saved memories

\- Supports general questions





\## Testing



The following features have been tested successfully:



\- Backend connection

\- User registration

\- User login

\- JWT token authentication

\- Add memory

\- View memories

\- Edit memory

\- Delete memory

\- Favorite and unfavorite memory

\- Search memories

\- Favorites list

\- Dashboard

\- Ask AI

\- Password reset



\## Future Improvements



Planned improvements for future versions:



\- Email-based password reset

\- Faster AI responses

\- Improved frontend UI

\- Mobile application

\- Memory categories and tags

\- Memory export and import

\- Advanced AI memory search

\- Cloud database support

\- Deployment to a public server





\## License



This project is developed as an academic and personal project.



© 2026 MemoryVault AI

