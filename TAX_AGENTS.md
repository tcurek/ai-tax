# Tax Return Agent Use Cases

This document outlines proposed agent roles for an AI-assisted tax return processing workflow.

## Orchestration Agent / LangGraph Workflow

A dedicated orchestration layer should coordinate the full workflow. LangGraph is a strong fit because tax preparation is stateful, conditional, and often requires loops back to the user for missing information.

Responsibilities:

- Track workflow state across documents, extracted data, user answers, forms, calculations, validation, and audit findings.
- Decide which agent or node runs next.
- Route back to the user when information is missing.
- Prevent downstream steps from running before prerequisites are complete.
- Maintain an audit trail of decisions, sources, and changes.
- Retry or escalate low-confidence OCR/extraction results.
- Enforce validation and human-review gates before export or filing.
- Keep the audit agent independent from preparation/filling agents.

Example workflow:

```text
Document Intake
  -> Classification
  -> Data Extraction
  -> Central Tax Data Store
  -> Interview / Missing Info
  -> Form Determination
  -> Tax Calculation
  -> Form Filling
  -> Validation
  -> Audit
  -> Human Review / Signoff
```

## Document Intake Agent

Reads uploaded files, images, and PDFs.

Responsibilities:

- Identify and inventory submitted documents.
- Detect duplicates, unreadable files, missing pages, or suspicious documents.
- Prepare files for OCR or structured extraction.

Example document types:

- W-2
- 1099-INT
- 1099-DIV
- 1099-NEC
- 1099-R
- 1098 / mortgage interest statements
- 1098-T education statements
- Brokerage statements
- Charitable contribution receipts
- Prior-year tax returns

Output: normalized document inventory with file references and status.

## Classification Agent

Categorizes each document into a known tax document type.

Responsibilities:

- Assign document category and tax year.
- Identify taxpayer/spouse/dependent association where possible.
- Flag uncertain classifications for review.

Output: categorized document records with confidence scores.

## Data Extraction Agent

Extracts structured tax data from categorized documents and writes it into the central tax data model.

Responsibilities:

- Extract box-level values from forms and statements.
- Normalize employer, payer, taxpayer, income, withholding, deduction, and credit data.
- Preserve provenance for every extracted value.

Each extracted value should include:

- Source file
- Page number or region, where available
- Form/box/line reference
- Confidence score
- Extraction method

Output: structured tax data stored in a canonical data model.

## Central Tax Data Store

The central data store is not an agent, but it is critical to the workflow.

Responsibilities:

- Act as the source of truth for taxpayer data.
- Store extracted document data, user answers, derived calculations, form mappings, and audit results.
- Preserve value provenance and change history.
- Avoid letting each agent invent its own schema.

## Tax Profile / Interview Agent

Reviews available data and asks follow-up questions.

Responsibilities:

- Determine missing taxpayer facts.
- Generate plain-language questions for the user.
- Update the taxpayer profile from user responses.
- Continue until required facts are complete or explicitly unresolved.

Example topics:

- Filing status
- Dependents
- Residency
- Health coverage
- Education expenses
- Retirement contributions
- Business income and expenses
- Home office
- Estimated tax payments
- Crypto or asset sales
- State/local tax facts

Output: completed taxpayer profile and unresolved question list.

## Form Determination Agent

Determines which federal and state forms/schedules are required.

Responsibilities:

- Analyze extracted data and interview answers.
- Select required forms and schedules.
- Explain why each form is needed.
- Identify missing information required to complete each form.

Example forms:

- Form 1040
- Schedule 1
- Schedule A
- Schedule C
- Schedule D
- Form 8949
- Form 8863
- Form 8889
- State return forms

Output: form plan with rationale and dependencies.

## Tax Calculation Agent

Calculates return values from the canonical data model.

Responsibilities:

- Calculate AGI, deductions, taxable income, credits, tax, payments, refund, or balance due.
- Maintain a calculation ledger with traceable inputs and formulas.
- Prefer deterministic code/rules over free-form LLM reasoning.

Output: calculation ledger mapped to tax form lines.

## Form Filling Agent

Populates draft tax forms from the central tax data model and calculation ledger.

Responsibilities:

- Fill form fields using extracted data, user answers, and calculated values.
- Preserve source references for each populated field.
- Mark fields that require user or professional review.

Output: draft tax forms with field-level provenance.

## Consistency / Validation Agent

Checks the draft return for missing values, reconciliation issues, and contradictions.

Responsibilities:

- Verify required fields are present.
- Reconcile totals across documents, calculations, and forms.
- Check that income and withholding totals match source documents.
- Detect duplicate income or omitted documents.
- Check federal/state consistency.
- Flag low-confidence or unsupported values.

Output: validation errors, warnings, and required corrections.

## Audit / Review Agent

Performs an independent final review. This agent should not directly modify the return.

Responsibilities:

- Identify unsupported claims or deductions.
- Flag unusual or high-risk tax positions.
- Detect missing forms or schedules.
- Review unresolved questions and low-confidence extractions.
- Produce a human-readable audit report.

Output: audit findings and recommended review actions.

## Human Review / Signoff Agent

Presents the final package to the user or tax professional for review.

Responsibilities:

- Summarize key return results.
- Highlight assumptions, unresolved issues, warnings, and audit findings.
- Require explicit human approval before export or filing preparation.
- Include clear disclaimers that generated outputs require human/professional review.

Output: final review package and approval status.

## Design Principles

- Use LangGraph or another workflow engine for orchestration, not one giant agent.
- Keep tax calculations deterministic and auditable.
- Maintain a central canonical tax data model.
- Store provenance for every extracted, answered, calculated, and filled value.
- Separate preparation agents from audit/review agents.
- Treat all tax documents and user tax data as highly sensitive.
- Build human-in-the-loop checkpoints into the workflow.
- Do not present generated outputs as professional tax advice without qualified review.
