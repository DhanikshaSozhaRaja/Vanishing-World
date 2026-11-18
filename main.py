import math
import pygame
import time
import rules

from compare_algorithms import (
    compare_algorithms,
    record_search_result,
    clear_search_result_cache,
)

from rules import (
    create_initial_state,
    move_state,
    generate_new_level,
    get_exit_tile,
    get_start_crystals,
    get_level_number,
    has_solution,
    is_human_goal_state,
    get_legal_moves,
    get_difficulty,
    set_difficulty,
)

from ai_search import (
    bfs_search,
    dfs_search,
    iddfs_search,
    greedy_search,
    a_star_search,
    evaluate_move_quality,
)


# --------------------------------------------------
# INITIALIZE PYGAME
# --------------------------------------------------

pygame.init()

WIDTH = 900
HEIGHT = 600

MAX_TILE_SIZE = 65
MIN_TILE_SIZE = 25

BOARD_Y = 130
BOARD_BOTTOM_LIMIT = 455
BOARD_SIDE_MARGIN = 55

# These are synchronized with rules.py.
ROWS = rules.ROWS
COLS = rules.COLS
WALLS = rules.WALLS

TILE_SIZE = MAX_TILE_SIZE
BOARD_WIDTH = COLS * TILE_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vanishing World - AI Puzzle Game")

clock = pygame.time.Clock()

title_font = pygame.font.Font(None, 42)
font = pygame.font.Font(None, 28)
small_font = pygame.font.Font(None, 21)
tiny_font = pygame.font.Font(None, 19)

BACKGROUND = (25, 30, 45)
TILE_COLOR = (65, 75, 95)
GRID_COLOR = (110, 120, 140)
PLAYER_COLOR = (50, 210, 100)
CRYSTAL_COLOR = (60, 200, 255)
EXIT_COLOR = (240, 190, 50)
WALL_COLOR = (15, 18, 28)
VANISHED_COLOR = (35, 38, 48)
WHITE = (245, 245, 245)
RED = (240, 75, 75)
PANEL_COLOR = (36, 43, 61)
PANEL_LINE = (85, 98, 122)
MUTED_TEXT = (180, 190, 207)

MAX_TILE_SIZE = 65
MIN_TILE_SIZE = 25
BOARD_Y = 130
BOARD_BOTTOM_LIMIT = 455
BOARD_SIDE_MARGIN = 55


def sync_board_layout():
    global ROWS, COLS, WALLS
    global TILE_SIZE, BOARD_WIDTH

    ROWS = rules.ROWS
    COLS = rules.COLS
    WALLS = rules.WALLS

    available_width = WIDTH - 2 * BOARD_SIDE_MARGIN
    available_height = BOARD_BOTTOM_LIMIT - BOARD_Y

    TILE_SIZE = min(
        MAX_TILE_SIZE,
        available_width // COLS,
        available_height // ROWS
    )

    BOARD_WIDTH = COLS * TILE_SIZE



# --------------------------------------------------
# INSTRUCTION SCREEN
# --------------------------------------------------

instructions_open = True
instruction_scroll = 0

# --------------------------------------------------
# PAUSE / RESUME
# --------------------------------------------------

game_paused = False
pause_started_at = None
pause_started_ticks = None
total_paused_time = 0.0

CLOSE_BUTTON = pygame.Rect(
    WIDTH // 2 - 80, HEIGHT - 55, 160, 40
)

BUTTON_COLOR = (50, 150, 210)
BUTTON_HOVER_COLOR = (70, 175, 235)

# --------------------------------------------------
# MENU BAR
# --------------------------------------------------

MENU_BAR_HEIGHT = 27
MENU_ITEMS = ["Game", "AI Tools", "Difficulty", "Help"]

MENU_RECTS = {}
MENU_DROPDOWN_RECTS = {}

menu_open = None

MENU_BG = (31, 38, 55)
MENU_HOVER = (65, 82, 110)
MENU_DISABLED = (115, 122, 137)

HINT_BUTTON_RECT = pygame.Rect(0, 0, 150, 32)
RESTART_BUTTON_RECT = pygame.Rect(0, 0, 112, 32)
PAUSE_BUTTON_RECT = pygame.Rect(0, 0, 125, 32)
NEXT_LEVEL_BUTTON_RECT = pygame.Rect(0, 0, 125, 32)

# --------------------------------------------------
# GAME STATE
# --------------------------------------------------

game_state = generate_new_level(advance_level=False)
sync_board_layout()

moves = 0
level_has_solution = has_solution()

game_started_at = None
final_game_time = 0.0

# AI playback
ai_moves = []
ai_move_index = 0
ai_playing = False
ai_next_move_time = 0

selected_algorithm = "A*"
ai_was_used = False
ai_nodes_explored = 0
ai_execution_time = 0.0

AI_MOVE_DELAY = 350

# Algorithm comparison
show_comparison = False
comparison_results = []

# Hints
MAX_HINTS_PER_LEVEL = 3
hints_remaining = MAX_HINTS_PER_LEVEL
hint_next_tile = None
hint_message = ""

# AI vs Human warning
challenge_warning_open = False

WARNING_RECT = pygame.Rect(210, 175, 480, 230)
WARNING_CLOSE_BUTTON = pygame.Rect(370, 330, 160, 42)

# AI vs Human
ai_vs_human_mode = False
ai_vs_human_turn = "HUMAN"

human_challenge_moves = 0
ai_challenge_moves = 0

human_challenge_time = 0.0
ai_challenge_time = 0.0

challenge_ai_pending = False
challenge_ai_next_time = 0

challenge_winner = None

human_crystals_collected = 0
ai_crystals_collected = 0

human_turn_time = 0.0
human_turn_started_at = None

challenge_ai_nodes = 0
challenge_ai_searches = 0

human_accuracy_total = 0
human_accuracy_count = 0

ai_accuracy_total = 0
ai_accuracy_count = 0

last_move_quality = ""
last_move_accuracy = 0
last_move_message = ""
last_move_player = ""


# --------------------------------------------------
# RESTART GAME
# --------------------------------------------------

def restart_game():
    global game_state, moves
    global game_started_at, final_game_time
    global ai_moves, ai_move_index, ai_playing
    global ai_next_move_time, selected_algorithm, ai_was_used
    global ai_nodes_explored, ai_execution_time
    global comparison_results
    global hints_remaining, hint_next_tile, hint_message
    global game_paused, pause_started_at
    global pause_started_ticks, total_paused_time

    game_paused = False
    pause_started_at = None
    pause_started_ticks = None
    total_paused_time = 0.0

    comparison_results = []
    clear_search_result_cache()
    hints_remaining = MAX_HINTS_PER_LEVEL
    hint_next_tile = None
    hint_message = ""

    game_state = create_initial_state()
    sync_board_layout()

    moves = 0
    game_started_at = None
    final_game_time = 0.0

    ai_moves = []
    ai_move_index = 0
    ai_playing = False
    ai_next_move_time = 0

    selected_algorithm = "A*"
    ai_was_used = False
    ai_nodes_explored = 0
    ai_execution_time = 0.0


# --------------------------------------------------
# NEXT LEVEL
# --------------------------------------------------

def next_level():
    global game_state, comparison_results, level_has_solution
    global moves, game_started_at, final_game_time
    global ai_moves, ai_move_index, ai_playing, ai_next_move_time
    global selected_algorithm, ai_was_used
    global ai_nodes_explored, ai_execution_time
    global ai_vs_human_mode, ai_vs_human_turn
    global human_challenge_moves, ai_challenge_moves
    global human_challenge_time, ai_challenge_time
    global challenge_ai_pending, challenge_ai_next_time
    global challenge_winner
    global human_crystals_collected, ai_crystals_collected
    global human_turn_time, human_turn_started_at
    global challenge_ai_nodes, challenge_ai_searches
    global hints_remaining, hint_next_tile, hint_message
    global game_paused, pause_started_at
    global pause_started_ticks, total_paused_time
    global last_move_quality, last_move_accuracy
    global last_move_message, last_move_player

    if game_state[3] != "won" and level_has_solution:
        return

    game_paused = False
    pause_started_at = None
    pause_started_ticks = None
    total_paused_time = 0.0
    clear_search_result_cache()
    comparison_results = []

    game_state = generate_new_level()
    sync_board_layout()
    level_has_solution = has_solution()
    game_state = generate_new_level()
    sync_board_layout()
    level_has_solution = has_solution()

    moves = 0
    game_started_at = None
    final_game_time = 0.0

    ai_moves = []
    ai_move_index = 0
    ai_playing = False
    ai_next_move_time = 0

    selected_algorithm = "A*"
    ai_was_used = False
    ai_nodes_explored = 0
    ai_execution_time = 0.0

    comparison_results = []

    hints_remaining = MAX_HINTS_PER_LEVEL
    hint_next_tile = None
    hint_message = ""

    challenge_winner = None

    human_challenge_moves = 0
    ai_challenge_moves = 0

    human_challenge_time = 0.0
    ai_challenge_time = 0.0

    human_crystals_collected = 0
    ai_crystals_collected = 0

    human_turn_time = 0.0
    human_turn_started_at = None

    challenge_ai_nodes = 0
    challenge_ai_searches = 0

    challenge_ai_pending = False
    challenge_ai_next_time = 0

    last_move_quality = ""
    last_move_accuracy = 0
    last_move_message = ""
    last_move_player = ""

    if ai_vs_human_mode and level_has_solution:
        ai_vs_human_turn = "AI"
        challenge_ai_pending = True
        challenge_ai_next_time = (
            pygame.time.get_ticks() + AI_MOVE_DELAY
        )
    else:
        ai_vs_human_turn = "HUMAN"


# --------------------------------------------------
# PAUSE AND RESUME
# --------------------------------------------------

def toggle_pause():
    global game_paused, pause_started_at
    global pause_started_ticks, total_paused_time
    global ai_next_move_time, challenge_ai_next_time

    if game_state[3] != "playing":
        return

    if not game_paused:
        game_paused = True
        pause_started_at = time.perf_counter()
        pause_started_ticks = pygame.time.get_ticks()
        return

    paused_ms = pygame.time.get_ticks() - pause_started_ticks

    if ai_playing:
        ai_next_move_time += paused_ms

    if challenge_ai_pending:
        challenge_ai_next_time += paused_ms

    total_paused_time += time.perf_counter() - pause_started_at

    game_paused = False
    pause_started_at = None
    pause_started_ticks = None


# --------------------------------------------------
# AI HINT SYSTEM
# --------------------------------------------------

def request_hint():
    global hints_remaining, hint_next_tile, hint_message

    if ai_vs_human_mode:
        hint_message = "Hints are disabled in AI vs Human mode."
        hint_next_tile = None
        return

    if game_state[3] != "playing":
        hint_message = "Hints are available only during gameplay."
        hint_next_tile = None
        return

    if hints_remaining <= 0:
        hint_next_tile = None
        hint_message = "No hints remaining for this level."
        return

    if ai_playing:
        hint_next_tile = None
        hint_message = "Pause AI playback or restart before requesting a hint."
        return

    path, nodes_explored = a_star_search(start_state=game_state)

    if not path:
        hint_next_tile = None
        hint_message = "A* could not find a winning route from this state."
        return

    direction = path[0]
    suggested_state = move_state(game_state, direction)

    if suggested_state is None or suggested_state[3] == "lost":
        hint_next_tile = None
        hint_message = "No safe hint is available from this state."
        return

    hint_next_tile = suggested_state[0]
    hints_remaining -= 1

    if len(suggested_state[2]) < len(game_state[2]):
        hint_message = f"Move {direction}: this move collects a crystal."
    elif not suggested_state[2]:
        hint_message = (
            f"Move {direction}: all crystals are collected; "
            "follow the route to the exit."
        )
    else:
        hint_message = (
            f"Move {direction}: this is the first step "
            "on an A* route to the goal."
        )


# --------------------------------------------------
# CHANGE DIFFICULTY
# --------------------------------------------------

def change_difficulty(new_difficulty):
    global game_state, level_has_solution
    global challenge_winner, human_challenge_moves, ai_challenge_moves
    global human_challenge_time, ai_challenge_time
    global human_crystals_collected, ai_crystals_collected
    global human_accuracy_total, human_accuracy_count
    global ai_accuracy_total, ai_accuracy_count
    global challenge_ai_pending, ai_vs_human_turn
    global challenge_ai_nodes, challenge_ai_searches

    if ai_vs_human_mode:
        return

    if not set_difficulty(new_difficulty):
        return

    restart_game()

    game_state = generate_new_level(advance_level=False)
    sync_board_layout()
    level_has_solution = has_solution()

    challenge_winner = None

    human_challenge_moves = 0
    ai_challenge_moves = 0

    human_challenge_time = 0.0
    ai_challenge_time = 0.0

    human_crystals_collected = 0
    ai_crystals_collected = 0

    human_accuracy_total = 0
    human_accuracy_count = 0

    ai_accuracy_total = 0
    ai_accuracy_count = 0

    challenge_ai_nodes = 0
    challenge_ai_searches = 0

    challenge_ai_pending = False
    ai_vs_human_turn = "HUMAN"


# --------------------------------------------------
# HANDLE PLAYER MOVEMENT
# --------------------------------------------------

def handle_move(direction):
    global game_state, moves
    global game_started_at, final_game_time
    global hint_next_tile, hint_message

    if game_state[3] != "playing":
        return

    new_state = move_state(game_state, direction)

    if new_state is None:
        return

    if game_started_at is None:
        game_started_at = time.perf_counter()

    if not ai_was_used and is_human_goal_state(new_state):
        new_state = (
            new_state[0],
            new_state[1],
            new_state[2],
            "won"
        )

    game_state = new_state
    moves += 1

    hint_next_tile = None
    hint_message = ""

    if game_state[3] in ("won", "lost"):
        final_game_time = calculate_elapsed_time()


# --------------------------------------------------
# START AI
# --------------------------------------------------

def start_ai(search_name, search_function):
    global ai_playing, ai_moves, ai_move_index
    global ai_next_move_time, selected_algorithm, ai_was_used
    global ai_nodes_explored, ai_execution_time

    # Start from the initial state of the current level.
    restart_game()

    ai_was_used = True
    selected_algorithm = search_name

    start_time = time.perf_counter()
    result = search_function()
    ai_execution_time = (
        time.perf_counter() - start_time
    ) * 1000

    if (
        isinstance(result, tuple)
        and len(result) == 2
        and isinstance(result[1], (int, float))
    ):
        solution, ai_nodes_explored = result
    else:
        solution = result
        ai_nodes_explored = None

    # Record the actual search result before playback begins.
    record_search_result(
        search_name,
        solution,
        ai_nodes_explored,
        ai_execution_time,
        status=(
            "Completed"
            if solution is not None
            else "No solution found"
        ),
    )

    ai_moves = solution if solution is not None else []
    ai_move_index = 0
    ai_playing = bool(ai_moves)
    ai_next_move_time = pygame.time.get_ticks()

# --------------------------------------------------
# UPDATE AI MOVEMENT
# --------------------------------------------------

def update_ai():
    global ai_move_index, ai_playing, ai_next_move_time

    if not ai_playing:
        return

    current_time = pygame.time.get_ticks()

    if current_time < ai_next_move_time:
        return

    if ai_move_index >= len(ai_moves):
        ai_playing = False
        return

    handle_move(ai_moves[ai_move_index])
    ai_move_index += 1

    if (
        game_state[3] != "playing"
        or ai_move_index >= len(ai_moves)
    ):
        ai_playing = False
        return

    ai_next_move_time = current_time + AI_MOVE_DELAY


# --------------------------------------------------
# AI VS HUMAN MODE
# --------------------------------------------------

def start_ai_vs_human():
    global ai_vs_human_mode, ai_vs_human_turn
    global human_challenge_moves, ai_challenge_moves
    global human_challenge_time, ai_challenge_time
    global challenge_ai_pending, challenge_ai_next_time
    global game_state, moves, game_started_at, final_game_time
    global ai_playing, ai_was_used, show_comparison
    global comparison_results, challenge_winner
    global human_crystals_collected, ai_crystals_collected
    global human_turn_time, human_turn_started_at
    global challenge_ai_nodes, challenge_ai_searches
    global human_accuracy_total, human_accuracy_count
    global ai_accuracy_total, ai_accuracy_count
    global last_move_quality, last_move_accuracy
    global last_move_message, last_move_player

    restart_game()

    ai_vs_human_mode = True
    ai_vs_human_turn = "HUMAN"

    human_challenge_moves = 0
    ai_challenge_moves = 0

    human_challenge_time = 0.0
    ai_challenge_time = 0.0

    challenge_ai_pending = False
    challenge_ai_next_time = 0

    game_state = create_initial_state()
    sync_board_layout()

    moves = 0
    game_started_at = None
    final_game_time = 0.0

    ai_playing = False
    ai_was_used = False

    show_comparison = False
    comparison_results = []

    challenge_winner = None

    human_crystals_collected = 0
    ai_crystals_collected = 0

    human_turn_time = 0.0
    human_turn_started_at = None

    challenge_ai_nodes = 0
    challenge_ai_searches = 0

    human_accuracy_total = 0
    human_accuracy_count = 0

    ai_accuracy_total = 0
    ai_accuracy_count = 0

    last_move_quality = ""
    last_move_accuracy = 0
    last_move_message = ""
    last_move_player = ""


def update_challenge_ai():
    global ai_vs_human_turn, challenge_ai_pending
    global challenge_ai_next_time
    global ai_challenge_moves, ai_challenge_time
    global game_state, moves, game_started_at, final_game_time
    global ai_crystals_collected, challenge_winner
    global challenge_ai_nodes, challenge_ai_searches
    global ai_accuracy_total, ai_accuracy_count
    global last_move_quality, last_move_accuracy
    global last_move_message, last_move_player

    if not ai_vs_human_mode or not challenge_ai_pending:
        return

    if game_state[3] != "playing":
        challenge_ai_pending = False
        return

    current_time = pygame.time.get_ticks()

    if current_time < challenge_ai_next_time:
        return

    search_start = time.perf_counter()
    path, nodes = a_star_search(start_state=game_state)
    search_elapsed = time.perf_counter() - search_start

    challenge_ai_nodes += nodes
    challenge_ai_searches += 1

    if not path:
        legal_moves = get_legal_moves(game_state)
        best_move = None
        best_score = float("-inf")

        for direction in legal_moves:
            next_state = move_state(game_state, direction)

            if next_state is None or next_state[3] == "lost":
                continue

            next_player, next_vanished, next_crystals, next_status = next_state
            score = -100 * len(next_crystals)

            if next_status == "won":
                score += 10000
            else:
                if next_crystals:
                    nearest_crystal = min(
                        abs(next_player[0] - crystal[0])
                        + abs(next_player[1] - crystal[1])
                        for crystal in next_crystals
                    )
                    score -= nearest_crystal

                exit_tile = get_exit_tile()
                exit_distance = (
                    abs(next_player[0] - exit_tile[0])
                    + abs(next_player[1] - exit_tile[1])
                )
                score -= exit_distance * 0.1

            if score > best_score:
                best_score = score
                best_move = direction

        if best_move is None:
            challenge_ai_pending = False
            game_state = (
                game_state[0],
                game_state[1],
                game_state[2],
                "lost",
            )
            challenge_winner = "HUMAN"

            if game_started_at is not None:
                final_game_time = calculate_elapsed_time()
            return

        direction = best_move
    else:
        direction = path[0]

    old_crystals = game_state[2]
    move_result = evaluate_move_quality(game_state, direction)

    last_move_quality = move_result["quality"]
    last_move_accuracy = move_result["accuracy"]
    last_move_player = "AI"

    if last_move_quality == "OPTIMAL":
        last_move_message = "AI preserved the shortest winning route."
    elif last_move_quality == "SUBOPTIMAL":
        last_move_message = "AI chose a move with a longer winning route."
    elif last_move_quality == "WINNING ROUTE LOST":
        last_move_message = "AI could not preserve a winning route."
    elif last_move_quality == "LOSING MOVE":
        last_move_message = "AI selected a move that causes a loss."
    else:
        last_move_message = "AI move evaluated."

    new_state = move_state(game_state, direction)

    if new_state is None:
        return

    ai_accuracy_total += move_result["accuracy"]
    ai_accuracy_count += 1

    ai_crystals_collected += (
        len(old_crystals) - len(new_state[2])
    )

    if game_started_at is None:
        game_started_at = time.perf_counter()

    game_state = new_state
    moves += 1
    ai_challenge_moves += 1
    ai_challenge_time += search_elapsed

    challenge_ai_pending = False

    if game_state[3] in ("won", "lost"):
        challenge_winner = (
            "AI" if game_state[3] == "won" else "HUMAN"
        )
        final_game_time = calculate_elapsed_time()
        return

    ai_vs_human_turn = "HUMAN"


def handle_challenge_human_move(direction):
    global ai_vs_human_turn, challenge_ai_pending
    global challenge_ai_next_time, human_challenge_moves
    global game_state, moves, game_started_at, final_game_time
    global human_crystals_collected, challenge_winner
    global human_accuracy_total, human_accuracy_count
    global last_move_quality, last_move_accuracy
    global last_move_message, last_move_player

    if not ai_vs_human_mode:
        return

    if ai_vs_human_turn != "HUMAN":
        return

    if challenge_ai_pending or game_state[3] != "playing":
        return

    old_crystals = game_state[2]
    move_result = evaluate_move_quality(game_state, direction)
    new_state = move_state(game_state, direction)

    if new_state is None:
        return

    # Invalid moves return the original state; do not count them.
    if new_state == game_state:
        return

    last_move_quality = move_result["quality"]
    last_move_accuracy = move_result["accuracy"]
    last_move_player = "HUMAN"

    if last_move_quality == "OPTIMAL":
        last_move_message = "Good move! Shortest winning route preserved."
    elif last_move_quality == "SUBOPTIMAL":
        last_move_message = "A winning route remains, but a shorter route exists."
    elif last_move_quality == "WINNING ROUTE LOST":
        last_move_message = "Warning: No winning route remains."
    elif last_move_quality == "LOSING MOVE":
        last_move_message = "This move causes a loss."
    else:
        last_move_message = "Move evaluated."

    human_accuracy_total += move_result["accuracy"]
    human_accuracy_count += 1

    human_crystals_collected += (
        len(old_crystals) - len(new_state[2])
    )

    if game_started_at is None:
        game_started_at = time.perf_counter()

    game_state = new_state
    moves += 1
    human_challenge_moves += 1

    if game_state[3] in ("won", "lost"):
        challenge_winner = (
            "HUMAN" if game_state[3] == "won" else "AI"
        )
        final_game_time = calculate_elapsed_time()
        challenge_ai_pending = False
        return

    ai_vs_human_turn = "AI"
    challenge_ai_pending = True
    challenge_ai_next_time = (
        pygame.time.get_ticks() + AI_MOVE_DELAY
    )


# --------------------------------------------------
# DRAW TEXT
# --------------------------------------------------

def draw_text(text, font_used, color, x, y):
    surface = font_used.render(str(text), True, color)
    rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)


# --------------------------------------------------
# DRAW GAME BOARD
# --------------------------------------------------

def draw_board(board_x):
    player, vanished_tiles, crystals, status = game_state

    # Scale visual elements to the tile size.
    exit_inset = max(3, TILE_SIZE // 8)
    player_radius = max(4, TILE_SIZE // 4)
    crystal_half_width = max(4, TILE_SIZE // 5)
    crystal_half_height = max(5, TILE_SIZE // 4)
    hint_inset = max(4, TILE_SIZE // 10)

    for row in range(ROWS):
        for col in range(COLS):
            x = board_x + col * TILE_SIZE
            y = BOARD_Y + row * TILE_SIZE
            position = (row, col)

            if position in vanished_tiles:
                tile_color = VANISHED_COLOR
            elif position in WALLS:
                tile_color = WALL_COLOR
            else:
                tile_color = TILE_COLOR

            tile_rect = pygame.Rect(
                x, y, TILE_SIZE, TILE_SIZE
            )

            pygame.draw.rect(screen, tile_color, tile_rect)
            pygame.draw.rect(screen, GRID_COLOR, tile_rect, 2)

            if (
                hint_next_tile == position
                and position not in vanished_tiles
                and position not in WALLS
            ):
                pygame.draw.rect(
                    screen,
                    (255, 90, 210),
                    tile_rect.inflate(
                        -hint_inset * 2,
                        -hint_inset * 2
                    ),
                    max(1, TILE_SIZE // 16),
                    border_radius=5,
                )

            # Exit
            if (
                position == get_exit_tile()
                and position not in vanished_tiles
            ):
                pygame.draw.rect(
                    screen,
                    EXIT_COLOR,
                    (
                        x + exit_inset,
                        y + exit_inset,
                        TILE_SIZE - exit_inset * 2,
                        TILE_SIZE - exit_inset * 2,
                    ),
                )

                draw_text(
                    "E",
                    small_font if TILE_SIZE < 40 else font,
                    WALL_COLOR,
                    x + TILE_SIZE // 2,
                    y + TILE_SIZE // 2,
                )

            # Crystals
            if position in crystals:
                center_x = x + TILE_SIZE // 2
                center_y = y + TILE_SIZE // 2

                points = [
                    (center_x, center_y - crystal_half_height),
                    (center_x + crystal_half_width, center_y),
                    (center_x, center_y + crystal_half_height),
                    (center_x - crystal_half_width, center_y),
                ]

                pygame.draw.polygon(
                    screen, CRYSTAL_COLOR, points
                )
                pygame.draw.polygon(
                    screen, WHITE, points, max(1, TILE_SIZE // 20)
                )

            # Player
            if position == player:
                center = (
                    x + TILE_SIZE // 2,
                    y + TILE_SIZE // 2,
                )

                pygame.draw.circle(
                    screen, PLAYER_COLOR, center, player_radius
                )
                pygame.draw.circle(
                    screen, WHITE, center, player_radius,
                    max(1, TILE_SIZE // 20)
                )


# --------------------------------------------------
# GAME TIME
# --------------------------------------------------

def calculate_elapsed_time():
    if game_started_at is None:
        return 0.0

    now = time.perf_counter()
    paused_now = 0.0

    if game_paused and pause_started_at is not None:
        paused_now = max(0.0, now - pause_started_at)

    elapsed = now - game_started_at - total_paused_time - paused_now
    return max(0.0, elapsed)


def get_elapsed_time():
    if game_state[3] in ("won", "lost"):
        return max(0.0, final_game_time)

    return calculate_elapsed_time()


# --------------------------------------------------
# GAME-OVER EXPLANATION
# --------------------------------------------------

def get_game_over_explanation():
    player, vanished_tiles, crystals, status = game_state

    if status == "won":
        if ai_was_used:
            return "Crystals collected; exit reached."
        if not crystals:
            return "All crystals collected; exit reached!"
        return "Exit reached after collecting a crystal."

    if status == "lost":
        if player == get_exit_tile() and crystals:
            return "Exit reached before all crystals were collected."
        return "No moves remain; vanished tiles or walls trapped you."

    return "Keep moving and plan your route carefully."


# --------------------------------------------------
# FINAL RESULTS PANEL
# --------------------------------------------------

def draw_results_panel():
    player, vanished_tiles, crystals, status = game_state

    panel_x = 425
    panel_y = 125
    panel_width = 425
    panel_height = 405

    panel_rect = pygame.Rect(
        panel_x, panel_y, panel_width, panel_height
    )

    pygame.draw.rect(
        screen, PANEL_COLOR, panel_rect, border_radius=10
    )
    pygame.draw.rect(
        screen, PANEL_LINE, panel_rect, 2, border_radius=10
    )

    collected = len(get_start_crystals()) - len(crystals)

    if status == "won":
        outcome = "AI WON!" if ai_was_used else "YOU WON!"
        outcome_color = PLAYER_COLOR
    else:
        outcome = "LEVEL FAILED"
        outcome_color = RED

    draw_text(
        "FINAL RESULTS", font, WHITE,
        panel_x + panel_width // 2, panel_y + 28
    )
    draw_text(
        outcome, font, outcome_color,
        panel_x + panel_width // 2, panel_y + 62
    )

    explanation = get_game_over_explanation()
    explanation_surface = tiny_font.render(
        explanation, True, MUTED_TEXT
    )
    explanation_rect = explanation_surface.get_rect(
        center=(panel_x + panel_width // 2, panel_y + 91)
    )
    screen.blit(explanation_surface, explanation_rect)

    star_y = panel_y + 119
    star_spacing = 48
    star_center_x = panel_x + panel_width // 2

    gold_color = (255, 200, 45)
    empty_star_color = (100, 105, 120)

    def draw_star(center_x, center_y, color):
        points = []

        for i in range(10):
            angle = -90 + i * 36
            radius = 17 if i % 2 == 0 else 8

            x = center_x + radius * math.cos(math.radians(angle))
            y = center_y + radius * math.sin(math.radians(angle))

            points.append((int(x), int(y)))

        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, WHITE, points, 1)

    for i in range(3):
        star_x = star_center_x + (i - 1) * star_spacing
        star_color = gold_color if i < collected else empty_star_color
        draw_star(star_x, star_y, star_color)

    rows = [
        ("Player type", "AI" if ai_was_used else "Human"),
        ("Outcome", "Won" if status == "won" else "Lost"),
        ("Moves made", str(moves)),
        ("Elapsed time", f"{get_elapsed_time():.2f} seconds"),
        (
            "Crystals collected",
            f"{collected}/{len(get_start_crystals())}"
        ),
    ]

    if ai_was_used:
        rows.extend([
            ("Algorithm", selected_algorithm),
            ("Solution length", str(len(ai_moves))),
            ("Search time", f"{ai_execution_time:.3f} ms"),
            (
                "Nodes explored",
                str(ai_nodes_explored)
                if ai_nodes_explored else "Not reported"
            ),
        ])

    table_top = panel_y + 145
    row_height = 27
    label_x = panel_x + 18
    value_x = panel_x + 210

    for index, (label, value) in enumerate(rows):
        row_y = table_top + index * row_height

        if index % 2 == 0:
            row_rect = pygame.Rect(
                panel_x + 10, row_y - 12,
                panel_width - 20, row_height
            )
            pygame.draw.rect(
                screen, (43, 51, 71), row_rect, border_radius=4
            )

        label_surface = tiny_font.render(label, True, MUTED_TEXT)
        value_surface = tiny_font.render(value, True, WHITE)

        screen.blit(label_surface, (label_x, row_y - 8))
        screen.blit(value_surface, (value_x, row_y - 8))


def draw_challenge_results_panel():
    panel_x = 425
    panel_y = 125
    panel_width = 425
    panel_height = 430

    panel_rect = pygame.Rect(
        panel_x, panel_y, panel_width, panel_height
    )

    pygame.draw.rect(
        screen, PANEL_COLOR, panel_rect, border_radius=12
    )
    pygame.draw.rect(
        screen, PANEL_LINE, panel_rect, 2, border_radius=12
    )

    if challenge_winner == "HUMAN":
        heading = "HUMAN WINS!"
        heading_color = PLAYER_COLOR
    elif challenge_winner == "AI":
        heading = "AI WINS!"
        heading_color = CRYSTAL_COLOR
    else:
        heading = "CHALLENGE OVER"
        heading_color = WHITE

    center_x = panel_x + panel_width // 2

    draw_text(
        "AI VS HUMAN RESULTS", font, WHITE,
        center_x, panel_y + 30
    )
    draw_text(
        heading, title_font, heading_color,
        center_x, panel_y + 70
    )

    pygame.draw.line(
        screen, PANEL_LINE,
        (panel_x + 20, panel_y + 100),
        (panel_x + panel_width - 20, panel_y + 100), 2
    )

    draw_text("HUMAN", font, PLAYER_COLOR,
              panel_x + 145, panel_y + 128)
    draw_text("AI (A*)", font, CRYSTAL_COLOR,
              panel_x + 335, panel_y + 128)

    draw_text("Moves", small_font, WHITE,
              panel_x + 45, panel_y + 165)
    draw_text(str(human_challenge_moves), small_font, WHITE,
              panel_x + 145, panel_y + 165)
    draw_text(str(ai_challenge_moves), small_font, WHITE,
              panel_x + 335, panel_y + 165)

    draw_text("Crystals", small_font, WHITE,
              panel_x + 45, panel_y + 200)
    total_crystals = len(get_start_crystals())

    draw_text(
        f"{human_crystals_collected}/{total_crystals}",
        small_font, WHITE, panel_x + 145, panel_y + 200
    )
    draw_text(
        f"{ai_crystals_collected}/{total_crystals}",
        small_font, WHITE, panel_x + 335, panel_y + 200
    )

    pygame.draw.line(
        screen, PANEL_LINE,
        (panel_x + 20, panel_y + 225),
        (panel_x + panel_width - 20, panel_y + 225), 1
    )

    draw_text(
        f"AI searches: {challenge_ai_searches}",
        small_font, WHITE, center_x, panel_y + 252
    )
    draw_text(
        f"Total nodes explored: {challenge_ai_nodes}",
        small_font, WHITE, center_x, panel_y + 282
    )
    draw_text(
        f"AI search time: {ai_challenge_time:.3f} sec",
        small_font, WHITE, center_x, panel_y + 312
    )

    human_accuracy = (
        human_accuracy_total / human_accuracy_count
        if human_accuracy_count > 0 else 0
    )
    ai_accuracy = (
        ai_accuracy_total / ai_accuracy_count
        if ai_accuracy_count > 0 else 0
    )

    draw_text(
        f"Human accuracy: {human_accuracy:.1f}%",
        small_font, PLAYER_COLOR, center_x, panel_y + 345
    )
    draw_text(
        f"AI accuracy: {ai_accuracy:.1f}%",
        small_font, CRYSTAL_COLOR, center_x, panel_y + 375
    )
    draw_text(
        f"Total game time: {final_game_time:.2f} sec",
        small_font, WHITE, center_x, panel_y + 405
    )


# --------------------------------------------------
# POPUPS AND FEEDBACK
# --------------------------------------------------

def draw_challenge_warning():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(190)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    pygame.draw.rect(
        screen, PANEL_COLOR, WARNING_RECT, border_radius=12
    )
    pygame.draw.rect(
        screen, PANEL_LINE, WARNING_RECT, 2, border_radius=12
    )

    draw_text(
        "AI VS HUMAN MODE", font, CRYSTAL_COLOR,
        WIDTH // 2, 205
    )
    draw_text(
        "Collect ALL 3 crystals and reach the exit",
        small_font, WHITE, WIDTH // 2, 245
    )
    draw_text(
        "to clear the level. This rule applies to both.",
        small_font, WHITE, WIDTH // 2, 272
    )

    mouse_position = pygame.mouse.get_pos()
    button_color = (
        BUTTON_HOVER_COLOR
        if WARNING_CLOSE_BUTTON.collidepoint(mouse_position)
        else BUTTON_COLOR
    )

    pygame.draw.rect(
        screen, button_color,
        WARNING_CLOSE_BUTTON, border_radius=8
    )

    draw_text(
        "CLOSE", font, WHITE,
        WARNING_CLOSE_BUTTON.centerx,
        WARNING_CLOSE_BUTTON.centery
    )


def draw_move_feedback():
    if not ai_vs_human_mode or not last_move_message:
        return

    feedback_y = 570

    if last_move_quality == "OPTIMAL":
        feedback_color = PLAYER_COLOR
    elif last_move_quality in ("SUBOPTIMAL", "WINNING ROUTE LOST"):
        feedback_color = CRYSTAL_COLOR
    else:
        feedback_color = RED

    draw_text(
        f"{last_move_player}: {last_move_quality} "
        f"({last_move_accuracy}%)",
        small_font, feedback_color, WIDTH // 2, feedback_y
    )
    draw_text(
        last_move_message,
        small_font, WHITE, WIDTH // 2, feedback_y + 22
    )


def draw_pause_overlay():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(190)
    overlay.fill((8, 10, 18))
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(
        WIDTH // 2 - 190, HEIGHT // 2 - 105, 380, 210
    )

    pygame.draw.rect(screen, PANEL_COLOR, panel, border_radius=14)
    pygame.draw.rect(screen, PANEL_LINE, panel, 2, border_radius=14)

    draw_text(
        "GAME PAUSED", title_font, WHITE,
        WIDTH // 2, panel.y + 45
    )
    draw_text(
        "P  -  Resume game", font, CRYSTAL_COLOR,
        WIDTH // 2, panel.y + 95
    )
    draw_text(
        "Your progress is preserved.", small_font, WHITE,
        WIDTH // 2, panel.y + 125
    )
    draw_text(
        "Press P again to continue.", tiny_font, MUTED_TEXT,
        WIDTH // 2, panel.y + 165
    )


# --------------------------------------------------
# MENU BAR AND DROPDOWNS
# --------------------------------------------------

def get_menu_options(menu_name):
    playing = game_state[3] == "playing"

    if menu_name == "Game":
        return [("Exit", True)]

    if menu_name == "AI Tools":
        normal_play = (
            playing and not ai_vs_human_mode and not ai_playing
        )

        return [
            ("Play BFS", normal_play),
            ("Play DFS", normal_play),
            ("Play IDDFS", normal_play),
            ("Play Greedy", normal_play),
            ("Play A*", normal_play),
            ("AI Hint", playing and not ai_vs_human_mode and not ai_playing),
            ("Compare Algorithms", game_state[3] == "won" and not ai_vs_human_mode),
            ("AI vs Human", not ai_vs_human_mode),
        ]

    if menu_name == "Difficulty":
        return [
            (name, not ai_vs_human_mode)
            for name in ("Easy", "Medium", "Hard")
        ]

    if menu_name == "Help":
        return [("Instructions / Controls", True)]

    return []


def draw_menu_bar():
    global MENU_RECTS, MENU_DROPDOWN_RECTS

    MENU_RECTS = {}
    MENU_DROPDOWN_RECTS = {}

    pygame.draw.rect(
        screen, MENU_BG, (0, 0, WIDTH, MENU_BAR_HEIGHT)
    )
    pygame.draw.line(
        screen, PANEL_LINE,
        (0, MENU_BAR_HEIGHT - 1),
        (WIDTH, MENU_BAR_HEIGHT - 1), 1
    )

    x = 14
    mouse_pos = pygame.mouse.get_pos()

    for label in MENU_ITEMS:
        text_surface = small_font.render(label, True, WHITE)
        rect = pygame.Rect(
            x - 7, 1, text_surface.get_width() + 20,
            MENU_BAR_HEIGHT - 2
        )
        MENU_RECTS[label] = rect

        if label == menu_open or rect.collidepoint(mouse_pos):
            pygame.draw.rect(
                screen, MENU_HOVER, rect, border_radius=4
            )

        screen.blit(text_surface, (x + 3, 4))
        x += text_surface.get_width() + 35

    if menu_open is None:
        return

    options = get_menu_options(menu_open)
    menu_rect = MENU_RECTS.get(menu_open)

    if not menu_rect or not options:
        return

    dropdown_width = 205 if menu_open == "AI Tools" else 185
    row_height = 30

    dropdown = pygame.Rect(
        menu_rect.x, MENU_BAR_HEIGHT,
        dropdown_width, row_height * len(options) + 6
    )

    pygame.draw.rect(
        screen, PANEL_COLOR, dropdown, border_radius=5
    )
    pygame.draw.rect(
        screen, PANEL_LINE, dropdown, 1, border_radius=5
    )

    for index, (label, enabled) in enumerate(options):
        row = pygame.Rect(
            dropdown.x + 3,
            dropdown.y + 3 + index * row_height,
            dropdown_width - 6,
            row_height
        )
        MENU_DROPDOWN_RECTS[label] = row

        if row.collidepoint(mouse_pos) and enabled:
            pygame.draw.rect(
                screen, MENU_HOVER, row, border_radius=3
            )

        color = WHITE if enabled else MENU_DISABLED
        label_surface = small_font.render(label, True, color)
        screen.blit(label_surface, (row.x + 9, row.y + 5))


def perform_menu_action(action):
    global menu_open, show_comparison
    global instructions_open, challenge_warning_open

    menu_open = None

    if action == "Exit":
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    elif action == "Play BFS":
        if game_state[3] == "playing" and not ai_vs_human_mode:
            start_ai("BFS", bfs_search)

    elif action == "Play DFS":
        if game_state[3] == "playing" and not ai_vs_human_mode:
            start_ai("DFS", dfs_search)

    elif action == "Play IDDFS":
        if game_state[3] == "playing" and not ai_vs_human_mode:
            start_ai("IDDFS", iddfs_search)

    elif action == "Play Greedy":
        if game_state[3] == "playing" and not ai_vs_human_mode:
            start_ai("Greedy", greedy_search)

    elif action == "Play A*":
        if game_state[3] == "playing" and not ai_vs_human_mode:
            start_ai("A*", a_star_search)

    elif action == "AI Hint":
        request_hint()

    elif action == "Compare Algorithms":
        if game_state[3] == "won" and not ai_vs_human_mode:
            show_comparison = True
            load_comparison_results()

    elif action == "AI vs Human":
        if not ai_vs_human_mode:
            start_ai_vs_human()
            challenge_warning_open = True

    elif action == "Easy":
        change_difficulty("EASY")

    elif action == "Medium":
        change_difficulty("MEDIUM")

    elif action == "Hard":
        change_difficulty("HARD")

    elif action == "Instructions / Controls":
        instructions_open = True


def handle_menu_click(position):
    global menu_open

    for label, rect in MENU_RECTS.items():
        if rect.collidepoint(position):
            menu_open = None if menu_open == label else label
            return True

    for label, rect in MENU_DROPDOWN_RECTS.items():
        if rect.collidepoint(position):
            options = get_menu_options(menu_open) if menu_open else []
            enabled = next(
                (state for name, state in options if name == label),
                False
            )

            if enabled:
                perform_menu_action(label)
            else:
                menu_open = None

            return True

    if menu_open is not None:
        menu_open = None

    return False


# --------------------------------------------------
# DRAW MAIN GAME SCREEN
# --------------------------------------------------

def draw_screen():
    screen.fill(BACKGROUND)

    player, vanished_tiles, crystals, status = game_state
    game_over = status in ("won", "lost")

    draw_text(
        "VANISHING WORLD", title_font, WHITE,
        WIDTH // 2, 43
    )
    draw_text(
        "Collect crystals and reach the exit",
        small_font, WHITE, WIDTH // 2, 70
    )
    draw_text(
        f"LEVEL {get_level_number()}",
        font, EXIT_COLOR, WIDTH // 2, 91
    )
    draw_text(
        f"Board: {ROWS} x {COLS}    Difficulty: {get_difficulty()}",
        small_font, CRYSTAL_COLOR, WIDTH // 2, 113
    )

    # The board stays left-aligned on results screens, leaving
    # space for the results panel. Otherwise, it is centered.
    board_x = (
        BOARD_SIDE_MARGIN
        if game_over or not level_has_solution
        else (WIDTH - BOARD_WIDTH) // 2
    )

    draw_board(board_x)
    board_center = board_x + BOARD_WIDTH // 2

    bottom_margin = 14
    side_margin = 18
    control_gap = 8

    RESTART_BUTTON_RECT.topleft = (
        side_margin,
        HEIGHT - bottom_margin
        - RESTART_BUTTON_RECT.height * 2 - control_gap
    )
    PAUSE_BUTTON_RECT.topleft = (
        side_margin,
        HEIGHT - bottom_margin - PAUSE_BUTTON_RECT.height
    )
    NEXT_LEVEL_BUTTON_RECT.topleft = (
        WIDTH - side_margin - NEXT_LEVEL_BUTTON_RECT.width,
        HEIGHT - bottom_margin - NEXT_LEVEL_BUTTON_RECT.height
    )

    next_allowed = status == "won" or not level_has_solution

    controls = [
        (RESTART_BUTTON_RECT, "Restart", True),
        (
            PAUSE_BUTTON_RECT,
            "Resume" if game_paused else "Pause",
            status == "playing" or game_paused
        ),
        (
            NEXT_LEVEL_BUTTON_RECT,
            "Next Level",
            next_allowed and not ai_playing
        ),
    ]

    mouse_position = pygame.mouse.get_pos()

    for button_rect, label, enabled in controls:
        fill = (
            MENU_HOVER
            if enabled and button_rect.collidepoint(mouse_position)
            else MENU_BG
        )

        if not enabled:
            fill = (38, 43, 55)

        pygame.draw.rect(
            screen, fill, button_rect, border_radius=6
        )
        pygame.draw.rect(
            screen, PANEL_LINE, button_rect, 1, border_radius=6
        )

        draw_text(
            label, small_font,
            WHITE if enabled else MENU_DISABLED,
            button_rect.centerx, button_rect.centery
        )

    draw_text(
        f"Moves: {moves}", font, WHITE,
        board_center - 70, 465
    )
    draw_text(
        f"Crystals left: {len(crystals)}",
        font, CRYSTAL_COLOR, board_center + 75, 465
    )

    if not ai_vs_human_mode and status == "playing" and level_has_solution:
        HINT_BUTTON_RECT.center = (board_center, 562)

        mouse_position = pygame.mouse.get_pos()
        button_color = (
            MENU_HOVER
            if HINT_BUTTON_RECT.collidepoint(mouse_position)
            else MENU_BG
        )

        pygame.draw.rect(
            screen, button_color,
            HINT_BUTTON_RECT, border_radius=7
        )
        pygame.draw.rect(
            screen, PANEL_LINE,
            HINT_BUTTON_RECT, 1, border_radius=7
        )

        draw_text(
            f"Hint ({hints_remaining} left)",
            small_font, CRYSTAL_COLOR,
            HINT_BUTTON_RECT.centerx, HINT_BUTTON_RECT.centery
        )

        if hint_message:
            draw_text(
                hint_message, tiny_font, WHITE,
                WIDTH // 2, 593
            )
    else:
        HINT_BUTTON_RECT.topleft = (-1000, -1000)

    if not level_has_solution:
        draw_text(
            "NO SOLUTION", title_font, RED,
            WIDTH // 2, 490
        )
        draw_text(
            "This level cannot be completed.",
            small_font, WHITE, WIDTH // 2, 520
        )
        draw_text(
            "Press N to generate the next level",
            font, EXIT_COLOR, WIDTH // 2, 560
        )
        draw_menu_bar()
        return

    if status == "won":
        if ai_vs_human_mode:
            draw_challenge_results_panel()
        else:
            draw_results_panel()
            draw_text(
                "LEVEL CLEARED!", font, PLAYER_COLOR,
                WIDTH // 2, 555
            )

    elif status == "lost":
        if ai_vs_human_mode:
            draw_challenge_results_panel()
        else:
            draw_results_panel()
            draw_text(
                "LEVEL FAILED!", font, RED,
                WIDTH // 2, 555
            )

    if status == "playing":
        if ai_vs_human_mode:
            if challenge_ai_pending or ai_vs_human_turn == "AI":
                turn_message = "AI is thinking..."
                turn_color = CRYSTAL_COLOR
            else:
                turn_message = "YOUR TURN"
                turn_color = PLAYER_COLOR

            draw_text(
                turn_message, font, turn_color,
                WIDTH // 2, 500
            )
            draw_text(
                "Q: Quit AI vs Human",
                small_font, WHITE, WIDTH // 2, 535
            )

        elif ai_playing:
            draw_text(
                "AI is playing...", small_font, CRYSTAL_COLOR,
                WIDTH // 2, 510
            )
        else:
            draw_text(
                "Use the arrow keys to move",
                small_font, WHITE, WIDTH // 2, 525
            )

    draw_move_feedback()
    draw_menu_bar()


# --------------------------------------------------
# ALGORITHM COMPARISON
# --------------------------------------------------

def load_comparison_results():
    global comparison_results

    if comparison_results:
        return

    comparison_results = compare_algorithms()

    if comparison_results is None:
        comparison_results = []


def draw_comparison_screen():
    screen.fill((20, 25, 40))

    draw_text(
        "AI ALGORITHM COMPARISON",
        title_font, WHITE, WIDTH // 2, 35
    )

    if not comparison_results:
        draw_text(
            "No comparison results available.",
            font, RED, WIDTH // 2, 180
        )
        draw_text(
            "Press C to return to the game",
            small_font, (255, 220, 100), WIDTH // 2, 565
        )
        return

    successful = [
        result for result in comparison_results
        if result.get("moves") is not None
        and result.get("status") == "Completed"
    ]

    measured_nodes = [
        result for result in comparison_results
        if result.get("nodes") is not None
    ]

    measured_times = [
        result for result in comparison_results
        if result.get("time") is not None
    ]

    shortest_moves = (
        min(result["moves"] for result in successful)
        if successful else None
    )

    # Compare efficiency only among searches that completed.
    completed_nodes = [
        result for result in successful
        if result.get("nodes") is not None
    ]
    completed_times = [
        result for result in successful
        if result.get("time") is not None
    ]

    fewest_nodes = (
        min(result["nodes"] for result in completed_nodes)
        if completed_nodes else None
    )

    fastest_time = (
        min(result["time"] for result in completed_times)
        if completed_times else None
    )

    # Table headings
    table_top = 82

    columns = [
        ("Algorithm", 115),
        ("Moves", 325),
        ("Nodes", 435),
        ("Time (ms)", 555),
        ("Status", 730),
    ]

    for heading, x in columns:
        draw_text(
            heading, small_font, CRYSTAL_COLOR, x, table_top
        )

    for index, result in enumerate(comparison_results):
        y = table_top + 33 + index * 32

        is_shortest = (
            shortest_moves is not None
            and result.get("moves") == shortest_moves
            and result.get("status") == "Completed"
        )

        name_color = (
            (120, 235, 160) if is_shortest else WHITE
        )

        draw_text(
            result["name"], tiny_font, name_color,
            columns[0][1], y
        )

        moves_value = result.get("moves")
        moves_text = str(moves_value) if moves_value is not None else "—"

        draw_text(
            moves_text, tiny_font, name_color,
            columns[1][1], y
        )

        nodes_value = result.get("nodes")
        nodes_text = str(nodes_value) if nodes_value is not None else "—"

        nodes_color = (
            (120, 235, 160)
            if (
                fewest_nodes is not None
                and nodes_value == fewest_nodes
                and result.get("status") == "Completed"
            )
            else WHITE
        )

        draw_text(
            nodes_text, tiny_font, nodes_color,
            columns[2][1], y
        )

        time_value = result.get("time")
        time_text = (
            f"{time_value:.2f}"
            if time_value is not None else "—"
        )

        time_color = (
            (120, 235, 160)
            if (
                fastest_time is not None
                and time_value == fastest_time
                and result.get("status") == "Completed"
            )
            else WHITE
        )

        draw_text(
            time_text, tiny_font, time_color,
            columns[3][1], y
        )

        status = result.get("status", "Unknown")

        # Shorten long statuses to keep the table aligned.
        if status == "Completed":
            status_text = "Completed"
        elif "limit" in status.lower():
            status_text = "Limit reached"
        elif "skipped" in status.lower():
            status_text = "Skipped"
        elif "no solution" in status.lower():
            status_text = "No solution"
        else:
            status_text = "Not completed"

        status_color = (
            (120, 235, 160)
            if status == "Completed"
            else MUTED_TEXT
        )

        draw_text(
            status_text, tiny_font, status_color,
            columns[4][1], y
        )

    draw_text(
        "Green indicates the best value among completed searches.",
        tiny_font, (120, 235, 160), WIDTH // 2, 265
    )

    # Nodes explored chart
    draw_text(
        "NODES EXPLORED",
        font, CRYSTAL_COLOR, WIDTH // 2, 295
    )

    chart_x = 265
    chart_y = 320
    chart_width = 455
    bar_height = 17
    bar_gap = 8

    max_nodes = max(
        (result["nodes"] for result in measured_nodes),
        default=1
    )
    max_nodes = max(max_nodes, 1)

    for index, result in enumerate(comparison_results):
        y = chart_y + index * (bar_height + bar_gap)

        draw_text(
            result["name"], tiny_font, WHITE,
            155, y + bar_height // 2
        )

        nodes_value = result.get("nodes")

        if nodes_value is None:
            draw_text(
                "Not measured", tiny_font, MUTED_TEXT,
                chart_x + 65, y + bar_height // 2
            )
            continue

        bar_width = int(
            nodes_value / max_nodes * chart_width
        )

        if nodes_value > 0:
            bar_width = max(bar_width, 2)

        is_best = (
            fewest_nodes is not None
            and nodes_value == fewest_nodes
            and result.get("status") == "Completed"
        )

        bar_color = (
            (120, 235, 160) if is_best else CRYSTAL_COLOR
        )

        pygame.draw.rect(
            screen, bar_color,
            (chart_x, y, bar_width, bar_height),
            border_radius=3
        )

        value_x = min(
            chart_x + bar_width + 30,
            WIDTH - 45
        )

        draw_text(
            nodes_value, tiny_font, WHITE,
            value_x, y + bar_height // 2
        )

    # Summary
    summary_y = 475

    if successful:
        shortest_names = [
            result["name"] for result in successful
            if result["moves"] == shortest_moves
        ]

        draw_text(
            f"Shortest completed solution: {shortest_moves} moves "
            f"({', '.join(shortest_names)})",
            tiny_font, (120, 235, 160),
            WIDTH // 2, summary_y
        )
    else:
        draw_text(
            "No completed search found a solution.",
            tiny_font, MUTED_TEXT,
            WIDTH // 2, summary_y
        )

    if fewest_nodes is not None:
        fewest_names = [
            result["name"] for result in completed_nodes
            if result["nodes"] == fewest_nodes
        ]
        draw_text(
            f"Fewest nodes among completed searches: "
            f"{', '.join(fewest_names)}",
            tiny_font, WHITE, WIDTH // 2, summary_y + 20
        )

    if fastest_time is not None:
        fastest_names = [
            result["name"] for result in completed_times
            if result["time"] == fastest_time
        ]
        draw_text(
            f"Fastest completed search: {', '.join(fastest_names)}",
            tiny_font, WHITE, WIDTH // 2, summary_y + 39
        )

    draw_text(
        "Press C to return to the game",
        small_font, (255, 220, 100), WIDTH // 2, 570
    )

# --------------------------------------------------
# INSTRUCTIONS
# --------------------------------------------------

def draw_instructions():
    screen.fill(BACKGROUND)

    draw_text(
        "VANISHING WORLD",
        title_font, CRYSTAL_COLOR, WIDTH // 2, 35
    )
    draw_text(
        "HOW TO PLAY", font, WHITE, WIDTH // 2, 75
    )

    content_area = pygame.Rect(35, 105, WIDTH - 70, 345)
    screen.set_clip(content_area)

    instructions = [
        ("OBJECTIVE", [
            "Human: collect at least 1 crystal and reach the exit.",
            "AI: collect all 3 crystals and reach the exit."
        ]),
        ("MOVEMENT", [
            "Use the arrow keys to move one tile at a time.",
            "You can move up, down, left, or right."
        ]),
        ("VANISHING TILES", [
            "Every tile you leave disappears permanently.",
            "You cannot enter a vanished tile again.",
            "Plan your route carefully to avoid getting trapped."
        ]),
        ("CRYSTALS", [
            "Collect crystals by moving onto their tiles.",
            "Human players need at least 1 crystal to win.",
            "AI algorithms must collect all 3 crystals."
        ]),
        ("WALLS AND BOUNDARIES", [
            "Walls and board edges block your movement.",
            "Choose another route when a path is blocked."
        ]),
        ("WINNING AND LOSING", [
            "WIN: Collect all crystals and reach the exit.",
            "LOSE: No legal moves remain before you win."
        ]),
        ("AI CONTROLS", [
            "1 - Breadth-First Search (BFS)",
            "2 - Depth-First Search (DFS)",
            "3 - Iterative Deepening DFS (IDDFS)",
            "4 - Greedy Best-First Search",
            "5 - A* Search",
            "The AI searches for a solution and plays it."
        ]),
        ("OTHER CONTROLS", [
            "H - Ask A* for a hint (3 hints per level).",
            "P - Pause or resume the game.",
            "R - Restart the current game.",
            "C - Open the algorithm comparison screen.",
            "N - Generate a next level, if enabled.",
            "Hints are disabled in AI vs Human mode."
        ])
    ]

    y = 115 - instruction_scroll

    for heading, lines in instructions:
        draw_text(
            heading, font, EXIT_COLOR, WIDTH // 2, y
        )
        y += 28

        for line in lines:
            draw_text(
                line, small_font, WHITE, WIDTH // 2, y
            )
            y += 24

        y += 12

    screen.set_clip(None)

    draw_text(
        "Scroll with your mouse wheel or use Up/Down arrows",
        small_font, CRYSTAL_COLOR, WIDTH // 2, 460
    )

    mouse_position = pygame.mouse.get_pos()
    button_color = (
        BUTTON_HOVER_COLOR
        if CLOSE_BUTTON.collidepoint(mouse_position)
        else BUTTON_COLOR
    )

    pygame.draw.rect(
        screen, button_color, CLOSE_BUTTON, border_radius=8
    )
    draw_text(
        "CLOSE", font, WHITE,
        CLOSE_BUTTON.centerx, CLOSE_BUTTON.centery
    )

    pygame.display.update()


def handle_instruction_scroll(event):
    global instructions_open, instruction_scroll

    if event.type == pygame.MOUSEWHEEL:
        instruction_scroll -= event.y * 25

    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_DOWN:
            instruction_scroll += 25
        elif event.key == pygame.K_UP:
            instruction_scroll -= 25
        elif event.key == pygame.K_PAGEDOWN:
            instruction_scroll += 150
        elif event.key == pygame.K_PAGEUP:
            instruction_scroll -= 150
        elif event.key == pygame.K_ESCAPE:
            instructions_open = False

    elif event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1 and CLOSE_BUTTON.collidepoint(event.pos):
            instructions_open = False

    instruction_scroll = max(
        0, min(instruction_scroll, 350)
    )


# --------------------------------------------------
# MAIN GAME LOOP
# --------------------------------------------------

def main():
    global show_comparison, instructions_open
    global game_paused
    global challenge_warning_open, ai_vs_human_mode
    global challenge_ai_pending, ai_vs_human_turn
    global challenge_ai_next_time

    global challenge_winner
    global human_challenge_moves, ai_challenge_moves
    global human_challenge_time, ai_challenge_time
    global human_crystals_collected, ai_crystals_collected
    global human_accuracy_total, human_accuracy_count
    global ai_accuracy_total, ai_accuracy_count
    global challenge_ai_nodes, challenge_ai_searches

    global last_move_quality, last_move_accuracy
    global last_move_message, last_move_player

    running = True

    while running:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif instructions_open:
                handle_instruction_scroll(event)

            elif challenge_warning_open:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        challenge_warning_open = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if (
                        event.button == 1
                        and WARNING_CLOSE_BUTTON.collidepoint(event.pos)
                    ):
                        challenge_warning_open = False

            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                if not show_comparison:
                    if HINT_BUTTON_RECT.collidepoint(event.pos):
                        request_hint()

                    elif RESTART_BUTTON_RECT.collidepoint(event.pos):
                        show_comparison = False

                        if ai_vs_human_mode:
                            start_ai_vs_human()
                        else:
                            restart_game()

                    elif PAUSE_BUTTON_RECT.collidepoint(event.pos):
                        if game_state[3] == "playing" or game_paused:
                            toggle_pause()

                    elif NEXT_LEVEL_BUTTON_RECT.collidepoint(event.pos):
                        if (
                            not ai_playing
                            and (
                                game_state[3] == "won"
                                or not level_has_solution
                            )
                        ):
                            show_comparison = False
                            next_level()

                    else:
                        handle_menu_click(event.pos)

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_p and not show_comparison:
                    if not instructions_open and not challenge_warning_open:
                        toggle_pause()
                    continue

                if game_paused:
                    continue

                if event.key == pygame.K_v and not ai_vs_human_mode:
                    start_ai_vs_human()
                    challenge_warning_open = True
                    continue

                if event.key == pygame.K_q and ai_vs_human_mode:
                    ai_vs_human_mode = False
                    challenge_warning_open = False
                    challenge_ai_pending = False
                    ai_vs_human_turn = "HUMAN"
                    restart_game()
                    continue

                if not ai_vs_human_mode:
                    if event.key == pygame.K_F1:
                        change_difficulty("EASY")
                        continue
                    elif event.key == pygame.K_F2:
                        change_difficulty("MEDIUM")
                        continue
                    elif event.key == pygame.K_F3:
                        change_difficulty("HARD")
                        continue

                if event.key == pygame.K_r:
                    show_comparison = False

                    if ai_vs_human_mode:
                        restart_game()

                        challenge_winner = None
                        human_challenge_moves = 0
                        ai_challenge_moves = 0
                        human_challenge_time = 0.0
                        ai_challenge_time = 0.0
                        human_crystals_collected = 0
                        ai_crystals_collected = 0

                        human_accuracy_total = 0
                        human_accuracy_count = 0
                        ai_accuracy_total = 0
                        ai_accuracy_count = 0

                        challenge_ai_nodes = 0
                        challenge_ai_searches = 0

                        last_move_quality = ""
                        last_move_accuracy = 0
                        last_move_message = ""
                        last_move_player = ""

                        if level_has_solution:
                            ai_vs_human_turn = "AI"
                            challenge_ai_pending = True
                            challenge_ai_next_time = (
                                pygame.time.get_ticks() + AI_MOVE_DELAY
                            )
                        else:
                            ai_vs_human_turn = "HUMAN"
                            challenge_ai_pending = False
                    else:
                        restart_game()

                    continue

                if event.key == pygame.K_n:
                    if (
                        not ai_playing
                        and (
                            game_state[3] == "won"
                            or not level_has_solution
                        )
                    ):
                        show_comparison = False
                        next_level()
                    continue

                elif event.key == pygame.K_c:
                    if game_state[3] == "won" and not ai_vs_human_mode:
                        show_comparison = not show_comparison

                        if show_comparison:
                            load_comparison_results()
                    continue

                if (
                    event.key == pygame.K_h
                    and game_state[3] == "playing"
                    and not show_comparison
                    and not ai_vs_human_mode
                ):
                    request_hint()
                    continue

                if (
                    game_state[3] == "playing"
                    and not show_comparison
                    and not ai_vs_human_mode
                ):
                    if event.key == pygame.K_1:
                        start_ai("BFS", bfs_search)
                    elif event.key == pygame.K_2:
                        start_ai("DFS", dfs_search)
                    elif event.key == pygame.K_3:
                        start_ai("IDDFS", iddfs_search)
                    elif event.key == pygame.K_4:
                        start_ai("Greedy", greedy_search)
                    elif event.key == pygame.K_5:
                        start_ai("A*", a_star_search)

                if (
                    game_state[3] == "playing"
                    and not show_comparison
                    and not ai_playing
                ):
                    if event.key == pygame.K_UP:
                        if ai_vs_human_mode:
                            handle_challenge_human_move("UP")
                        else:
                            handle_move("UP")

                    elif event.key == pygame.K_DOWN:
                        if ai_vs_human_mode:
                            handle_challenge_human_move("DOWN")
                        else:
                            handle_move("DOWN")

                    elif event.key == pygame.K_LEFT:
                        if ai_vs_human_mode:
                            handle_challenge_human_move("LEFT")
                        else:
                            handle_move("LEFT")

                    elif event.key == pygame.K_RIGHT:
                        if ai_vs_human_mode:
                            handle_challenge_human_move("RIGHT")
                        else:
                            handle_move("RIGHT")

        if (
            not instructions_open
            and not challenge_warning_open
            and not game_paused
            and not show_comparison
            and level_has_solution
            and game_state[3] == "playing"
        ):
            if ai_vs_human_mode:
                update_challenge_ai()
            else:
                update_ai()

        if instructions_open:
            draw_instructions()
        elif challenge_warning_open:
            draw_screen()
            draw_challenge_warning()
        elif show_comparison:
            draw_comparison_screen()
        else:
            draw_screen()

        if (
            game_paused
            and not instructions_open
            and not challenge_warning_open
            and not show_comparison
        ):
            draw_pause_overlay()

        if (
            not instructions_open
            and not challenge_warning_open
            and not show_comparison
        ):
            draw_menu_bar()

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


# --------------------------------------------------
# RUN GAME
# --------------------------------------------------

if __name__ == "__main__":
    sync_board_layout()
    main()
