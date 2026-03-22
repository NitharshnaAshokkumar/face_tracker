import numpy as np
import sys
import os

# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import compute_cosine_similarity

def test_cosine_similarity():
    v1 = np.array([1.0, 0.0, 0.0])
    v2 = np.array([1.0, 0.0, 0.0])
    assert compute_cosine_similarity(v1, v2) == 1.0
    
    v3 = np.array([0.0, 1.0, 0.0])
    assert compute_cosine_similarity(v1, v3) == 0.0
    
    v4 = np.array([-1.0, 0.0, 0.0])
    assert compute_cosine_similarity(v1, v4) == -1.0
    
    assert compute_cosine_similarity(None, v1) == 0.0
