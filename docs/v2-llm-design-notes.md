# v2 LLM Design Notes

## Purpose

v2 introduces a local LLM support layer using Ollama.

The LLM is not used for reconciliation matching or exception classification. It is used only after deterministic exception detection to generate analyst-support content.

## Why Local Ollama

A local model is useful for a portfolio prototype because it demonstrates how an AI-assisted workflow can be integrated without sending synthetic financial records to a hosted API.

## Control Boundary

The deterministic engine produces:

- matched transactions
- possible matches
- exceptions queue
- data quality issues
- summary report

The LLM layer reads only the deterministic `exceptions_queue.csv` and generates:

- exception explanation
- recommended next step
- draft analyst note
- risk/control consideration

## Reliability Controls

The v2 LLM script includes:

- structured JSON schema for model output
- low-temperature generation
- deterministic fallback templates if the local model is unavailable
- preservation of the original exception classification

## Future Improvements

Potential future enhancements:

- prompt evaluation set
- comparison between template output and LLM output
- reviewer approval workflow
- red-flag detection for unsupported LLM claims
- audit logging of generated notes
