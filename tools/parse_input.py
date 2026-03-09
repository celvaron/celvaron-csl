#!/usr/bin/env python3
"""
parse_input.py — Convert structured data (CSV or JSON) to a CSL scaffold

Reads a CSV or JSON file containing company/entity data and outputs a .csl
file scaffold with TODO comments marking required fields that are missing.

Useful for: bootstrapping a CSL model from a spreadsheet, CRM export, or
structured data dump.

Usage:
  python parse_input.py <input-file>
  python parse_input.py <input-file> --format csv
  python parse_input.py <input-file> --format json
  python parse_input.py <input-file> --entity offering
  python parse_input.py <input-file> --entity metric
  python parse_input.py <input-file> -o scaffold.csl
  python parse_input.py <input-file> --entity company --format json -o company.csl

Options:
  --format csv|json   Input format (auto-detected from file extension if omitted)
  --entity TYPE       Target CSL entity type for the rows (default: auto-detect)
  -o FILE             Write output to FILE instead of stdout

CSV format notes:
  - First row must be a header row.
  - Column names are mapped to CSL field names (case-insensitive, spaces→camelCase).
  - Each data row becomes one entity block.
  - An 'name' or '<entityType>Name' column is used as the entity name.

JSON format notes:
  - Accepts an array of objects  [ {...}, {...} ]
  - Or a single object           { "entities": [ {...}, {...} ] }
  - Each object becomes one entity block.
"""

import sys
import re
import json
import argparse
import csv as csv_module
from pathlib import Path


# ── Field name normalisation ───────────────────────────────────────────────────

def to_camel_case(s: str) -> str:
    """Convert 'Some Field Name' or 'some_field_name' to 'someFieldName'."""
    s = s.strip()
    # Replace underscores and hyphens with spaces
    s = re.sub(r'[_\-]+', ' ', s)
    parts = s.split()
    if not parts:
        return s
    return parts[0].lower() + ''.join(p.capitalize() for p in parts[1:])


def to_pascal_case(s: str) -> str:
    """Convert a string to PascalCase for use as an entity name."""
    s = re.sub(r'[^a-zA-Z0-9\s_\-]', '', s)
    s = re.sub(r'[_\-\s]+', ' ', s).strip()
    return ''.join(word.capitalize() for word in s.split()) or "Unnamed"


# ── Entity type detection ──────────────────────────────────────────────────────

ENTITY_TYPES = [
    "company", "offering", "segment", "market", "outcome", "capability",
    "process", "step", "team", "role", "package", "pricingModel",
    "journey", "system", "objective", "metric",
]

# Field names that are strong hints for a given entity type
ENTITY_HINTS = {
    "company":      {"industry", "stage"},
    "offering":     {"offeringtype", "offertype", "producttype"},
    "segment":      {"operatesin", "segmentsize"},
    "market":       {"marketsize", "marketregion", "region"},
    "outcome":      {"outcometype"},
    "capability":   {"maturitylevel", "maturity"},
    "process":      {"processowner"},
    "step":         {"steporder", "stepnumber"},
    "team":         {"teamsize"},
    "role":         {"performedby"},
    "package":      {"tier", "billingcycle", "billingperiod"},
    "pricingmodel": {"pricingtype"},
    "journey":      {"stages"},
    "system":       {"systemtype"},
    "objective":    {"timeframe"},
    "metric":       {"unit", "target", "baseline"},
}


def detect_entity_type(columns: list) -> str:
    """Guess the entity type from the column names."""
    col_set = {to_camel_case(c).lower() for c in columns}
    scores = {etype: 0 for etype in ENTITY_TYPES}
    for etype, hints in ENTITY_HINTS.items():
        for hint in hints:
            if hint in col_set:
                scores[etype] += 1
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else "offering"  # default guess


# ── Required fields per entity type ───────────────────────────────────────────

REQUIRED_FIELDS = {
    "company":      ["industry"],
    "offering":     ["type", "targets"],
    "segment":      ["operatesIn"],
    "market":       [],
    "outcome":      ["type"],
    "capability":   ["maturityLevel"],
    "process":      [],
    "step":         ["order", "partOf"],
    "team":         ["ownedBy"],
    "role":         ["performedBy"],
    "package":      ["tier", "price", "billingCycle"],
    "pricingModel": ["type"],
    "journey":      ["targets"],
    "system":       ["type"],
    "objective":    [],
    "metric":       ["unit"],
}

# Fields that accept a reference (entity name) not a quoted string
REFERENCE_FIELDS = {
    "targets", "delivers", "requires", "operatesIn", "measuredBy",
    "achievedThrough", "supports", "dependsOn", "ownedBy", "owns",
    "performedBy", "uses", "partOf",
}

# Fields that are numeric
NUMERIC_FIELDS = {"price", "size", "target", "baseline", "userLimit", "order"}


def format_value(field: str, value: str) -> str:
    """Format a value appropriately for CSL output."""
    if not value or value.strip() == "":
        return ""
    value = value.strip()
    if field in REFERENCE_FIELDS:
        # References should not be quoted — convert to PascalCase
        return to_pascal_case(value)
    if field in NUMERIC_FIELDS:
        try:
            f = float(value)
            return str(int(f)) if f == int(f) else str(f)
        except ValueError:
            pass
    # Quote strings
    escaped = value.replace('"', '\\"')
    return f'"{escaped}"'


# ── Name extraction ────────────────────────────────────────────────────────────

NAME_COLUMN_CANDIDATES = ["name", "entityname", "companyname", "offeringname",
                          "segmentname", "metricname", "capabilityname",
                          "processname", "teamname", "packagename", "title"]


def extract_name(row: dict, entity_type: str) -> str:
    """Find the entity name from a row dict."""
    # Try entity-specific name column first
    type_key = f"{entity_type}name"
    for raw_key, value in row.items():
        key_norm = to_camel_case(raw_key).lower()
        if key_norm == type_key and value and value.strip():
            return to_pascal_case(value.strip())

    # Try generic name columns
    for raw_key, value in row.items():
        key_norm = to_camel_case(raw_key).lower()
        if key_norm in NAME_COLUMN_CANDIDATES and value and value.strip():
            return to_pascal_case(value.strip())

    # Fall back to first column value
    first_val = next(iter(row.values()), "")
    if first_val and first_val.strip():
        return to_pascal_case(first_val.strip())

    return "Unnamed"


# ── CSL block renderer ─────────────────────────────────────────────────────────

def render_entity_block(entity_type: str, name: str, fields: dict) -> str:
    """
    Render a single CSL entity block as a string.
    Missing required fields get # TODO comments.
    """
    lines = [f"{entity_type} {name} {{"]

    # Write fields present in the data
    for field, value in fields.items():
        if not value:
            continue
        formatted = format_value(field, value)
        if formatted:
            lines.append(f"  {field}: {formatted}")

    # Add TODO comments for required fields that are missing
    required = REQUIRED_FIELDS.get(entity_type, [])
    present  = set(fields.keys())
    for req in required:
        if req not in present or not fields.get(req, "").strip():
            lines.append(f"  {req}: # TODO: required — fill in {req}")

    lines.append("}")
    return "\n".join(lines)


def render_scaffold(entity_type: str, rows: list, source_path: str) -> str:
    """Render a full CSL scaffold file from a list of row dicts."""
    output_lines = [
        f'# Generated scaffold — {source_path}',
        f'# Entity type: {entity_type}',
        f'# Rows parsed: {len(rows)}',
        '# Review all # TODO fields before using this model.\n',
        'version: "1.0"',
        'author: "# TODO: add author name"',
        'description: "# TODO: add model description"',
        '',
    ]

    for row in rows:
        name = extract_name(row, entity_type)

        # Build field map from row — normalise column names to camelCase
        fields = {}
        for raw_key, value in row.items():
            field = to_camel_case(raw_key)
            # Skip name-like columns — they become the entity name, not a field
            if field.lower() in {c.lower() for c in NAME_COLUMN_CANDIDATES}:
                continue
            if field.lower() == f"{entity_type}name":
                continue
            fields[field] = value if isinstance(value, str) else str(value)

        block = render_entity_block(entity_type, name, fields)
        output_lines.append(block)
        output_lines.append("")

    return "\n".join(output_lines)


# ── Input readers ──────────────────────────────────────────────────────────────

def read_csv(path: Path) -> tuple:
    """Return (columns, rows) where rows is a list of dicts."""
    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv_module.DictReader(f)
        columns = reader.fieldnames or []
        for row in reader:
            rows.append(dict(row))
    return list(columns), rows


def read_json(path: Path) -> tuple:
    """Return (columns, rows). Accepts array or {entities: [...]} wrapper."""
    data = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict):
        # Try common wrapper keys
        for key in ("entities", "items", "data", "records", "results"):
            if key in data and isinstance(data[key], list):
                rows = data[key]
                break
        else:
            rows = [data]  # single object — treat as one row
    else:
        print(f"Error: unexpected JSON structure in {path}", file=sys.stderr)
        sys.exit(1)

    # Flatten nested objects to top-level string values for scaffold generation
    flat_rows = []
    for row in rows:
        flat = {}
        for k, v in row.items():
            if isinstance(v, (str, int, float, bool)):
                flat[k] = str(v)
            elif isinstance(v, list):
                flat[k] = ", ".join(str(i) for i in v)
            elif isinstance(v, dict):
                # Flatten one level deep
                for sub_k, sub_v in v.items():
                    flat[f"{k}_{sub_k}"] = str(sub_v)
            else:
                flat[k] = str(v) if v is not None else ""
        flat_rows.append(flat)

    columns = list(flat_rows[0].keys()) if flat_rows else []
    return columns, flat_rows


# ── Entry point ────────────────────────────────────────────────────────────────

def detect_format(path: Path, hint: str) -> str:
    if hint:
        return hint.lower()
    suffix = path.suffix.lower()
    if suffix in (".csv",):
        return "csv"
    if suffix in (".json", ".jsonl"):
        return "json"
    print(
        f"Warning: cannot detect format from extension '{suffix}'. "
        "Defaulting to CSV. Use --format to specify.",
        file=sys.stderr,
    )
    return "csv"


def main():
    ap = argparse.ArgumentParser(
        description="Convert CSV or JSON data to a CSL entity scaffold."
    )
    ap.add_argument("path", help="Path to the input file (CSV or JSON)")
    ap.add_argument("--format", choices=["csv", "json"],
                    help="Input format (auto-detected if omitted)")
    ap.add_argument("--entity", choices=ENTITY_TYPES,
                    help=f"Target entity type (auto-detected if omitted)")
    ap.add_argument("-o", "--output", help="Write output to this file (default: stdout)")
    args = ap.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    fmt = detect_format(path, args.format)

    if fmt == "csv":
        columns, rows = read_csv(path)
    else:
        columns, rows = read_json(path)

    if not rows:
        print("Error: no data rows found in input file.", file=sys.stderr)
        sys.exit(1)

    entity_type = args.entity or detect_entity_type(columns)
    print(
        f"Detected entity type: {entity_type} ({len(rows)} row(s))",
        file=sys.stderr,
    )

    scaffold = render_scaffold(entity_type, rows, str(path))

    if args.output:
        Path(args.output).write_text(scaffold, encoding="utf-8")
        print(f"Scaffold written to {args.output}", file=sys.stderr)
    else:
        print(scaffold)


if __name__ == "__main__":
    main()
