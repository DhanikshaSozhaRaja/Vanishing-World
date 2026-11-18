import time
import rules

from ai_search import (
    bfs_search,
    dfs_search,
    iddfs_search,
    greedy_search,
    a_star_search,
    SearchLimitReached,
)

# Genuine measurements from AI runs already performed in the current level.
_SEARCH_RESULT_CACHE = {}


def clear_search_result_cache():
    """Clear measurements when a new game or level starts."""
    _SEARCH_RESULT_CACHE.clear()


def record_search_result(name, solution, nodes, elapsed_ms, status=None):
    """Record actual results from the search used for AI playback."""
    aliases = {
        "Greedy": "Greedy Best-First",
        "Greedy Best First": "Greedy Best-First",
        "A* Search": "A*",
    }
    name = aliases.get(name, name)
    if status is None:
        status = "Completed" if solution is not None else "No solution found"

    _SEARCH_RESULT_CACHE[name] = {
        "name": name,
        "moves": len(solution) if solution is not None else None,
        "nodes": nodes,
        "time": elapsed_ms,
        "path": " -> ".join(solution) if solution is not None else status,
        "status": status,
        "source": "Previously recorded AI run",
    }


def get_comparison_plan(rows, cols):
    """Choose suitable algorithms and node limits for this board."""
    size = max(rows, cols)

    if size <= 5:
        return {
            "BFS": (bfs_search, 10000),
            "DFS": (dfs_search, 10000),
            "IDDFS": (iddfs_search, 10000),
            "Greedy Best-First": (greedy_search, 10000),
            "A*": (a_star_search, 10000),
        }

    if size <= 7:
        return {
            "BFS": (bfs_search, 5000),
            "DFS": (dfs_search, 5000),
            "IDDFS": (iddfs_search, 5000),
            "Greedy Best-First": (greedy_search, 10000),
            "A*": (a_star_search, 10000),
        }

    if size <= 9:
        return {
            "BFS": None,
            "DFS": (dfs_search, 3000),
            "IDDFS": None,
            "Greedy Best-First": (greedy_search, 5000),
            "A*": (a_star_search, 5000),
        }

    return {
        "BFS": None,
        "DFS": None,
        "IDDFS": None,
        "Greedy Best-First": (greedy_search, 3000),
        "A*": (a_star_search, 3000),
    }


def compare_algorithms(start_state=None):
    """Compare algorithms using cached measurements where available."""
    if start_state is None:
        start_state = rules.create_initial_state()

    plan = get_comparison_plan(rules.ROWS, rules.COLS)
    results = []

    print("\nVANISHING WORLD - AI ALGORITHM COMPARISON")
    print("=" * 90)
    print(f"Board size: {rules.ROWS} x {rules.COLS}")

    for name, algorithm_plan in plan.items():
        # Reuse results from an AI run on this level.
        cached = _SEARCH_RESULT_CACHE.get(name)
        if cached is None and name == "Greedy Best-First":
            cached = _SEARCH_RESULT_CACHE.get("Greedy")

        if cached is not None:
            result = dict(cached)
            result["name"] = name
            results.append(result)
            print(f"{name}: reused previously recorded AI statistics")
            continue

        if algorithm_plan is None:
            result = {
                "name": name,
                "moves": None,
                "nodes": None,
                "time": None,
                "path": "Not run for this board size",
                "status": "Skipped — board too large for default comparison",
                "source": "Not run",
            }
            results.append(result)
            print(f"{name}: {result['status']}")
            continue

        search_function, node_limit = algorithm_plan
        print(f"\nRunning {name} (limit: {node_limit:,} explored states)...")

        start_time = time.perf_counter()
        solution = None
        nodes_explored = None
        status = "Not completed"

        try:
            solution, nodes_explored = search_function(
                start_state=start_state,
                max_nodes=node_limit,
            )
            status = "Completed" if solution is not None else "No solution found"
        except SearchLimitReached as error:
            nodes_explored = error.nodes_explored
            status = "Stopped — search limit reached"

        execution_time = (time.perf_counter() - start_time) * 1000
        moves = len(solution) if solution is not None else None

        result = {
            "name": name,
            "moves": moves,
            "nodes": nodes_explored,
            "time": execution_time,
            "path": " -> ".join(solution) if solution is not None else status,
            "status": status,
            "source": "Measured during comparison",
        }
        results.append(result)
        print(
            f"{name}: {status}; moves={moves}; nodes={nodes_explored}; "
            f"time={execution_time:.3f} ms"
        )

    print("\nFINAL RESULTS")
    print("=" * 100)
    print(f"{'Algorithm':<22}{'Moves':<12}{'Nodes':<14}{'Time (ms)':<15}Status")
    print("-" * 100)

    for result in results:
        moves_text = str(result["moves"]) if result["moves"] is not None else "—"
        nodes_text = str(result["nodes"]) if result["nodes"] is not None else "—"
        time_text = (
            f"{result['time']:.3f}" if result["time"] is not None else "—"
        )
        print(
            f"{result['name']:<22}{moves_text:<12}{nodes_text:<14}"
            f"{time_text:<15}{result['status']}"
        )

    successful = [
        result for result in results
        if result["moves"] is not None and result["status"] == "Completed"
    ]

    print("\nBEST SOLUTION FOUND")
    print("=" * 40)
    if successful:
        shortest = min(successful, key=lambda item: item["moves"])
        print("Algorithm:", shortest["name"])
        print("Moves:", shortest["moves"])
        print("Path:", shortest["path"])
        print("Note: shortest among completed solutions shown.")
    else:
        print("No completed search found a solution within its search budget.")

    print("\nComparison completed.")
    return results


if __name__ == "__main__":
    compare_algorithms()
