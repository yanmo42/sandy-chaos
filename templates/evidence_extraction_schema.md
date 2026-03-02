# Evidence Extraction Schema (CSV Header)

```csv
source_id,url_or_doi,query,claim_supported,method_type,dataset_or_context,key_result,limitation,extraction_confidence,reviewer_status,notes
```

## Field notes

- `source_id`: stable row ID (e.g., S001)
- `claim_supported`: one concise claim this row helps evaluate
- `extraction_confidence`: low | medium | high
- `reviewer_status`: pending | accepted | rejected
