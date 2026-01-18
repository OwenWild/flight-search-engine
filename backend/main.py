from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import httpx
import os

from data.FlightSearchQuery import FlightSearchQuery

app = FastAPI(title="Flight Search Engine")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: replace with actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/status")
async def get_status():
    """Validates the backend is running."""
    return {
        "status": "online",
        "service": "flight-search-backend",
        "version": "2.0.0"
    }

@app.post("/search")
async def search_flights(query: FlightSearchQuery):
    """
    Search for flights.
    """
    try:
        async with httpx.AsyncClient() as client:
            # TODO: Call flight API here
            # response = await client.get("https://api.example.com/flights", params=query.model_dump())
            # data = response.json()
            pass

        # Mock Data
        return {
            "status": "success",
            "search_criteria": query,
            "results": [
                {"id": 1, "airline": "FastAPI Air", "price": 450},
                {"id": 2, "airline": "Async Airways", "price": 520}
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- 5. Run the server ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)