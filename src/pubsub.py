topics = dict()

def get_topic(topic: str) -> any:
    if not topic in topics:
        return None
    return topics[topic]
def set_topic(topic: str, value: any) -> None:
    topics[topic] = value
