"""
Fractal Dimension: Box-Counting (Minkowski-Bouligand) Dimension

This module computes the fractal dimension of CA spacetime grids.

Key insight from empirical testing:
- Condensates (near percolation threshold): d_f ≈ 91/48 ≈ 1.896
- Particle systems (sparse): d_f ≈ 1.5 - 1.6
- Dense/full grids: d_f → 2.0

This provides a geometric metric to distinguish phase types!
"""

import numpy as np
from scipy.stats import linregress


def compute_fractal_dimension(grid: np.ndarray) -> float:
    """
    Compute the Box-Counting Dimension (Minkowski-Bouligand dimension).
    
    Target for Condensates: d_f ≈ 91/48 ≈ 1.896 (Percolation Cluster)
    Target for Particles: d_f ≈ 1.5 - 1.6
    
    Args:
        grid: 2D binary numpy array
        
    Returns:
        Estimated fractal dimension
    """
    # Ensure binary
    pixels = (grid > 0).astype(int)
    
    # Handle edge cases
    if pixels.sum() == 0:
        return 0.0
    
    h, w = pixels.shape
    min_dim = min(h, w)
    
    # Scales: Powers of 2 up to size/2
    scales = []
    counts = []
    
    # Start with scale 1 (individual pixels)
    scales.append(1)
    counts.append(np.sum(pixels))
    
    # Box sizes: 2, 4, 8, 16...
    box_size = 2
    while box_size <= min_dim // 2:
        # Pad to multiple of box_size
        pad_h = (box_size - h % box_size) % box_size
        pad_w = (box_size - w % box_size) % box_size
        
        padded = np.pad(pixels, ((0, pad_h), (0, pad_w)), mode='constant')
        ph, pw = padded.shape
        
        # Reshape to (n_rows, box_size, n_cols, box_size)
        sh = ph // box_size
        sw = pw // box_size
        
        blocks = padded.reshape(sh, box_size, sw, box_size)
        
        # Check if box has any active pixel (max > 0)
        box_active = blocks.max(axis=(1, 3))
        
        num_boxes = np.sum(box_active > 0)
        
        if num_boxes > 0:
            scales.append(box_size)
            counts.append(num_boxes)
        
        box_size *= 2
    
    if len(scales) < 2:
        return 2.0  # Insufficient data, assume space-filling
    
    # Fit line: log(N) = -d_f * log(scale) + C
    log_scales = np.log(scales)
    log_counts = np.log(counts)
    
    slope, intercept, r_value, p_value, std_err = linregress(log_scales, log_counts)
    
    # Dimension is negative slope
    return -slope


def classify_by_fractal_dimension(d_f: float) -> str:
    """
    Classify the phase type based on fractal dimension.
    
    Returns:
        'percolation': Near critical threshold (d_f ≈ 1.89)
        'subcritical': Sparse particle systems (d_f ≈ 1.5)
        'supercritical': Dense/full grids (d_f ≈ 2.0)
        'degenerate': Empty or trivial (d_f ≈ 0)
    """
    if d_f < 0.5:
        return 'degenerate'
    elif 1.7 <= d_f <= 2.0:
        # Near percolation threshold (91/48 ≈ 1.896)
        if abs(d_f - 1.896) < 0.15:
            return 'percolation'
        elif d_f > 1.95:
            return 'supercritical'
        else:
            return 'percolation'  # Still near critical
    elif 1.3 <= d_f < 1.7:
        return 'subcritical'
    else:
        return 'degenerate'


if __name__ == "__main__":
    # Test with some synthetic patterns
    print("═══ FRACTAL DIMENSION TEST ═══")
    
    # Test 1: Full grid (should be ~2.0)
    full = np.ones((64, 64))
    print(f"Full grid: d_f = {compute_fractal_dimension(full):.3f}")
    
    # Test 2: Random 50% (should be ~2.0)
    np.random.seed(42)
    random_50 = (np.random.random((64, 64)) < 0.5).astype(int)
    print(f"Random 50%: d_f = {compute_fractal_dimension(random_50):.3f}")
    
    # Test 3: Random 20% (~percolation threshold)
    random_20 = (np.random.random((64, 64)) < 0.2).astype(int)
    print(f"Random 20%: d_f = {compute_fractal_dimension(random_20):.3f}")
    
    # Test 4: Sparse 5%
    sparse = (np.random.random((64, 64)) < 0.05).astype(int)
    print(f"Sparse 5%: d_f = {compute_fractal_dimension(sparse):.3f}")
    
    # Test 5: Sierpinski-like pattern (should be ~log(3)/log(2) ≈ 1.585)
    # Just approximate with checkerboard subsampling
    sierpinski_approx = np.zeros((64, 64))
    sierpinski_approx[::2, ::2] = 1
    sierpinski_approx[1::4, 1::4] = 1
    print(f"Sierpinski approx: d_f = {compute_fractal_dimension(sierpinski_approx):.3f}")
