// types/Case.ts
export interface Case {
  case_id: string;
  title: string;
  service: string[];
  symptom: string;
  root_cause?: string;
  fix_summary: string;
  steps?: string[];
  links?: { label: string; url: string }[];
  env: "cloud" | "on-prem" | "both";
  created_at: string;
  score?: number; // relevance
}