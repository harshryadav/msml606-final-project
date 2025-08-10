from __future__ import annotations

from typing import Dict, List, Tuple, Optional
import heapq


def dijkstra(adj: Dict[int, List[Tuple[int, float]]], source: int) -> Tuple[Dict[int, float], Dict[int, Optional[int]]]:
    """
    Classic Dijkstra's algorithm on a non-negative weighted directed graph.

    adj: adjacency list {u: [(v, weight), ...]}
    source: source node id

    Returns (dist, prev):
      - dist: shortest distance from source to each reachable node
      - prev: predecessor map for path reconstruction
    """
    dist: Dict[int, float] = {source: 0.0}
    prev: Dict[int, Optional[int]] = {source: None}
    pq: List[Tuple[float, int]] = [(0.0, source)]
    visited = set()

    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        for v, w in adj.get(u, []):
            nd = d + w
            if v not in dist or nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    return dist, prev


def build_star_graph(costs: List[float]) -> Dict[int, List[Tuple[int, float]]]:
    """
    Construct a star graph: node 0 is the source; edges 0->i have weight = costs[i-1].
    This lets Dijkstra pick the node with minimum cost using standard shortest path.
    """
    adj: Dict[int, List[Tuple[int, float]]] = {0: []}
    for i, c in enumerate(costs, start=1):
        adj[0].append((i, float(c)))
        # no edges back; single-hop star is enough for our selection
    return adj


def choose_min_cost_index(costs: List[float]) -> Tuple[int, float]:
    """
    Use Dijkstra over a star graph to choose the index with minimum cost.
    Returns (index_in_input, min_cost).
    """
    if not costs:
        return -1, float("inf")
    adj = build_star_graph(costs)
    dist, _ = dijkstra(adj, 0)
    # nodes are 1..n; pick min dist among them
    best_node, best_cost = min(((node, d) for node, d in dist.items() if node != 0), key=lambda x: x[1])
    # convert back to 0-based index
    return best_node - 1, best_cost

