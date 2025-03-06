import threading
import time


class ThreadManager:
    def __init__(self):
        """Initializes the thread manager."""
        self.threads: dict[str, threading.Thread] = {}
        self.stop_events: dict[str, threading.Event] = {}

    def start_thread(self, name, target, args=()):
        """
        Starts a new thread if it’s not already running.

        Parameters:
        - name (str): Unique thread name.
        - target (function): Function to run in the thread.
        - args (tuple): Arguments to pass to the function.
        """
        if name in self.threads and self.threads[name].is_alive():
            print(f"[WARNING] Thread '{name}' is already running.")
            return

        stop_event = threading.Event()
        self.stop_events[name] = stop_event
        thread = threading.Thread(
            target=target, args=(stop_event, *args), daemon=True
        )
        self.threads[name] = thread
        thread.start()
        print(f"[INFO] Thread '{name}' started.")

    def stop_thread(self, name):
        """
        Stops a running thread gracefully.

        Parameters:
        - name (str): Name of the thread to stop.
        """
        if name in self.stop_events:
            self.stop_events[name].set()  # Signal the thread to stop
            self.threads[name].join()  # Wait for it to terminate
            del self.threads[name]
            del self.stop_events[name]
            print(f"[INFO] Thread '{name}' stopped.")
        else:
            print(f"[ERROR] No such thread '{name}' found.")

    def stop_all_threads(self):
        """Stops all running threads."""
        for name in list(self.threads.keys()):
            self.stop_thread(name)

    def is_running(self, name):
        """Returns True if a thread is running, False otherwise."""
        return name in self.threads and self.threads[name].is_alive()

    def list_threads(self):
        """Returns a list of currently active threads."""
        return [
            name for name, thread in self.threads.items() if thread.is_alive()
        ]


# Example Usage
if __name__ == "__main__":

    # Example Worker Function
    def worker(stop_event, duration=10):
        """
        Simulated worker function that runs until stopped.

        Parameters:
        - stop_event (threading.Event): Event used to signal stopping.
        - duration (int): How long the thread runs before checking for stop signal.
        """
        print("[Worker] Thread started.")
        for i in range(duration):
            if stop_event.is_set():
                print("[Worker] Stopping thread.")
                break
            print(f"[Worker] Running... {i+1}")
            time.sleep(1)  # Simulate work
        print("[Worker] Thread exited.")

    manager = ThreadManager()

    # Start multiple threads
    manager.start_thread("task1", worker, (5,))
    manager.start_thread("task2", worker, (7,))

    time.sleep(3)  # Let them run for a while

    # Stop one thread
    manager.stop_thread("task1")

    # Check running threads
    print("Active threads:", manager.list_threads())

    # Stop all threads
    manager.stop_all_threads()
    print("All threads stopped.")
