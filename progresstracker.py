
import threading


class ProgressTracker:
    """Shared progress and stop signal between the moderation worker thread and the terminal."""

    def __init__(self):
        self.__lock = threading.Lock()            # One thread at a time
        self.__stop_event = threading.Event()
        self.__done = 0
        self.__total = 0

    def start(self, total: int) -> None:
        """Called by the worker when number of comments is known."""
        with self.__lock:
            self.__total = total
            self.__done = 0

    def record_done(self) -> None:
        """Called by the worker after each comment."""
        with self.__lock:
            self.__done +=1 

    def snapshot(self) -> tuple[int, int]:
        """Called by the main thread to draw the progress bar."""
        with self.__lock:
            return self.__done, self.__total

    def request_stop(self) -> None:
        """Called by the main thread when the user presses Ctrl+C."""
        self.__stop_event.set()

    @property
    def stop_requested(self) -> bool:
        return self.__stop_event.is_set()

    def pause(self, seconds: float) -> bool:
        """Returns True if it woke because of a stop, False if the full duration passed."""
        return self.__stop_event.wait(seconds)