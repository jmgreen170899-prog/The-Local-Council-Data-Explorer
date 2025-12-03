/**
 * API functions for the planning feature.
 */

import type { PlanningResponse, ApiError } from "./types";

// Falls back to relative URL for local dev (uses vite proxy) or nginx proxy
const API_BASE = `${import.meta.env.VITE_API_BASE_URL || ''}/api/planning`;
const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 1000;

async function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Fetch planning applications for a given local planning authority.
 * Includes retry logic for transient failures.
 */
export async function fetchPlanningApplications(
  lpa: string,
  dateFrom: string = "",
  dateTo: string = ""
): Promise<PlanningResponse> {
  const params = new URLSearchParams();
  params.append("lpa", lpa);
  if (dateFrom) params.append("date_from", dateFrom);
  if (dateTo) params.append("date_to", dateTo);

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
      
      return response.json() as Promise<PlanningResponse>;
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
