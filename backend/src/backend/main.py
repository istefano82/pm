from fastapi import FastAPI, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import secrets

app = FastAPI(title="Project Management MVP Backend")

# Hardcoded credentials for MVP
VALID_USERNAME = "user"
VALID_PASSWORD = "password"

# Simple in-memory token store (for MVP only - not production)
valid_tokens = set()

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    message: str

@app.post("/api/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login with hardcoded credentials"""
    if request.username != VALID_USERNAME or request.password != VALID_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate token
    token = secrets.token_urlsafe(32)
    valid_tokens.add(token)
    
    return LoginResponse(token=token, message="Login successful")

@app.post("/api/logout")
async def logout(authorization: str = Header(None)):
    """Logout and invalidate token"""
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        valid_tokens.discard(token)
    
    return {"message": "Logged out successfully"}

@app.get("/api/verify")
async def verify(authorization: str = Header(None)):
    """Verify authentication token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization[7:]
    if token not in valid_tokens:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return {"status": "authenticated"}

@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "Backend is running"}

# Mount NextJS static assets
app.mount("/_next", StaticFiles(directory="static/_next"), name="next_static")

# Mount favicon and other public files
app.mount("/public", StaticFiles(directory="static"), name="public_files")

# Catch-all SPA route handler - serves index.html for any non-API path
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    """Serve index.html for all non-API routes (SPA routing)"""
    # Don't serve HTML for actual files that exist
    if full_path and ("." in full_path or full_path.startswith("_next")):
        return FileResponse(f"static/{full_path}")
    
    # For all other paths, serve index.html (SPA routing)
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)