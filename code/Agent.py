# -------------------------------------------------------------

# This program solves Blocks World problem using four algorithms:
# - Depth first search
# - Breadth first search
# - Best first search
# - A*

# Author: Nikolaos Nikolaidis (ics23080)
# --------------------------------------------------------------

'''
My implementation feathures the list as a data structure to store the blocks in the piles.

for example:

[A, B, C] is a pile with block C on top, B in the middle and A on the bottom.

[[A, B, C], [D], [E, F]] is the state of the blocks world with three piles. The first pile has blocks C, B, A, 
the second pile has block D and the third pile has blocks F, E.
'''


import os
import time

# Node class representing each state in the search tree
class TreeNode:
    def __init__(self):
        self.state = None        # Current state of the blocks
        self.parent = None       # Parent node
        self.g = 0               # Cost to reach this node (for A* search)
        self.h = 0               # Heuristic estimate (for A* and Best-First Search)
        self.f = 0               # Total estimated cost (g + h)
        self.action = None       # Action that led to this state

# Class representing a node in the frontier (linked list for frontier management)
class Frontier:
    def __init__(self):
        self.next = None         # Pointer to the next node in the frontier
        self.node = None         # TreeNode stored at this frontier node

# Parse the input file to extract objects, initial state, and goal state
# Input: filename (string)
# Output: list of objects, initial state, and goal state

def parse_blocks_file(filename):
    with open(filename, "r") as file:
        file.readline()  # Skip the first two lines
        file.readline()
        
        # Parse objects section
        ob_string = ""
        line = ""
        while True:
            line = file.readline()
            if ":INIT" in line:
                break
            ob_string += line.strip() + " "            
        objects = ob_string.replace("(:objects", "").replace(")", "").split()

        # Parse initial state
        # h variable is a list of lists that represent the piles of blocks [ [A, B, C], [D], [E, F] ]
        # The blocks are placed in a dictionary A:B, B:C, D:E where the key is the block and the value is the block that is on top of it
        in_string = line.strip() + " "
        while True:
            if "(HANDEMPTY)" in line:
                break
            line = file.readline()
            in_string += line.strip() + " "
        in_string = in_string.replace("(:INIT", "").replace("(HANDEMPTY))", "")
        top = []
        on_dict = {}
        
        in_string = in_string.strip()
        for part in in_string.split(")"):
            part = part.strip()
            if part == "":
                continue
            if part.startswith("(CLEAR"):
                continue
            elif part.startswith("(ONTABLE"):
                _, obj = part.replace("(", "").replace(")", "").split()
                top.append(obj)
            elif part.startswith("(ON"):
                _, above, below = part.replace("(", "").replace(")", "").split()
                on_dict[below] = above
                
        # We are using the dictionary to create the piles of blocks
        h = []
        for base in top:
            stack = [base]
            while stack[-1] in on_dict:
                stack.append(on_dict[stack[-1]])
            h.append(stack)
        
        # Parse goal state
        # Same as above
        goal_string = ""
        while True:
            line = file.readline()
            if not line:
                break
            goal_string += line.strip() + " "
        goal_string = goal_string.replace("(:goal (AND", "").replace("))", "").strip()
        goal = []
        first = True
        for part in goal_string.split(")"):
            part = part.strip()
            if part.startswith("(ON"):
                _, above, below = part.replace("(", "").replace(")", "").split()
                
                if first:
                    goal.append(above)
                    first = False      
                goal.append(below)       
        goal.reverse()

        return objects, h, goal

# Helper function to determine which blocks are clear (nothing on top)
def get_clear(state):
    l = []
    for i in range(len(state)):
        l.append(state[i][-1])  # Last block in each pile is clear
    return l

# Heuristic function for estimating the cost to reach the goal from the current state
# We take every block in EVERY pile and calculate the distance from its current position to its goal position
# We sum all these distances to get the heuristic value
# It calls the manhattan distance as many times as the number of blocks in the state
def heuristic(state, goal):
    pile = -1
    h = 0
    for structure in state:
        pile += 1
        index = -1
        for _ in structure:
            index += 1
            h += manhattan_distance(pile, index, state, goal)

    return h

# Calculates Manhattan distance (number of misplaced blocks)
# For a single block (index) in a pile (pile), it calculates the distance based on the blocks on the bottom of the pile
def manhattan_distance(pile, index, state, goal):
    list_goal = []
    list_current = []
    for i in range(len(goal)):
        if goal[i] == state[pile][index]:
            break
        list_goal.append(goal[i])
    for i in range(0, index):
        list_current.append(state[pile][i])
        
    # Negative value means the block is in the correct position

    if list_current == list_goal:
        return -len(list_current)
    else:
        return len(list_current)

# Compares two states to check if they are equal (used for goal checking)
def check_if_equals(s1, s2):
    if len(s1) != len(s2):
        return False

    sorted_list1 = sorted(s1, key=lambda x: x)
    sorted_list2 = sorted(s2, key=lambda x: x)

    return sorted_list1 == sorted_list2

# Checks if a node's state matches any of its parent states (cycle prevention)
def check_with_parents(new_node):
    parent = new_node.parent
    while parent is not None:
        if check_if_equals(new_node.state, parent.state):
            return False
        parent = parent.parent
    return True   

# Checks if the current state is the solution (goal state achieved)
def is_solution(state, goal):
    temp_goal = []
    temp_goal.append(goal)
    return check_if_equals(state, temp_goal)

# Maps method strings to corresponding search algorithms (1 = BFS, 2 = DFS, 3 = Best-First, 4 = A*)
def get_method(string):
	if string == "breadth":
		return 1
	elif string == "depth":
		return 2
	elif string == "best":
		return 3
	elif string == "astar":
		return 4
	else:
		return -1

"""
    Writes the actions leading to the solution into a file, starting from the root to the solution.
    The output file name is based on the input file name.
"""
def write_solution_to_file(solution_node, input_filename, method_string):
    output_filename = input_filename.replace(".txt", f"-output-{method_string}.txt")
    actions = []
    current = solution_node

    while current is not None:
        if current.action is not None:  # Exclude the root node as it has no action
            actions.append(current.action)
        current = current.parent

    # Reverse actions to write them from the root to the solution
    actions.reverse()

    with open(output_filename, "w") as file:
        for action in actions:
            file.write(action + "\n")

    print(f"Solution actions have been written to '{output_filename}'.")

def initialize_search(state, method, goal):
    # Initialize the search by creating the root node
    root = TreeNode()
    root.state = state
    root.g = 0  # Cost from start to current node
    root.h = heuristic(state, goal)  # Heuristic estimate to goal

    # Set f value based on the selected method
    if method == 3:  # Best-First Search
        root.f = root.h
    elif method == 4:  # A* Search
        root.f = root.g + root.h
    else:
        root.f = 0  # For Breadth-First and Depth-First Search
        
    add_frontier_front(root)  # Add root to the frontier

# Add node to the front of the frontier (for DFS)
def add_frontier_front(node):
    global frontier_head
    new_frontier = Frontier()
    new_frontier.node = node
    new_frontier.next = frontier_head
    frontier_head = new_frontier

# Add node to the back of the frontier (for BFS)
def add_frontier_back(node):
    global frontier_head
    new_frontier = Frontier()
    new_frontier.node = node
    new_frontier.next = None

    # If frontier is empty, set head to new node
    if frontier_head is None:
        frontier_head = new_frontier
    else:
        # Traverse to the end and add the node
        current = frontier_head
        while current.next is not None:
            current = current.next
        current.next = new_frontier

# Add node to the frontier in order (for Best-First and A*)
def add_frontier_in_order(node):
    global frontier_head
    new_frontier = Frontier()
    new_frontier.node = node
    new_frontier.next = None

    # If the frontier is empty, insert as head
    if frontier_head is None:
        frontier_head = new_frontier
        return

    # Insert node at appropriate position based on f and h values
    if (node.f < frontier_head.node.f) or (node.f == frontier_head.node.f and node.h < frontier_head.node.h):
        new_frontier.next = frontier_head
        frontier_head = new_frontier
        return

    # Traverse and insert in sorted order
    current = frontier_head
    while (current.next is not None and (current.next.node.f < node.f or \
        (current.next.node.f == node.f and current.next.node.h < node.h))):
        current = current.next
    
    new_frontier.next = current.next
    current.next = new_frontier    

# Find all possible children nodes from the current state
def find_children(current_node, method):
    clear_blocks = get_clear(current_node.state)  # Get blocks that can be moved
    children_created = False

    # Loop through each clear block to generate new states
    for i, block in enumerate(clear_blocks):
        origin = "table" if len(current_node.state[i]) == 1 else current_node.state[i][-2]  # Determine origin for state field
        # the minus 2 is to get the block that is on bottom of the block that is being moved (because the block on top is -1)
        
        # Move block to table (new pile) if len is one that means that its already on the table
        if len(current_node.state[i]) > 1:
            new_state = [pile[:] for pile in current_node.state]  # Deep copy state
            new_state[i].pop()  # Remove block from current pile
            new_state.append([block])  # Place block on table
            new_state = [pile for pile in new_state if pile]  # Remove empty piles
            
            action = f"Move({block}, {origin}, table)"
            if create_and_add_child(current_node, new_state, action, method):
                children_created = True

        # Move block to another pile
        for j, target in enumerate(clear_blocks):
            if i != j:
                new_state = [pile[:] for pile in current_node.state]  # Deep copy state
                new_state[i].pop()  # Remove block from current pile
                new_state[j].append(block)  # Place block on target pile
                new_state = [pile for pile in new_state if pile]  # Remove empty piles

                action = f"Move({block}, {origin}, {target})"
                if create_and_add_child(current_node, new_state, action, method):
                    children_created = True

    return children_created

# Keep track of visited states to avoid cycles
visited_states = set()

# Normalize state for consistent comparison and hashing
def normalize_state(state):
    return tuple(tuple(pile) for pile in sorted(state, key=lambda x: (len(x), x)))

# Create a child node and add it to the frontier if not visited
def create_and_add_child(parent_node, new_state, action, method):
    global visited_states
    
    normalized_state = normalize_state(new_state)
    if normalized_state in visited_states:
        return False  # Skip if already visited
    
    # Create child node
    child_node = TreeNode()
    child_node.state = new_state
    child_node.parent = parent_node
    child_node.action = action
    child_node.g = parent_node.g + 1  # Increment cost
    child_node.h = heuristic(new_state, goal)  # Heuristic estimate

    # Set f value based on method
    if method == 3:  # Best-First Search
        child_node.f = child_node.h
    elif method == 4:  # A* Search
        child_node.f = child_node.g + child_node.h
    else:
        child_node.f = 0  # For BFS and DFS

    # Mark state as visited and add to frontier
    visited_states.add(normalized_state)
    if method == 1:
        add_frontier_back(child_node)
    elif method == 2:
        add_frontier_front(child_node)
    elif method in (3, 4):
        add_frontier_in_order(child_node)
    
    return True

# Main search function
def search(method):
    global frontier_head
    start_time = time.time()  # Start timer

    while frontier_head is not None:
        # Check if search exceeds time limit
        elapsed_time = time.time() - start_time
        if elapsed_time > 60:
            print("Search timed out after 60 seconds.")
            return None

        current_node = frontier_head.node

        # Check if solution is found
        if is_solution(current_node.state, goal):
            print(f"Solution found in {elapsed_time:.2f} seconds.")
            return current_node

        frontier_head = frontier_head.next  # Remove node from frontier

        find_children(current_node, method)  # Generate children

    print("No solution found.")
    return None   

# Debugging function to print frontier size
# def debug():
#     if frontier_head is None:
#         print("The frontier is empty.")
#         return
    
#     current = frontier_head
#     count = 1
#     while current is not None:
#         current = current.next
#         count += 1

# Validate filename input and check existence
def get_valid_filename():
    while True:
        filename = input("Enter the filename (with or without .txt): ").strip()
        if not filename.endswith(".txt"):
            filename += ".txt"
        if not os.path.exists(filename):
            print(f"Error: File '{filename}' does not exist. Please try again.")
        else:
            return filename


#---------- MAIN ----------#
try:
    filename = get_valid_filename()
except Exception as e:
    print(f"An error occurred: {e}")
    exit()

objects, s, goal = parse_blocks_file(filename)
solution_node = None
frontier_head = None
method_string = input("Select method: breadth, depth, best, astar: ").strip().lower()
method = get_method(method_string)

if method == -1:
    print("Invalid method.")
    exit()

initialize_search(s, method, goal)
start_time = time.time()
solution_node = search(method)
end_time = time.time()

if solution_node:
    print(f"Total search time: {end_time - start_time:.2f} seconds.")
    write_solution_to_file(solution_node, filename, method_string)
else:
    print("No solution found to write to file.")

# optional print
# def print_result(solution_node):
#     print(solution_node.state)
#     parent = solution_node.parent
#     while parent is not None:
#         print(parent.state)
#         parent = parent.parent


# print_result(solution_node)