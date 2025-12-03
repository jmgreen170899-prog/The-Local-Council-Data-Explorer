/**
 * API functions for the air quality feature.
 */

import type { AirQualityResponse, ApiError } from "./types";

const API_BASE = "/api/air-quality";
const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 1000;

async function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Fetch air quality data for a given area.
 * Includes retry logic for transient failures.
 */
export async function fetchAirQuality(
  area: string = ""
): Promise<AirQualityResponse> {
  const params = new URLSearchParams();
  if (area) params.append("area", area);

  let lastError: ApiError = { message: "Unknown error" };

  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      const response = await fetch(`${API_BASE}?${params.toString()}`);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = (errorData as { detail?: string }).detail || `HTTP error ${response.status}`;
        
        if (response.status >= 500 && attempt < MAX_RETRIES - 1) {
          await delay(RETRY_DELAY_MS * (attempt + 1));
          continue;
        }
        
        throw { message: errorMessage, status: response.status } as ApiError;
      }
      
      return response.json() as Promise<AirQualityResponse>;
    } catch (error) {
      if ((error as ApiError).status !== undefined) {
        throw error;
      }
      
      lastError = { message: error instanceof Error ? error.message : "Network error" };
      
      if (attempt < MAX_RETRIES - 1) {
        await delay(RETRY_DELAY_MS * (attempt + 1));
      }
    }
  }

  throw lastError;
}
