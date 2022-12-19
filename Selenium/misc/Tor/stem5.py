import io
import time

import pycurl

import stem.control

# Taken from https://stem.torproject.org/tutorials/to_russia_with_love.html#custom-path-selection


EXIT_FINGERPRINT = '07ACFB0801E4F74F5610F870B5FCBB5539DBCBD1'

SOCKS_PORT = 9050
CONNECTION_TIMEOUT = 30  # timeout before we give up on a circuit

def query(url):
  """
  Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
  """

  output = io.BytesIO()

  query = pycurl.Curl()
  query.setopt(pycurl.URL, url)
  query.setopt(pycurl.PROXY, 'localhost')
  query.setopt(pycurl.PROXYPORT, SOCKS_PORT)
  query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
  query.setopt(pycurl.CONNECTTIMEOUT, CONNECTION_TIMEOUT)
  query.setopt(pycurl.WRITEFUNCTION, output.write)

  try:
    query.perform()
    return output.getvalue()
  except pycurl.error as exc:
    raise ValueError("Unable to reach %s (%s)" % (url, exc))


def scan(controller, path):
  """
  Fetch check.torproject.org through the given path of relays, providing back
  the time it took.
  """

  circuit_id = controller.new_circuit(path, await_build = True)

  def attach_stream(stream):
    if stream.status == 'NEW':
      controller.attach_stream(stream.id, circuit_id)

  controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)

  try:
    controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us
    start_time = time.time()

    check_page = query('https://check.torproject.org/')


    if 'Congratulations. This browser is configured to use Tor.' not in str(check_page):
      raise ValueError("Request didn't have the right content")

    return time.time() - start_time
  finally:
    controller.remove_event_listener(attach_stream)
    controller.set_conf('__LeaveStreamsUnattached', '0')



with stem.control.Controller.from_port() as controller:
  controller.authenticate("kode112")

  relay_fingerprints = [desc.fingerprint for desc in controller.get_network_statuses()]

  for fingerprint in relay_fingerprints:
    try:
      time_taken = scan(controller, [fingerprint, EXIT_FINGERPRINT])
      print('%s  to %s => %0.2f seconds' % (fingerprint,EXIT_FINGERPRINT, time_taken))
    except Exception as exc:
      print('%s => %s' % (fingerprint, exc))