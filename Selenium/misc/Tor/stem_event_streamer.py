import functools
import time
try:
  from misc.Tor.stem_circuit_info import return_circuit_status 
except:
  from stem_circuit_info import return_circuit_status 
from stem import StreamStatus, SocketError
from stem.connection import IncorrectPassword, MissingPassword, MissingAuthInfo
from stem.control import EventType, Controller
import os

from dotenv import load_dotenv

# Originally from https://stem.torproject.org/tutorials/examples/exit_used.html


logging_global = print
controller = None
vars_global = None

def is_tor_ready():
  global controller
  global logging_global

  if controller is None:
    setup_controller()

  response=controller.get_info("status/bootstrap-phase")
  if(response.find('SUMMARY="Done"') > 0):
    logging_global("bootstrapped OK, Tor is ready to use")
    return True
  else:
    #FIXME: Should be a warning instead of logging.info
    logging_global("Bootstrap not finished: " + response)
    return False


def setup_controller(logging=None):
  global controller
  global logging_global

  if logging is not None:
    logging_global = logging.info
  else:
    logging_global = print

  if controller is None:
    load_dotenv()
    try:
      controller = Controller.from_port(port=9051)
      controller.authenticate(os.environ.get("TOR_CONTROL_PASSWORD",None))
    except SocketError as e:
      # Error described: https://stem.torproject.org/api/control.html#stem.control.Controller
      # Could also start it ourself: https://stem.torproject.org/api/process.html
      logging_global("Error setting up controller: " + str(e))
      # FIXME: Report error to mongodb
      raise e
    except (IncorrectPassword, MissingPassword, MissingAuthInfo) as e:
      logging_global("Error setting up controller: " + str(e))
      # FIXME: Report error to mongodb
      raise e
    except Exception as e:
      logging_global("Error setting up controller: " + str(e))
      raise e
      

  return

def setup_event_streamer(vars=None,logging=None):
  global logging_global
  global controller
  global vars_global

  logging_global("Tracking requests for tor exits. Press 'enter' to end.")
  logging_global("")

  setup_controller(logging)


  stream_listener = functools.partial(stream_event, controller)
  controller.add_event_listener(stream_listener, EventType.STREAM)
  
  
  if vars is None: # If called by '__name__ == '__main__'
    input()  # wait for user to press enter
    close_event_streamer()
  else:
    vars_global = vars
  


def stream_event(controller, event):
  global vars_global
  if event.circ_id and (event.status == StreamStatus.SUCCEEDED ): # or event.status == StreamStatus.CLOSED):
    # if it is the TURN server that is the target
    if event.target_address == "130.225.170.247" and "3000" != str(event.target_port):
      logging_global("Found the TURN server!")
      logging_global(f"event.target {event.target }")


    if "3478" == str(event.target_port) : # This is not the correct port. It should be the port, that the TURN server allocates for the client.
     
      logging_global(f"{event.target_address},{event.target},{event}")
      logging_global(f"Circuit id: {event.circ_id}")
      circ = controller.get_circuit(event.circ_id)

      exit_fingerprint = circ.path[-1][0]
      exit_relay = controller.get_network_status(exit_fingerprint)

      logging_global("Exit relay for our connection to %s" % (event.target))
      logging_global("  address: %s:%i" % (exit_relay.address, exit_relay.or_port))
      logging_global("  fingerprint: %s" % exit_relay.fingerprint)
      logging_global("  nickname: %s" % exit_relay.nickname)
      try:
        logging_global("  locale: %s" % controller.get_info("ip-to-country/%s" % exit_relay.address, 'unknown'))
      except:
        pass

      if vars_global:
        vars_global.latest_circuit = return_circuit_status(exit_relay.address)

      logging_global("")
    

def close_event_streamer():
  global controller
  global vars_global
  
  
  if controller and type(controller) == Controller:
    logging_global(("Controller:",controller.is_alive(),"Socket:",controller.get_socket()._is_alive))
    result = controller.close()
    logging_global(("Controller:",controller.is_alive(),"Socket:",controller.get_socket()._is_alive))
    logging_global("Done closing the Tor controller")
    try:
      return vars_global.latest_circuit
    except:
      return {}
  else:
    return {}

import logging
import logging.handlers

if __name__ == '__main__':

  logging.basicConfig(
          format='%(asctime)s %(levelname)-8s %(message)s',
          level=logging.INFO,
          datefmt='%Y-%m-%d %H:%M:%S')
  setup_controller(logging)
  while not is_tor_ready():
    time.sleep(1)
  setup_event_streamer()