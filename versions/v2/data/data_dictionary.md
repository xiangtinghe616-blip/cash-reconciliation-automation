# Data Dictionary — v2 Synthetic Reconciliation Data

## bank_statement_v2.csv

| Field | Meaning |
|---|---|
| bank_transaction_id | Synthetic row-level bank transaction identifier |
| account_id | Cash account identifier |
| bank_account_name | Human-readable account name |
| transaction_date | Transaction date from the bank statement |
| posting_date | Bank posting date |
| currency | Transaction currency |
| amount | Transaction amount |
| direction | credit or debit |
| transaction_type | Transaction category |
| reference_id | Standardized transaction reference |
| raw_reference | Raw bank-side reference before normalization |
| counterparty | Counterparty name |
| description | Bank statement description |
| source_file_id | Synthetic bank statement source file |

## internal_cash_ledger_v2.csv

| Field | Meaning |
|---|---|
| ledger_transaction_id | Synthetic row-level internal ledger transaction identifier |
| account_id | Cash account identifier |
| entity | Internal legal/entity label |
| ledger_date | Internal ledger posting date |
| value_date | Value/effective date |
| currency | Transaction currency |
| amount | Transaction amount |
| direction | credit or debit |
| transaction_type | Transaction category |
| reference_id | Standardized transaction reference |
| raw_reference | Raw internal-side reference before normalization |
| counterparty | Counterparty name |
| description | Internal ledger description |
| source_system | Internal source system |
| batch_id | Synthetic batch identifier |
| created_by | Simulated source of the internal posting |

## scenario_manifest_v2.csv

Documents the seeded scenario and expected classification for each synthetic case.
