/**
 * Represents a single leg of a journey (e.g., JFK to LHR)
 */
export interface FlightSegment {
  origin: string;        // e.g., "SFO"
  destination: string;   // e.g., "JFK"
  start_time: string;     // ISO 8601 string (e.g., "2024-12-01T10:30:00Z")
  end_time: string;       // ISO 8601 string
}

/**
 * Represents a full flight search result (an "itinerary")
 */
export interface FlightSearchResult {
  airline: string;       // e.g., "United Airlines"
  date: string;          // e.g., "2024-12-01"
  price: number;         // e.g., 450.50
  segments: FlightSegment[];
}

/**
 * The expected response from your flight search endpoint
 */
export type FlightSearchResponse = FlightSearchResult[];