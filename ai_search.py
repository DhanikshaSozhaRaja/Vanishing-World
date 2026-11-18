from collections import deque
import heapq
from rules import (
    create_initial_state,
    get_legal_moves,
    move_state,
    is_goal_state,
    get_exit_tile,
)


class SearchLimitReached(Exception):
    """Raised when a search exceeds its allowed node budget."""

    def __init__(self, nodes_explored):
        self.nodes_explored = nodes_explored
        super().__init__("Search node limit reached")


def check_search_limit(nodes_explored, max_nodes):
    if max_nodes is not None and nodes_explored >= max_nodes:
        raise SearchLimitReached(nodes_explored)


# bfs
def bfs_search(start_state=None, max_nodes=None):
    """Find a solution using Breadth-First Search."""

    if start_state is None:
        start_state = create_initial_state()

    # Queue stores states waiting to be explored.
    queue = deque([start_state])

    # Store visited states to avoid repeated exploration.
    visited = {start_state}

    # Store each state's parent and the move used to reach it.
    parent = {
        start_state: None
    }

    # Count how many states are explored.
    nodes_explored = 0

    while queue:

        current_state = queue.popleft()
        nodes_explored += 1

        # Check whether the goal has been reached.
        if is_goal_state(current_state):
            path = []

            # Trace backwards from the goal to the start.
            state = current_state

            while parent[state] is not None:
                previous_state, direction = parent[state]
                path.append(direction)
                state = previous_state

            # Reverse to get the moves from start to goal.
            path.reverse()

            return path, nodes_explored

        check_search_limit(nodes_explored, max_nodes)

        # A lost state cannot lead to a solution.
        if current_state[3] == "lost":
            continue

        # Explore every legal move from this state.
        for direction in get_legal_moves(current_state):

            next_state = move_state(
                current_state,
                direction
            )

            if next_state is None:
                continue

            if next_state in visited:
                continue

            # Ignore states that end in a loss.
            if next_state[3] == "lost":
                continue

            visited.add(next_state)

            parent[next_state] = (
                current_state,
                direction
            )

            queue.append(next_state)

    # The queue is empty: no solution was found.
    return None, nodes_explored


# dfs
def dfs_search(start_state=None, max_nodes=None):
    """Find a solution using Depth-First Search."""

    if start_state is None:
        start_state = create_initial_state()

    # Stack stores states waiting to be explored.
    stack = [start_state]

    visited = {start_state}

    # Remember the previous state and direction.
    parent = {
        start_state: None
    }

    nodes_explored = 0

    while stack:

        current_state = stack.pop()
        nodes_explored += 1

        # Check whether the goal has been reached.
        if is_goal_state(current_state):

            path = []
            state = current_state

            while parent[state] is not None:
                previous_state, direction = parent[state]
                path.append(direction)
                state = previous_state

            path.reverse()

            return path, nodes_explored
        check_search_limit(nodes_explored, max_nodes)

        # Do not expand losing states.
        if current_state[3] == "lost":
            continue

        # Explore legal moves.
        for direction in get_legal_moves(current_state):

            next_state = move_state(
                current_state,
                direction
            )

            if next_state is None:
                continue

            if next_state in visited:
                continue

            if next_state[3] == "lost":
                continue

            visited.add(next_state)

            parent[next_state] = (
                current_state,
                direction
            )

            stack.append(next_state)

    return None, nodes_explored


# iddfs

def iddfs_search(max_depth=25, start_state=None, max_nodes=None):
    """Find a solution using Iterative Deepening DFS."""

    if start_state is None:
        start_state = create_initial_state()
    total_nodes_explored = 0

    # Increase the depth limit after each search.
    for depth_limit in range(max_depth + 1):

        visited = set()

        def depth_limited_search(state, depth, path):
            nonlocal total_nodes_explored

            total_nodes_explored += 1

            # Check for a winning state.
            if is_goal_state(state):
                return path
            check_search_limit(total_nodes_explored, max_nodes)

            # Stop if the depth limit is reached.
            if depth >= depth_limit:
                return None

            # Do not explore losing states.
            if state[3] == "lost":
                return None

            # Avoid exploring the same state repeatedly
            # during this depth-limit iteration.
            if state in visited:
                return None

            visited.add(state)

            for direction in get_legal_moves(state):

                next_state = move_state(state, direction)

                if next_state is None:
                    continue

                if next_state[3] == "lost":
                    continue

                result = depth_limited_search(
                    next_state,
                    depth + 1,
                    path + [direction]
                )

                if result is not None:
                    return result

            return None

        solution = depth_limited_search(
            start_state,
            0,
            []
        )

        if solution is not None:
            return solution, total_nodes_explored

    return None, total_nodes_explored


# greedy best first search

def manhattan_distance(position1, position2):
    """Calculate the Manhattan distance between two positions."""
    return (
        abs(position1[0] - position2[0])
        + abs(position1[1] - position2[1])
    )


def greedy_heuristic(state):
    """Estimate the distance to remaining crystals and the exit."""

    player, vanished, crystals, status = state
    exit_tile = get_exit_tile()

    if not crystals:
        return manhattan_distance(player, exit_tile)

    targets = list(crystals) + [exit_tile]
    current_position = player
    total_distance = 0

    while targets:
        nearest_target = min(
            targets,
            key=lambda target: manhattan_distance(
                current_position, target
            )
        )

        total_distance += manhattan_distance(
            current_position, nearest_target
        )

        current_position = nearest_target
        targets.remove(nearest_target)

    return total_distance


def greedy_search(start_state=None, max_nodes=None):
    """Find a solution using Greedy Best-First Search."""

    if start_state is None:
        start_state = create_initial_state()

    # Each entry contains heuristic score, tie-breaker, and state.
    counter = 0
    priority_queue = [
        (greedy_heuristic(start_state), counter, start_state)
    ]

    visited = {start_state}
    parent = {start_state: None}
    nodes_explored = 0

    while priority_queue:

        _, _, current_state = heapq.heappop(priority_queue)
        nodes_explored += 1

        if is_goal_state(current_state):
            path = []
            state = current_state

            while parent[state] is not None:
                previous_state, direction = parent[state]
                path.append(direction)
                state = previous_state

            path.reverse()
            return path, nodes_explored

        check_search_limit(nodes_explored, max_nodes)

        if current_state[3] == "lost":
            continue

        for direction in get_legal_moves(current_state):

            next_state = move_state(current_state, direction)

            if next_state is None:
                continue

            if next_state in visited:
                continue

            if next_state[3] == "lost":
                continue

            visited.add(next_state)

            parent[next_state] = (current_state, direction)

            counter += 1

            score = greedy_heuristic(next_state)

            heapq.heappush(
                priority_queue,
                (score, counter, next_state)
            )

    return None, nodes_explored


# A* search

def a_star_heuristic(state):
    """Estimate a lower bound on the remaining distance."""

    player, vanished, crystals, status = state
    exit_tile = get_exit_tile()

    targets = list(crystals) + [exit_tile]

    if not targets:
        return 0

    distances = [
        manhattan_distance(player, target)
        for target in targets
    ]

    return max(distances)

def a_star_search(start_state=None, max_nodes=None):
    """Find a solution using A* Search."""

    if start_state is None:
        start_state = create_initial_state()
    counter = 0

    # Store: f-score, tie-breaker, g-score, state.
    priority_queue = [
        (
            a_star_heuristic(start_state),
            counter,
            0,
            start_state
        )
    ]

    # Store the lowest known cost to reach each state.
    g_score = {start_state: 0}

    # Remember the previous state and the move used.
    parent = {start_state: None}

    nodes_explored = 0

    while priority_queue:

        f_score, _, current_g, current_state = (
            heapq.heappop(priority_queue)
        )

        # Ignore an outdated queue entry.
        if current_g != g_score.get(current_state):
            continue

        nodes_explored += 1

        # Check whether the puzzle is solved.
        if is_goal_state(current_state):

            path = []
            state = current_state

            while parent[state] is not None:
                previous_state, direction = parent[state]
                path.append(direction)
                state = previous_state

            path.reverse()

            return path, nodes_explored

        check_search_limit(nodes_explored, max_nodes)

        # A losing state cannot lead to a solution.
        if current_state[3] == "lost":
            continue

        # Explore all legal moves.
        for direction in get_legal_moves(current_state):

            next_state = move_state(
                current_state,
                direction
            )

            if next_state is None:
                continue

            if next_state[3] == "lost":
                continue

            # Every move has a cost of 1.
            new_g_score = current_g + 1

            # Update only if this route is cheaper.
            if new_g_score < g_score.get(
                next_state, float("inf")
            ):

                g_score[next_state] = new_g_score

                parent[next_state] = (
                    current_state,
                    direction
                )

                h_score = a_star_heuristic(next_state)
                new_f_score = new_g_score + h_score

                counter += 1

                heapq.heappush(
                    priority_queue,
                    (
                        new_f_score,
                        counter,
                        new_g_score,
                        next_state
                    )
                )

    # No solution was found.
    return None, nodes_explored



def evaluate_move_quality(state, direction):
    """Evaluate a move without allowing unlimited search."""

    from rules import move_state, ROWS, COLS

    # Reduce the analysis budget as the board grows.
    board_size = max(ROWS, COLS)

    if board_size <= 5:
        max_nodes = 5000
    elif board_size <= 7:
        max_nodes = 2500
    elif board_size <= 9:
        max_nodes = 1000
    else:
        max_nodes = 400

    try:
        # Find the best path before the move.
        original_path, _ = a_star_search(
            start_state=state,
            max_nodes=max_nodes,
        )

        if original_path is None:
            return {
                "quality": "NO WINNING PATH",
                "accuracy": 0,
                "remaining_moves": None,
            }

        # Reject illegal moves before evaluating them.
        if direction not in get_legal_moves(state):
            return {
                "quality": "INVALID MOVE",
                "accuracy": 0,
                "remaining_moves": None,
            }

        next_state = move_state(state, direction)

        if next_state is None or next_state[3] == "lost":
            return {
                "quality": "LOSING MOVE",
                "accuracy": 0,
                "remaining_moves": None,
            }

        if next_state[3] == "won":
            return {
                "quality": "OPTIMAL",
                "accuracy": 100,
                "remaining_moves": 0,
            }

        # Evaluate the position after the move.
        next_path, _ = a_star_search(
            start_state=next_state,
            max_nodes=max_nodes,
        )

        if next_path is None:
            return {
                "quality": "NO WINNING PATH",
                "accuracy": 0,
                "remaining_moves": None,
            }

        best_total_moves = len(original_path)
        actual_total_moves = 1 + len(next_path)

        if actual_total_moves <= best_total_moves:
            quality = "OPTIMAL"
            accuracy = 100
        else:
            quality = "SUBOPTIMAL"
            extra_moves = actual_total_moves - best_total_moves
            accuracy = max(0, round(100 / (1 + extra_moves)))

        return {
            "quality": quality,
            "accuracy": accuracy,
            "remaining_moves": len(next_path),
        }

    except SearchLimitReached:
        return {
            "quality": "ANALYSIS LIMIT REACHED",
            "accuracy": None,
            "remaining_moves": None,
        }



if __name__ == "__main__":

    print("Running A* Search...")

    solution, nodes_explored = a_star_search()

    print("Nodes explored:", nodes_explored)

    if solution is None:
        print("No solution found for the current level.")
    else:
        print("Solution found!")
        print("Number of moves:", len(solution))
        print("Moves:", solution)
