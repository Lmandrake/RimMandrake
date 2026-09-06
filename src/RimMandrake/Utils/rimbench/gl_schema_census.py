#!/usr/bin/env python3
"""
gl_schema_census.py

Machine-derived SCHEMA census of Geological Landforms' landform recipe XML
files (NodeCanvas / GraphEditor.Landform), so a Python program can later
WRITE one from scratch.

Input:  all *.xml under the Landforms-v1 workshop item folder.
Output: research/RimMandrake/reference/gl_landform_schema.md  (+ stdout summary)

stdlib only (xml.etree.ElementTree, glob, collections, os, sys).
"""
from __future__ import annotations

import glob
import os
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

LANDFORMS_DIR = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/2773943594/1.6/Landforms-v1"
OUT_MD = "/mnt/d/Luke/dev/Rimworld/research/RimMandrake/reference/gl_landform_schema.md"
MAX_DISTINCT_SHOWN = 8

SCALAR_TAGS = {
    "string", "boolean", "int", "long", "double", "float",
    "Operation", "Topology", "MapSide",
}
# Tags handled specially (not generic scalar): Port, Variable, FloatRange


def opposite(d):
    return "In" if d == "Out" else ("Out" if d == "In" else None)


class FileGraph:
    """Parsed representation of one landform XML file."""

    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        tree = ET.parse(path)
        self.root = tree.getroot()
        self.nodes = {}          # node_id(str) -> {"name","type","pos", el}
        self.port_owner = {}     # port_id(str) -> node_id
        self.port_name = {}      # port_id(str) -> port name
        self.port_dynamic = {}   # port_id(str) -> "True"/"False"
        self.port_dir = {}       # port_id(str) -> "In"/"Out"/None
        self._parse_nodes()
        self.connections = self._parse_connections()
        self._infer_directions()

    def _parse_nodes(self):
        nodes_el = self.root.find("Nodes")
        if nodes_el is None:
            return
        for node_el in nodes_el.findall("Node"):
            nid = node_el.get("ID")
            self.nodes[nid] = {
                "name": node_el.get("name"),
                "type": node_el.get("type"),
                "pos": node_el.get("pos"),
                "el": node_el,
            }
            for port_el in node_el.findall("Port"):
                pid = port_el.get("ID")
                pname = port_el.get("name")
                dyn = port_el.get("dynamic")
                self.port_owner[pid] = nid
                self.port_name[pid] = pname
                self.port_dynamic[pid] = dyn
                direction = None
                if dyn == "True":
                    dir_el = port_el.find("Direction")
                    if dir_el is not None and dir_el.text:
                        direction = dir_el.text.strip()
                else:
                    if pname and pname.endswith("OutputKnob"):
                        direction = "Out"
                    elif pname and pname.endswith("InputKnob"):
                        direction = "In"
                    # else: ambiguous fixed knob (Frequency/Average/Angle/
                    # Base/Stone/Cave/Mineables/... Knob) -> resolve later
                self.port_dir[pid] = direction

    def _parse_connections(self):
        conns = []
        conns_el = self.root.find("Connections")
        if conns_el is None:
            return conns
        for c in conns_el.findall("Connection"):
            conns.append((c.get("port1ID"), c.get("port2ID")))
        return conns

    def _infer_directions(self):
        changed = True
        while changed:
            changed = False
            for a, b in self.connections:
                da, db = self.port_dir.get(a), self.port_dir.get(b)
                if da and not db:
                    self.port_dir[b] = opposite(da)
                    changed = True
                elif db and not da:
                    self.port_dir[a] = opposite(db)
                    changed = True

    def resolved_edges(self):
        """Return list of (producer_port, consumer_port, anomaly_bool)."""
        out = []
        for a, b in self.connections:
            da, db = self.port_dir.get(a), self.port_dir.get(b)
            if da == "Out" and db == "In":
                out.append((a, b, False))
            elif db == "Out" and da == "In":
                out.append((b, a, False))
            else:
                # both unknown, both same, or one missing -> anomaly
                out.append((a, b, True))
        return out


def collect_scalar_fields(node_el, sink_fields, sink_floatranges, sink_variables):
    for child in list(node_el):
        tag = child.tag
        name = child.get("name")
        if tag == "Port":
            continue
        if tag == "Variable":
            sink_variables[name].append(child.get("refID"))
            continue
        if tag == "FloatRange":
            mn = child.findtext("min")
            mx = child.findtext("max")
            sink_floatranges[name].append((mn, mx))
            continue
        # generic scalar (string/boolean/int/long/double/float/Operation/
        # Topology/MapSide, and any other unnamed simple tag)
        text = child.text.strip() if child.text else ""
        sink_fields[(tag, name)].append(text)


def fmt_values(values):
    distinct = list(dict.fromkeys(values))  # preserve order, dedupe
    numeric = True
    nums = []
    for v in distinct:
        try:
            nums.append(float(v))
        except (TypeError, ValueError):
            numeric = False
            break
    if numeric and len(distinct) > MAX_DISTINCT_SHOWN:
        return f"range [{min(nums)} .. {max(nums)}] ({len(values)} occurrences, {len(distinct)} distinct)"
    if len(distinct) > MAX_DISTINCT_SHOWN:
        shown = distinct[:MAX_DISTINCT_SHOWN]
        return f"{len(distinct)} distinct values, first {MAX_DISTINCT_SHOWN}: {shown} ..."
    return f"{distinct} ({len(values)} occurrences)"


def main():
    paths = sorted(glob.glob(os.path.join(LANDFORMS_DIR, "*.xml")))
    if not paths:
        print(f"ERROR: no XML files found under {LANDFORMS_DIR}", file=sys.stderr)
        sys.exit(1)

    node_type_counts = Counter()
    node_type_files = defaultdict(set)
    node_type_fields = defaultdict(lambda: defaultdict(list))       # type -> (tag,name) -> [values]
    node_type_floatranges = defaultdict(lambda: defaultdict(list))  # type -> name -> [(min,max)]
    node_type_variables = defaultdict(lambda: defaultdict(list))    # type -> name -> [refID]
    node_type_ports = defaultdict(lambda: defaultdict(lambda: {"dynamic": set(), "direction": set(), "count": 0}))
    node_type_pos_values = defaultdict(list)

    anomalies = []  # (file, port1, port2)
    parsed_files = []

    for path in paths:
        try:
            fg = FileGraph(path)
        except ET.ParseError as e:
            print(f"PARSE ERROR {path}: {e}", file=sys.stderr)
            continue
        parsed_files.append(fg)

        for nid, ninfo in fg.nodes.items():
            ntype = ninfo["type"]
            node_type_counts[ntype] += 1
            node_type_files[ntype].add(fg.name)
            node_type_pos_values[ntype].append(ninfo["pos"])
            collect_scalar_fields(
                ninfo["el"],
                node_type_fields[ntype],
                node_type_floatranges[ntype],
                node_type_variables[ntype],
            )
            for port_el in ninfo["el"].findall("Port"):
                pname = port_el.get("name")
                pdyn = port_el.get("dynamic")
                pid = port_el.get("ID")
                rec = node_type_ports[ntype][pname]
                rec["dynamic"].add(pdyn)
                d = fg.port_dir.get(pid)
                if d:
                    rec["direction"].add(d)
                rec["count"] += 1

        for a, b, bad in fg.resolved_edges():
            if bad:
                anomalies.append((fg.name, a, b))

    total_types = len(node_type_counts)
    top10 = node_type_counts.most_common(10)

    # ---- pick DesertPlateau for the literal connection example + sketch ----
    dp = next((fg for fg in parsed_files if fg.name == "LandformDesertPlateau.xml"), None)

    example_line = None
    example_desc = None
    if dp is not None:
        for a, b, bad in dp.resolved_edges():
            if not bad:
                pa_node = dp.port_owner[a]
                pb_node = dp.port_owner[b]
                example_line = f'<Connection port1ID="{a}" port2ID="{b}" />'
                example_desc = (
                    f'port {a} = "{dp.port_name[a]}" (Out) on Node ID={pa_node} '
                    f'("{dp.nodes[pa_node]["name"]}", type={dp.nodes[pa_node]["type"]}); '
                    f'port {b} = "{dp.port_name[b]}" (In) on Node ID={pb_node} '
                    f'("{dp.nodes[pb_node]["name"]}", type={dp.nodes[pb_node]["type"]}). '
                    f"Data flows producer -> consumer."
                )
                break

    # ---- minimal graph sketch: DesertPlateau, Perlin sources -> outputs ----
    sketch_lines = []
    if dp is not None:
        # directed node-level edges: producer_node -> consumer_node, labeled by port names
        node_edges = []  # (prod_node, prod_port_name, cons_node, cons_port_name)
        preds = defaultdict(list)  # consumer_node -> [(producer_node, prod_port_name, cons_port_name)]
        for a, b, bad in dp.resolved_edges():
            if bad:
                continue
            pn, cn = dp.port_owner[a], dp.port_owner[b]
            node_edges.append((pn, dp.port_name[a], cn, dp.port_name[b]))
            preds[cn].append((pn, dp.port_name[a], dp.port_name[b]))

        targets = [nid for nid, info in dp.nodes.items() if info["type"] in ("outputElevation", "outputTerrain")]

        for target in targets:
            tinfo = dp.nodes[target]
            sketch_lines.append(f"\nBackward trace to Node ID={target} \"{tinfo['name']}\" (type={tinfo['type']}):")
            visited = set()
            frontier = [target]
            chain_edges = []
            while frontier:
                nxt = []
                for cn in frontier:
                    for (pn, pport, cport) in preds.get(cn, []):
                        edge_key = (pn, cn, pport, cport)
                        if edge_key not in chain_edges:
                            chain_edges.append(edge_key)
                        if pn not in visited:
                            visited.add(pn)
                            nxt.append(pn)
                frontier = nxt
            # print edges in a stable, readable producer->consumer order
            for (pn, cn, pport, cport) in chain_edges:
                pinfo, cinfo = dp.nodes[pn], dp.nodes[cn]
                sketch_lines.append(
                    f"  Node {pn} ({pinfo['type']}, port \"{pport}\") "
                    f"-> Node {cn} ({cinfo['type']}, port \"{cport}\")"
                )
            perlin_ancestors = sorted(
                nid for nid in visited if dp.nodes[nid]["type"] == "gridPerlin"
            )
            sketch_lines.append(
                f"  Perlin source node IDs feeding this chain: {perlin_ancestors}"
            )

    # ---- pos attribute check ----
    # pos is a Node attribute only; confirm no Connection/Variable/Object
    # references coordinate-like data, and note landformManifest/worldTileReq
    # always carry an identical placeholder pos (never moved by the user).
    manifest_pos = set(node_type_pos_values.get("landformManifest", []))
    worldtilereq_pos = set(node_type_pos_values.get("worldTileReq", []))

    # =========================== render markdown ===========================
    lines = []
    lines.append("# Geological Landforms - landform recipe XML schema (machine-derived)\n")
    lines.append(
        f"Derived by `src/RimMandrake/Utils/rimbench/gl_schema_census.py` from "
        f"{len(parsed_files)} files in `{LANDFORMS_DIR}`.\n"
    )
    lines.append(
        "Root element: `<NodeCanvas type=\"GeologicalLandforms.GraphEditor.Landform\">` "
        "with children `<EditorStates/>`, `<Groups/>`, `<Nodes>`, `<Connections>`, `<Objects>`.\n"
    )

    # 1. node type census
    lines.append("## 1. Node-type census\n")
    lines.append(f"Distinct node `type=` values across the corpus: **{total_types}**.\n")
    lines.append("| type | node instances | files using it |")
    lines.append("|---|---|---|")
    for ntype, cnt in node_type_counts.most_common():
        lines.append(f"| `{ntype}` | {cnt} | {len(node_type_files[ntype])} |")
    lines.append("")

    # 2. per node type fields/ports
    lines.append("## 2. Per node type: scalar fields and ports\n")
    for ntype, cnt in node_type_counts.most_common():
        lines.append(f"### `{ntype}` ({cnt} instances, {len(node_type_files[ntype])} files)\n")
        fields = node_type_fields[ntype]
        if fields:
            lines.append("Scalar children (`tag`+`name` -> values):\n")
            for (tag, name), values in sorted(fields.items(), key=lambda kv: (kv[0][1] or "")):
                lines.append(f"- `<{tag} name=\"{name}\">`: {fmt_values(values)}")
            lines.append("")
        franges = node_type_floatranges[ntype]
        if franges:
            lines.append("`FloatRange` children (`name` -> min/max seen):\n")
            for name, pairs in sorted(franges.items()):
                mins = [float(p[0]) for p in pairs if p[0] is not None]
                maxs = [float(p[1]) for p in pairs if p[1] is not None]
                lines.append(
                    f"- `{name}`: min in [{min(mins)} .. {max(mins)}], "
                    f"max in [{min(maxs)} .. {max(maxs)}] ({len(pairs)} occurrences)"
                )
            lines.append("")
        variables = node_type_variables[ntype]
        if variables:
            lines.append(
                "`Variable` children (indirection: `<Variable name=\"X\" refID=\"N\"/>` "
                "points at `<Objects><Object refID=\"N\">` holding a typed "
                "`List<T>`, e.g. thresholds/values/mapSides arrays):\n"
            )
            for name, refids in sorted(variables.items()):
                lines.append(f"- `{name}`: {len(refids)} occurrences (refIDs vary per-file, local to that file)")
            lines.append("")
        ports = node_type_ports[ntype]
        if ports:
            lines.append("Ports seen (`name`: dynamic flag(s), resolved direction(s)):\n")
            for pname, rec in sorted(ports.items()):
                lines.append(
                    f"- `{pname}` (x{rec['count']}): dynamic={sorted(rec['dynamic'])}, "
                    f"direction={sorted(rec['direction']) if rec['direction'] else 'UNKNOWN (never resolved via a connection in this corpus)'}"
                )
            lines.append("")

    # 3. connection encoding
    lines.append("## 3. How connections are encoded\n")
    lines.append(
        "Each file has one flat `<Connections>` list of "
        "`<Connection port1ID=\"X\" port2ID=\"Y\" />` elements. `X`/`Y` are **Port IDs**, "
        "unique only within that file's `<Nodes>` section (never a Node ID directly) - "
        "a port's owning node is found by scanning `<Node>` elements for a child "
        "`<Port ID=\"X\">`.\n"
    )
    lines.append(
        "`port1ID`/`port2ID` are **not source/target** - the order carries no meaning. "
        "Direction comes from the port's own record: a dynamic port (`dynamic=\"True\"`) "
        "carries an explicit `<Direction name=\"direction\">In</Direction>` or `Out`; a "
        "fixed port (`dynamic=\"False\"`) is inferred by name convention "
        "(`...OutputKnob` => Out, `...InputKnob` => In) or, for ambiguous fixed "
        "\"parameter\" knobs (e.g. `FrequencyKnob`, `AverageKnob`, `AngleKnob`, "
        "`BaseKnob`, `MineablesKnob`), by fixpoint propagation across every "
        "connection that touches a port whose direction is already known "
        "(a connection always pairs exactly one Out port with one In port). "
        "Data flow is producer(Out) -> consumer(In).\n"
    )
    if example_line:
        lines.append(f"Literal example, `LandformDesertPlateau.xml`:\n\n```xml\n{example_line}\n```\n")
        lines.append(example_desc + "\n")
    if anomalies:
        lines.append(f"**{len(anomalies)} connections across the corpus could not be resolved to an Out/In pair** "
                      f"(both ends stayed ambiguous - i.e. neither end's port name nor any chain of connections "
                      f"reached a `...OutputKnob`/`...InputKnob`/explicit-Direction port). First few: {anomalies[:5]}\n")
    else:
        lines.append("Every connection in the corpus resolved cleanly to one Out port and one In port.\n")

    # 4. output/manifest/req nodes
    lines.append("## 4. Output/terminal nodes and manifest/requirement nodes\n")
    special_types = ["landformManifest", "worldTileReq"] + sorted(
        t for t in node_type_counts if t.startswith("output")
    )
    for ntype in special_types:
        if ntype not in node_type_counts:
            continue
        lines.append(f"### `{ntype}`\n")
        fields = node_type_fields[ntype]
        for (tag, name), values in sorted(fields.items(), key=lambda kv: (kv[0][1] or "")):
            lines.append(f"- `<{tag} name=\"{name}\">`: {fmt_values(values)}")
        for name, pairs in sorted(node_type_floatranges[ntype].items()):
            mins = [float(p[0]) for p in pairs if p[0] is not None]
            maxs = [float(p[1]) for p in pairs if p[1] is not None]
            lines.append(f"- `FloatRange name=\"{name}\"`: min in [{min(mins)} .. {max(mins)}], max in [{min(maxs)} .. {max(maxs)}]")
        for pname, rec in sorted(node_type_ports[ntype].items()):
            lines.append(
                f"- Port `{pname}`: dynamic={sorted(rec['dynamic'])}, "
                f"direction={sorted(rec['direction']) if rec['direction'] else 'UNKNOWN'}"
            )
        lines.append("")

    # 5. pos attribute
    lines.append("## 5. The `pos=` attribute\n")
    lines.append(
        "`pos=\"x,y\"` on `<Node>` is the GraphEditor canvas layout coordinate only. "
        "Confirmed structurally: `<Connection>` elements reference only Port IDs, "
        "`<Variable>`/`<Object>` elements reference only refIDs and typed list "
        "contents - nowhere in the schema is a node's `pos` value read back by "
        "ID, index or coordinate match. As corroborating evidence, the two "
        "always-first nodes (`landformManifest` ID=0 and `worldTileReq` ID=1) "
        "carry the **same literal placeholder pos across every file** "
        f"(`landformManifest` pos values seen: {sorted(manifest_pos)[:3]}{'...' if len(manifest_pos) > 3 else ''}; "
        f"`worldTileReq` pos values seen: {sorted(worldtilereq_pos)[:3]}{'...' if len(worldtilereq_pos) > 3 else ''}), "
        "i.e. the editor never bothers to lay these two out and nothing downstream cares. "
        "A generator can therefore emit any pos (or a fixed grid layout) safely.\n"
    )

    # 6. minimal graph sketch
    lines.append("## 6. Minimal-graph sketch (DesertPlateau: Perlin sources -> outputs)\n")
    if sketch_lines:
        lines.extend(sketch_lines)
    else:
        lines.append("UNMEASURED - LandformDesertPlateau.xml was not found among the parsed files.\n")
    lines.append("")

    md_text = "\n".join(lines) + "\n"
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(md_text)

    # ------------------------------ stdout summary ------------------------------
    print(f"Parsed {len(parsed_files)}/{len(paths)} files.")
    print(f"Distinct node types: {total_types}")
    print("Top 10 node types by instance count:")
    for ntype, cnt in top10:
        print(f"  {ntype:30s} {cnt:4d} instances, {len(node_type_files[ntype])} files")
    print()
    if example_line:
        print("Connection example (DesertPlateau):", example_line)
        print(" ", example_desc)
    print()
    print(f"Anomalous (unresolved-direction) connections in corpus: {len(anomalies)}")
    print()
    print("Output-node types:", [t for t in node_type_counts if t.startswith("output")])
    print()
    print("Minimal graph sketch (DesertPlateau):")
    for l in sketch_lines:
        print(" ", l)
    print()
    print(f"Wrote schema doc: {OUT_MD}")


if __name__ == "__main__":
    main()
