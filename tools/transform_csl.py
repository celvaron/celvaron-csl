#!/usr/bin/env python3
"""
transform_csl.py — Transform a CSL model to Graph Model JSON

Reads a .csl file and outputs the canonical Graph Model JSON used by other tools.

Usage:
  python transform_csl.py <path/to/model.csl>
  python transform_csl.py <path/to/model.csl> -o output.json
  python transform_csl.py <path/to/model.csl> --pretty
  python transform_csl.py <path/to/model.csl> --state asis
  python transform_csl.py <path/to/model.csl> --state tobe
  python transform_csl.py <path/to/model.csl> --author "Jane Smith"

Options:
  -o FILE        Write output to FILE instead of stdout
  --pretty       Pretty-print JSON with 2-space indentation
  --state        Filter to 'asis' (exclude changeType:"new") or
                 'tobe' (exclude changeType:"retired") entities
  --author TEXT  Override the author in the graph meta block
"""

import sys
import re
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone


# ── Shared parser (same logic as validate_csl.py) ─────────────────────────────

ENTITY_TYPES = {
    "company", "offering", "segment", "market", "outcome", "capability",
    "process", "step", "team", "role", "package", "pricingModel",
    "journey", "system", "objective", "metric",
}

REFERENCE_FIELDS = {
    "targets", "delivers", "requires", "operatesIn", "measuredBy",
    "achievedThrough", "supports", "dependsOn", "ownedBy", "owns",
    "performedBy", "uses", "partOf",
}

# Relationship type to use when generating edges from a given field name
FIELD_TO_RELATIONSHIP = {
    "targets":         "targets",
    "delivers":        "delivers",
    "requires":        "requires",
    "operatesIn":      "operatesIn",
    "measuredBy":      "measuredBy",
    "achievedThrough": "achievedThrough",
    "supports":        "supports",
    "dependsOn":       "dependsOn",
    "ownedBy":         "ownedBy",
    "owns":            "owns",
    "performedBy":     "performedBy",
    "uses":            "uses",
    "partOf":          "partOf",
}


def strip_comments(source: str) -> str:
    lines = []
    for line in source.splitlines():
        idx = line.find("#")
        if idx != -1:
            line = line[:idx]
        lines.append(line)
    return "\n".join(lines)


def tokenise(source: str):
    token_re = re.compile(
        r'"(?:[^"\\]|\\.)*"'
        r'|[-]?\d+(?:\.\d+)?'
        r'|[A-Za-z_][A-Za-z0-9_]*'
        r'|[{}[\]:,]'
        r'|\S+'
    )
    for lineno, line in enumerate(source.splitlines(), start=1):
        for m in token_re.finditer(line):
            yield lineno, m.group(0)


class CSLParser:
    def __init__(self, source: str):
        cleaned = strip_comments(source)
        self._tokens = list(tokenise(cleaned))
        self._pos = 0
        self.header = {}
        self.entities = []

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
            raise ValueError(f"Expected '{value}' got '{tok}' at line {lineno}")
        return lineno, tok

    def _at_end(self):
        return self._pos >= len(self._tokens)

    def parse(self):
        while not self._at_end():
            lineno, tok = self._peek()
            if tok in ("version", "author", "description", "state"):
                self._parse_header_field()
            elif tok == "import":
                self._consume()
                if not self._at_end():
                    self._consume()
            elif tok in ENTITY_TYPES:
                self._parse_entity()
            else:
                self._consume()

    def _parse_header_field(self):
        _, key = self._consume()
        _, colon = self._peek()
        if colon == ":":
            self._consume()
        _, value = self._consume()
        self.header[key] = value.strip('"')

    def _parse_entity(self):
        lineno, entity_type = self._consume()
        _, name = self._peek()
        if name is None or name == "{":
            return
        _, name = self._consume()

        _, brace = self._peek()
        if brace != "{":
            return
        self._consume()

        fields = {}
        while not self._at_end():
            _, next_tok = self._peek()
            if next_tok == "}":
                self._consume()
                break
            try:
                field_name, field_value, field_lineno = self._parse_field()
                fields[field_name] = field_value
            except Exception:
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
        _, colon = self._peek()
        if colon != ":":
            raise ValueError(f"Expected ':' after '{key}' at line {lineno}")
        self._consume()
        value, value_lineno = self._parse_value()
        return key, value, lineno

    def _parse_value(self):
        lineno, tok = self._peek()
        if tok is None:
            raise ValueError("Unexpected end of file")
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
                _, key = self._consume()
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


# ── Graph Model builder ────────────────────────────────────────────────────────

def clean_value(v):
    """Strip surrounding quotes from a string value."""
    if isinstance(v, str):
        return v.strip('"')
    if isinstance(v, list):
        return [clean_value(i) for i in v]
    if isinstance(v, dict):
        return {k: clean_value(vv) for k, vv in v.items()}
    return v


def coerce_field(name, value):
    """Attempt type coercion for well-known numeric fields."""
    numeric_fields = {"price", "size", "target", "baseline", "userLimit"}
    if name in numeric_fields:
        try:
            f = float(value)
            return int(f) if f == int(f) else f
        except (ValueError, TypeError):
            pass
    if value in ("true", "True"):
        return True
    if value in ("false", "False"):
        return False
    return clean_value(value)


def build_node(entity):
    node_id = f"{entity['type']}:{entity['name']}"
    props = {"name": entity["name"]}

    for field, raw_value in entity["fields"].items():
        if field in REFERENCE_FIELDS:
            continue  # references become edges, not node properties
        props[field] = coerce_field(field, clean_value(raw_value))

    return {
        "id": node_id,
        "type": entity["type"],
        "properties": props,
    }


def build_edges(entity):
    edges = []
    src_id = f"{entity['type']}:{entity['name']}"

    for field, raw_value in entity["fields"].items():
        if field not in REFERENCE_FIELDS:
            continue
        relationship = FIELD_TO_RELATIONSHIP[field]
        refs = raw_value if isinstance(raw_value, list) else [raw_value]
        for ref in refs:
            if not isinstance(ref, str):
                continue
            ref_name = ref.strip('"')
            if not ref_name:
                continue
            # We'll resolve the target type later; use placeholder prefix
            edges.append({
                "_source_name": entity["name"],
                "_target_name": ref_name,
                "source": src_id,
                "target": f"?:{ref_name}",  # resolved in pass 2
                "relationship": relationship,
            })
    return edges


def resolve_edge_targets(edges, name_to_id):
    resolved = []
    for edge in edges:
        target_name = edge["_target_name"]
        if target_name in name_to_id:
            edge = dict(edge)
            edge["target"] = name_to_id[target_name]
            del edge["_source_name"]
            del edge["_target_name"]
            resolved.append(edge)
        # Silently skip unresolvable edges (already caught by validator)
    return resolved


# ── State filtering ────────────────────────────────────────────────────────────

def filter_entities(entities, state):
    """
    'asis'  — exclude entities with changeType: "new"
    'tobe'  — exclude entities with changeType: "retired"
    """
    if state is None:
        return entities
    result = []
    for e in entities:
        change = clean_value(e["fields"].get("changeType", ""))
        if state == "asis" and change == "new":
            continue
        if state == "tobe" and change == "retired":
            continue
        result.append(e)
    return result


# ── Entry point ────────────────────────────────────────────────────────────────

def build_graph_model(source, state_filter=None, author_override=None):
    parser = CSLParser(source)
    parser.parse()

    entities = filter_entities(parser.entities, state_filter)

    # Build name → node_id map for edge resolution
    name_to_id = {}
    for e in entities:
        name_to_id[e["name"]] = f"{e['type']}:{e['name']}"

    nodes = [build_node(e) for e in entities]

    raw_edges = []
    for e in entities:
        raw_edges += build_edges(e)
    edges = resolve_edge_targets(raw_edges, name_to_id)

    # Deduplicate edges
    seen_edges = set()
    unique_edges = []
    for edge in edges:
        key = (edge["source"], edge["target"], edge["relationship"])
        if key not in seen_edges:
            seen_edges.add(key)
            unique_edges.append(edge)

    meta = {
        "cslVersion":   parser.header.get("version", "1.0"),
        "author":       author_override or parser.header.get("author", ""),
        "description":  parser.header.get("description", ""),
        "state":        parser.header.get("state", ""),
        "generatedAt":  datetime.now(timezone.utc).isoformat(),
        "nodeCount":    len(nodes),
        "edgeCount":    len(unique_edges),
    }

    return {
        "meta":  meta,
        "nodes": nodes,
        "edges": unique_edges,
    }


def main():
    ap = argparse.ArgumentParser(description="Transform a CSL file to Graph Model JSON.")
    ap.add_argument("path", help="Path to the .csl file")
    ap.add_argument("-o", "--output", help="Write output to this file (default: stdout)")
    ap.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    ap.add_argument("--state", choices=["asis", "tobe"],
                    help="Filter to as-is or to-be state")
    ap.add_argument("--author", help="Override author in meta block")
    args = ap.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    source = path.read_text(encoding="utf-8")
    graph = build_graph_model(source, state_filter=args.state, author_override=args.author)

    indent = 2 if args.pretty else None
    output_str = json.dumps(graph, indent=indent)

    if args.output:
        Path(args.output).write_text(output_str, encoding="utf-8")
        print(f"Graph model written to {args.output}", file=sys.stderr)
    else:
        print(output_str)


if __name__ == "__main__":
    main()
