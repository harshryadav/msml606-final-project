from __future__ import annotations

from typing import Dict, List, Tuple
import heapq


def dijkstra_shortest_paths(graph: Dict[int, List[Tuple[int, float]]], start: int) -> Dict[int, float]:
    """Simple Dijkstra over adjacency list graph."""
    dist: Dict[int, float] = {start: 0.0}
    pq: List[Tuple[float, int]] = [(0.0, start)]
    visited = set()
    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        for v, w in graph.get(u, []):
            nd = d + w
            if v not in dist or nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist

