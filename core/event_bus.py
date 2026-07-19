class EventBus:
    """Pub/Sub — מתווך בין מי שמכריז על אירועים למי שמאזין."""

    def __init__(self):
        self.subscribers = {}

    # "כשיקרה האירוע הזה בעתיד — אנא הפעל את הפונקציה שלי."
    def subscribe(self, event_name, callback):
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []   # יוצרים רשימה ריקה אם אין
        self.subscribers[event_name].append(callback)

    # "האירוע קרה עכשיו! לכי למגירה שלו, והפעילי את כל הפונקציות שיש בה."
    def publish(self, event_name, data=None):
        for callback in self.subscribers.get(event_name, []):
            callback(data)


if __name__ == "__main__":
    bus = EventBus()
    received = []

    bus.subscribe("test_event", lambda data: received.append(data))
    bus.publish("test_event", "hello")
    bus.publish("nobody_listens", "should not crash")

    assert received == ["hello"], f"expected ['hello'], got {received}"
    print("EventBus OK")