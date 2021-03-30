import queue


class MessageAnnouncer:
    """ Creates sse announcer
    """

    def __init__(self):
        """ Inits array
        """

        self.listeners = []

    def listen(self):
        """ Creates queue

        Returns:
            queue: Message queue
        """

        q = queue.Queue(maxsize=5)
        self.listeners.append(q)
        return q

    def announce(self, msg):
        """ Announces message

        Args:
            msg (str): Message
        """

        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(msg)
            except queue.Full:
                del self.listeners[i]
