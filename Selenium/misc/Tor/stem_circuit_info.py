from stem import CircStatus
from stem.control import Controller
from hurry.filesize import size

from stem.util.log import get_logger
import os
global return_dict

# Orginally from: https://stem.torproject.org/tutorials/examples/exit_used.html
# Remixed with this: https://stem.torproject.org/tutorials/the_little_relay_that_could.html


def node_data(entry,controller):
  nickname = "Unknown"

  fingerprint, nickname = entry

  desc = controller.get_network_status(fingerprint, None)
  address = desc.address if desc else 'unknown'
  return fingerprint, nickname, desc, address

def printer(start_str,entry,controller,circuit_index):
  fingerprint, nickname, desc, address = node_data(entry,controller)
  IP = f"ip-to-country/{address}"
  #print(f"{start_str}: {fingerprint} ({nickname}, {address},{ controller.get_info(IP)})")
  return_dict["Circuits"][circuit_index][start_str] = {"Fingerprint":fingerprint,"Nickname":nickname,"Address":address,"Country":controller.get_info(IP)}


def return_circuit_status(exit_IP):
  global return_dict
  return_dict = {"Circuit_type":"Tor","Circuits":{}}
  with Controller.from_port(port = 9051) as controller:
    controller.authenticate(os.environ.get("TOR_CONTROL_PASSWORD",None))
    logger = get_logger()
    logger.propagate = False
    bytes_read = controller.get_info("traffic/read")
    bytes_written = controller.get_info("traffic/written")
    traffic_downloaded = size(int(bytes_read))
    traffic_uploaded = size(int(bytes_written))

    #print("The client has downloaded:",traffic_downloaded,"\nThe client has uploaded: ",traffic_uploaded)

    for circ in sorted(controller.get_circuits()):
      if circ.status != CircStatus.BUILT:
        continue

      
      if len(circ.path) == 1:
        continue
      entry_node, middle_node = circ.path[0], circ.path[1]
      for i, entry in enumerate(circ.path):
        div = '+' if (i == len(circ.path) - 1) else '|'
        _,_,_,address = node_data(entry,controller)
        
        if exit_IP == address and i == len(circ.path) - 1:
          return_dict["Circuits"][circ.id] = {}
          #print("")
          #print("Circuit %s (%s)" % (circ.id, circ.purpose))
          #print("Found a matching IP address of the exit node!")
          #printer("Entry Node",entry_node,controller,circ.id)
          #printer("Middle Node",middle_node,controller,circ.id)
          #printer("Exit node",entry,controller,circ.id)
  
  return return_dict 




if __name__ == "__main__":
  # Insert the IP you are looking for
  return_circuit_status("62.102.148.68")
    

"""
# From https://stem.torproject.org/tutorials/examples/list_circuits.html
with Controller.from_port(port = 9051) as controller:
  controller.authenticate(os.environ.get("TOR_CONTROL_PASSWORD",None))

  bytes_read = controller.get_info("traffic/read")
  bytes_written = controller.get_info("traffic/written")
  traffic_downloaded = size(int(bytes_read))
  traffic_uploaded = size(int(bytes_written))

  print("I have downloaded:",traffic_downloaded,"\nI Have uploaded: ",traffic_uploaded)

  for circ in sorted(controller.get_circuits()):
    if circ.status != CircStatus.BUILT:
      continue

    print("")
    print("Circuit %s (%s)" % (circ.id, circ.purpose))


    for i, entry in enumerate(circ.path):
      div = '+' if (i == len(circ.path) - 1) else '|'
      fingerprint, nickname = entry

      desc = controller.get_network_status(fingerprint, None)
      address = desc.address if desc else 'unknown'

      print(" %s- %s (%s, %s)" % (div, fingerprint, nickname, address))
"""