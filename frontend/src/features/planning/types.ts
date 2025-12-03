/**
 * Types for the planning feature.
 */

export interface PlanningApplication {
  reference: string;
  address: string;
  proposal: string;
  status: string;
  received_date: string;
}

export interface PlanningResponse {
  lpa: string;
  applications: PlanningApplication[];
}
