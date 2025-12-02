/**
 * Types for the air quality feature.
 */

export interface Pollutant {
  name: string;
  value: number;
  units: string;
}

export interface AirQualityResponse {
  area: string;
  max_daqi: number;
  summary: string;
  pollutants: Pollutant[];
}
