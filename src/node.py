from pubsub import set_topic, get_topic

class Node:
    """
    Base class for nodes, including sensors
    """
    def __init__(self):
        pass
    def update(self):
        """
        Updates the sensor if needed. This must be implemented, and it should call set_topic() if it is a sensor.
        """
        raise NotImplementedError("update() needs to be implemented")
    def set_topic(self, topic: str, value: any) -> None:
        """
        Calling set_topic on a node is the same as calling it on pubsub.
        """
        set_topic(topic, value)
    def get_topic(self, topic: str) -> any:
        """
        Calling set_topic on a node is the same as calling it on pubsub.
        """
        return get_topic(topic)

