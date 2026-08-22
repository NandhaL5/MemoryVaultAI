from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google import genai
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
import database

SECRET_KEY = "memoryvault-secret-key-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    client = None


# =========================================================
# PASSWORD CONFIGURATION
# =========================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str):
    # bcrypt supports maximum 72 bytes
    password = password.encode("utf-8")[:72].decode(
        "utf-8",
        errors="ignore"
    )

    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):

    password = password.encode("utf-8")[:72].decode(
        "utf-8",
        errors="ignore"
    )

    return pwd_context.verify(
        password,
        hashed_password
    )


# =========================================================
# FASTAPI APP
# =========================================================

def create_access_token(user_id: int):
    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode = {
        "user_id": user_id,
        "exp": expire
    }

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
def get_current_user(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("user_id")

        if user_id is None:
            return None

        return int(user_id)

    except JWTError:
        return None

app = FastAPI(
    title="MemoryVault AI",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://memoryvaultai-1.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# MODELS
# =========================================================

class Memory(BaseModel):
    user_id:int

    title: str = Field(
        ...,
        min_length=3,
        max_length=100
    )

    content: str = Field(
        ...,
        min_length=5
    )

    favorite: int = 0


class AIRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=2
    )


class RegisterRequest(BaseModel):

    name: str = Field(
        ...,
        min_length=2,
        max_length=50
    )

    email: str

    password: str = Field(
        ...,
        min_length=6,
        max_length=72
    )


class LoginRequest(BaseModel):

    email: str

    password: str


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "project": "MemoryVault AI",
        "message": "Backend Started Successfully",
        "gemini_api_loaded": GEMINI_API_KEY is not None
    }


# =========================================================
# REGISTER
# =========================================================

@app.post("/register")
def register_user(data: RegisterRequest):

    try:

        database.cursor.execute(
            "SELECT id FROM users WHERE email=?",
            (data.email,)
        )

        existing_user = database.cursor.fetchone()

        if existing_user:

            return {
                "status": "failed",
                "message": "Email already registered"
            }

        hashed_password = hash_password(
            data.password
        )

        created_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        database.cursor.execute(
            """
            INSERT INTO users
            (name, email, password, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                data.name,
                data.email,
                hashed_password,
                created_at
            )
        )

        database.conn.commit()

        return {
            "status": "success",
            "message": "User Registered Successfully",
            "name": data.name,
            "email": data.email
        }

    except Exception as e:

        print("REGISTER ERROR:", str(e))

        return {
            "status": "failed",
            "message": "Registration failed",
            "error": str(e)
        }


# =========================================================
# LOGIN
# =========================================================

@app.post("/login")
def login_user(data: LoginRequest):

    try:

        database.cursor.execute(
            """
            SELECT id, name, email, password
            FROM users
            WHERE email=?
            """,
            (data.email,)
        )

        user = database.cursor.fetchone()

        if user is None:

            return {
                "status": "failed",
                "message": "User not found"
            }

        if not verify_password(
            data.password,
            user[3]
        ):

            return {
                "status": "failed",
                "message": "Incorrect password"
            }

        return {
            "status": "success",
            "message": "Login Successful",
            "user_id": user[0],
            "access_token":
            create_access_token(user[0]),
            "name": user[1],
            "email": user[2]
        }

    except Exception as e:

        print("LOGIN ERROR:", str(e))

        return {
            "status": "failed",
            "message": "Login failed",
            "error": str(e)
        }
    # =========================================================
# FORGOT PASSWORD
# =========================================================

@app.post("/forgot-password")
def forgot_password(email: str):

    try:

        database.cursor.execute(
            "SELECT id FROM users WHERE email=?",
            (email,)
        )

        user = database.cursor.fetchone()

        if user is None:
            return {
                "status": "failed",
                "message": "Email not registered"
            }

        return {
            "status": "success",
            "message": "Email verified. Password reset can continue.",
            "user_id": user[0]
        }

    except Exception as e:

        print("FORGOT PASSWORD ERROR:", str(e))

        return {
            "status": "failed",
            "message": "Forgot password failed"
        }
    # =========================================================
# RESET PASSWORD
# =========================================================

class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str = Field(min_length=6)


@app.post("/reset-password")
def reset_password(data: ResetPasswordRequest):

    try:

        database.cursor.execute(
            "SELECT id FROM users WHERE email=?",
            (data.email,)
        )

        user = database.cursor.fetchone()

        if user is None:
            return {
                "status": "failed",
                "message": "Email not registered"
            }

        hashed_password = hash_password(data.new_password)

        database.cursor.execute(
            """
            UPDATE users
            SET password=?
            WHERE email=?
            """,
            (hashed_password, data.email)
        )

        database.conn.commit()

        return {
            "status": "success",
            "message": "Password reset successfully"
        }

    except Exception as e:

        print("RESET PASSWORD ERROR:", str(e))

        return {
            "status": "failed",
            "message": "Password reset failed"
        }


# =========================================================
# ADD MEMORY
# =========================================================

@app.post("/memory")
def add_memory(memory: Memory):

    try:

        created_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        database.cursor.execute(
            """
            INSERT INTO memories
            (user_id,title, content, created_at, favorite)
            VALUES (?, ?, ?, ?,?)
            """,
            (
                memory.user_id,
                memory.title,
                memory.content,
                created_at,
                memory.favorite
            )
        )

        database.conn.commit()

        return {
            "status": "success",
            "message": "Memory Saved Successfully"
        }

    except Exception as e:

        print("MEMORY SAVE ERROR:", str(e))

        return {
            "status": "failed",
            "message": "Memory save failed",
            "error": str(e)
        }


# =========================================================
# GET ALL MEMORIES
# =========================================================

@app.get("/memories")
def get_memories(token:str):

    try:
        user_id=get_current_user(token)

        if user_id is None:
            return {
                "status": "failed",
                "message": "Invalid or expired token"
            }
        database.cursor.execute(
            """
            SELECT
                id,
                user_id,
                title,
                content,
                created_at,
                favorite
            FROM memories
            WHERE user_id=?
            ORDER BY id ASC
            """,(user_id,)
        )

        memories = database.cursor.fetchall()

        return {
            "count": len(memories),
            "memories": memories
        }

    except Exception as e:

        print("GET MEMORIES ERROR:", str(e))

        return {
            "status": "failed",
            "message": "Could not load memories",
            "error": str(e)
        }
@app.get("/favorites")
def get_favorites(token: str):

    try:
        user_id = get_current_user(token)

        if user_id is None:
            return {
                "status": "failed",
                "message": "Invalid or expired token"
            }

        # Create a separate cursor for this request
        favorites_cursor = database.conn.cursor()

        favorites_cursor.execute(
            """
            SELECT
                id,
                user_id,
                title,
                content,
                created_at,
                favorite
            FROM memories
            WHERE user_id=? AND favorite=1
            ORDER BY id ASC
            """,
            (user_id,)
        )

        favorites = favorites_cursor.fetchall()

        favorites_cursor.close()

        print("FAVORITES DEBUG:", favorites)

        return {
            "status": "success",
            "count": len(favorites),
            "favorites": favorites
        }

    except Exception as e:

        print("GET FAVORITES ERROR:", str(e))

        return {
            "status": "failed",
            "message": "Could not load favorite memories",
            "error": str(e)
        }
# =========================================================
# UPDATE MEMORY
# =========================================================
@app.put("/memory/{memory_id}")
def update_memory(
    memory_id: int,
    token: str,
    memory: Memory
):

    try:

        user_id = get_current_user(token)

        if user_id is None:
            return {
                "status": "failed",
                "message": "Invalid or expired token"
            }

        database.cursor.execute(
            """
            UPDATE memories
            SET
                title=?,
                content=?,
                favorite=?
            WHERE id=? AND user_id=?
            """,
            (
                memory.title,
                memory.content,
                memory.favorite,
                memory_id,
                user_id
            )
        )

        if database.cursor.rowcount == 0:
            return {
                "status": "failed",
                "message": "Memory not found"
            }

        database.conn.commit()

        return {
            "status": "success",
            "message": "Memory Updated Successfully"
        }

    except Exception as e:

        print("UPDATE MEMORY ERROR:", str(e))

        return {
            "status": "failed",
            "message": "Memory update failed",
            "error": str(e)
        }

# =========================================================
# DELETE MEMORY
# =========================================================

@app.delete("/memory/{memory_id}")
def delete_memory(
    memory_id: int,
    token: str
):

    try:

        user_id = get_current_user(token)

        if user_id is None:
            return {
                "status": "failed",
                "message": "Invalid or expired token"
            }

        database.cursor.execute(
            "DELETE FROM memories WHERE id=? AND user_id=?",
            (memory_id, user_id)
        )

        database.conn.commit()

        if database.cursor.rowcount == 0:
            return {
                "status": "failed",
                "message": "Memory not found"
            }

        return {
            "status": "success",
            "message": "Memory Deleted Successfully"
        }

    except Exception as e:

        print("DELETE MEMORY ERROR:", str(e))

        return {
            "status": "failed",
            "message": "Memory deletion failed",
            "error": str(e)
        }
# =========================================================
# SEARCH MEMORY
# =========================================================

@app.get("/search")
def search_memory(
    keyword: str = Query(..., min_length=1),
    token: str = Query(...)
):

    try:

        user_id = get_current_user(token)

        if user_id is None:
            return {
                "status": "failed",
                "message": "Invalid or expired token"
            }

        database.cursor.execute(
            """
            SELECT
                id,
                user_id,
                title,
                content,
                created_at,
                favorite
            FROM memories
            WHERE user_id=?
            AND (
                title LIKE ?
                OR content LIKE ?
            )
            ORDER BY id ASC
            """,
            (
                user_id,
                f"%{keyword}%",
                f"%{keyword}%"
            )
        )

        memories = database.cursor.fetchall()

        return {
            "count": len(memories),
            "memories": memories
        }

    except Exception as e:

        print("SEARCH ERROR:", str(e))

        return {
            "status": "failed",
            "message": "Search failed",
            "error": str(e)
        }


# =========================================================
# ASK AI
# =========================================================
@app.post("/ask-ai")
def ask_ai(
    data: AIRequest,
    token: str
):

    if client is None:
        return {
            "status": "failed",
            "message": "Gemini API key is not configured."
        }

    try:

        user_id = get_current_user(token)

        if user_id is None:
            return {
                "status": "failed",
                "message": "Invalid or expired token"
            }

        database.cursor.execute(
            """
            SELECT
                id,
                user_id,
                title,
                content,
                created_at,
                favorite
            FROM memories
            WHERE user_id=?
            ORDER BY id DESC
            """,
            (user_id,)
        )

        memories = database.cursor.fetchall()

        if memories:

            memory_text = ""

            for memory in memories:

                favorite_status = (
                    "Yes" if memory[5] == 1 else "No"
                )

                memory_text += f"""
Memory ID: {memory[0]}
Title: {memory[2]}
Content: {memory[3]}
Created At: {memory[4]}
Favorite: {favorite_status}
"""

        else:

            memory_text = "No saved memories available."

        prompt = f"""
You are MemoryVault AI,
a personal memory assistant.

Saved memories:
--------------------
{memory_text}
--------------------

User question:
{data.question}

Instructions:
1. Use saved memories when relevant.
2. Never invent personal memories.
3. If personal information is not found, clearly say it was not found.
4. For general questions, answer normally.
5. Keep the answer simple and clear.

Answer the user now.
"""

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return {
            "status": "success",
            "question": data.question,
            "answer": response.text
        }

    except Exception as e:

        print("GEMINI ERROR:", str(e))

        return {
            "status": "failed",
            "message": "AI service is temporarily unavailable.",
            "error": str(e)
        }
       
    # =========================================================
# USER PROFILE
# =========================================================
@app.get("/profile")
def get_profile(token: str):

    try:
        user_id = get_current_user(token)

        if user_id is None:
            return {
                "status": "failed",
                "message": "Invalid or expired token"
            }

        database.cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                created_at
            FROM users
            WHERE id=?
            """,
            (user_id,)
        )

        user = database.cursor.fetchone()

        if user is None:
            return {
                "status": "failed",
                "message": "User not found"
            }

        return {
            "status": "success",
            "profile": user
        }

    except Exception as e:

        print("GET PROFILE ERROR:", str(e))

        return {
            "status": "failed",
            "message": "Could not load profile",
            "error": str(e)
        }
    # =========================================================
# DASHBOARD
# =========================================================
@app.get("/dashboard")
def get_dashboard(token: str):

    try:
        user_id = get_current_user(token)

        if user_id is None:
            return {
                "status": "failed",
                "message": "Invalid or expired token"
            }

        database.cursor.execute(
            "SELECT COUNT(*) FROM memories WHERE user_id=?",
            (user_id,)
        )
        total_memories = database.cursor.fetchone()[0]

        database.cursor.execute(
            "SELECT COUNT(*) FROM memories WHERE user_id=? AND favorite=1",
            (user_id,)
        )
        favorite_memories = database.cursor.fetchone()[0]

        return {
            "status": "success",
            "dashboard": {
                "total_memories": total_memories,
                "favorite_memories": favorite_memories
            }
        }

    except Exception as e:

        print("DASHBOARD ERROR:", str(e))

        return {
            "status": "failed",
            "message": "Could not load dashboard",
            "error": str(e)
        }
