/**
 * Centralized API client configuration.
 *
 * Provides a single source of truth for the API base URL and shared utilities.
 */

/**
 * Base URL for the backend API.
 * Configured via VITE_API_BASE_URL environment variable.
 * Defaults to "/api" for production builds where nginx proxies requests to the backend.
 * IMPORTANT: Do not set to Docker-internal hostnames - browsers cannot resolve them.
 */
export const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

/** Maximum number of retry attempts for transient failures */
export const MAX_RETRIES = 3;

/** Base delay in milliseconds between retry attempts */
export const RETRY_DELAY_MS = 1000;

/**
 * Helper function to create a delay.
 * @param ms - Delay in milliseconds
 */
export async function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Standard API error type.
 */
export interface ApiError {
  message: string;
  status?: number;
}
