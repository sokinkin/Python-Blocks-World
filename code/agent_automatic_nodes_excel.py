import os
import time
import pandas as pd
# List of filenames to test
# This python file counts the number of nodes the solution has and outputs it to an excel file

filenames = [
    "probBLOCKS-4-0.txt", "probBLOCKS-4-1.txt", "probBLOCKS-4-2.txt",
    "probBLOCKS-5-0.txt", "probBLOCKS-5-1.txt", "probBLOCKS-5-2.txt",
    "probBLOCKS-6-0.txt", "probBLOCKS-6-1.txt", "probBLOCKS-6-2.txt",
    "probBLOCKS-7-0.txt", "probBLOCKS-7-1.txt", "probBLOCKS-7-2.txt",
    "probBLOCKS-8-0.txt", "probBLOCKS-8-1.txt", "probBLOCKS-8-2.txt",
    "probBLOCKS-9-0.txt", "probBLOCKS-9-1.txt", "probBLOCKS-9-2.txt",
]


# filenames = [
#     "probBLOCKS-10-0.txt", "probBLOCKS-10-1.txt", "probBLOCKS-10-2.txt",
#     "probBLOCKS-11-0.txt", "probBLOCKS-11-1.txt", "probBLOCKS-11-2.txt",
#     "probBLOCKS-12-0.txt", "probBLOCKS-12-1.txt",
#     "probBLOCKS-13-0.txt", "probBLOCKS-13-1.txt",
#     "probBLOCKS-14-0.txt", "probBLOCKS-14-1.txt",
#     "probBLOCKS-15-0.txt", "probBLOCKS-15-1.txt",
#     "probBLOCKS-16-1.txt", "probBLOCKS-16-2.txt",
#     "probBLOCKS-17-0.txt", "probBLOCKS-17-1.txt",
# ]

# filenames = [
#     "probBLOCKS-18-0.txt", "probBLOCKS-18-1.txt",
#     "probBLOCKS-19-0.txt", "probBLOCKS-19-1.txt",
#     "probBLOCKS-20-0.txt", "probBLOCKS-20-1.txt",
#     "probBLOCKS-25-0.txt", "probBLOCKS-25-1.txt",
#     "probBLOCKS-28-0.txt", "probBLOCKS-28-1.txt",
#     "probBLOCKS-30-0.txt", "probBLOCKS-30-1.txt",
#     "probBLOCKS-35-0.txt", "probBLOCKS-35-1.txt",
#     "probBLOCKS-40-0.txt", "probBLOCKS-40-1.txt",
#     "probBLOCKS-45-0.txt", "probBLOCKS-45-1.txt",
#     "probBLOCKS-50-0.txt", "probBLOCKS-50-1.txt",
#     "probBLOCKS-55-0.txt", "probBLOCKS-55-1.txt",
#     "probBLOCKS-60-0.txt", "probBLOCKS-60-1.txt"
    
# ]

methods = ["breadth", "depth", "best", "astar"]

results = []

class TreeNode:
    def __init__(self):
        self.state = None
        self.parent = None
        self.g = 0
        self.h = 0
        self.f = 0
        self.action = None

class Frontier:
    def __init__(self):
        self.next = None
        self.node = None

def parse_blocks_file(filename):
    with open(filename, "r") as file:
        file.readline()
        file.readline()
        
        # --------------------------- objects
        ob_string = ""
        line = ""
        while True:
            line = file.readline()
            if ":INIT" in line:
                break
            ob_string += line.strip() + " "            
        objects = ob_string.replace("(:objects", "").replace(")", "").split()

        # --------------------------- current
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
        h = []
        for base in top:
            stack = [base]
            while stack[-1] in on_dict:
                stack.append(on_dict[stack[-1]])
            h.append(stack)
        
        #----------------------------------------- goal
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

def get_clear(state):
    l = []
    for i in range(len(state)):
        l.append(state[i][-1])
    return l

def heuristic(state, goal):
    pile = -1
    h = 0
    for structure in state:
        pile = pile + 1
        index = -1
        for _ in structure:
            index = index + 1
            h = h + manhattan_distance(pile, index, state, goal)

    return h

def manhattan_distance(pile, index, state, goal):
    list_goal = []
    list_current = []
    for i in range(len(goal)):
        if goal[i] == state[pile][index]:
            break
        list_goal.append(goal[i])
    for i in range(0, index):
        list_current.append(state[pile][i])

    if list_current == list_goal:
        return -len(list_current)
    else:
        return len(list_current)

def check_if_equals(s1, s2):
    if len(s1) != len(s2):
        return False

    sorted_list1 = sorted(s1, key=lambda x: x)
    sorted_list2 = sorted(s2, key=lambda x: x)

    return sorted_list1 == sorted_list2

def check_with_parents(new_node):
    parent = new_node.parent
    while parent is not None:
        if check_if_equals(new_node.state, parent.state):
            return False
        parent = parent.parent
    return True   

def is_solution(state, goal):
    temp_goal = []
    temp_goal.append(goal)
    return check_if_equals(state, temp_goal)
      
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

def write_solution_to_file(solution_node, input_filename, method_string):
    """
    Writes the actions leading to the solution into a file, starting from the root to the solution.
    The output file name is based on the input file name.
    """
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
    root = TreeNode()
    root.state = state
    root.g = 0
    root.h = heuristic(state, goal)

    if method == 3:
        root.f = root.h
    elif method == 4:
        root.f = root.g + root.h
    else:
        root.f = 0
        
    add_frontier_front(root)
    
def add_frontier_front(node):
    global frontier_head
    new_frontier = Frontier()
    new_frontier.node = node
    new_frontier.next = frontier_head
    frontier_head = new_frontier
    
def add_frontier_back(node):
    global frontier_head
    new_frontier = Frontier()
    new_frontier.node = node
    new_frontier.next = None
    
    if frontier_head is None:
        frontier_head = new_frontier
    else:
        current = frontier_head
        while current.next is not None:
            current = current.next
        current.next = new_frontier

def add_frontier_in_order(node):
    global frontier_head
    new_frontier = Frontier()
    new_frontier.node = node
    new_frontier.next = None
    
    if frontier_head is None:
        frontier_head = new_frontier
        return
    
    if (node.f < frontier_head.node.f) or (node.f == frontier_head.node.f and node.h < frontier_head.node.h):
        new_frontier.next = frontier_head
        frontier_head = new_frontier
        return
    
    current = frontier_head
    while (current.next is not None and (current.next.node.f < node.f or \
        (current.next.node.f == node.f and current.next.node.h < node.h))):
        current = current.next
    
    new_frontier.next = current.next
    current.next = new_frontier    

def find_children(current_node, method):
    clear_blocks = get_clear(current_node.state)
    children_created = False

    for i, block in enumerate(clear_blocks):
        # Determine the origin BEFORE modifying the state
        origin = "table" if len(current_node.state[i]) == 1 else current_node.state[i][-2]
        
        if len(current_node.state[i]) > 1:
            new_state = [pile[:] for pile in current_node.state]
            new_state[i].pop()
            new_state.append([block])

            new_state = [pile for pile in new_state if pile]

            action = f"Move({block}, {origin}, table)"
            if create_and_add_child(current_node, new_state, action, method):
                children_created = True

        for j, target in enumerate(clear_blocks):
            if i != j:
                new_state = [pile[:] for pile in current_node.state]
                new_state[i].pop()
                new_state[j].append(block)

                new_state = [pile for pile in new_state if pile]

                action = f"Move({block}, {origin}, {target})"
                if create_and_add_child(current_node, new_state, action, method):
                    children_created = True

    return children_created

visited_states = set()

def normalize_state(state):
    return tuple(tuple(pile) for pile in sorted(state, key=lambda x: (len(x), x)))

def create_and_add_child(parent_node, new_state, action, method):
    global visited_states
    
    normalized_state = normalize_state(new_state)
    if normalized_state in visited_states:
        return False  # Already visited, skip this state
    
    # Create the new child node
    child_node = TreeNode()
    child_node.state = new_state
    child_node.parent = parent_node
    child_node.action = action
    child_node.g = parent_node.g + 1
    child_node.h = heuristic(new_state, goal)

    # Compute f based on the method
    if method == 3:  # Best-First Search
        child_node.f = child_node.h
    elif method == 4:  # A* Search
        child_node.f = child_node.g + child_node.h
    else:
        child_node.f = 0  # For BFS and DFS

    # Add the state to the visited set and frontier
    visited_states.add(normalized_state)
    if method == 1:
        add_frontier_back(child_node)
    elif method == 2:
        add_frontier_front(child_node)
    elif method in (3, 4):
        add_frontier_in_order(child_node)
    
    return True

        
def search(method):
    global frontier_head

    start_time = time.time()  # Start the timer

    while frontier_head is not None:
        # Check if time has exceeded 60 seconds
        elapsed_time = time.time() - start_time
        if elapsed_time > 60:
            print("Search timed out after 60 seconds.")
            return None

        current_node = frontier_head.node

        # Check if the current node is a solution
        if is_solution(current_node.state, goal):
            print(f"Solution found in {elapsed_time:.2f} seconds.")
            return current_node

        # Remove the first node of the frontier
        frontier_head = frontier_head.next

        # Attempt to find children for the current node
        find_children(current_node, method)

    print("No solution found.")
    return None   
        
def debug():
    if frontier_head is None:
        print("The frontier is empty.")
        return
    
    current = frontier_head
    count = 1
    while current is not None:
        current = current.next
        count += 1

def get_valid_filename():
    while True:
        filename = input("Enter the filename (with or without .txt): ").strip()

        # Add .txt if missing
        if not filename.endswith(".txt"):
            filename += ".txt"

        # Check if file exists
        if not os.path.exists(filename):
            print(f"Error: File '{filename}' does not exist. Please try again.")
        else:
            return filename

methods = ["breadth", "depth", "best", "astar"]

results_data = []
results = []


def count_solution_nodes(solution_node):
    count = 0
    current = solution_node
    while current is not None:
        count += 1
        current = current.parent
    return count

for filename in filenames:
    if not os.path.exists(filename):
        print(f"File {filename} not found. Skipping.")
        continue

    row_data = {'Problem': filename}

    for method_string in methods:
        print(f"Running {method_string} search on {filename}...")

        objects, s, goal = parse_blocks_file(filename)
        solution_node = None
        frontier_head = None
        visited_states.clear()

        method = get_method(method_string)

        initialize_search(s, method, goal)

        solution_node = search(method)
        
        if solution_node:
            nodes_generated = count_solution_nodes(solution_node)
        else:
            nodes_generated = 0
        
        row_data[method_string] = nodes_generated

    results_data.append(row_data)

# Save results to Excel
output_df = pd.DataFrame(results_data)
output_df.to_excel('3_nodes.xlsx', index=False)