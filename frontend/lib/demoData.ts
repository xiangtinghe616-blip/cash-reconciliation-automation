export type BreakItem = {
  exceptionId: string;
  breakType: string;
  priority: "High" | "Medium" | "Low";
  slaStatus: "BREACHED" | "DUE_TODAY" | "WITHIN_SLA";
  ageDays: number;
  amountGap: string;
  recommendedAction: string;
  reason: string;
};

export type EvidenceField = {
  field: string;
  bankValue: string;
  ledgerValue: string;
  status: "match" | "difference" | "missing";
  note: string;
};

export type Candidate = {
  source: "Rule-based" | "Splink" | "Split-payment";
  confidence: string;
  rationale: string;
};

export type ReconciliationSummary = {
  runId: string;
  bankTransactions: number;
  ledgerTransactions: number;
  totalTransactions: number;
  deterministicMatches: number;
  candidateLinks: number;
  splinkCandidates: number;
  splitPaymentCandidates: number;
  candidateEvidenceTotal: number;
  exceptionsForReview: number;
  slaBreached: number;
  autoMatchRate: number;
};

export const reconciliationSummary: ReconciliationSummary = {
  runId: "demo-fallback",
  bankTransactions: 595,
  ledgerTransactions: 600,
  totalTransactions: 1195,
  deterministicMatches: 399,
  candidateLinks: 468,
  splinkCandidates: 567,
  splitPaymentCandidates: 15,
  candidateEvidenceTotal: 1050,
  exceptionsForReview: 342,
  slaBreached: 336,
  autoMatchRate: 54,
};

export const priorityQueue: BreakItem[] = [
  {
    exceptionId: "EXC-000342",
    breakType: "AMOUNT_MISMATCH",
    priority: "High",
    slaStatus: "BREACHED",
    ageDays: 12,
    amountGap: "CAD 2,450.00",
    recommendedAction: "Escalate",
    reason: "High-priority amount mismatch with breached SLA.",
  },
  {
    exceptionId: "EXC-000219",
    breakType: "UNMATCHED_BANK_TRANSACTION",
    priority: "High",
    slaStatus: "BREACHED",
    ageDays: 9,
    amountGap: "CAD 1,180.00",
    recommendedAction: "Review bank-side evidence",
    reason: "Bank-side cash movement has no confirmed ledger record.",
  },
  {
    exceptionId: "EXC-000117",
    breakType: "UNMATCHED_LEDGER_TRANSACTION",
    priority: "Medium",
    slaStatus: "DUE_TODAY",
    ageDays: 5,
    amountGap: "CAD 760.00",
    recommendedAction: "Prioritize review today",
    reason: "Ledger-side item is approaching SLA breach.",
  },
];

export const evidenceByExceptionId: Record<string, EvidenceField[]> = {
  "EXC-000342": [
    {
      field: "Amount",
      bankValue: "CAD 12,450.00",
      ledgerValue: "CAD 10,000.00",
      status: "difference",
      note: "Amount gap detected. Requires analyst review before resolution.",
    },
    {
      field: "Transaction Date",
      bankValue: "2026-05-21",
      ledgerValue: "2026-05-20",
      status: "difference",
      note: "One-day timing difference may be explainable.",
    },
    {
      field: "Reference",
      bankValue: "INV-8891",
      ledgerValue: "8891",
      status: "match",
      note: "Normalized reference suggests same business event.",
    },
    {
      field: "Counterparty",
      bankValue: "Northstar Trading Ltd",
      ledgerValue: "Northstar Trading",
      status: "match",
      note: "Counterparty similarity is high.",
    },
    {
      field: "Account / Currency / Direction",
      bankValue: "ACC-102 / CAD / Credit",
      ledgerValue: "ACC-102 / CAD / Credit",
      status: "match",
      note: "Core account attributes align.",
    },
  ],
  "EXC-000219": [
    {
      field: "Amount",
      bankValue: "CAD 1,180.00",
      ledgerValue: "No ledger record",
      status: "missing",
      note: "Bank transaction is present, but no confirmed ledger entry exists.",
    },
    {
      field: "Transaction Date",
      bankValue: "2026-05-18",
      ledgerValue: "No ledger record",
      status: "missing",
      note: "No ledger-side date available for comparison.",
    },
    {
      field: "Reference",
      bankValue: "DEP-4402",
      ledgerValue: "No ledger record",
      status: "missing",
      note: "Candidate search should focus on nearby deposit references.",
    },
    {
      field: "Counterparty",
      bankValue: "Harbor Retail Group",
      ledgerValue: "No ledger record",
      status: "missing",
      note: "Counterparty may help find a delayed ledger posting.",
    },
  ],
  "EXC-000117": [
    {
      field: "Amount",
      bankValue: "No bank record",
      ledgerValue: "CAD 760.00",
      status: "missing",
      note: "Ledger transaction is present, but bank-side settlement is missing.",
    },
    {
      field: "Transaction Date",
      bankValue: "No bank record",
      ledgerValue: "2026-05-19",
      status: "missing",
      note: "Check bank activity around this date for delayed settlement.",
    },
    {
      field: "Reference",
      bankValue: "No bank record",
      ledgerValue: "PMT-1179",
      status: "missing",
      note: "Reference should be searched against bank memo variants.",
    },
    {
      field: "Counterparty",
      bankValue: "No bank record",
      ledgerValue: "Cedar Supply Co",
      status: "missing",
      note: "Counterparty can support follow-up investigation.",
    },
  ],
};

export const candidatesByExceptionId: Record<string, Candidate[]> = {
  "EXC-000342": [
    {
      source: "Rule-based",
      confidence: "0.84",
      rationale: "Same account, currency, direction, similar reference, one-day date gap.",
    },
    {
      source: "Splink",
      confidence: "0.91",
      rationale: "High probabilistic similarity across reference and counterparty despite amount gap.",
    },
    {
      source: "Split-payment",
      confidence: "Review",
      rationale: "Possible partial settlement pattern. Analyst should verify amount composition.",
    },
  ],
  "EXC-000219": [
    {
      source: "Splink",
      confidence: "0.67",
      rationale: "Weak candidate found through counterparty and date proximity.",
    },
  ],
  "EXC-000117": [
    {
      source: "Rule-based",
      confidence: "0.72",
      rationale: "Ledger reference resembles nearby bank memo but bank-side amount is not confirmed.",
    },
  ],
};
