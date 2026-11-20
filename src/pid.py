import time

class PID:
    def __init__(self, kp, ki, kd, integral_range=None, max_integral=None):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral_range = integral_range
        self.max_integral = max_integral
        self.reset()
    
    def reset(self):
        self.integral = 0
        self.previous_error = 0
        self.previous_time = None

    def calculate(self, error, time=None):
        if time is None:
            time = time.time()
        dt = time - self.previous_time if self.previous_time is not None else 0
        self.previous_time = time

        if self.integral_range is not None and abs(error) > self.integral_range:
            self.integral = 0
        else:
            self.integral += error * dt
            if self.max_integral is not None:
                self.integral = max(-self.max_integral, min(self.max_integral, self.integral))

        derivative = (error - self.previous_error) / dt if dt > 1e-9 else 0
        self.previous_error = error

        return self.kp * error + self.ki * self.integral + self.kd * derivative
