from pubsub import set_topic


class Sensor:
    """
    Base class for sensors
    """

    def __init__(self):
        pass

    def update(self):
        """
        Updates the sensor if needed. This must be implemented, and it should call set_topic().
        """
        raise NotImplementedError("update() needs to be implemented")

    def set_topic(self, topic: str, value: any) -> None:
        """
        Calling set_topic on a sensor is the same as calling it on pubsub.
        """
        set_topic(topic, value)
