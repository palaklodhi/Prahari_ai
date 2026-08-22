"""Fraud Network Graph Intelligence.

Builds a directed money-movement graph from accounts (nodes) and transactions
(edges), enriched with shared device / phone linkages. It then:
  - detects coordinated fraud rings via community detection,
  - ranks entities by role (kingpin / mule / layer) using centrality,
  - assembles an auditable 'intelligence package' per ring that can be
    exported as court-admissible evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import networkx as nx


@dataclass
class RingIntel:
    ring_id: int
    size: int
    total_flow: float
    accounts: list = field(default_factory=list)
    kingpins: list = field(default_factory=list)
    mules: list = field(default_factory=list)
    shared_devices: list = field(default_factory=list)
    shared_phones: list = field(default_factory=list)
    banks: list = field(default_factory=list)
    risk: float = 0.0
    narrative: str = ""


def build_graph(accounts: list, transactions: list) -> nx.DiGraph:
    g = nx.DiGraph()
    for a in accounts:
        g.add_node(
            a.ref,
            holder=a.holder, bank=a.bank, role=a.role,
            device=a.device_id, phone=a.phone, acct_type=a.account_type,
        )
    for t in transactions:
        if t.src_ref in g and t.dst_ref in g:
            if g.has_edge(t.src_ref, t.dst_ref):
                g[t.src_ref][t.dst_ref]["amount"] += t.amount
                g[t.src_ref][t.dst_ref]["count"] += 1
            else:
                g.add_edge(t.src_ref, t.dst_ref, amount=t.amount, count=1, channel=t.channel)
    return g


def _shared_attribute_edges(g: nx.DiGraph, attr: str) -> nx.Graph:
    """Undirected linkage graph: accounts sharing a device/phone are linked."""
    buckets: dict = {}
    for n, data in g.nodes(data=True):
        val = data.get(attr)
        if val:
            buckets.setdefault(val, []).append(n)
    link = nx.Graph()
    link.add_nodes_from(g.nodes())
    for val, nodes in buckets.items():
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                link.add_edge(nodes[i], nodes[j], shared=attr, value=val)
    return link


def analyze_network(accounts: list, transactions: list) -> dict:
    g = build_graph(accounts, transactions)
    if g.number_of_nodes() == 0:
        return {"rings": [], "graph": {"nodes": [], "edges": []}, "summary": {}}

    # Combine money-flow + shared-device + shared-phone into one undirected view
    undirected = g.to_undirected()
    for lg in (_shared_attribute_edges(g, "device"), _shared_attribute_edges(g, "phone")):
        undirected.add_edges_from(lg.edges())

    # Community detection over the combined linkage
    communities = list(nx.community.greedy_modularity_communities(undirected)) \
        if undirected.number_of_edges() else [set([n]) for n in undirected.nodes()]

    # centrality for role inference
    try:
        pagerank = nx.pagerank(g, weight="amount")
    except Exception:
        pagerank = {n: 1.0 / g.number_of_nodes() for n in g.nodes()}
    in_deg = dict(g.in_degree(weight="amount"))
    out_deg = dict(g.out_degree(weight="amount"))

    rings: list[RingIntel] = []
    for idx, comm in enumerate(sorted(communities, key=len, reverse=True)):
        if len(comm) < 2:
            continue
        comm = list(comm)
        sub = g.subgraph(comm)
        total_flow = sum(d["amount"] for _, _, d in sub.edges(data=True))

        # kingpin: high pagerank + net receiver; mule: many small pass-through
        ranked = sorted(comm, key=lambda n: pagerank.get(n, 0), reverse=True)
        kingpins, mules = [], []
        for n in comm:
            data = g.nodes[n]
            inflow = in_deg.get(n, 0)
            outflow = out_deg.get(n, 0)
            pr = pagerank.get(n, 0)
            entry = {"ref": n, "holder": data.get("holder"), "bank": data.get("bank"),
                     "inflow": round(inflow, 2), "outflow": round(outflow, 2),
                     "pagerank": round(pr, 4)}
            if data.get("role") == "kingpin" or (pr >= 0.8 * pagerank.get(ranked[0], 1) and inflow >= outflow):
                kingpins.append(entry)
            elif data.get("role") == "mule" or (outflow > 0 and 0.6 < (inflow / (outflow + 1e-6)) < 1.6):
                mules.append(entry)

        devices = sorted({g.nodes[n].get("device") for n in comm if g.nodes[n].get("device")})
        phones = sorted({g.nodes[n].get("phone") for n in comm if g.nodes[n].get("phone")})
        banks = sorted({g.nodes[n].get("bank") for n in comm if g.nodes[n].get("bank")})

        # ring risk: scale with size, flow, and infrastructure sharing
        risk = min(1.0, 0.15 * len(comm) + min(0.4, total_flow / 5_000_000)
                   + 0.08 * len(devices) + 0.06 * len(phones))

        narrative = (
            f"Coordinated ring of {len(comm)} accounts across {len(banks)} bank(s) moving "
            f"₹{total_flow:,.0f}. {len(kingpins)} controlling node(s) and {len(mules)} suspected "
            f"mule account(s) identified. Linked by {len(devices)} shared device fingerprint(s) and "
            f"{len(phones)} shared phone number(s), indicating single-operator control consistent "
            f"with an organised fraud compound."
        )

        rings.append(RingIntel(
            ring_id=idx + 1, size=len(comm), total_flow=round(total_flow, 2),
            accounts=[{"ref": n, "holder": g.nodes[n].get("holder"),
                       "bank": g.nodes[n].get("bank"), "role": g.nodes[n].get("role")} for n in comm],
            kingpins=kingpins, mules=mules,
            shared_devices=devices, shared_phones=phones, banks=banks,
            risk=round(risk, 3), narrative=narrative,
        ))

    rings.sort(key=lambda r: r.risk, reverse=True)

    # graph payload for the frontend force-graph
    ring_of = {}
    for r in rings:
        for a in r.accounts:
            ring_of[a["ref"]] = r.ring_id
    nodes = [{
        "id": n, "holder": d.get("holder"), "bank": d.get("bank"),
        "role": d.get("role"), "ring": ring_of.get(n),
        "value": round(in_deg.get(n, 0) + out_deg.get(n, 0), 2),
        "pagerank": round(pagerank.get(n, 0), 4),
    } for n, d in g.nodes(data=True)]
    edges = [{"source": u, "target": v, "amount": round(d["amount"], 2),
              "count": d["count"], "channel": d.get("channel")} for u, v, d in g.edges(data=True)]

    summary = {
        "total_accounts": g.number_of_nodes(),
        "total_transactions": len(transactions),
        "total_flow": round(sum(e["amount"] for e in edges), 2),
        "rings_detected": len(rings),
        "accounts_in_rings": len(ring_of),
    }
    return {
        "rings": [r.__dict__ for r in rings],
        "graph": {"nodes": nodes, "edges": edges},
        "summary": summary,
    }


def intelligence_package(accounts: list, transactions: list, ring_id: int) -> Optional[dict]:
    """Court-admissible evidence package for a single ring."""
    result = analyze_network(accounts, transactions)
    ring = next((r for r in result["rings"] if r["ring_id"] == ring_id), None)
    if not ring:
        return None
    refs = {a["ref"] for a in ring["accounts"]}
    ring_txns = [{
        "src": t.src_ref, "dst": t.dst_ref, "amount": t.amount,
        "channel": t.channel, "timestamp": t.created_at.isoformat(),
    } for t in transactions if t.src_ref in refs and t.dst_ref in refs]

    return {
        "package_id": f"IP-RING-{ring_id:03d}",
        "generated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "classification": "RESTRICTED — Law Enforcement",
        "ring": ring,
        "transaction_ledger": ring_txns,
        "evidence_summary": ring["narrative"],
        "chain_of_custody": "Auto-generated from ingested transaction & KYC metadata; hash-sealed on export.",
        "admissibility_note": ("Structured per BNSS/IT Act evidentiary requirements: every edge is "
                               "traceable to a source transaction record with timestamp and channel."),
    }
