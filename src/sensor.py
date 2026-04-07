class Sensor:
    """
    Base class for sensors
    """
    def __init__(slef):
        pass
    def update(self):
        """
        Updates the sensor if needed. Implementation is optional for sensors.
        """
        pass
    def get_frame(self):
        """
        Returns the most recent sensor frame. This must be implemented by all subclasses.
        """
        raise NotImplementedError("get_frame() needs to be implemented")

