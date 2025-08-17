from typing import List, Tuple
import heapq

class _MaxHeapWrapper:
    """
    Wrapper for items in a max-heap. Inverts the comparison logic
    so that heapq (a min-heap) can be used as a max-heap.
    """
    def __init__(self, item):
        self.item = item

    def __lt__(self, other):
        # Invert comparison for max-heap behavior
        return self.item[0] > other.item[0]
    
    def __eq__(self, other):
        return self.item[0] == other.item[0]

def heap_sort(arr: List[Tuple[float, int]]) -> List[Tuple[float, int]]:
    """
    Sorts a list of (score, index) tuples in descending order of score
    using a heap. Handles both numeric scores and wrapper objects
    that support comparison.
    """
    # Check if the first element's score is a number or a custom object
    if arr and hasattr(arr[0][0], 'value'): # Heuristic for ComparableCounter
        # Use a wrapper to simulate max-heap without negation for custom objects
        heap = [_MaxHeapWrapper(item) for item in arr]
        heapq.heapify(heap)
        out: List[Tuple[float, int]] = []
        while heap:
            out.append(heapq.heappop(heap).item)
        return out
    else:
        # Original implementation for numeric scores by negating them
        heap = [(-score, idx) for score, idx in arr]
        heapq.heapify(heap)
        out: List[Tuple[float, int]] = []
        while heap:
            score_neg, idx = heapq.heappop(heap)
            out.append((-score_neg, idx))
        return out

