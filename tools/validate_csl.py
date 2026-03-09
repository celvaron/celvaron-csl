#!/usr/bin/env python3
"""
validate_csl.py — CSL file validator

Runs 5 validation layers against a .csl file:
  Layer 1: Syntax
  Layer 2: Reference integrity
  Layer 3: Structural constraints
  Layer 4: Semantic warnings
  Layer 5: Completeness suggestions

Usage:
  python validate_csl.py <path/to/model.csl>
  python validate_csl.py <path/to/model.csl> --strict
  python validate_csl.py <path/to/model.csl> --json
  python validate_csl.py <path/to/model.csl> --quiet

Options:
  --strict   Exit with code 1 if any warnings are present (in addition to errors)
  --json     Output results as JSON instead of human-readable text
  --quiet    Suppress all output; use exit code only (0 = pass, 1 = fail)
"""

import sys
import re
import json
import argparse
from pathlib import Path


# ── Token / parsing helpers ────────────────────────────────────────────────────

ENTITY_TYPES = {
    "company", "offering", "segment", "market", "outcome", "capability",
    "process", "step", "team", "role", "package", "pricingModel",
    "journey", "system", "objective", "metric",
}

RESERVED_WORDS = ENTITY_TYPES | {"version", "author", "description", "state", "import"}

VALID_CHANGE_TYPES = {"new", "enhanced", "retired"}

# Fields that must be a reference to another entity name (not a quoted string)
REFERENCE_FIELDS = {
    "targets", "delivers", "requires", "operatesIn", "measuredBy",
    "achievedThrough", "supports", "dependsOn", "ownedBy", "owns",
    "performedBy", "uses", "partOf",
}


def strip_comments(source: str) -> str:
    """Remove # line comments, preserving newlines for line-number tracking."""
    lines = []
    for line in source.splitlines():
        # Strip inline comments but keep newline count accurate
        idx = line.find("#")
        if idx != -1:
            line = line[:idx]
        lines.append(line)
    return "\n".join(lines)


def tokenise(source: str):
    """
    Yield (line_no, token) tuples.
    Tokens: strings (quoted), numbers, booleans, identifiers, symbols ({}[]:,).
    """
    token_re = re.compile(
        r'"(?:[^"\\]|\\.)*"'    # quoted string
        r'|[-]?\d+(?:\.\d+)?'  # number
        r'|[A-Za-z_][A-Za-z0-9_]*'  # identifier
        r'|[{}[\]:,]'           # symbols
        r'|\S+'                  # anything else (error token)
    )
    for lineno, line in enumerate(source.splitlines(), start=1):
        for m in token_re.finditer(line):
            yield lineno, m.group(0)


class ParseError(Exception):
    def __init__(self, message, lineno=None):
        super().__init__(message)
        self.lineno = lineno


class CSLParser:
    """
    Lightweight recursive-descent parser.
    Builds a list of Entity objects and collects header fields.
    Does NOT evaluate semantics — that is left to the validation layers.
    """

    def __init__(self, source: str):
        cleaned = strip_comments(source)
        self._tokens = list(tokenise(cleaned))
        self._pos = 0
        self.header = {}
        self.entities = []  # list of dicts: {type, name, lineno, fields}
        self.errors = []    # ParseError list (Layer 1)

    # ── Low-level token helpers ────────────────────────────────────────────────

    def _peek(self):
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return None, None

    def _consume(self):
        tok = self._tokens[self._pos]
        self._pos += 1
        return tok

    def _expect(self, value=None):
        lineno, tok = self._consume()
        if value and tok != value:
            raise ParseError(f"Expected '{value}' but got '{tok}'", lineno)
        return lineno, tok

    def _at_end(self):
        return self._pos >= len(self._tokens)

    # ── Top-level parse ────────────────────────────────────────────────────────

    def parse(self):
        while not self._at_end():
            lineno, tok = self._peek()
            if tok in ("version", "author", "description", "state"):
                self._parse_header_field()
            elif tok == "import":
                self._consume()  # skip import lines for now
                while not self._at_end():
                    ln, t = self._peek()
                    if t and t not in ("\n",):
                        self._consume()
                    break
            elif tok in ENTITY_TYPES:
                self._parse_entity()
            else:
                # Unknown top-level token — record error and skip line
                self.errors.append(ParseError(
                    f"E001: Unexpected token '{tok}' at top level", lineno
                ))
                self._consume()

    def _parse_header_field(self):
        lineno, key = self._consume()
        _, colon = self._peek()
        if colon == ":":
            self._consume()
        _, value = self._consume()
        self.header[key] = value.strip('"')

    def _parse_entity(self):
        lineno, entity_type = self._consume()
        _, name = self._peek()
        if name is None or name in ("{",):
            self.errors.append(ParseError(
                f"E002: Entity '{entity_type}' is missing a name", lineno
            ))
            return
        _, name = self._consume()

        # Validate PascalCase
        if not re.match(r'^[A-Z][A-Za-z0-9]*$', name):
            self.errors.append(ParseError(
                f"E101: Entity name '{name}' must be PascalCase (start with uppercase letter)", lineno
            ))

        try:
            _, brace = self._expect("{")
        except ParseError as e:
            self.errors.append(e)
            return

        fields = {}
        while not self._at_end():
            _, next_tok = self._peek()
            if next_tok == "}":
                self._consume()
                break
            try:
                field_name, field_value, field_lineno = self._parse_field()
                fields[field_name] = (field_value, field_lineno)
            except ParseError as e:
                self.errors.append(e)
                # Skip to next field or closing brace
                while not self._at_end():
                    _, t = self._peek()
                    if t in ("}", "\n") or (t and re.match(r'^[a-z]', t)):
                        break
                    self._consume()

        self.entities.append({
            "type": entity_type,
            "name": name,
            "lineno": lineno,
            "fields": fields,
        })

    def _parse_field(self):
        lineno, key = self._consume()

        # Key must be camelCase identifier
        if not re.match(r'^[a-z][A-Za-z0-9]*$', key):
            raise ParseError(
                f"E102: Field name '{key}' must be camelCase", lineno
            )

        _, colon = self._peek()
        if colon != ":":
            raise ParseError(f"E001: Expected ':' after field '{key}'", lineno)
        self._consume()

        value, value_lineno = self._parse_value()
        return key, value, lineno

    def _parse_value(self):
        lineno, tok = self._peek()
        if tok is None:
            raise ParseError("E001: Unexpected end of file in field value", lineno)

        if tok == "[":
            return self._parse_list(), lineno
        elif tok == "{":
            return self._parse_object(), lineno
        else:
            self._consume()
            return tok, lineno

    def _parse_list(self):
        self._expect("[")
        items = []
        while not self._at_end():
            _, tok = self._peek()
            if tok == "]":
                self._consume()
                break
            elif tok == "{":
                items.append(self._parse_object())
            elif tok == ",":
                self._consume()
            else:
                _, v = self._consume()
                items.append(v)
        return items

    def _parse_object(self):
        self._expect("{")
        obj = {}
        while not self._at_end():
            _, tok = self._peek()
            if tok == "}":
                self._consume()
                break
            elif tok == ",":
                self._consume()
            elif tok and re.match(r'^[a-zA-Z_]', tok):
                lineno, key = self._consume()
                _, colon = self._peek()
                if colon == ":":
                    self._consume()
                _, val = self._peek()
                if val == "[":
                    obj[key] = self._parse_list()
                elif val == "{":
                    obj[key] = self._parse_object()
                else:
                    _, val = self._consume()
                    obj[key] = val
            else:
                self._consume()
        return obj


# ── Validation layers ──────────────────────────────────────────────────────────

def layer1_syntax(parser):
    """Return errors already collected during parsing."""
    results = []
    for e in parser.errors:
        results.append({
            "layer": 1,
            "severity": "error",
            "code": _extract_code(str(e), "E001"),
            "message": str(e),
            "line": e.lineno,
        })
    return results


def layer2_references(entities):
    """Check that all reference fields point to declared entity names."""
    declared = {e["name"] for e in entities}
    results = []
    for entity in entities:
        for field, (value, lineno) in entity["fields"].items():
            if field not in REFERENCE_FIELDS:
                continue
            refs = value if isinstance(value, list) else [value]
            for ref in refs:
                if isinstance(ref, str) and ref.startswith('"'):
                    continue  # quoted string — not a reference
                if isinstance(ref, (dict, list)):
                    continue
                ref_clean = ref.strip('"')
                if ref_clean and ref_clean not in declared:
                    results.append({
                        "layer": 2,
                        "severity": "error",
                        "code": "E201",
                        "message": f"E201: Undefined reference '{ref_clean}' in '{entity['name']}.{field}'",
                        "line": lineno,
                    })
    return results


def layer3_structure(entities):
    """Check required fields and structural constraints per entity type."""
    required_fields = {
        "company":       ["industry"],
        "offering":      ["type", "targets"],
        "segment":       ["operatesIn"],
        "market":        [],
        "outcome":       ["type"],
        "capability":    ["maturityLevel"],
        "process":       [],
        "step":          ["order", "partOf"],
        "team":          ["ownedBy"],
        "role":          ["performedBy"],
        "package":       ["tier", "price", "billingCycle"],
        "pricingModel":  ["type"],
        "journey":       ["targets"],
        "system":        ["type"],
        "objective":     [],
        "metric":        ["unit"],
    }
    results = []
    for entity in entities:
        etype = entity["type"]
        req = required_fields.get(etype, [])
        for field in req:
            if field not in entity["fields"]:
                results.append({
                    "layer": 3,
                    "severity": "error",
                    "code": "E301",
                    "message": (
                        f"E301: Required field '{field}' missing from "
                        f"{etype} '{entity['name']}'"
                    ),
                    "line": entity["lineno"],
                })

    # step.order must be a positive integer
    for entity in entities:
        if entity["type"] == "step" and "order" in entity["fields"]:
            val, lineno = entity["fields"]["order"]
            try:
                n = int(val)
                if n < 1:
                    raise ValueError
            except (ValueError, TypeError):
                results.append({
                    "layer": 3,
                    "severity": "error",
                    "code": "E302",
                    "message": f"E302: step.order must be a positive integer in '{entity['name']}'",
                    "line": lineno,
                })

    # package.tier must be entry|standard|premium
    valid_tiers = {"entry", "standard", "premium"}
    for entity in entities:
        if entity["type"] == "package" and "tier" in entity["fields"]:
            val, lineno = entity["fields"]["tier"]
            clean = val.strip('"')
            if clean not in valid_tiers:
                results.append({
                    "layer": 3,
                    "severity": "error",
                    "code": "E303",
                    "message": (
                        f"E303: package.tier '{clean}' is invalid in '{entity['name']}'. "
                        f"Must be one of: {', '.join(sorted(valid_tiers))}"
                    ),
                    "line": lineno,
                })

    # changeType must be new|enhanced|retired
    for entity in entities:
        if "changeType" in entity["fields"]:
            val, lineno = entity["fields"]["changeType"]
            clean = val.strip('"')
            if clean not in VALID_CHANGE_TYPES:
                results.append({
                    "layer": 3,
                    "severity": "error",
                    "code": "E304",
                    "message": (
                        f"E304: changeType '{clean}' is invalid in '{entity['name']}'. "
                        f"Must be one of: {', '.join(sorted(VALID_CHANGE_TYPES))}"
                    ),
                    "line": lineno,
                })

    return results


def layer4_semantics(entities):
    """Emit warnings for suspicious but not invalid patterns."""
    results = []
    names = [e["name"] for e in entities]

    # Duplicate names
    seen = set()
    for entity in entities:
        n = entity["name"]
        if n in seen:
            results.append({
                "layer": 4,
                "severity": "warning",
                "code": "W001",
                "message": f"W001: Duplicate entity name '{n}'",
                "line": entity["lineno"],
            })
        seen.add(n)

    # Offering with no package
    package_targets = set()
    for e in entities:
        if e["type"] == "package" and "partOf" in e["fields"]:
            val, _ = e["fields"]["partOf"]
            refs = val if isinstance(val, list) else [val]
            for r in refs:
                if isinstance(r, str):
                    package_targets.add(r.strip('"'))

    for e in entities:
        if e["type"] == "offering" and e["name"] not in package_targets:
            results.append({
                "layer": 4,
                "severity": "warning",
                "code": "W002",
                "message": f"W002: Offering '{e['name']}' has no associated package",
                "line": e["lineno"],
            })

    # Metric with target <= baseline (except where baseline is 0 and target > 0)
    for e in entities:
        if e["type"] == "metric":
            target = e["fields"].get("target")
            baseline = e["fields"].get("baseline")
            unit_field = e["fields"].get("unit")
            if target and baseline and unit_field:
                unit_val, _ = unit_field
                t_val, t_line = target
                b_val, _ = baseline
                try:
                    t = float(t_val)
                    b = float(b_val)
                    # For "lower is better" units
                    lower_is_better = any(
                        k in unit_val.lower()
                        for k in ["days", "hours", "count", "rate", "percent"]
                    )
                    if not lower_is_better and t <= b and b != 0:
                        results.append({
                            "layer": 4,
                            "severity": "warning",
                            "code": "W003",
                            "message": (
                                f"W003: Metric '{e['name']}' has target ({t}) <= baseline ({b}). "
                                "Verify direction — use lower values for 'lower is better' metrics."
                            ),
                            "line": t_line,
                        })
                except (ValueError, TypeError):
                    pass

    # process with no steps
    process_names = {e["name"] for e in entities if e["type"] == "process"}
    step_processes = set()
    for e in entities:
        if e["type"] == "step" and "partOf" in e["fields"]:
            val, _ = e["fields"]["partOf"]
            step_processes.add(val.strip('"') if isinstance(val, str) else "")

    for name in process_names:
        if name not in step_processes:
            entity = next(e for e in entities if e["name"] == name)
            results.append({
                "layer": 4,
                "severity": "warning",
                "code": "W004",
                "message": f"W004: Process '{name}' has no steps defined",
                "line": entity["lineno"],
            })

    return results


def layer5_completeness(entities, header):
    """Suggest improvements to make the model more complete."""
    results = []

    # Missing header fields
    for field in ("version", "author", "description"):
        if field not in header:
            results.append({
                "layer": 5,
                "severity": "suggestion",
                "code": "S001",
                "message": f"S001: Header field '{field}' is missing",
                "line": None,
            })

    # Company missing description
    for e in entities:
        if e["type"] == "company" and "description" not in e["fields"]:
            results.append({
                "layer": 5,
                "severity": "suggestion",
                "code": "S002",
                "message": f"S002: Company '{e['name']}' has no description",
                "line": e["lineno"],
            })

    # Offering missing delivers
    for e in entities:
        if e["type"] == "offering" and "delivers" not in e["fields"]:
            results.append({
                "layer": 5,
                "severity": "suggestion",
                "code": "S003",
                "message": f"S003: Offering '{e['name']}' has no 'delivers' outcome — add outcome linkage",
                "line": e["lineno"],
            })

    # Outcome with no metric
    outcome_names = {e["name"] for e in entities if e["type"] == "outcome"}
    measured_outcomes = set()
    for e in entities:
        if e["type"] == "outcome" and "measuredBy" in e["fields"]:
            val, _ = e["fields"]["measuredBy"]
            refs = val if isinstance(val, list) else [val]
            for r in refs:
                if isinstance(r, str):
                    measured_outcomes.add(r.strip('"'))
    # outcomes that have no measuredBy field
    for e in entities:
        if e["type"] == "outcome" and "measuredBy" not in e["fields"]:
            results.append({
                "layer": 5,
                "severity": "suggestion",
                "code": "S004",
                "message": f"S004: Outcome '{e['name']}' has no measuredBy metric",
                "line": e["lineno"],
            })

    # No objectives defined
    if not any(e["type"] == "objective" for e in entities):
        results.append({
            "layer": 5,
            "severity": "suggestion",
            "code": "S005",
            "message": "S005: No objectives defined — consider adding strategic objectives",
            "line": None,
        })

    return results


# ── Helpers ────────────────────────────────────────────────────────────────────

def _extract_code(message, default):
    m = re.match(r'^(E\d+|W\d+|S\d+)', message)
    return m.group(1) if m else default


# ── Output formatters ──────────────────────────────────────────────────────────

def format_text(all_results, path, header, entity_count):
    lines = [f"CSL Validation — {path}"]
    lines.append(f"  Entities parsed: {entity_count}")
    if "version" in header:
        lines.append(f"  CSL version: {header['version']}")
    lines.append("")

    errors   = [r for r in all_results if r["severity"] == "error"]
    warnings = [r for r in all_results if r["severity"] == "warning"]
    suggestions = [r for r in all_results if r["severity"] == "suggestion"]

    def fmt_result(r):
        loc = f" (line {r['line']})" if r.get("line") else ""
        return f"  [{r['severity'].upper():10}] {r['message']}{loc}"

    if errors:
        lines.append(f"ERRORS ({len(errors)}):")
        for r in errors:
            lines.append(fmt_result(r))
        lines.append("")

    if warnings:
        lines.append(f"WARNINGS ({len(warnings)}):")
        for r in warnings:
            lines.append(fmt_result(r))
        lines.append("")

    if suggestions:
        lines.append(f"SUGGESTIONS ({len(suggestions)}):")
        for r in suggestions:
            lines.append(fmt_result(r))
        lines.append("")

    if not all_results:
        lines.append("PASSED — no issues found.")
    else:
        total = len(all_results)
        lines.append(
            f"Summary: {len(errors)} error(s), {len(warnings)} warning(s), "
            f"{len(suggestions)} suggestion(s)  [{total} total]"
        )

    return "\n".join(lines)


def format_json(all_results, path, header, entity_count):
    errors   = [r for r in all_results if r["severity"] == "error"]
    warnings = [r for r in all_results if r["severity"] == "warning"]
    suggestions = [r for r in all_results if r["severity"] == "suggestion"]
    output = {
        "file": str(path),
        "valid": len(errors) == 0,
        "entityCount": entity_count,
        "summary": {
            "errors": len(errors),
            "warnings": len(warnings),
            "suggestions": len(suggestions),
        },
        "results": all_results,
    }
    return json.dumps(output, indent=2)


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Validate a CSL model file.")
    ap.add_argument("path", help="Path to the .csl file")
    ap.add_argument("--strict", action="store_true",
                    help="Treat warnings as errors")
    ap.add_argument("--json", action="store_true",
                    help="Output results as JSON")
    ap.add_argument("--quiet", action="store_true",
                    help="Suppress output; use exit code only")
    args = ap.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(2)

    source = path.read_text(encoding="utf-8")
    parser = CSLParser(source)
    parser.parse()

    all_results = []
    all_results += layer1_syntax(parser)
    all_results += layer2_references(parser.entities)
    all_results += layer3_structure(parser.entities)
    all_results += layer4_semantics(parser.entities)
    all_results += layer5_completeness(parser.entities, parser.header)

    has_errors   = any(r["severity"] == "error"   for r in all_results)
    has_warnings = any(r["severity"] == "warning"  for r in all_results)

    if not args.quiet:
        if args.json:
            print(format_json(all_results, path, parser.header, len(parser.entities)))
        else:
            print(format_text(all_results, path, parser.header, len(parser.entities)))

    fail = has_errors or (args.strict and has_warnings)
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
