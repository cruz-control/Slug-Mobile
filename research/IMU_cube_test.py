"""
LSM9DS1 IMU -> rotating cube + colored arrows (pygame). Runs on a Raspberry Pi.

    pip install pygame adafruit-circuitpython-lsm9ds1

    python imu_cube.py               # live: show cube, log to imu_<date>.csv
    python imu_cube.py imu_xxx.csv   # replay a logged CSV (works on any PC)

Keys: Q / ESC = quit, R = zero the velocity estimate.

World frame is x = north, y = west, z = up. All arrows are drawn in that
world frame, so the magnetic-field arrow should stay put while the cube turns.
"""
import csv
import math
import sys
import time

import pygame

G = 9.80665                 # m/s^2
MAG_SIGN = (-1, -1, 1)      # LSM9DS1 mag X/Y can be inverted vs accel/gyro.
                            # If the cube yaws the wrong way, try (1, 1, 1).
W, H = 800, 600
CUBE_HALF = 0.8

# name, color, scale (world units per unit of the quantity), unit
ARROWS = [
    ("Heading (cube +X face)", (0, 255, 255), 2.0, ""),
    ("Acceleration (gravity removed)", (255, 70, 70), 0.30, "m/s^2"),
    ("Velocity (estimated)", (255, 220, 0), 2.0, "m/s"),
    ("Angular velocity", (80, 255, 80), 0.8, "rad/s"),
    ("Magnetic field", (90, 140, 255), 5.0, "gauss"),
]
MAX_ARROW = 2.8

# ---- sensor values (same globals as before) ----
sensor = None
accel = (0, 0, 0)
gyro = (0, 0, 0)
mag = (0, 0, 0)
temp = 0
timestamp = -1

# ---- estimator state ----
q = [1.0, 0.0, 0.0, 0.0]    # body -> world quaternion (w, x, y, z)
vel = [0.0, 0.0, 0.0]       # world frame, m/s
lin_acc = [0.0, 0.0, 0.0]   # world frame, gravity removed
last_ts = None
t_start = None

screen = None
font = None


# ----------------------------------------------------------------- IMU side
def init_sensor():
    global sensor
    import board
    import busio
    import adafruit_lsm9ds1
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_lsm9ds1.LSM9DS1_I2C(i2c)


def update():
    """Read the IMU, then run the orientation filter."""
    global accel, gyro, mag, temp, timestamp
    accel = sensor.acceleration      # (x, y, z) m/s^2
    gyro = sensor.gyro               # (x, y, z) rad/s
    mag = sensor.magnetic            # (x, y, z) gauss
    temp = sensor.temperature        # deg C
    timestamp = time.time()
    process()


def rot(q):
    """Rotation matrix body -> world."""
    w, x, y, z = q
    return ((1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)),
            (2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)),
            (2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)))


def mul(R, v):
    return tuple(R[i][0] * v[0] + R[i][1] * v[1] + R[i][2] * v[2] for i in range(3))


def norm(v):
    return math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)


def mag_aligned():
    return tuple(m * s for m, s in zip(mag, MAG_SIGN))


def process():
    """Mahony AHRS (gyro + accel + mag), then gravity-free accel and velocity."""
    global q, vel, lin_acc, last_ts, t_start
    if last_ts is None:
        last_ts = t_start = timestamp
        return
    dt = min(max(timestamp - last_ts, 0.0), 0.2)
    last_ts = timestamp
    kp = 8.0 if timestamp - t_start < 2.0 else 1.0   # converge fast at start

    w, x, y, z = q
    ax, ay, az = accel
    gx, gy, gz = gyro
    ex = ey = ez = 0.0
    an = norm(accel)
    if an > 0:
        ax, ay, az = ax / an, ay / an, az / an
        vx = 2 * (x * z - w * y)                      # gravity dir in body frame
        vy = 2 * (w * x + y * z)
        vz = w * w - x * x - y * y + z * z
        ex, ey, ez = ay * vz - az * vy, az * vx - ax * vz, ax * vy - ay * vx
        m = mag_aligned()
        mn = norm(m)
        if mn > 0:
            mx, my, mz = m[0] / mn, m[1] / mn, m[2] / mn
            hx = 2 * mx * (0.5 - y * y - z * z) + 2 * my * (x * y - w * z) + 2 * mz * (x * z + w * y)
            hy = 2 * mx * (x * y + w * z) + 2 * my * (0.5 - x * x - z * z) + 2 * mz * (y * z - w * x)
            bx = math.hypot(hx, hy)
            bz = 2 * mx * (x * z - w * y) + 2 * my * (y * z + w * x) + 2 * mz * (0.5 - x * x - y * y)
            wx = 2 * bx * (0.5 - y * y - z * z) + 2 * bz * (x * z - w * y)
            wy = 2 * bx * (x * y - w * z) + 2 * bz * (w * x + y * z)
            wz = 2 * bx * (w * y + x * z) + 2 * bz * (0.5 - x * x - y * y)
            ex += my * wz - mz * wy
            ey += mz * wx - mx * wz
            ez += mx * wy - my * wx
    gx, gy, gz = gx + kp * ex, gy + kp * ey, gz + kp * ez

    w, x, y, z = (w + 0.5 * dt * (-x * gx - y * gy - z * gz),
                  x + 0.5 * dt * (w * gx + y * gz - z * gy),
                  y + 0.5 * dt * (w * gy - x * gz + z * gx),
                  z + 0.5 * dt * (w * gz + x * gy - y * gx))
    n = math.sqrt(w * w + x * x + y * y + z * z)
    q = [w / n, x / n, y / n, z / n]

    # linear acceleration (gravity removed) and a drift-limited velocity estimate
    a_w = mul(rot(q), accel)
    lin_acc = [a_w[0], a_w[1], a_w[2] - G]
    still = abs(norm(accel) - G) < 0.4 and norm(gyro) < 0.1
    decay = math.exp(-dt * (8.0 if still else 0.2))  # snap to 0 at rest, slow leak otherwise
    for i in range(3):
        vel[i] = (vel[i] + lin_acc[i] * dt) * decay


def euler_deg():
    w, x, y, z = q
    roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
    pitch = math.asin(max(-1.0, min(1.0, 2 * (w * y - z * x))))
    yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
    return math.degrees(roll), math.degrees(pitch), (-math.degrees(yaw)) % 360  # compass heading


# --------------------------------------------------------------- graphics side
def init_graph(w=W, h=H):
    global screen, font
    pygame.init()
    screen = pygame.display.set_mode((w, h))
    pygame.display.set_caption("IMU cube")
    font = pygame.font.Font(None, 22)


AZ, EL, CAM, SCALE = math.radians(35), math.radians(25), 9.0, 105.0


def project(p):
    """World (north, west, up) -> screen pixel, with a slight perspective."""
    n, wst, u = p
    e = -wst
    x1 = e * math.cos(AZ) - n * math.sin(AZ)
    y1 = e * math.sin(AZ) + n * math.cos(AZ)
    sx = x1
    sy = u * math.cos(EL) + y1 * math.sin(EL)
    depth = y1 * math.cos(EL) - u * math.sin(EL)
    f = CAM / (CAM + depth)
    return (screen.get_width() / 2 + sx * f * SCALE,
            screen.get_height() / 2 - sy * f * SCALE)


def draw_arrow(vec, scale, color):
    length = norm(vec) * scale
    if length < 0.05:
        return
    length = min(length, MAX_ARROW)
    k = length / norm(vec)
    p0 = project((0, 0, 0))
    p1 = project((vec[0] * k, vec[1] * k, vec[2] * k))
    pygame.draw.line(screen, color, p0, p1, 3)
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    l = math.hypot(dx, dy)
    if l < 8:
        return
    ux, uy = dx / l, dy / l
    pts = [p1]
    for s in (1, -1):
        c, sn = math.cos(math.radians(25)), s * math.sin(math.radians(25))
        pts.append((p1[0] - 13 * (ux * c - uy * sn), p1[1] - 13 * (uy * c + ux * sn)))
    pygame.draw.polygon(screen, color, pts)


def draw_cube(R):
    verts = [((i & 1) * 2 - 1, ((i >> 1) & 1) * 2 - 1, ((i >> 2) & 1) * 2 - 1) for i in range(8)]
    pts = [project(mul(R, tuple(c * CUBE_HALF for c in v))) for v in verts]
    for i in range(8):
        for bit in (1, 2, 4):
            j = i ^ bit
            if j > i:
                front = (i & 1) and (j & 1)           # the +X face is drawn brighter
                pygame.draw.line(screen, (235, 235, 235) if front else (120, 130, 145),
                                 pts[i], pts[j], 2 if front else 1)


def draw_grid():
    for k in range(-3, 4):
        pygame.draw.line(screen, (35, 42, 52), project((k, -3, -1.6)), project((k, 3, -1.6)))
        pygame.draw.line(screen, (35, 42, 52), project((-3, k, -1.6)), project((3, k, -1.6)))
    screen.blit(font.render("N", True, (140, 150, 165)), project((3.3, 0, -1.6)))


def draw_legend():
    pad, row = 8, 22
    width = max(font.size(name)[0] for name, *_ in ARROWS) + 2 * pad + 34
    height = len(ARROWS) * row + 2 * pad
    box = pygame.Surface((width, height), pygame.SRCALPHA)
    box.fill((20, 24, 30, 200))
    screen.blit(box, (screen.get_width() - width - 10, screen.get_height() - height - 10))
    for i, (name, color, _, _) in enumerate(ARROWS):
        y = screen.get_height() - height - 10 + pad + i * row + row // 2
        x = screen.get_width() - width - 10 + pad
        pygame.draw.line(screen, color, (x, y), (x + 22, y), 4)
        screen.blit(font.render(name, True, (210, 215, 225)), (x + 30, y - 7))


def draw_frame(status):
    screen.fill((10, 12, 16))
    draw_grid()
    R = rot(q)
    draw_cube(R)

    vectors = [
        (R[0][0], R[1][0], R[2][0]),           # heading = body +X axis in world
        lin_acc,
        vel,
        mul(R, gyro),
        mul(R, mag_aligned()),
    ]
    for vec, (_, color, scale, _) in zip(vectors, ARROWS):
        if norm(vec) > 1e-6:
            draw_arrow(vec, scale, color)

    roll, pitch, heading = euler_deg()
    lines = [status,
             f"roll {roll:+6.1f}  pitch {pitch:+6.1f}  heading {heading:5.1f} deg",
             f"|accel| {norm(lin_acc):4.2f} m/s^2   |vel| {norm(vel):4.2f} m/s",
             f"gyro {norm(gyro):4.2f} rad/s   temp {temp:4.1f} C"]
    for i, t in enumerate(lines):
        screen.blit(font.render(t, True, (200, 210, 220)), (10, 8 + i * 18))
    draw_legend()
    pygame.display.flip()


def alive():
    global vel
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            return False
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_q, pygame.K_ESCAPE):
                return False
            if ev.key == pygame.K_r:
                vel[:] = [0.0, 0.0, 0.0]
    return True


# ------------------------------------------------------------------- run modes
def live():
    init_sensor()
    init_graph()
    path = time.strftime("imu_%Y%m%d_%H%M%S.csv")
    clock = pygame.time.Clock()
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "ax", "ay", "az", "gx", "gy", "gz", "mx", "my", "mz", "temp"])
        while alive():
            update()
            writer.writerow([timestamp, *accel, *gyro, *mag, temp])
            draw_frame(f"LIVE  logging to {path}")
            clock.tick(60)
    print("saved", path)


def replay(path):
    global accel, gyro, mag, temp, timestamp
    init_graph()
    with open(path) as f:
        rows = csv.reader(f)
        next(rows)  # header
        prev = None
        for row in rows:
            if not alive():
                break
            v = [float(c) for c in row]
            timestamp, accel, gyro, mag, temp = v[0], tuple(v[1:4]), tuple(v[4:7]), tuple(v[7:10]), v[10]
            process()
            draw_frame(f"REPLAY  {path}")
            if prev is not None:
                pygame.time.wait(int(min(max((timestamp - prev) * 1000, 0), 500)))
            prev = timestamp


if __name__ == "__main__":
    replay(sys.argv[1]) if len(sys.argv) > 1 else live()