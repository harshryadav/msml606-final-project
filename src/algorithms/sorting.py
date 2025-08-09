from typing import List, Tuple


def quicksort(arr: List[Tuple[float, int]]) -> List[Tuple[float, int]]:
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2][0]
    left = [x for x in arr if x[0] > pivot]  # sort descending by score
    mid = [x for x in arr if x[0] == pivot]
    right = [x for x in arr if x[0] < pivot]
    return quicksort(left) + mid + quicksort(right)


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

