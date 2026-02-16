# Beads Task Status

Last updated from Beads data: 2026-02-15 23:58 UTC

## Summary

- Total issues: 31
- Open: 14
- Done: 14
- In progress: 0
- Epics: 5
- Tasks: 26

## Open Items

| ID | Priority | Type | Title |
|---|---:|---|---|
| money-analyzer-3.3 | P1 | task | Build bank-to-Amazon transaction matcher |
| money-analyzer-3 | P2 | epic | EPIC: Amazon order enrichment and matching |
| money-analyzer-3.1 | P2 | task | Research and implement Amazon order export path |
| money-analyzer-3.2 | P2 | task | Build Amazon normalized CSV adapter |
| money-analyzer-3.4 | P2 | task | Add match confidence scoring and review output |
| money-analyzer-4 | P2 | epic | EPIC: AI enrichment for unknown transactions |
| money-analyzer-4.1 | P2 | task | Define enrichment contract and model I/O |
| money-analyzer-4.2 | P2 | task | Build enrichment pipeline for low-confidence transactions |
| money-analyzer-4.4 | P2 | task | Add human-review override workflow |
| money-analyzer-5.1 | P2 | task | Add parse error handling and run reports |
| money-analyzer-4.3 | P3 | task | Add enrichment caching and idempotency |
| money-analyzer-5 | P3 | epic | EPIC: Reliability and developer workflow |
| money-analyzer-5.2 | P3 | task | Add config system for parsers and thresholds |
| money-analyzer-5.3 | P3 | task | Write end-to-end runbook and examples |

## Recently Done

| ID | Priority | Type | Title |
|---|---:|---|---|
| money-analyzer-1 | P1 | epic | EPIC: Statement ingestion + normalization pipeline |
| money-analyzer-1.1 | P1 | task | Define canonical transaction schema |
| money-analyzer-1.2 | P1 | task | Define parser interface and validation contract |
| money-analyzer-1.3 | P1 | task | Build parser registry and routing wrapper |
| money-analyzer-1.6 | P1 | task | Add parser test harness with golden fixtures |
| money-analyzer-1.7 | P1 | task | Implement N26 statement parser |
| money-analyzer-1.8 | P1 | task | Implement C24 statement parser |
| money-analyzer-1.9 | P1 | task | Implement Vivid statement parser |
| money-analyzer-1.4 | P2 | task | Build per-statement CSV exporter |
| money-analyzer-1.5 | P2 | task | Build ingestion CLI for PDF->CSV |
| money-analyzer-2 | P2 | epic | EPIC: Consolidation and reconciliation |
| money-analyzer-2.1 | P2 | task | Build CSV combiner for normalized master ledger |

## Refresh

```bash
python3 scripts/export_beads_status.py
```
