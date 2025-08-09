from typing import Iterable, List, Tuple
import heapq


def top_k_by_score(items: Iterable[Tuple[float, int]], k: int) -> List[Tuple[float, int]]:
    """
    Return top-k items by score using a min-heap of size k.
    Items are (score, index) tuples; higher score is better.
    """
    heap: List[Tuple[float, int]] = []
    for score, idx in items:
        if len(heap) < k:
            heapq.heappush(heap, (score, idx))
        else:
            if score > heap[0][0]:
                heapq.heapreplace(heap, (score, idx))
    # Return in descending score order
    return sorted(heap, key=lambda x: x[0], reverse=True)

