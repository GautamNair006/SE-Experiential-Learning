import math

class Fruit:
    def __init__(self, x, y, vx, vy, gravity, radius=28, kind="fruit"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.gravity = gravity
        self.radius = radius
        self.kind = kind  # "fruit" or "bomb"
        self.sliced = False

    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy

    def contains_point(self, x, y):
        return math.hypot(self.x - x, self.y - y) <= self.radius

    def intersects_segment(self, p1, p2):
        """Checks if the line segment from p1 to p2 intersects this fruit's circle."""
        x1, y1 = p1
        x2, y2 = p2

        # Vector from p1 to p2
        dx = x2 - x1
        dy = y2 - y1

        # Length squared of segment
        len_sq = dx * dx + dy * dy
        if len_sq == 0:
            return self.contains_point(x1, y1)

        # Projection parameter t of circle center onto line segment [0, 1]
        t = max(0.0, min(1.0, ((self.x - x1) * dx + (self.y - y1) * dy) / len_sq))

        # Closest point on the segment to the fruit's center
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy

        # Distance from closest point to fruit center
        return math.hypot(self.x - closest_x, self.y - closest_y) <= self.radius

    def off_screen(self, height):
        return self.y - self.radius > height