from fastapi import FastAPI, Request, HTTPException
import httpx, os

app = FastAPI()
TARGET_BASE_URL = os.getenv("TARGET_BASE_URL", "https://api.groq.com/openai/v1")
TARGET_API_KEY = os.getenv("TARGET_API_KEY", "")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD", "")

@app.api_route("/{path:path}", methods=["GET", "POST"])
async def proxy(request: Request, path: str):
    auth = request.headers.get("Authorization", "")
    if PROXY_PASSWORD and auth != f"Bearer {PROXY_PASSWORD}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    headers = dict(request.headers)
    headers["Authorization"] = f"Bearer {TARGET_API_KEY}"
    headers.pop("host", None)
    
    body = await request.body()
    
    async with httpx.AsyncClient() as client:
        req = client.build_request(
            request.method, f"{TARGET_BASE_URL}/{path}", headers=headers, content=body
        )
        response = await client.send(req, stream=True)
        return response
