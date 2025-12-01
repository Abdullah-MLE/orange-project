import queue
import threading

class QueueManager:
    """
    A thread-safe wrapper around queue.Queue to manage the flow of classification results.
    """
    def __init__(self, max_size=1000):
        self._queue = queue.Queue(maxsize=max_size)
        self._lock = threading.Lock()

    def push(self, item):
        """
        Push an item into the queue.
        """
        try:
            self._queue.put(item, block=False)
        except queue.Full:
            pass

    def pop(self, block=True, timeout=None):
        """
        Pop an item from the queue.
        """
        try:
            return self._queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None

    def peek(self):
        """
        Peek at the head of the queue without removing it.
        """
        with self._queue.mutex:
            if self._queue.queue:
                return self._queue.queue[0]
            return None

    def size(self):
        """
        Return the current size of the queue.
        """
        return self._queue.qsize()

    def clear(self):
        """
        Clear all items from the queue.
        """
        with self._queue.mutex:
            self._queue.queue.clear()

    def get_all(self):
        """
        Return a list of all items in the queue (snapshot).
        Useful for GUI display.
        """
        with self._queue.mutex:
            return list(self._queue.queue)
