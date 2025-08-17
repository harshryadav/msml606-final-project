import time
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from functools import total_ordering

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.algorithms.heap_topk import top_k_by_score
from src.algorithms.sorting import heap_sort
from src.data.loader import read_listings

@total_ordering
class ComparableCounter:
    def __init__(self, value, counter):
        self.value = value
        self.counter = counter

    def __lt__(self, other):
        self.counter['comparisons'] += 1
        return self.value < other.value

    def __eq__(self, other):
        self.counter['comparisons'] += 1
        return self.value == other.value

def run_performance_analysis():
    try:
        df = read_listings(pd.read_csv("data/dc-listings.csv"))
    except FileNotFoundError:
        print("DC listings not found")
        return

    np.random.seed(42)
    pairs = [(np.random.rand(), i) for i in range(len(df))]
    
    k_values = [10, 50, 100, 250, 500, 1000, 1500, 2000, 3000, 4000, 5000, 6000]
    
    metrics = {
        'top_k': {'times': [], 'comparisons': []},
        'heap_sort': {'times': [], 'comparisons': []}
    }
    valid_k_values = []

    for k in k_values:
        if k > len(pairs):
            continue
        valid_k_values.append(k)

        # Test Top-K
        comp_counter = {'comparisons': 0}
        counted_pairs = [(ComparableCounter(s, comp_counter), i) for s, i in pairs]
        
        start_time = time.time()
        top_k_by_score(counted_pairs, k)
        end_time = time.time()

        metrics['top_k']['times'].append(end_time - start_time)
        metrics['top_k']['comparisons'].append(comp_counter['comparisons'])

        # Test HeapSort
        comp_counter = {'comparisons': 0}
        counted_pairs = [(ComparableCounter(s, comp_counter), i) for s, i in pairs]

        start_time = time.time()
        heap_sort(counted_pairs)
        end_time = time.time()

        metrics['heap_sort']['times'].append(end_time - start_time)
        metrics['heap_sort']['comparisons'].append(comp_counter['comparisons'])

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))
    fig.suptitle('Performance Analysis: Top-K vs. HeapSort', fontsize=16)

    ax1.plot(valid_k_values, metrics['top_k']['times'], 'o-', label='Top-K Algorithm (O(n log k))')
    ax1.plot(valid_k_values, metrics['heap_sort']['times'], 's-', label='HeapSort Method (O(n log n))')
    ax1.set_xlabel('K value (number of listings)')
    ax1.set_ylabel('Runtime (in seconds)')
    ax1.set_title('Runtime Analysis')
    ax1.legend()
    ax1.grid(True)

    ax2.plot(valid_k_values, metrics['top_k']['comparisons'], 'o-', label='Top-K Algorithm')
    ax2.plot(valid_k_values, metrics['heap_sort']['comparisons'], 's-', label='HeapSort Method')
    ax2.set_xlabel('K value (number of listings)')
    ax2.set_ylabel('Number of Comparisons')
    ax2.set_title('Comparison Count Analysis')
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    
    output_path = os.path.join(os.path.dirname(__file__), 'performance_analysis.png')
    plt.savefig(output_path)


if __name__ == '__main__':
    run_performance_analysis()
