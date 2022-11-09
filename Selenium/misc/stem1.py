from stem import CircStatus
from stem.control import Controller
from hurry.filesize import size

with Controller.from_port(port = 9051) as controller:
  controller.authenticate("kode112")

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
