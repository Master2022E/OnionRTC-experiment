from stem import CircStatus
from stem.control import Controller

def get_circuits():
  circuits = []
  with Controller.from_port(port = 9051) as controller:
    controller.authenticate("your password")
    for circ in sorted(controller.get_circuits()):
      if circ.status != CircStatus.BUILT:
        continue
      circuit = ["circ-{}".format(circ.id)]
      for i, entry in enumerate(circ.path):
        fingerprint, nickname = entry

        desc = controller.get_network_status(fingerprint, None)
        address = desc.address if desc else 'unknown'
        circuit.append(address)
      circuits.append(circuit)
  return circuits


import requests
import json

API_KEY="" # put your key here

def locate(address):
    request_url = "https://ipgeolocation.abstractapi.com/v1/?api_key={}&ip_address={}".format(API_KEY, address)
    response = requests.get(request_url)
    return response.json()