# Artificial Intelligence Nanodegree
## Introductory Project: Diagonal Sudoku Solver

# Question 1 (Naked Twins)
Q: How do we use constraint propagation to solve the naked twins problem?  
A: Well, the "naked twins" problem is really just a special case of the "naked Ns" problem.
The principle applies to any closed group, ie: any set of N boxes within a unit that all have exactly the same N values.
I've encountered lots of situations with N=3, maybe a couple of N=4, but I've never seen more than that.
N > 7 has no practical value, because if N=9 then no values have been eliminated from any of the boxes in the unit
and if N=8, then the last remaining box will be solved by the "only choice" method.

The algorithm is:
* Iterate through the units. For each unit:
    * Iterate through the boxes in the unit. For each box:
        * Select all boxes in the unit that have the same possibile values as the box
        * If the number of boxes (the selected boxes + the original box) with the same values is the same as the number of possibilities:
            * Remove all those possibilites from the un-selected boxes

# Question 2 (Diagonal Sudoku)
Q: How do we use constraint propagation to solve the diagonal sudoku problem?  
A: Yeah...I don't like the way this question is phrased, because it implies that the diagonal is a solution strategy, when it is, in fact, a constraint.
The diagonal is nothing more than an additional unit, so simply by adding ```[A1, B2, C3...I9]``` to the list of units you force that unit to be satisfied, just like any other.

The standard 27 units (9 rows, 9 columns, and 9 squares), are purely arbitrary and even those are not required.
Any combination of units is valid so long as every box is accounted for by at least one unit.

And, of course, units needn't be contiguous. You could have a symmetric unit like
```[B2, B5, B8, E2, E5, E8, H2, H5, H8]```, or it could be any random set of 9 boxes.

There are 27 units in a standard sudoku. A diagonal sudoku has 29.
The more units there are, the smaller the search space, making the puzzle technically easier to solve, though more difficult to create.

### Install

This project requires **Python 3**.

We recommend students install [Anaconda](https://www.continuum.io/downloads), a pre-packaged Python distribution that contains all of the necessary libraries and software for this project. 
Please try using the environment we provided in the Anaconda lesson of the Nanodegree.

##### Optional: Pygame

Optionally, you can also install pygame if you want to see your visualization. If you've followed our instructions for setting up our conda environment, you should be all set.

If not, please see how to download pygame [here](http://www.pygame.org/download.shtml).

### Code

* `solutions.py` - You'll fill this in as part of your solution.
* `solution_test.py` - Do not modify this. You can test your solution by running `python solution_test.py`.
* `PySudoku.py` - Do not modify this. This is code for visualizing your solution.
* `visualize.py` - Do not modify this. This is code for visualizing your solution.

### Visualizing

To visualize your solution, please only assign values to the values_dict using the ```assign_values``` function provided in solution.py

### Data

The data consists of a text file of diagonal sudokus for you to solve.