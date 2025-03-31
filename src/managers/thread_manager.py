import threading
import time

from src.logging.logger import *
from src.utils.constants import *


class ThreadManager:
    def __init__(self):
        """Initializes the thread manager."""
        self.threads: dict[str, threading.Thread] = {}
        self.events: dict[str, threading.Event] = {}
        # Set up logging
        self.logger: logging = Logger(
            "ThreadManager",
            console_level=logging.INFO,
            console_logging=EN_CONSOLE_LOGGING,
        )

    def start_thread(self, name, target, args=()):
        """
        Starts a new thread if it's not already running.

        Parameters:
        - name (str): Unique thread name.
        - target (function): Function to run in the thread.
        - args (tuple): Arguments to pass to the function.
        """
        if name in self.threads and self.threads[name].is_alive():
            self.logger.warning(f"Thread '{name}' is already running.")
            return

        event = threading.Event()
        self.events[name] = event
        thread = threading.Thread(
            target=target, args=(event, *args), daemon=True
        )
        self.threads[name] = thread
        thread.start()
        self.logger.info(f"Thread '{name}' started.")

    def stop_thread(self, name):
        """
        Stops a running thread gracefully.

        Parameters:
        - name (str): Name of the thread to stop.
        """
        if name in self.events:
            if self.threads[name] is threading.current_thread():
                return
            self.events[name].set()  # Signal the thread to stop
            self.threads[name].join()  # Wait for it to terminate
            del self.threads[name]
            del self.events[name]
            self.logger.info(f"Thread '{name}' stopped.")
        else:
            self.logger.error(f"No such thread '{name}' found.")

    def stop_all_threads(self):
        """Stops all running threads."""
        for name in list(self.threads.keys()):
            self.stop_thread(name)

    def pause_thread(self, name):
        """
        Pauses a running thread.

        Parameters
        ----------
        name : str
            Name of the thread to pause.
        """
        if name in self.events:
            self.events[name].set()
            self.logger.info(f"Thread '{name}' paused.")
        else:
            self.logger.error(f"No such thread '{name}' found.")

    def resume_thread(self, name):
        """
        Resumes a paused thread.

        Parameters
        ----------
        name : str
            Name of the thread to resume.
        """
        if name in self.events:
            self.events[name].clear()
            self.logger.info(f"Thread '{name}' resumed.")
        else:
            self.logger.error(f"No such thread '{name}' found.")

    def is_running(self, name):
        """Returns True if a thread is running, False otherwise."""
        return name in self.threads and self.threads[name].is_alive()

    def is_paused(self, name):
        """Returns True if a thread is paused, False otherwise."""
        return self.events[name].is_set() and self.threads[name].is_alive()

    def list_threads(self):
        """Returns a list of currently active threads."""
        return [
            name for name, thread in self.threads.items() if thread.is_alive()
        ]


# Example Usage
if __name__ == "__main__":

    # Example Worker Function
    def worker(stop_event, pause_event, duration=10):
        """
        Simulated worker function that runs until stopped.

        Parameters
        ----------
        stop_event : threading.Event
            Event used to signal stopping.
        pause_event : threading.Event
            Event used to signal pausing.
        duration : int
            How long the thread runs before checking for stop signal.
        """
        print("[Worker] Thread started.")
        for i in range(duration):
            if stop_event.is_set():
                print("[Worker] Stopping thread.")
                break
            while pause_event.is_set():
                time.sleep(0.1)  # Wait while paused
            print(f"[Worker] Running... {i+1}")
            time.sleep(1)  # Simulate work
        print("[Worker] Thread exited.")

    manager = ThreadManager()

    # Start multiple threads
    manager.start_thread("task1", worker, (10,))
    manager.start_thread("task2", worker, (15,))

    time.sleep(3)  # Let them run for a while

    # Pause one thread
    manager.pause_thread("task1")
    time.sleep(2)  # Pause for a while
    manager.resume_thread("task1")

    # Stop one thread
    manager.stop_thread("task1")

    # Check running threads
    print("Active threads:", manager.list_threads())

    # Stop all threads
    manager.stop_all_threads()
    print("All threads stopped.")
