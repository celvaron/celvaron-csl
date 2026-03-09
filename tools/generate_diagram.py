#!/usr/bin/env python3
"""
generate_diagram.py — Generate Mermaid diagrams from a CSL Graph Model JSON

Reads a Graph Model JSON file (produced by transform_csl.py) and outputs
Mermaid diagram code for one of five supported view types.

Usage:
  python generate_diagram.py <graph.json>
  python generate_diagram.py <graph.json> --view architecture
  python generate_diagram.py <graph.json> --view capability-map
  python generate_diagram.py <graph.json> --view process-flow
  python generate_diagram.py <graph.json> --view value-stream
  python generate_diagram.py <graph.json> --view package-architecture
  python generate_diagram.py <graph.json> --view architecture -o diagram.md
  python generate_diagram.py <graph.json> --view architecture --title "My Company"

View types:
  architecture          Top-level: company -> offerings -> segments (default)
  capability-map        Capabilities grouped by team, arrows to offerings
  process-flow          Process steps with dependencies (flowchart)
  value-stream          Market -> segment -> outcome -> offering chain
  package-architecture  Offering -> packages and pricing models
"""

import sys
import re
import json
import argparse
from pathlib import Path


# ── Colour palette (classDef — all nodes of each type get coloured) ────────────

CLASS_STYLES = {
    "company":    "fill:#1e293b,color:#fff,stroke:#0f172a",
    "offering":   "fill:#d97706,color:#fff,stroke:#b45309",
    "segment":    "fill:#2d8f6f,color:#fff,stroke:#1d6b52",
    "market":     "fill:#1a6b9a,color:#fff,stroke:#115478",
    "outcome":    "fill:#7a4fa3,color:#fff,stroke:#5b3a7a",
    "capability": "fill:#0891b2,color:#fff,stroke:#0e7490",
    "process":    "fill:#059669,color:#fff,stroke:#047857",
    "step":       "fill:#6ee7b7,color:#1a1a1a,stroke:#059669",
    "team":       "fill:#6366f1,color:#fff,stroke:#4f46e5",
    "metric":     "fill:#94a3b8,color:#1a1a1a,stroke:#64748b",
    "package":    "fill:#f59e0b,color:#fff,stroke:#d97706",
    "objective":  "fill:#ef4444,color:#fff,stroke:#dc2626",
    "system":     "fill:#475569,color:#fff,stroke:#334155",
    "role":       "fill:#a78bfa,color:#fff,stroke:#7c3aed",
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def safe_id(node_id: str) -> str:
    return node_id.replace(":", "_").replace(" ", "_").replace("-", "_")


def readable(name: str) -> str:
    """PascalCase -> spaced words: ProjectFlow -> Project Flow."""
    return re.sub(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])', " ", name)


def lbl(node: dict, extra: str = "") -> str:
    """Node label: readable name, optional subtitle."""
    name = readable(node["properties"].get("name", node["id"]))
    return f"{name}<br/>{extra}" if extra else name


def nodes_of(nodes, *types):
    return [n for n in nodes if n["type"] in types]


def edges_of(edges, *rels):
    return [e for e in edges if e["relationship"] in rels]


def add_styles(lines, nodes, used_ids):
    """Emit classDef blocks + class assignments for every used node."""
    used_types = {n["type"] for n in nodes if n["id"] in used_ids}
    for t, style in CLASS_STYLES.items():
        if t in used_types:
            lines.append(f"    classDef {t}Style {style}")
    for n in nodes:
        if n["id"] in used_ids and n["type"] in CLASS_STYLES:
            lines.append(f"    class {safe_id(n['id'])} {n['type']}Style")


# ── View: architecture ────────────────────────────────────────────────────────

def view_architecture(nodes, edges, title):
    lines = ["graph TD"]
    if title:
        lines.append(f"    %% {title}")

    relevant = {"company", "offering", "segment", "market"}
    used, edge_lines = set(), []

    for e in edges_of(edges, "targets", "operatesIn"):
        s = next((n for n in nodes if n["id"] == e["source"]), None)
        t = next((n for n in nodes if n["id"] == e["target"]), None)
        if not s or not t or s["type"] not in relevant or t["type"] not in relevant:
            continue
        edge_lines.append(f"    {safe_id(e['source'])} --> {safe_id(e['target'])}")
        used.update([e["source"], e["target"]])

    for n in nodes:
        if n["id"] not in used:
            continue
        nid = safe_id(n["id"])
        lbl_text = lbl(n)
        shape = {
            "company":  f'(["{lbl_text}"])',
            "offering": f'("{lbl_text}")',
            "segment":  f'["{lbl_text}"]',
            "market":   f'[/"{lbl_text}"/]',
        }.get(n["type"], f'["{lbl_text}"]')
        lines.append(f"    {nid}{shape}")

    lines += edge_lines
    if len(lines) > 2:
        add_styles(lines, nodes, used)
    else:
        lines.append("    %% No architecture edges found")
    return "\n".join(lines)


# ── View: capability-map ──────────────────────────────────────────────────────

def view_capability_map(nodes, edges, title):
    lines = ["graph LR"]
    if title:
        lines.append(f"    %% {title}")

    used, edge_lines = set(), []
    owns_e     = edges_of(edges, "owns")
    supports_e = edges_of(edges, "supports")
    depends_e  = edges_of(edges, "dependsOn")

    teams        = nodes_of(nodes, "team")
    capabilities = nodes_of(nodes, "capability")
    offerings    = nodes_of(nodes, "offering")

    # Map team -> its capabilities
    team_caps   = {t["id"]: [] for t in teams}
    orphan_caps = []
    for cap in capabilities:
        owner = next(
            (e["source"] for e in owns_e
             if e["target"] == cap["id"]
             and any(n["id"] == e["source"] and n["type"] == "team" for n in nodes)),
            None,
        )
        dest = team_caps.get(owner) if owner else None
        (dest if dest is not None else orphan_caps).append(cap)

    # Team subgraphs
    for team in teams:
        caps = team_caps.get(team["id"], [])
        if not caps:
            continue
        sg   = safe_id(team["id"]) + "_sg"
        name = readable(team["properties"].get("name", team["id"]))
        lines.append(f'    subgraph {sg}["{name}"]')
        for cap in caps:
            m = cap["properties"].get("maturityLevel", "")
            lines.append(f'        {safe_id(cap["id"])}("{lbl(cap, m)}")')
            used.add(cap["id"])
        lines.append("    end")
        used.add(team["id"])

    for cap in orphan_caps:
        m = cap["properties"].get("maturityLevel", "")
        lines.append(f'    {safe_id(cap["id"])}("{lbl(cap, m)}")')
        used.add(cap["id"])

    # Offering nodes reachable via supports
    supported = {e["target"] for e in supports_e if any(c["id"] == e["source"] for c in capabilities)}
    for off in offerings:
        if off["id"] not in supported:
            continue
        lines.append(f'    {safe_id(off["id"])}{chr(91)}"{lbl(off)}"{chr(93)}')
        used.add(off["id"])

    for e in supports_e:
        s = next((n for n in nodes if n["id"] == e["source"]), None)
        t = next((n for n in nodes if n["id"] == e["target"]), None)
        if s and t and s["type"] == "capability" and t["type"] == "offering":
            edge_lines.append(f"    {safe_id(e['source'])} --> {safe_id(e['target'])}")

    for e in depends_e:
        s = next((n for n in nodes if n["id"] == e["source"]), None)
        t = next((n for n in nodes if n["id"] == e["target"]), None)
        if s and t and s["type"] == "capability" and t["type"] == "capability":
            edge_lines.append(f"    {safe_id(e['source'])} -.-> {safe_id(e['target'])}")

    lines += edge_lines
    if len(lines) > 2:
        add_styles(lines, nodes, used)
    else:
        lines.append("    %% No capability edges found")
    return "\n".join(lines)


# ── View: process-flow ────────────────────────────────────────────────────────

def view_process_flow(nodes, edges, title):
    lines = ["flowchart TD"]
    if title:
        lines.append(f"    %% {title}")

    processes = nodes_of(nodes, "process")
    steps     = nodes_of(nodes, "step")

    if not processes:
        lines.append("    %% No processes defined in this model")
        return "\n".join(lines)

    part_of_e = edges_of(edges, "partOf")
    depends_e = edges_of(edges, "dependsOn")

    for proc in processes:
        pid   = safe_id(proc["id"])
        pname = readable(proc["properties"].get("name", proc["id"]))
        lines.append(f'    subgraph {pid}["{pname}"]')

        proc_steps = [
            s for s in steps
            if any(e["source"] == s["id"] and e["target"] == proc["id"] for e in part_of_e)
        ]
        proc_steps.sort(key=lambda s: int(s["properties"].get("order", 99)))

        for step in proc_steps:
            sid   = safe_id(step["id"])
            order = step["properties"].get("order", "?")
            name  = readable(step["properties"].get("name", step["id"]))
            lines.append(f'        {sid}["{order}. {name}"]')

        lines.append("    end")

        for step in proc_steps:
            for e in depends_e:
                if e["source"] == step["id"]:
                    dep = next((n for n in steps if n["id"] == e["target"]), None)
                    if dep:
                        lines.append(f"    {safe_id(e['target'])} --> {safe_id(step['id'])}")

    step_ids = {safe_id(s["id"]) for s in steps}
    if step_ids:
        lines.append(f"    classDef stepStyle {CLASS_STYLES['step']}")
        lines.append("    class " + ",".join(sorted(step_ids)) + " stepStyle")

    return "\n".join(lines)


# ── View: value-stream ────────────────────────────────────────────────────────

def view_value_stream(nodes, edges, title):
    lines = ["graph TD"]
    if title:
        lines.append(f"    %% {title}")

    relevant = {"market", "segment", "outcome", "offering", "metric"}
    used, edge_lines = set(), []

    for e in edges_of(edges, "operatesIn", "targets", "delivers", "measuredBy"):
        s = next((n for n in nodes if n["id"] == e["source"]), None)
        t = next((n for n in nodes if n["id"] == e["target"]), None)
        if not s or not t or s["type"] not in relevant or t["type"] not in relevant:
            continue
        edge_lines.append(f"    {safe_id(e['source'])} --> {safe_id(e['target'])}")
        used.update([e["source"], e["target"]])

    for n in nodes:
        if n["id"] not in used:
            continue
        nid      = safe_id(n["id"])
        lbl_text = lbl(n)
        nt       = n["type"]
        if nt == "market":
            lines.append(f'    {nid}[/"{lbl_text}"/]')
        elif nt == "segment":
            lines.append(f'    {nid}["{lbl_text}"]')
        elif nt == "outcome":
            lines.append(f'    {nid}{{"{lbl_text}"}}')
        elif nt == "offering":
            lines.append(f'    {nid}("{lbl_text}")')
        elif nt == "metric":
            lines.append(f'    {nid}[("{lbl_text}")]')

    lines += edge_lines
    if len(lines) > 2:
        add_styles(lines, nodes, used)
    else:
        lines.append("    %% No value-stream edges found")
    return "\n".join(lines)


# ── View: package-architecture ────────────────────────────────────────────────

def view_package_architecture(nodes, edges, title):
    lines = ["graph TD"]
    if title:
        lines.append(f"    %% {title}")

    used, edge_lines = set(), []

    for e in edges_of(edges, "partOf"):
        s = next((n for n in nodes if n["id"] == e["source"]), None)
        t = next((n for n in nodes if n["id"] == e["target"]), None)
        if s and t and s["type"] == "package" and t["type"] == "offering":
            edge_lines.append(f"    {safe_id(e['target'])} --> {safe_id(e['source'])}")
            used.update([e["source"], e["target"]])

    for e in edges_of(edges, "requires"):
        s = next((n for n in nodes if n["id"] == e["source"]), None)
        t = next((n for n in nodes if n["id"] == e["target"]), None)
        if s and t and s["type"] == "offering" and t["type"] == "offering":
            edge_lines.append(f"    {safe_id(e['source'])} -.-> {safe_id(e['target'])}")
            used.update([e["source"], e["target"]])

    for n in nodes:
        if n["id"] not in used:
            continue
        nid = safe_id(n["id"])
        if n["type"] == "offering":
            lines.append(f'    {nid}["{lbl(n)}"]')
        elif n["type"] == "package":
            props    = n["properties"]
            tier     = props.get("tier", "")
            price    = props.get("price", "")
            billing  = props.get("billingCycle", "")
            price_s  = f"${price}/{billing}" if price != "" and billing else ""
            extra    = f"{tier}  {price_s}".strip()
            lines.append(f'    {nid}("{lbl(n, extra)}")')

    lines += edge_lines
    if len(lines) > 2:
        add_styles(lines, nodes, used)
    else:
        lines.append("    %% No package edges found")
    return "\n".join(lines)


# ── Dispatch ──────────────────────────────────────────────────────────────────

VIEW_GENERATORS = {
    "architecture":         view_architecture,
    "capability-map":       view_capability_map,
    "process-flow":         view_process_flow,
    "value-stream":         view_value_stream,
    "package-architecture": view_package_architecture,
}


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="Generate a Mermaid diagram from a CSL Graph Model JSON file."
    )
    ap.add_argument("path", help="Path to the graph model JSON file")
    ap.add_argument(
        "--view",
        choices=list(VIEW_GENERATORS.keys()),
        default="architecture",
        help="Diagram view type (default: architecture)",
    )
    ap.add_argument("-o", "--output", help="Write output to this file (default: stdout)")
    ap.add_argument("--title", default="", help="Optional diagram title")
    args = ap.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        graph = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON -- {e}", file=sys.stderr)
        sys.exit(1)

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    title = args.title or graph.get("meta", {}).get("description", "")

    generator = VIEW_GENERATORS[args.view]
    diagram   = generator(nodes, edges, title)
    output    = f"```mermaid\n{diagram}\n```\n"

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Diagram written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
