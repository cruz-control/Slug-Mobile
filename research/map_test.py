
"""
Hokuyo (hokuyolx) -> pygame graph, with every scan logged to CSV.
 
    pip install hokuyolx pygame
 
    python lidar_plot.py                  # live: plot + log to scan_<date>.csv
    python lidar_plot.py scan_xxx.csv     # replay a logged CSV
 
CSV format: header = "timestamp" + one angle (rad) per column,
            each row = timestamp + one distance (mm) per column.
"""
import csv
import math
import sys
import time
from typing import List, Optional
 
import pygame
from hokuyolx import HokuyoLX
 
SIZE = 600            # graph is SIZE x SIZE pixels
MAX_RANGE_MM = 5000   # distance at the edge of the graph
MIN_RANGE_MM = 20     # readings below this are error codes
 
lidar: Optional[HokuyoLX] = None
timestamp = -1
distances: List[float] = []
screen: Optional[pygame.Surface] = None
 
 
def init_graph(size: int):
    global screen, SIZE
    SIZE = size
    pygame.init()
    screen = pygame.display.set_mode((size, size))
    pygame.display.set_caption("Hokuyo scan")
 
 
def clear_graph():
    """Background + a ring every metre + the sensor at the centre."""
    screen.fill((10, 12, 16))
    c = SIZE // 2
    for r_mm in range(1000, MAX_RANGE_MM + 1, 1000):
        pygame.draw.circle(screen, (45, 52, 62), (c, c), int(r_mm * c / MAX_RANGE_MM), 1)
    pygame.draw.circle(screen, (255, 255, 255), (c, c), 4)
 
 
def plot(x: float, y: float):
    """Plot one point (mm; x = right, y = forward) on the graph."""
    c = SIZE / 2
    scale = c / MAX_RANGE_MM
    px, py = int(c + x * scale), int(c - y * scale)
    if 0 <= px < SIZE and 0 <= py < SIZE:
        pygame.draw.circle(screen, (0, 255, 120), (px, py), 2)
 
 
def draw_scan(angles, dists):
    clear_graph()
    for a, d in zip(angles, dists):
        if d < MIN_RANGE_MM:
            continue
        # angle 0 = straight ahead; flip the sign of x if your plot is mirrored
        plot(-d * math.sin(a), d * math.cos(a))
    pygame.display.flip()
 
 
def alive() -> bool:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key in (pygame.K_q, pygame.K_ESCAPE)):
            return False
    return True
 
 
def update(writer=None):
    global timestamp, distances
    timestamp, scan = lidar.get_dist()
    angles = lidar.get_angles()
    distances = [float(d) for d in scan]
    draw_scan(angles, distances)
    if writer:
        writer.writerow([timestamp, *distances])
 
 
def live():
    global lidar
    lidar = HokuyoLX()
    init_graph(SIZE)
    path = time.strftime("scan_%Y%m%d_%H%M%S.csv")
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", *lidar.get_angles()])
        while alive():
            update(writer)
    lidar.close()
    print("saved", path)
 
 
def replay(path: str):
    init_graph(SIZE)
    with open(path) as f:
        rows = csv.reader(f)
        angles = [float(a) for a in next(rows)[1:]]
        prev = None
        for row in rows:
            if not alive():
                break
            ts = float(row[0])
            draw_scan(angles, [float(d) for d in row[1:]])
            if prev is not None:  # pace playback by the recorded timestamps (ms)
                pygame.time.wait(int(min(max(ts - prev, 0), 1000)))
            prev = ts
 
 
if __name__ == "__main__":
    replay(sys.argv[1]) if len(sys.argv) > 1 else live()