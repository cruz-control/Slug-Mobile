from node import Node
from pubsub import get_topic, set_topic

class Teleop(Node):
    def __init__(self):
        super().__init__()

    def start(self):
        pass

    def clamp(self, x, a, b):
        return min(b, max(a, x))

    def update(self):
        # Get controller input
        x = get_topic('controller/right_x')
        y = -get_topic('controller/left_y')

        # Use quadratic scaling for easier control at low speeds
        x *= abs(x)
        y *= abs(y)

        # Reduce dead zone
        if y > 0:
            y += 15 / 400
        else:
            y -= 15 / 400
        
        # Clamp y in the allowed range and set pulse widths
        y = self.clamp(y, -1, 1)
        set_topic('motors/drive', y)
        set_topic('motors/steer', x)

    def stop(self):
        pass