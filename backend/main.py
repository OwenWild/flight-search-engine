from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import httpx
import os
import asyncio
from datetime import date, datetime
from typing import List, Dict, Any

from FlightCache import FlightCache
from data.FlightRoute import FlightRoute
from data.FlightSearchQuery import FlightSearchQuery
from data.FlightSearchResult import FlightSearchResult, FlightSegment, FlightSearchResultByCombination


@asynccontextmanager
async def lifespan(app: FastAPI):
    cleanup_task = asyncio.create_task(cache_cleaner())
    yield

    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        print("Background cache cleaner error.") # TODO: Build proper logging

app = FastAPI(title="Flight Search Engine", lifespan=lifespan)
token = None 
base = "https://test.api.amadeus.com"  # or https://api.amadeus.com for prod
client_id = os.environ["AMADEUS_CLIENT_ID"]
client_secret = os.environ["AMADEUS_CLIENT_SECRET"]
token_lock = asyncio.Lock() # this stops multiple versions calling the new create function

flight_cache = FlightCache()

async def get_token(client: httpx.AsyncClient) -> str:
    r = await client.post(
        f"{base}/v1/security/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=20,
    )
    return r.json()["access_token"]
async def ensure_token(client: httpx.AsyncClient) -> str:
    global token
    if token is not None:
        return token
    async with token_lock: # stops extra token calls
        if token is None: #check after lock leaves
            token = await get_token(client)
    return token

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
    try:
        async with httpx.AsyncClient() as client:
            global token
            token = await ensure_token(client)

            results = []

            for origin, dest, dt in parse_query(query):
                dt_str = dt.isoformat()
                route = FlightRoute(origin, dest, convert_string_to_date(dt_str))

                # Check cache
                cached_data = flight_cache.get(route)
                if cached_data:
                    results.append(cached_data)
                    continue

                # If not in cache, call API
                params = {
                    "originLocationCode": origin,
                    "destinationLocationCode": dest,
                    "departureDate": dt_str,
                    "adults": 1,
                    "currencyCode": "USD",
                    "max": 50,
                }

                r = await client.get(
                    f"{base}/v2/shopping/flight-offers",
                    params=params,
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=30,
                )

                data = r.json()
                flights = parse_amadeus_results(data.get("data", []), route)
                flight_dicts = flights.model_dump()
                flight_cache.set(route, flight_dicts)

                results.append(flight_dicts)

        results.sort(key=lambda r: r["flights"][0]["price"])

        return results[:6]

    except Exception as e:
        print(f"Error: {e}")  # Log it
        raise HTTPException(status_code=500, detail=str(e))



def parse_query(q: FlightSearchQuery):
    # yields (origin, destination, date)
    for o in q.origins:
        for d in q.destinations:
            for dt in q.departure_dates:
                yield (o.upper().strip(), d.upper().strip(), dt)
   
   
def convert_string_to_datetime(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))

def convert_string_to_date(s: str) -> date:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).date()
             
def parse_amadeus_results(amadeus_offers: List[Dict[str, Any]], route: FlightRoute) -> FlightSearchResultByCombination:
    flights: List[FlightSearchResult] = []

    for offer in amadeus_offers:
        itin = offer["itineraries"][0]
        segs = itin["segments"]

        segments = [
            FlightSegment(
                origin=s["departure"]["iataCode"],
                destination=s["arrival"]["iataCode"],
                start_time=convert_string_to_datetime(s["departure"]["at"]),
                end_time=convert_string_to_datetime(s["arrival"]["at"]),
            )
            for s in segs
        ]

        airline = (offer.get("validatingAirlineCodes") or [segs[0].get("carrierCode", "")])[0]
        price = float(offer["price"]["total"])

        flights.append(
            FlightSearchResult(
                airline=airline,
                price=price,
                segments=segments,
            )
        )

    flights.sort(key=lambda r: r.price)

    return FlightSearchResultByCombination(
        date=route.date,
        origin=route.origin,
        destination=route.destination,
        flights=flights
    )



async def cache_cleaner():
    """Run cleanup every hour."""
    while True:
        try:
            await asyncio.sleep(3600)
            flight_cache.cleanup()
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error in cache cleaner: {e}")



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
    
    
    
    
    
    
    
    
    
    ## DATA RETURNED FROM BACKEND
#    [
#   {
#     "airline": "TK",
#     "date": "2026-01-19",
#     "price": 780.1,
#     "segments": [
#       {
#         "origin": "BOS",
#         "destination": "IST",
#         "start_time": "2026-01-19T20:00:00",
#         "end_time": "2026-01-20T13:25:00"
#       },
#       {
#         "origin": "IST",
#         "destination": "SYD",
#         "start_time": "2026-01-20T15:30:00",
#         "end_time": "2026-01-21T19:50:00"
#       }
#     ]
#   },
#   {
#     "airline": "QR",
#     "date": "2026-01-19",
#     "price": 1106.8,
#     "segments": [
#       {
#         "origin": "BOS",
#         "destination": "DOH",
#         "start_time": "2026-01-19T21:05:00",
#         "end_time": "2026-01-20T17:00:00"
#       },
#       {
#         "origin": "DOH",
#         "destination": "SYD",
#         "start_time": "2026-01-20T20:40:00",
#         "end_time": "2026-01-21T18:50:00"
#       }
#     ]
#   },
#   {
#     "airline": "EK",
#     "date": "2026-01-19",
#     "price": 1384.3,
#     "segments": [
#       {
#         "origin": "BOS",
#         "destination": "DXB",
#         "start_time": "2026-01-19T22:10:00",
#         "end_time": "2026-01-20T19:20:00"
#       },
#       {
#         "origin": "DXB",
#         "destination": "SYD",
#         "start_time": "2026-01-20T21:45:00",
#         "end_time": "2026-01-21T18:35:00"
#       }
#     ]
#   },
#   {
#     "airline": "B6",
#     "date": "2026-01-19",
#     "price": 1495.8,
#     "segments": [
#       {
#         "origin": "BOS",
#         "destination": "DOH",
#         "start_time": "2026-01-19T21:05:00",
#         "end_time": "2026-01-20T17:00:00"
#       },
#       {
#         "origin": "DOH",
#         "destination": "SYD",
#         "start_time": "2026-01-20T20:40:00",
#         "end_time": "2026-01-21T18:50:00"
#       }
#     ]
#   },
#   {
#     "airline": "EY",
#     "date": "2026-01-19",
#     "price": 1504.3,
#     "segments": [
#       {
#         "origin": "BOS",
#         "destination": "DCA",
#         "start_time": "2026-01-19T20:00:00",
#         "end_time": "2026-01-19T21:51:00"
#       },
#       {
#         "origin": "IAD",
#         "destination": "AUH",
#         "start_time": "2026-01-20T21:10:00",
#         "end_time": "2026-01-21T19:05:00"
#       },
#       {
#         "origin": "AUH",
#         "destination": "SYD",
#         "start_time": "2026-01-21T21:05:00",
#         "end_time": "2026-01-22T17:55:00"
#       }
#     ]
#   },
#   {
#     "airline": "EY",
#     "date": "2026-01-19",
#     "price": 1504.3,
#     "segments": [
#       {
#         "origin": "BOS",
#         "destination": "DCA",
#         "start_time": "2026-01-19T20:00:00",
#         "end_time": "2026-01-19T21:51:00"
#       },
#       {
#         "origin": "IAD",
#         "destination": "AUH",
#         "start_time": "2026-01-20T21:10:00",
#         "end_time": "2026-01-21T19:05:00"
#       },
#       {
#         "origin": "AUH",
#         "destination": "SYD",
#         "start_time": "2026-01-22T09:50:00",
#         "end_time": "2026-01-23T06:35:00"
#       }
#     ]
#   }
# ]

