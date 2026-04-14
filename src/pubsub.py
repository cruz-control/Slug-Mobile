topics = dict()

def get_topic(topic: str) -> any:
    with topic:
        if not topic in topics:
            return None
        return topics[topic]
def set_topic(topic: str, value: any) -> None:
    with topic:
        topics[topic] = value
