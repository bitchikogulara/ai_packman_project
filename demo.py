import random
import time

from pacmen_solver import PacmenProblem


PROJECT_GRID = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]


def render(grid, positions):
    
    rows = len(grid)
    cols = len(grid[0])
    out = [["#" if grid[r][c] == 1 else "." for c in range(cols)]
           for r in range(rows)]
    for i, (r, c) in enumerate(positions):
        marker = str(i + 1)
        
        out[r][c] = "*" if out[r][c] not in (".", "#") else marker
    return "\n".join("".join(row) for row in out)


def demo_single_instance(problem, n=3, seed=1):
    print("=" * 70)
    print(f"Demo 1 — single instance with n={n} pacmen")
    print("=" * 70)
    rng = random.Random(seed)
    start = problem.random_positions(n, rng)
    print(f"start positions: {start}\n")

    t0 = time.perf_counter()
    path, expanded = problem.a_star(start)
    dt = time.perf_counter() - t0

    if path is None:
        print("A* found no solution.")
        return

    print(f"A* solved it in {dt:.4f}s, expanded {expanded} states, "
          f"path length = {len(path) - 1} steps.\n")
    for step, positions in enumerate(path):
        print(f"--- step {step} ---")
        print(render(problem.grid, positions))
        print()


def demo_benchmark(problem, n_values=(2, 3, 4), runs_per_n=3,
                   dfs_node_cap=200_000):
    print("=" * 70)
    print("Demo 2 — A* vs DFS benchmark")
    print("=" * 70)
    print(f"Maze: {problem.rows}x{problem.cols}, "
          f"free cells: {len(problem.free_cells)}")
    print("Branching factor 5^n, state space (free_cells)^n\n")

    header = (
        f"{'n':<3}{'Run':<5}{'A* time(s)':<12}{'A* steps':<10}"
        f"{'A* expanded':<14}{'DFS time(s)':<13}{'DFS steps':<11}"
        f"{'DFS visits':<12}"
    )

    for n in n_values:
        rng = random.Random(n)  
        print(f"--- n = {n} pacmen " + "-" * 50)
        print(header)
        for r in range(1, runs_per_n + 1):
            start = problem.random_positions(n, rng)

            t0 = time.perf_counter()
            path_a, exp_a = problem.a_star(start)
            t_a = time.perf_counter() - t0
            steps_a = len(path_a) - 1 if path_a else "—"

            t0 = time.perf_counter()
            path_d, vis_d = problem.dfs(
                start, max_depth=20, max_nodes=dfs_node_cap,
            )
            t_d = time.perf_counter() - t0
            steps_d = len(path_d) - 1 if path_d else "DNF"

            print(
                f"{n:<3}{r:<5}{t_a:<12.4f}{str(steps_a):<10}"
                f"{exp_a:<14}{t_d:<13.4f}{str(steps_d):<11}"
                f"{vis_d:<12}",
                flush=True,
            )
        print()


def main():
    problem = PacmenProblem(PROJECT_GRID)
    demo_single_instance(problem, n=3, seed=1)
    demo_benchmark(problem, n_values=(2, 3, 4), runs_per_n=3)


if __name__ == "__main__":
    main()
