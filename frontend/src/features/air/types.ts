/**
 * Types for the air quality feature.
 */

export interface Pollutant {
  name: string;
  value: number;
  units: string;
  band?: string | null;
  index?: number | null;
}

export interface AirQualityResponse {
  area: string;
  max_daqi: number;
  summary: string;
  pollutants: Pollutant[];
  forecast_date?: string | null;
}

export interface AirQualityRequest {
  area?: string;
}

export interface ApiError {
  message: string;
  status?: number;
}
