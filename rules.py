
import random
from collections import deque

# ----------------------------------------
# BOARD SETTINGS
# ----------------------------------------

ROWS = 5
COLS = 5

START_PLAYER = (0, 0)
START_CRYSTALS = frozenset([(0, 4), (2, 2), (4, 1)])
EXIT_TILE = (4, 4)

WALLS = set()
SPECIAL_TILES = set()
GUARANTEED_PATH = []

LEVEL_NUMBER = 1
CRYSTAL_COUNT = 3
DIFFICULTY = "MEDIUM"

# Board size, wall range and crystal count for each level tier.
LEVEL_SETTINGS = [
    (1, 3, 5, 3, 5, 3),
    (4, 6, 7, 8, 12, 4),
    (7, 9, 9, 16, 22, 5),
    (10, 12, 11, 26, 34, 6),
    (13, 999999, 13, 38, 50, 7),
]

# Difficulty modifies the wall density and route length.
DIFFICULTY_SETTINGS = {
    "EASY":   {"wall_factor": 0.75, "path_factor": 0.80},
    "MEDIUM": {"wall_factor": 1.00, "path_factor": 1.00},
    "HARD":   {"wall_factor": 1.25, "path_factor": 1.15},
}

DIRECTIONS = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1),
}


# ----------------------------------------
# LEVEL INFORMATION
# ----------------------------------------

def get_exit_tile():
    return EXIT_TILE


def get_start_crystals():
    return START_CRYSTALS


def get_level_number():
    return LEVEL_NUMBER


def get_difficulty():
    return DIFFICULTY


def get_special_tiles():
    return set(SPECIAL_TILES)


def get_level_settings(level):
    for first, last, size, wall_min, wall_max, crystals in LEVEL_SETTINGS:
        if first <= level <= last:
            return size, wall_min, wall_max, crystals

    return 13, 38, 50, 7


def set_difficulty(difficulty):
    global DIFFICULTY

    difficulty = difficulty.upper()

    if difficulty in DIFFICULTY_SETTINGS:
        DIFFICULTY = difficulty
        return True

    return False


def configure_board(level):
    """Set board dimensions and objective counts for a level."""
    global ROWS, COLS, CRYSTAL_COUNT

    size, _, _, crystal_count = get_level_settings(level)

    ROWS = size
    COLS = size
    CRYSTAL_COUNT = crystal_count


# ----------------------------------------
# GAME STATE
# ----------------------------------------

def create_initial_state():
    return (
        START_PLAYER,
        frozenset(),
        START_CRYSTALS,
        "playing"
    )


def inside_board(position):
    row, col = position
    return 0 <= row < ROWS and 0 <= col < COLS


# ----------------------------------------
# LEGAL MOVEMENT
# ----------------------------------------

def get_legal_moves(state):
    player, vanished, crystals, status = state

    if status != "playing":
        return []

    legal_moves = []

    for direction, (dr, dc) in DIRECTIONS.items():
        destination = (player[0] + dr, player[1] + dc)

        if not inside_board(destination):
            continue
        if destination in WALLS:
            continue
        if destination in vanished:
            continue

        legal_moves.append(direction)

    return legal_moves


def is_human_goal_state(state):
    player, vanished, crystals, status = state
    collected = len(START_CRYSTALS) - len(crystals)

    return player == EXIT_TILE and collected >= 1


def is_ai_goal_state(state):
    player, vanished, crystals, status = state

    return player == EXIT_TILE and len(crystals) == 0


def move_state(state, direction):
    player, vanished, crystals, status = state

    if status != "playing":
        return state

    if direction not in get_legal_moves(state):
        return state

    dr, dc = DIRECTIONS[direction]
    new_player = (player[0] + dr, player[1] + dc)

    # The tile being left disappears permanently.
    new_vanished = frozenset(set(vanished) | {player})

    # Collect a crystal when entering its tile.
    new_crystals = frozenset(
        crystal for crystal in crystals
        if crystal != new_player
    )

    new_status = "playing"

    if new_player == EXIT_TILE:
        if not new_crystals:
            new_status = "won"
        else:
            new_status = "lost"

    new_state = (
        new_player,
        new_vanished,
        new_crystals,
        new_status
    )

    if new_status == "playing" and not get_legal_moves(new_state):
        new_state = (
            new_player,
            new_vanished,
            new_crystals,
            "lost"
        )

    return new_state


def is_goal_state(state):
    player, vanished, crystals, status = state

    return (
        status == "won"
        and player == EXIT_TILE
        and len(crystals) == 0
    )


# ----------------------------------------
# PATH GENERATION
# ----------------------------------------

def create_fallback_path(target_length):
    """
    Create a safe, self-avoiding path by traversing rows
    in alternating directions.
    """
    full_path = []

    for row in range(ROWS):
        columns = range(COLS) if row % 2 == 0 else range(COLS - 1, -1, -1)

        for col in columns:
            full_path.append((row, col))

    return full_path[:target_length]


def create_random_path():
    """
    Generate a self-avoiding path from the starting tile.
    Use a bounded number of attempts to avoid infinite recursion.
    """
    settings = DIFFICULTY_SETTINGS[DIFFICULTY]

    total_tiles = ROWS * COLS
    _, _, _, crystal_count = get_level_settings(LEVEL_NUMBER)

    # Make later levels require longer routes.
    base_length = int(total_tiles * 0.42)
    target_length = int(base_length * settings["path_factor"])

    target_length = max(target_length, crystal_count + 3)
    target_length = min(target_length, total_tiles)

    # Try random paths first.
    for _ in range(40):
        target = random.randint(
            max(crystal_count + 3, target_length - 3),
            min(total_tiles, target_length + 3)
        )

        path = [START_PLAYER]
        visited = {START_PLAYER}

        def extend_path():
            if len(path) == target:
                return True

            row, col = path[-1]
            candidates = []

            for dr, dc in DIRECTIONS.values():
                next_position = (row + dr, col + dc)

                if not inside_board(next_position):
                    continue
                if next_position in visited:
                    continue

                candidates.append(next_position)

            random.shuffle(candidates)

            for position in candidates:
                path.append(position)
                visited.add(position)

                if extend_path():
                    return True

                path.pop()
                visited.remove(position)

            return False

        if extend_path():
            return path

    # Guaranteed fallback: a non-repeating snake route.
    target = min(target_length, total_tiles)
    return create_fallback_path(target)


# ----------------------------------------
# WALL GENERATION
# ----------------------------------------

def generate_walls(path):
    """Place walls only outside the guaranteed safe route."""
    path_positions = set(path)

    available = [
        (row, col)
        for row in range(ROWS)
        for col in range(COLS)
        if (row, col) not in path_positions
    ]

    _, wall_min, wall_max, _ = get_level_settings(LEVEL_NUMBER)
    factor = DIFFICULTY_SETTINGS[DIFFICULTY]["wall_factor"]

    scaled_min = max(0, round(wall_min * factor))
    scaled_max = max(scaled_min, round(wall_max * factor))

    wall_count = min(
        random.randint(scaled_min, scaled_max),
        len(available)
    )

    return set(random.sample(available, wall_count))


# ----------------------------------------
# SOLVABILITY CHECK
# ----------------------------------------

def has_solution():
    """
    Verify the stored guaranteed route by simulating it.
    This avoids exploring an enormous state space on large boards.
    """
    if not GUARANTEED_PATH:
        return False

    state = create_initial_state()

    for current, destination in zip(
        GUARANTEED_PATH,
        GUARANTEED_PATH[1:]
    ):
        if state[0] != current:
            return False

        direction = None

        for name, (dr, dc) in DIRECTIONS.items():
            if (
                current[0] + dr,
                current[1] + dc
            ) == destination:
                direction = name
                break

        if direction is None or direction not in get_legal_moves(state):
            return False

        state = move_state(state, direction)

        if state[3] == "lost":
            return False

    return is_goal_state(state)


# ----------------------------------------
# GENERATE A NEW LEVEL
# ----------------------------------------

def generate_new_level(advance_level=True):
    global ROWS, COLS
    global START_CRYSTALS, EXIT_TILE
    global LEVEL_NUMBER, CRYSTAL_COUNT
    global GUARANTEED_PATH

    # Determine the level being generated before configuring its board.
    target_level = LEVEL_NUMBER + 1 if advance_level else LEVEL_NUMBER

    configure_board(target_level)

    _, _, _, CRYSTAL_COUNT = get_level_settings(target_level)

    # Generate a safe route and its walls.
    path = create_random_path()

    # Keep at least enough safe route positions for all crystals.
    if len(path) < CRYSTAL_COUNT + 2:
        path = create_fallback_path(CRYSTAL_COUNT + 2)

    new_exit = path[-1]

    # Crystals are guaranteed to be on the route, never at start or exit.
    crystal_candidates = path[1:-1]
    new_crystals = frozenset(
        random.sample(crystal_candidates, CRYSTAL_COUNT)
    )

    new_walls = generate_walls(path)

    # A bonus tile, if used by the UI, is also on the safe route.
    special_candidates = [
        position for position in path[1:-1]
        if position not in new_crystals
    ]

    new_special_tiles = set()
    if special_candidates:
        new_special_tiles.add(random.choice(special_candidates))

    START_CRYSTALS = new_crystals
    EXIT_TILE = new_exit
    GUARANTEED_PATH = list(path)

    WALLS.clear()
    WALLS.update(new_walls)

    SPECIAL_TILES.clear()
    SPECIAL_TILES.update(new_special_tiles)

    # Commit the level number only after creating the level.
    LEVEL_NUMBER = target_level

    # Validate the generated route. Retry with a safe fallback if needed.
    if not has_solution():
        GUARANTEED_PATH = create_fallback_path(
            max(CRYSTAL_COUNT + 2, len(path))
        )
        EXIT_TILE = GUARANTEED_PATH[-1]

        candidates = GUARANTEED_PATH[1:-1]
        START_CRYSTALS = frozenset(
            random.sample(candidates, CRYSTAL_COUNT)
        )

        WALLS.clear()
        WALLS.update(generate_walls(GUARANTEED_PATH))

        SPECIAL_TILES.clear()

        if not has_solution():
            # A route without walls is the final guaranteed fallback.
            WALLS.clear()
            SPECIAL_TILES.clear()

            if not has_solution():
                raise RuntimeError(
                    "Could not generate a solvable level."
                )

    return create_initial_state()
