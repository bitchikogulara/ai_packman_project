import heapq
import random
from itertools import product


MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]


class State:
    

    __slots__ = ("positions", "g", "h", "f", "parent")

    def __init__(self, positions, g=0, h=0.0, parent=None):
        self.positions = positions
        self.g = g
        self.h = h
        self.f = g + h
        self.parent = parent

    def __lt__(self, other):
        return self.f < other.f

    def __eq__(self, other):
        return isinstance(other, State) and self.positions == other.positions

    def __hash__(self):
        return hash(self.positions)


class _NodeBudgetExceeded(Exception):
    
    pass


class PacmenProblem:
    

    def __init__(self, grid):
        
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if grid else 0
        self.free_cells = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if grid[r][c] == 0
        ]
        self._neighbors_of = self._precompute_neighbors()

    
    def _is_valid(self, x, y):
        
        return (
            0 <= x < self.rows
            and 0 <= y < self.cols
            and self.grid[x][y] == 0
        )

    def _precompute_neighbors(self):
        
        table = {}
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == 0:
                    options = []
                    for dr, dc in MOVES:
                        nr, nc = r + dr, c + dc
                        if self._is_valid(nr, nc):
                            options.append((nr, nc))
                    table[(r, c)] = tuple(options)
        return table

    
    def is_goal(self, positions):
        
        first = positions[0]
        for p in positions:
            if p != first:
                return False
        return True

    def heuristic(self, positions):
        
        xmin = xmax = positions[0][0]
        ymin = ymax = positions[0][1]
        for x, y in positions:
            if x < xmin: xmin = x
            elif x > xmax: xmax = x
            if y < ymin: ymin = y
            elif y > ymax: ymax = y
        dx = xmax - xmin
        dy = ymax - ymin
        return 0.5 * (dx if dx > dy else dy)

    def gen_neighbors(self, state):
        
        per_pacman = [self._neighbors_of[p] for p in state.positions]
        out = []
        for combo in product(*per_pacman):
            ns = State(positions=combo, g=state.g + 1, parent=state)
            ns.h = self.heuristic(combo)
            ns.f = ns.g + ns.h
            out.append(ns)
        return out

    
    def _reconstruct_path(self, parents, end):
        
        path = []
        cur = end
        while cur is not None:
            path.append(cur)
            cur = parents[cur]
        path.reverse()
        return path

    
    def a_star(self, start_positions):
        
        start = tuple(start_positions)
        h0 = self.heuristic(start)

        
        counter = 0
        open_heap = [(h0, counter, 0, start)]
        parents = {start: None}
        best_g = {start: 0}
        closed = set()
        expanded = 0

        while open_heap:
            f, _, g, pos = heapq.heappop(open_heap)

            if pos in closed:
                continue

            if self.is_goal(pos):
                return self._reconstruct_path(parents, pos), expanded

            closed.add(pos)
            expanded += 1

            per_pacman = [self._neighbors_of[p] for p in pos]
            ng = g + 1
            for combo in product(*per_pacman):
                if combo in closed:
                    continue
                if ng < best_g.get(combo, 1 << 30):
                    best_g[combo] = ng
                    parents[combo] = pos
                    nh = self.heuristic(combo)
                    counter += 1
                    heapq.heappush(open_heap, (ng + nh, counter, ng, combo))

        return None, expanded

    
    def dfs(self, start_positions, max_depth=20, max_nodes=200_000):
        
        start = tuple(start_positions)
        visited = set()
        parents = {start: None}
        stats = {"visited": 0}

        def rec(pos, depth):
            stats["visited"] += 1
            if stats["visited"] > max_nodes:
                raise _NodeBudgetExceeded
            if self.is_goal(pos):
                return self._reconstruct_path(parents, pos)
            if depth >= max_depth:
                return None
            visited.add(pos)
            per_pacman = [self._neighbors_of[p] for p in pos]
            for combo in product(*per_pacman):
                if combo in visited:
                    continue
                
                
                parents[combo] = pos
                result = rec(combo, depth + 1)
                if result is not None:
                    return result
            return None

        try:
            path = rec(start, 0)
        except _NodeBudgetExceeded:
            path = None
        return path, stats["visited"]

    
    def random_positions(self, n, rng=None):
        
        rnd = rng if rng is not None else random
        return [rnd.choice(self.free_cells) for _ in range(n)]
