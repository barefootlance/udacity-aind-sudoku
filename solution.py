from string import ascii_uppercase, hexdigits
from math import sqrt, pow
import logging

# when checking to see if the reduce has stalled, 
# we can check either for a change in boxes
# or a change in values
STALL_BOXES = True
STALL_VALUES = not STALL_BOXES
stall_check = STALL_BOXES

# unit_size is the number of boxes in a unit
# TODO: make this work for unit_size = 16.
unit_size = 9
assert pow(int(sqrt(unit_size)), 2) == unit_size, "unit_size must be a square, ie: 9, 16, 25, etc"

# rows are alpha characters
assert unit_size <= len(ascii_uppercase), "Not enough characters for rows naming convention"
rows = ascii_uppercase[:unit_size]

# cols are digits 
assert unit_size <= len(hexdigits)-1, "Not enough characters for cols naming convention"
cols = hexdigits[1:unit_size+1]

def cross(a, b):
    "Cross product of elements in A and elements in B."
    return [s+t for s in a for t in b]

# Each square in the grid is a "box"
boxes = cross(rows, cols)

# A "unit" is a group of boxes. 
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diagonal_units = [[r+c for (r,c) in zip(rows, cols)], [r+c for (r,c) in zip(rows, reversed(cols))]]

# A standard Sudoku puzzle
standard_unitlist = row_units + column_units + square_units

# A standard Sudoku puzzle with the additionl restriction that
# the diagonals must also contain a unique value.
project_unitlist = standard_unitlist + diagonal_units

# The variable containing the unitlist we're using.
# NOTE: this must be set before calling solve and cannot be changed after calling it
unitlist = standard_unitlist

# Dictionary associating a box with the units it is in
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)

# Dictionary associating a box with all other boxes in the units it is in
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

# The value to be interpreted as an empty box when reading in a grid string
empty_grid_value = '.'

# All possible values a box can contain
assert unit_size <= len(hexdigits)-1, "Not enough characters for values naming convention"
all_possible_box_values = hexdigits[1:unit_size+1]

assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = all_possible_box_values
    for c in grid:
        if c in digits:
            chars.append(c)
        elif c == empty_grid_value:
            chars.append(digits)
        else:
            assert False
    assert len(chars) == len(boxes)
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    sqrt_unit_size = int(sqrt(unit_size))
    line = '+'.join(['-'*(width*sqrt_unit_size)]*sqrt_unit_size)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print

def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value 
    from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            #values[peer] = values[peer].replace(digit,'')
            assign_value(values, peer, values[peer].replace(digit,''))
    return values

def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, 
    assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for unit in unitlist:
        for digit in all_possible_box_values:
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                #values[dplaces[0]] = digit
                assign_value(values, dplaces[0], digit)
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    # NOTE: this works for any size of closed group, not just 2
    # so if there are three boxes with the same three values the
    # algorithm will pick that up as well, for example.
    for unit in unitlist:
        for box in unit:
            if len(values[box]) > 1:
                twins = [twin for twin in unit if twin != box and values[box] == values[twin]]
                if len(twins)+1 == len(values[box]):
                    for peer in unit:
                        if peer != box and not peer in twins:
                            for digit in values[box]:
                                #values[peer] = values[peer].replace(digit,'')
                                assign_value(values, peer, values[peer].replace(digit,''))
                                
    return values

def trace_step(method, values):
    """
    Records the changes in the puzzle for each step.
    Input: 
        method: The function to apply.
        values: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    box_count = len([box for box in values.keys() if len(values[box]) == 1])
    char_count = len(''.join([chars for chars in values.values()]))
    values = method(values)
    box_change = len([box for box in values.keys() if len(values[box]) == 1]) - box_count
    char_change = char_count - len(''.join([chars for chars in values.values()]))
    logging.info(method.__name__ + ' Change: ' \
        + str(box_change) + ' boxes, ' \
        + str(char_change) + ' chars')
    return values

def is_solved(values):
    """
    Returns true if the puzzle is solved
    """
    # only one value per box
    if len([box for box in values.keys() if len(values[box]) == 1]) != len(boxes):
        return False

    # no duplicate values in any units
    for unit in unitlist:
        if len(set([values[box] for box in unit])) != unit_size:
            return False
    
    # yay!
    return True

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    strategies = [eliminate, only_choice, naked_twins]
    stalled = False
    while not stalled:

        stall_values_before = \
            len([box for box in values.keys() if len(values[box]) == 1]) \
            if stall_check == STALL_BOXES else \
            len(''.join([chars for chars in values.values()]))

        # call each of the reduction strategies in turn
        for strategy in strategies:
            values = trace_step(strategy, values)
            if is_solved(values):
                return values

        stall_values_after = \
            len([box for box in values.keys() if len(values[box]) == 1]) \
            if stall_check == STALL_BOXES else \
            len(''.join([chars for chars in values.values()]))

        stalled = stall_values_before == stall_values_after

        # If any box has no possible values then we've failed to fine a solution
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False

    return values

def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    assert len(values) == len(boxes), "The values and boxes have different lengths."

    # First, reduce the puzzle using the previous function
    result = reduce_puzzle(values)
    if result == False:
        return False
    
    # Chose one of the unfilled square s with the fewest possibilities
    remaining = [box for box in values if len(values[box]) > 1]
    if len(remaining) < 1:
        return result

    minBox = min(remaining, key=lambda x: len(values[x]))
    
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), 
    # return that answer!
    for c in values[minBox]:
        d = dict(values)
        #d[minBox] = c
        assign_value(d, minBox, c)
        logging.info('Recurse: ' + minBox + ' = ' + c)
        result = search(d)
        if is_solved(result):
            return result
        logging.info('Failed recursing: ' + minBox + ' = ' + c)
            
    return False

def solve(grid, unit_list=project_unitlist, stallcheck=STALL_BOXES, log_level=logging.WARN):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
        unit_list: the list of units to use for this puzzle. NOTE: each box must be in at least one unit
        log_level: set to logging.WARN by default. Set to logging.INFO to see a trace of the steps
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    # verify that each of the boxes is in at least one unit
    unitsListBoxes = set([box for unit in unit_list for box in unit])
    assert len(unitsListBoxes) == len(boxes), "Each box must appear in at least one unit"
    global unitlist
    unitlist = unit_list

    # set up the logging
    logging.basicConfig(level=log_level)

    logging.info('Start: ' + grid)

    logging.info('Stall checking: ' + ('boxes' if stallcheck == STALL_BOXES else 'values'))
    global stall_check
    stall_check = stallcheck

    result = search(grid_values(grid))

    if (result == False):
        logging.warn('Failed to find solution.')
    else:
        end_grid = ''.join([result[str(r)+str(c)] for r in rows for c in cols])
        logging.info('End  : ' + end_grid)

    return result

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid, stallcheck=STALL_VALUES, log_level=logging.INFO))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
