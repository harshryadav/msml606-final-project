from typing import List, Tuple


def heap_sort(arr: List[Tuple[float, int]]) -> List[Tuple[float, int]]:
    # simple heap sort to descending by score
    import heapq

    heap = [(-score, idx) for score, idx in arr]
    heapq.heapify(heap)
    out: List[Tuple[float, int]] = []
    while heap:
        score_neg, idx = heapq.heappop(heap)
        out.append((-score_neg, idx))
    return out

