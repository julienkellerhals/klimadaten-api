import queue


class MessageAnnouncer:
    """ Creates sse announcer
    """

    def __init__(self):
        """ Inits array
        """

        self.listeners = []

    def format_sse(self, data: str) -> str:
        """ Converts string to sse format

        Args:
            data (str): String to be converted to sse format

        Returns:
            str: sse string
        """

        msg = f'data: {data}\n\n'
        return msg

    def stream(self):
        """ Creates stream

        Yields:
            str: Message yield
        """

        messages = self.listen()  # returns a queue.Queue

        while True:
            msg = messages.get()  # blocks until a new message arrives
            yield msg

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
