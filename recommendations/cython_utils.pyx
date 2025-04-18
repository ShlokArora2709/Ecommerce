import numpy as np
cimport numpy as np
import heapq

def fast_recommendations(np.ndarray[double, ndim=1] user_vector, 
                         np.ndarray[double, ndim=2] item_vectors,
                         int top_n,
                         list item_ids):
    cdef int i, j
    cdef int n_items = item_vectors.shape[0]
    cdef int n_factors = user_vector.shape[0]
    cdef double score, total
    cdef list scores = []

    for i in range(n_items):
        total = 0.0
        for j in range(n_factors):
            total += user_vector[j] * item_vectors[i, j]
        

        heapq.heappush(scores, (-total, item_ids[i]))
        
        if len(scores) > top_n:
            heapq.heappop(scores)
    
    # Extract results
    cdef list result = []
    while scores:
        score, item_id = heapq.heappop(scores)
        result.insert(0, (item_id, -score))  
    
    return result