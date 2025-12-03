/**
 * Types for the planning feature.
 */

export interface PlanningApplication {
  reference: string;
  address: string;
  proposal: string;
  status: string;
  received_date: string;
  decision_date?: string | null;
  decision?: string | null;
  applicant_name?: string | null;
  application_type?: string | null;
}

export interface PlanningResponse {
  lpa: string;
  applications: PlanningApplication[];
  total_count: number;
}

export interface PlanningRequest {
  lpa: string;
  date_from?: string;
  date_to?: string;
}
