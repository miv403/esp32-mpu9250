import pygame
import math
import sys
import time
import threading
import queue
from device import Device

# Screen dimensions
WIDTH, HEIGHT = 800, 600
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2 + 40

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 0, 0)
GREEN = (0, 200, 0)
BLUE = (80, 180, 255)
SKY = (120, 180, 255)
GROUND = (132, 157, 29)
GRAY = (180, 180, 180)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Attitude indicator')
font = pygame.font.SysFont('Liberation Mono', 18)
font_small = pygame.font.SysFont('Liberation Mono', 14)


class StdoutCatcher:
    # Device class prints all serial to stdout
    # it should be redirect to use properly
    def __init__(self, q):
        self.q = q
        self._buffer = ''
    def write(self, s):
        self._buffer += s
        while '\n' in self._buffer:
            line, self._buffer = self._buffer.split('\n', 1)
            self.q.put(line)
    def flush(self):
        pass

def data_reader_thread(q, error_q):
    # uses StdoutCatcher to redirect stdout
    # pushes all lines to queue
    import sys as _sys
    try:
        esp32 = None
        catcher = StdoutCatcher(q)
        old_stdout = _sys.stdout
        _sys.stdout = catcher
        try:
            esp32 = Device()
        finally:
            _sys.stdout = old_stdout
    except Exception as e:
        error_q.put(str(e))

def draw_horizon(surface, roll, pitch):
    # SKY ve GROUND dikdörtgenlerini çizer ve 
    # pitch değerine göre yüksekliklerini hesaplar
    # roll değerine göre dikdörtgenleri döndürür
    
    roll = -roll  # Reverse roll for correct direction

    pitch_offset =  pitch * 3
    H = WIDTH * 2  # or HEIGHT * 2, just make sure it's big enough
    W = HEIGHT * 2

    horizon_surface = pygame.Surface((W, H), pygame.SRCALPHA)
    horizon_center_y = H // 2

    horizon_line_y = horizon_center_y + pitch_offset

    pygame.draw.rect(horizon_surface, SKY, (0, 0, W, horizon_line_y))
    pygame.draw.rect(horizon_surface, GROUND, (0, horizon_line_y, W, H - horizon_line_y))

    rotated_horizon = pygame.transform.rotate(horizon_surface, roll)
    rect = rotated_horizon.get_rect(center=(CENTER_X, CENTER_Y))

    surface.blit(rotated_horizon, rect)

def draw_pitch_ruler(surface, roll):
    # renders the lines to measure pitch.
    # uses roll values to make it parallel with horizon
    
    line_length = WIDTH // 5
    spacing = 30  # pixels between lines
    center_x = CENTER_X
    center_y = CENTER_Y

    # The pitch values for the markers (in degrees)
    pitch_values = [-45, -40, -35, -30, -25, -20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45]

    for i, p in enumerate(pitch_values):
        if i % 2 != 0:
            line_length /= 1.5

        # Offset from center, positive p is above, negative is below
        offset = -p * spacing / 10  # e.g., -20 -> +30px above, +20 -> -30px below
        # Calculate the center of this marker, rotated by roll
        dx = -math.sin(math.radians(roll)) * offset
        dy = math.cos(math.radians(roll)) * offset
        cx = center_x + dx
        cy = center_y + dy

        # Calculate the endpoints of the short line, perpendicular to roll
        angle = math.radians(roll)
        dx_line = (line_length / 2) * math.cos(angle)
        dy_line = (line_length / 2) * math.sin(angle)
        x1 = cx - dx_line
        y1 = cy - dy_line
        x2 = cx + dx_line
        y2 = cy + dy_line

        pygame.draw.line(surface, WHITE, (x1, y1), (x2, y2), 2)
        if i % 2 == 0:
            # Draw the pitch value label next to the line
            label = font_small.render(str(p), True, WHITE)
            label_offset = 10  # distance from the line
            label_x = cx - (line_length / 2) * math.cos(angle) - label.get_width() - label_offset
            label_y = cy - (line_length / 2) * math.sin(angle) - label.get_height() // 2
            surface.blit(label, (label_x, label_y))

        line_length = WIDTH // 5

def draw_compass(surface, yaw):
    # Compass in right bottom corner, use yaw directly
    yaw -= 180
    radius = 30
    margin = 65
    cx = WIDTH - radius - margin 
    cy = HEIGHT - radius - margin
    pygame.draw.circle(surface, WHITE, (cx, cy), radius, 2)
    directions = ['N', 'E', 'S', 'W']
    for i, d in enumerate(directions):
        angle = math.radians(i * 90)
        tx = cx + (radius + 15) * math.sin(angle)
        ty = cy - (radius + 15) * math.cos(angle)
        label = font_small.render(d, True, WHITE)
        surface.blit(label, (tx - label.get_width() // 2, ty - label.get_height() // 2))
    arrow_angle = math.radians(yaw)  # Use yaw directly
    ax = cx + radius * math.sin(arrow_angle)
    ay = cy - radius * math.cos(arrow_angle)
    pygame.draw.line(surface, RED, (cx, cy), (ax, ay), 4)
    head_len = 10
    left = math.radians(yaw - 20)
    right = math.radians(yaw + 20)
    lx = cx + (radius - head_len) * math.sin(left)
    ly = cy - (radius - head_len) * math.cos(left)
    rx = cx + (radius - head_len) * math.sin(right)
    ry = cy - (radius - head_len) * math.cos(right)
    pygame.draw.polygon(surface, RED, [(ax, ay), (lx, ly), (rx, ry)])

def draw_overlays(  surface, roll, pitch, yaw,
                    accel, gyro, mag, temp,
                    serial_error, last_data_time):
    
    # renders sensor data and errors on screen
    
    pygame.draw.rect(surface, BLACK, (0, 0, WIDTH, 30))
    pygame.draw.rect(surface, BLACK, (0, HEIGHT - 30, WIDTH, 30))
    rpy = font_small.render(f'Roll: {roll:.1f}  Pitch: {pitch:.1f}  Yaw: {yaw:.1f}', True, WHITE)
    surface.blit(rpy, (10, HEIGHT - 55))

    now = time.time()

    accelstr = f"Accel: {accel[0]:.1f},{accel[1]:.1f},{accel[2]:.1f}"
    gyrostr  = f"Gyro: {gyro[0]:.1f},{gyro[1]:.1f},{gyro[2]:.1f}"
    magstr   = f"Mag: {mag[0]:.1f},{mag[1]:.1f},{mag[2]:.1f}"
    tempstr  = f"Temp: {temp:.1f}"

    accel_render = font_small.render(accelstr , True, WHITE)
    gyro_render  = font_small.render(gyrostr  , True, WHITE)
    mag_render   = font_small.render(magstr   , True, WHITE)
    temp_render  = font_small.render(tempstr  , True, WHITE)

    surface.blit(accel_render, (WIDTH - 190, HEIGHT - 220))
    surface.blit(gyro_render , (WIDTH - 190, HEIGHT - 205))
    surface.blit(mag_render  , (WIDTH - 190, HEIGHT - 190))
    surface.blit(temp_render , (WIDTH - 190, HEIGHT - 175))

    if serial_error:
        err = font.render(f'Serial error: {serial_error}', True, RED)
        surface.blit(err, (CENTER_X - err.get_width() // 2, HEIGHT // 2))
    elif now - last_data_time > 2:
        warn = font.render('No data from device!', True, RED)
        surface.blit(warn, (CENTER_X - warn.get_width() // 2, HEIGHT // 2))

def draw_roll_arc(surface, roll, center_x=CENTER_X, top_margin=110, arc_radius=120):

    # renders an angle meter to show roll data top of the screen

    arc_center = (center_x, top_margin + arc_radius)
    arc_start = -150  # leftmost angle (degrees, 0=right, 90=down)
    arc_end = -30     # rightmost angle

    # Draw tick marks and labels
    for angle in range(arc_start, arc_end+1, 10):  # every 10°
        rad = math.radians(angle)
        # Start and end points of the tick
        x1 = arc_center[0] + arc_radius * math.cos(rad)
        y1 = arc_center[1] + arc_radius * math.sin(rad)
        tick_length = 16 if angle % 30 == 0 else 8
        x2 = arc_center[0] + (arc_radius + tick_length) * math.cos(rad)
        y2 = arc_center[1] + (arc_radius + tick_length) * math.sin(rad)
        pygame.draw.line(surface, WHITE, (x1, y1), (x2, y2), 2)
        # Draw label at major ticks
        if angle % 30 == 0:
            label_val = angle + 90  # -60 to +60
            label = font_small.render(str(label_val), True, WHITE)
            lx = arc_center[0] + (arc_radius + tick_length + 18) * math.cos(rad) - label.get_width() // 2
            ly = arc_center[1] + (arc_radius + tick_length + 18) * math.sin(rad) - label.get_height() // 2
            surface.blit(label, (lx, ly))

    # Draw red triangle pointer for current roll
    # Clamp roll to [-60, 60]
    roll = max(-60, min(60, roll))
    pointer_angle = math.radians(roll - 90)  # convert roll to arc angle
    px = arc_center[0] + (arc_radius - 24) * math.cos(pointer_angle)
    py = arc_center[1] + (arc_radius - 24) * math.sin(pointer_angle)
    # Triangle points
    tri_base = 10
    tri_height = 18
    # Perpendicular direction for base
    perp_angle = pointer_angle + math.pi / 2
    p1 = (px, py)
    p2 = (px + tri_base * math.cos(perp_angle), py + tri_base * math.sin(perp_angle))
    p3 = (px - tri_base * math.cos(perp_angle), py - tri_base * math.sin(perp_angle))
    p_tip = (px + tri_height * math.cos(pointer_angle), py + tri_height * math.sin(pointer_angle))
    pygame.draw.polygon(surface, RED, [p2, p3, p_tip])

def draw_compass_strip(surface, yaw, margin=30, strip_width=500, strip_height=36):
    cx = WIDTH // 2
    top = margin
    left = cx - strip_width // 2
    right = cx + strip_width // 2

    # Draw background
    pygame.draw.rect(surface, (30, 30, 30), (left, top, strip_width, strip_height), border_radius=8)
    pygame.draw.rect(surface, WHITE, (left, top, strip_width, strip_height), 2, border_radius=8)

    # Tick parameters
    tick_spacing = 15  # degrees between ticks
    px_per_deg = strip_width / 120  # show ±60° around current yaw
    major_tick_len = 18

    # The range of degrees to show (centered on yaw)
    min_deg = yaw - 60
    max_deg = yaw + 60

    # Draw ticks and labels
    for deg in range(int(min_deg // tick_spacing) * tick_spacing, int(max_deg // tick_spacing + 1) * tick_spacing, tick_spacing):
        # Compute position relative to center
        rel_deg = (deg - yaw)
        # Wrap rel_deg to [-180, 180] for correct display
        if rel_deg < -180:
            rel_deg += 360
        elif rel_deg > 180:
            rel_deg -= 360
        x = cx + rel_deg * px_per_deg
        if left <= x <= right:
            # Draw tick
            pygame.draw.line(surface, WHITE, (x, top + strip_height - 1), (x, top + strip_height - major_tick_len), 2)
            # Draw label
            label_deg = deg % 360
            if label_deg in [0, 90, 180, 270]:
                label = {0: 'N', 90: 'E', 180: 'S', 270: 'W'}[label_deg]
                label_surf = font.render(label, True, WHITE)
                surface.blit(label_surf, (x - label_surf.get_width() // 2, top + 2))
            else:
                label_surf = font_small.render(str(int(label_deg)), True, GRAY)
                surface.blit(label_surf, (x - label_surf.get_width() // 2, top + 2))

    # Draw center indicator (triangle)
    tri_w = 16
    tri_h = 12
    tri_x = cx
    tri_y = top + strip_height - 2
    pygame.draw.polygon(surface, RED, [
        (tri_x, tri_y),
        (tri_x - tri_w // 2, tri_y - tri_h),
        (tri_x + tri_w // 2, tri_y - tri_h)
    ])

# serial port data format:
#   roll,pitch,yaw,accX,accY,accZ,gyroX,gyroY,gyroZ,magX,magY,magZ,temp
def main():
    last_data_time = 0
    serial_error = None

    rpy   = [0.0, 0.0, 0.0] # roll-pitch-yaw
    accel = [0.0, 0.0, 0.0]
    gyro  = [0.0, 0.0, 0.0]
    mag   = [0.0, 0.0, 0.0]
    temp = 0                # temprature

    clock = pygame.time.Clock()
    data_q = queue.Queue()
    error_q = queue.Queue()
    t = threading.Thread(   target=data_reader_thread,
                            args=(data_q, error_q), daemon=True)
    t.start()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # Get latest data from queue
        try:
            while True:
                line = data_q.get_nowait()
                line = line.strip()
                if line and (',' in line):
                    parts = line.split(',')
                    if len(parts) == 13:
                        try:
                            rpy[0],   rpy[1],   rpy[2]   = map(float, parts[0:3])
                            accel[0], accel[1], accel[2] = map(float, parts[3:6])
                            gyro[0],  gyro[1],  gyro[2]  = map(float, parts[6:9])
                            mag[0],   mag[1],   mag[2]   = map(float, parts[9:12])
                            temp                         = float(     parts[12])
                            last_data_time = time.time()
                        except ValueError:
                            pass
        except queue.Empty:
            pass
        try:
            while True:
                serial_error = error_q.get_nowait()
        except queue.Empty:
            pass
        screen.fill(BLACK)
        draw_horizon      ( screen, rpy[0], rpy[1])
        draw_pitch_ruler  ( screen, rpy[0])
        draw_roll_arc     ( screen, rpy[0])
        draw_compass      ( screen, rpy[2])
        draw_compass_strip( screen, rpy[2])
        draw_overlays     ( screen, rpy[0], rpy[1], rpy[2],
                            accel, gyro, mag, temp,
                            serial_error, last_data_time)
        pygame.display.flip() # swaps the display buffer
        clock.tick(60)
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main() 
