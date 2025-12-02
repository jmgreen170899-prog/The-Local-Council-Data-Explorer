/**
 * API functions for the bins feature.
 */

import type { BinCollectionResponse } from "./types";

const API_BASE = "/api/bins";

/**
 * Fetch bin collection data for a given postcode or UPRN.
 */
export async function fetchBinCollections(
  postcode: string = "",
  uprn: string = ""
): Promise<BinCollectionResponse> {
  const params = new URLSearchParams();
  if (postcode) params.append("postcode", postcode);
  if (uprn) params.append("uprn", uprn);

  const response = await fetch(`${API_BASE}?${params.toString()}`);
  if (!response.ok) {
    throw new Error("Failed to fetch bin collections");
  }
  return response.json();
}
