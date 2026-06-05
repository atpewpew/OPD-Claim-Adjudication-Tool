export interface ClaimSubmitForm {
  member_id: string;
  treatment_date: string;
  claim_amount: number;
  hospital_name?: string | null;
  cashless_request: boolean;
  pre_auth_provided: boolean;
  previous_claims_same_day: number;
}

export type ClaimDecision = "APPROVED" | "REJECTED" | "PARTIAL" | "MANUAL_REVIEW";

export interface ClaimResponse {
  claim_id: string;
  member_id: string;
  member_name: string;
  treatment_date: string; // ISO date string (YYYY-MM-DD)
  submitted_amount: number;
  hospital_name: string | null;
  decision: ClaimDecision;
  approved_amount: number | null;
  rejection_reasons: string[];
  rejected_items: string[];
  rule_matrix: Record<string, string>;
  deductions: Record<string, number>;
  confidence_score: number | null;
  notes: string | null;
  next_steps: string | null;
  extracted_data?: Record<string, any> | null;
  document_urls: string[];
  created_at: string; // ISO datetime string
}

export interface ClaimsListResponse {
  claims: ClaimResponse[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface StatsResponse {
  total: number;
  approved: number;
  rejected: number;
  partial: number;
  manual_review: number;
  total_approved_amount: number;
  avg_confidence: number;
}

export interface AppealRequest {
  note: string;
}
