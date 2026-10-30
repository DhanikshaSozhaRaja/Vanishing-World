# Vanishing World – An AI Puzzle-Survival Game

## 1. Project Overview

**Vanishing World** is an AI-based puzzle-survival game developed using Python and Pygame.

The player must collect crystals and reach the exit while navigating a grid where every tile visited disappears permanently. The game includes manual gameplay and AI-based solving techniques.

The project demonstrates different Artificial Intelligence search algorithms through an interactive puzzle game.

## 2. Game Objective

- Start from the designated starting position.
- Collect the required crystals.
- Reach the exit to complete the level.
- Avoid walls and previously vanished tiles.
- Plan movements carefully because visited tiles cannot be used again.

## 3. Technologies Used

- **Python 3.11** – Main programming language.
- **Pygame** – Game interface and graphics.
- **VS Code** – Development environment.

## 4. AI Algorithms Implemented

The following search algorithms are implemented:

1. **Breadth-First Search (BFS)** – Explores states level by level.
2. **Depth-First Search (DFS)** – Explores one path deeply before backtracking.
3. **Iterative Deepening DFS (IDDFS)** – Repeatedly performs depth-limited searches.
4. **Greedy Best-First Search** – Selects states based on their estimated distance to the goal.
5. **A* Search** – Uses path cost and heuristic estimation to find a solution.

The algorithms can be compared based on:
- Number of moves taken.
- Number of nodes explored.
- Execution time.

## 5. Implemented Features

- Interactive 5×5 grid-based gameplay.
- Player movement using keyboard controls.
- Crystal collection and exit mechanism.
- Permanent disappearance of visited tiles.
- Walls and movement restrictions.
- AI autoplay using implemented search algorithms.
- Random level generation.
- Level progression with increasing board sizes and difficulty.
- AI algorithm comparison.
- Game completion and result screens.
- No-solution detection.
- Difficulty selection.
- AI vs Human gameplay mode.
- Move-quality evaluation for comparing AI and human decisions.
- Dynamic board layout to support different board sizes.

## 6. Higher-Level AI Strategy

For higher-level boards, the planned strategy is to use **Greedy Best-First Search as the only AI solving algorithm**.

This is intended to reduce the computational cost of searching larger game boards.

Lower-level boards support multiple search algorithms for comparison, while higher-level boards focus on Greedy Best-First Search.

## 7. How to Run the Project

### Step 1: Install Python

Install Python 3.11 or later.

### Step 2: Install Pygame

```bash
pip install pygame
```

### Step 3: Open the Project Folder

Open the project in VS Code.

### Step 4: Run the Game

```bash
python main.py
```

If using the project's virtual environment on Windows:

```bash
.\.venv\Scripts\python.exe main.py
```

## 8. Game Controls

The following controls are available in Vanishing World:

| Key / Input          | Function                                                                   |
| -------------------- | -------------------------------------------------------------------------- |
| Arrow Keys (↑ ↓ ← →) | Move the player in the selected direction.                                 |
| 1                    | Start AI using Breadth-First Search (BFS).                                 |
| 2                    | Start AI using Depth-First Search (DFS).                                   |
| 3                    | Start AI using Iterative Deepening DFS (IDDFS).                            |
| 4                    | Start AI using Greedy Best-First Search.                                   |
| 5                    | Start AI using A\* Search.                                                 |
| H                    | Request an AI hint.                                                        |
| R                    | Restart the current level.                                                 |
| N                    | Move to the next level (when the current level is won or has no solution). |
| C                    | Open or close the AI algorithm comparison screen after winning a level.    |
| P                    | Pause or resume the game.                                                  |
| V                    | Enter AI vs Human challenge mode.                                          |
| Q                    | Exit AI vs Human challenge mode.                                           |
| F1                   | Set difficulty to Easy.                                                    |
| F2                   | Set difficulty to Medium.                                                  |
| F3                   | Set difficulty to Hard.                                                    |
| ESC                  | Close the challenge warning popup.                                         |
| Mouse Click          | Interact with on-screen buttons and menus.                                 |

### Additional Notes

- AI algorithm shortcuts (1–5), hints (H), and normal movement are disabled or restricted in AI vs Human mode.
- In AI vs Human mode, the AI and human take turns making moves.
- The next-level option is available only after winning or when the generated level has no solution.
- The comparison screen is available after winning a level outside AI vs Human mode.

Important: These controls are based on the event-handling code you shared. The exact behavior of mouse buttons depends on the menu and button-handling functions elsewhere in `main.py`.

## 9. Project Objective

The main objective of this project is to understand and demonstrate how different AI search strategies solve problems involving pathfinding, state-space exploration, heuristic evaluation, and decision-making.

The game provides a visual way to understand the strengths and limitations of different search algorithms.

## 10. Future Enhancements

- Improve AI decision-making for larger boards.
- Add more advanced search strategies.
- Enhance the AI vs Human comparison system.
- Add more puzzle elements and special tiles.
- Improve game graphics and animations.
- Add detailed performance statistics and level-wise reports.

---

**Project:** Vanishing World – An AI Puzzle-Survival Game  
**Course:** Artificial Intelligence with Python  
**Language:** Python  
**Interface:** Pygame
