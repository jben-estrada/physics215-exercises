"""
Basis code source: https://github.com/AllenDowney/ThinkComplexity2/blob/master/code/Sand.py
Original author: `AllenDowney`

Modifications done on `Sand.py`:
- The class `Cell2DViewer`, and its subclass `SandPile2DViewer` and its instances are removed.
- The driver function `main` is removed.
- The `single_source` function is removed.
- The method `draw` of class `SandPile` is overriden to match the color map of plots used in the book.
"""

import itertools

import numpy as np
import matplotlib.pyplot as plt

from Cell2D import Cell2D, draw_array
from scipy.signal import correlate2d


class SandPile(Cell2D):
    """Diffusion Cellular Automaton."""

    kernel = np.array([[0, 1, 0],
                       [1,-4, 1],
                       [0, 1, 0]], dtype=np.int32)

    def __init__(self, n, m=None, level=9):
        """Initializes the attributes.

        n: number of rows
        m: number of columns
        level: starting value for all cells
        """
        m = n if m is None else m
        self.array = np.ones((n, m), dtype=np.int32) * level
        self.reset()

    def reset(self):
        """Start keeping track of the number of toppled cells.
        """
        self.toppled_seq = []

    def step(self, K=3):
        """Executes one time step.
        
        returns: number of cells that toppled
        """
        toppling = self.array > K
        num_toppled = np.sum(toppling)
        self.toppled_seq.append(num_toppled)

        c = correlate2d(toppling, self.kernel, mode='same')
        self.array += c
        return num_toppled
    
    def drop(self):
        """Increments a random cell."""
        a = self.array
        n, m = a.shape
        index = np.random.randint(n), np.random.randint(m)
        a[index] += 1
    
    def run(self):
        """Runs until equilibrium.
        
        returns: duration, total number of topplings
        """
        total = 0
        for i in itertools.count(1):
            num_toppled = self.step()
            total += num_toppled
            if num_toppled == 0:
                return i, total

    def drop_and_run(self):
        """Drops a random grain and runs to equilibrium.
        
        returns: duration, total_toppled
        """
        self.drop()
        duration, total_toppled = self.run()
        return duration, total_toppled
    
    def draw(self):
        """
        Draws the cells.
        
        Source: Chapter 08 Jupyter notebook of ThinkComplexity2
        """
        draw_array(self.array, cmap='YlOrRd', vmax=5)
