import os
import time

from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

load_dotenv()

DATA_DIR = os.getenv("DATA_DIR")


class OnWatch:
    """
    Starts monitoring changes @ data_dir
    """

    watch_dir = DATA_DIR

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watch_dir)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()
            print("Stopped monitoring data changes.")

        self.observer.join()


class Handler(FileSystemEventHandler):
    """
    Checks for FileSystem events
    """

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
        elif event.event_type == "created":
            pass
        elif event.event_type == "modified":
            pass
