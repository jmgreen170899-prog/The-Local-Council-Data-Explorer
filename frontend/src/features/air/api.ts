/**
 * API functions for the air quality feature.
 */

import type { AirQualityResponse } from "./types";

const API_BASE = "/api/air-quality";

/**
 * Fetch air quality data for a given area.
 */
export async function fetchAirQuality(
  area: string = ""
): Promise<AirQualityResponse> {
  const params = new URLSearchParams();
  if (area) params.append("area", area);

  const response = await fetch(`${API_BASE}?${params.toString()}`);
  if (!response.ok) {
    throw new Error("Failed to fetch air quality data");
  }
  return response.json();
}
