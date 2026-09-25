from threading import Lock

topics = dict()
locks = dict()

def get_lock(topic):
    if not topic in locks:
        locks[topic] = Lock()
    return locks[topic]

def get_topic(topic: str) -> any:
    with get_lock(topic):
        if not topic in topics:
            return None
        return topics[topic]

def set_topic(topic: str, value: any) -> None:
    with get_lock(topic):
        topics[topic] = value
