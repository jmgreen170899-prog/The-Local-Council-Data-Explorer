/**
 * API functions for the planning feature.
 */

import type { PlanningResponse } from "./types";

const API_BASE = "/api/planning";

/**
 * Fetch planning applications for a given local planning authority.
 */
export async function fetchPlanningApplications(
  lpa: string = "",
  dateFrom: string = "",
  dateTo: string = ""
): Promise<PlanningResponse> {
  const params = new URLSearchParams();
  if (lpa) params.append("lpa", lpa);
  if (dateFrom) params.append("date_from", dateFrom);
  if (dateTo) params.append("date_to", dateTo);

  const response = await fetch(`${API_BASE}?${params.toString()}`);
  if (!response.ok) {
    throw new Error("Failed to fetch planning applications");
  }
  return response.json();
}
