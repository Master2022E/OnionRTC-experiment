import queue
import time
from stem.control import EventType, Controller
import os
from dotenv import load_dotenv

# Taken from https://stem.torproject.org/tutorials/tortoise_and_the_hare.html

with Controller.from_port() as controller:
  load_dotenv()
  controller.authenticate(os.environ.get("TOR_CONTROL_PASSWORD",None))

  start_time = time.time()
  event_queue = queue.Queue()

  controller.add_event_listener(lambda event: event_queue.put(event), EventType.BW)

  while time.time() - start_time < 2:
    event = event_queue.get()
    print('I got a BW event for %i bytes downloaded and %i bytes uploaded' % (event.read, event.written))