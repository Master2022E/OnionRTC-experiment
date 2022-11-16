import functools

from stem import StreamStatus
from stem.control import EventType, Controller
import os

from dotenv import load_dotenv





def main():
  print("Tracking requests for tor exits. Press 'enter' to end.")
  print("")

  load_dotenv()

  with Controller.from_port(port=9051) as controller:
    controller.authenticate(os.environ.get("TOR_CONTROL_PASSWORD",None))

    stream_listener = functools.partial(stream_event, controller)
    controller.add_event_listener(stream_listener, EventType.STREAM)

    input()  # wait for user to press enter


def stream_event(controller, event):
  if (event.status == StreamStatus.SUCCEEDED or event.status == StreamStatus.CLOSED) and event.circ_id:
    if ":3478" in event.target :
     
      print(event.target_address,event.target,event)
      print("Circuit id: ",event.circ_id)
      circ = controller.get_circuit(event.circ_id)

      exit_fingerprint = circ.path[-1][0]
      exit_relay = controller.get_network_status(exit_fingerprint)

      print("Exit relay for our connection to %s" % (event.target))
      print("  address: %s:%i" % (exit_relay.address, exit_relay.or_port))
      print("  fingerprint: %s" % exit_relay.fingerprint)
      print("  nickname: %s" % exit_relay.nickname)
      print("  locale: %s" % controller.get_info("ip-to-country/%s" % exit_relay.address, 'unknown'))
      print("")


if __name__ == '__main__':
  main()