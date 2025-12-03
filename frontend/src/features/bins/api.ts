/**
 * API functions for the bins feature.
 */

import type { BinCollectionResponse } from "./types";
import {
  API_BASE,
  MAX_RETRIES,
  RETRY_DELAY_MS,
  delay,
  type ApiError,
} from "../../api/client";

/**
 * Fetch bin collection data for a given postcode or UPRN.
 * Includes retry logic for transient failures.
 */
export async function fetchBinCollections(
  postcode: string = "",
  uprn: string = "",
  houseNumber: string = ""
): Promise<BinCollectionResponse> {
  const params = new URLSearchParams();
  if (postcode) params.append("postcode", postcode);
  if (uprn) params.append("uprn", uprn);
  if (houseNumber) params.append("house_number", houseNumber);

  let lastError: ApiError = { message: "Unknown error" };

  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      const response = await fetch(`${API_BASE}/bins?${params.toString()}`);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = (errorData as { detail?: string }).detail || `HTTP error ${response.status}`;
        
        if (response.status >= 500 && attempt < MAX_RETRIES - 1) {
          await delay(RETRY_DELAY_MS * (attempt + 1));
          continue;
        }
        
        throw { message: errorMessage, status: response.status } as ApiError;
      }
      
      return response.json() as Promise<BinCollectionResponse>;
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
