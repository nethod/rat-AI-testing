"""
AI Rat and Cheese

Install:
  pip install pygame

Run:
  python3 main.py
"""

import random
import heapq
import pygame

# Simple top-down grid settings
TILE_SIZE = 32
GRID_W = 20
GRID_H = 15
WALL_COUNT = 55
FPS = 10

# Colors
BG = (20, 20, 24)
GRID = (40, 40, 48)
WALL = (90, 90, 100)
RAT = (160, 160, 255)
CHEESE = (255, 220, 80)
TEXT = (240, 240, 240)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((GRID_W * TILE_SIZE, GRID_H * TILE_SIZE + 40))
        pygame.display.set_caption("AI Rat and Cheese")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.score = 0
        self.reset_map(keep_score=True)

    def reset_map(self, keep_score=True):
        if not keep_score:
            self.score = 0

        # Build empty board
        self.walls = set()
        all_tiles = [(x, y) for y in range(GRID_H) for x in range(GRID_W)]

        # Place rat and cheese on random empty tiles
        self.rat = random.choice(all_tiles)
        remain = [t for t in all_tiles if t != self.rat]
        self.cheese = random.choice(remain)

        # Add random walls, but keep rat<->cheese path available
        candidates = [t for t in all_tiles if t not in (self.rat, self.cheese)]
        random.shuffle(candidates)
        for tile in candidates:
            if len(self.walls) >= WALL_COUNT:
                break
            self.walls.add(tile)
            if not self.path_exists(self.rat, self.cheese):
                self.walls.remove(tile)

    def neighbors(self, node):
        x, y = node
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_W and 0 <= ny < GRID_H and (nx, ny) not in self.walls:
                yield (nx, ny)

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # A* pathfinding from start to goal
    def astar(self, start, goal):
        open_heap = [(0, start)]
        came_from = {}
        g_score = {start: 0}

        while open_heap:
            _, current = heapq.heappop(open_heap)
            if current == goal:
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path

            for nxt in self.neighbors(current):
                tentative = g_score[current] + 1
                if tentative < g_score.get(nxt, 10**9):
                    came_from[nxt] = current
                    g_score[nxt] = tentative
                    f = tentative + self.heuristic(nxt, goal)
                    heapq.heappush(open_heap, (f, nxt))

        return []

    def path_exists(self, start, goal):
        return len(self.astar(start, goal)) > 0

    def respawn_cheese(self):
        empties = [
            (x, y)
            for y in range(GRID_H)
            for x in range(GRID_W)
            if (x, y) not in self.walls and (x, y) != self.rat
        ]
        random.shuffle(empties)
        for pos in empties:
            if self.path_exists(self.rat, pos):
                self.cheese = pos
                return
        # Fallback: rebuild map if none valid
        self.reset_map(keep_score=True)

    def update(self):
        # Rat moves one tile at a time along A* path to cheese
        path = self.astar(self.rat, self.cheese)
        if len(path) >= 2:
            self.rat = path[1]

        # If rat reaches cheese, score and respawn cheese
        if self.rat == self.cheese:
            self.score += 1
            self.respawn_cheese()

    def draw(self):
        self.screen.fill(BG)

        # Grid and world
        for y in range(GRID_H):
            for x in range(GRID_W):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, GRID, rect, 1)
                if (x, y) in self.walls:
                    pygame.draw.rect(self.screen, WALL, rect)

        # Cheese and rat
        cx, cy = self.cheese
        rx, ry = self.rat
        cheese_rect = pygame.Rect(cx * TILE_SIZE + 6, cy * TILE_SIZE + 6, TILE_SIZE - 12, TILE_SIZE - 12)
        rat_rect = pygame.Rect(rx * TILE_SIZE + 5, ry * TILE_SIZE + 5, TILE_SIZE - 10, TILE_SIZE - 10)
        pygame.draw.rect(self.screen, CHEESE, cheese_rect, border_radius=6)
        pygame.draw.rect(self.screen, RAT, rat_rect, border_radius=8)

        # Score and controls
        hud_rect = pygame.Rect(0, GRID_H * TILE_SIZE, GRID_W * TILE_SIZE, 40)
        pygame.draw.rect(self.screen, (10, 10, 12), hud_rect)
        msg = f"Score: {self.score}   |   R: reset map   ESC: quit"
        self.screen.blit(self.font.render(msg, True, TEXT), (8, GRID_H * TILE_SIZE + 10))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.reset_map(keep_score=True)

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    Game().run()
