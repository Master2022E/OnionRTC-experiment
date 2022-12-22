#!/usr/bin/python3
# Generated by Selenium IDE
import traceback
from selenium.common import *

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
import subprocess

from misc.Tor.stem_event_streamer import setup_event_streamer, close_event_streamer, is_tor_ready, setup_controller

import socket
from dotenv import load_dotenv
import pyfiglet
import sys
import argparse

import os
import logging
import logging.handlers
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

from misc.mongo_report_ssh import close_mongo_connection, create_client_report

"""
Python script for running WebRTC session tests using Selenium and different anonymization services.

The script can be run from the command line with the -h flag to see the available options.

Written by: Christian Mark and Jonas Thomsen 2022
"""

"""
selenium_execute_with_retry() and selenium_wrapper() are taken from
https://betterprogramming.pub/a-simple-addition-to-your-selenium-test-framework-that-makes-it-more-robust-and-reliable-e9cf97f52e78?gi=bb10badcc8b0
"""

def selenium_execute_with_retry(execute, command,
                                params):
  """Run a single selenium command and retry once.
  The retry happens for certain errors that are likely to be resolved
  by retrying.
  """
  try:
    return execute(command, params)
  except Exception as e:
    if isinstance(e, ALWAYS_RETRY_EXCEPTIONS):
      # Retry
      time.sleep(1)
      return execute(command, params)
    else:
      raise

def selenium_wrapper(selenium_api):
  if not getattr(selenium_api, "_patched", False):
    orig_execute = selenium_api.execute

    def execute(driver_command, params=None):
      try:
        result = selenium_execute_with_retry(orig_execute, driver_command, params)
      except Exception:
        raise
      return result

    selenium_api.execute = execute
    selenium_api._patched = True

  return selenium_api


ALWAYS_RETRY_EXCEPTIONS = (
      ElementNotInteractableException,
      NoSuchWindowException,
      NoSuchElementException,
      NoSuchFrameException,
      NoSuchAttributeException,
      InvalidElementStateException,
      ElementNotVisibleException,
      TimeoutException
  )

# Define a consistent state space for the test
states_str = ["setup_client","check_media","check_webrtc_settings",
              "starting_session","waiting_for_call","call_in_progress","call_ended",
              "teardown","done","error"]
states = dict()
for state in states_str:
    states[state] = state

# Report types
logging_str = ["NOT_SET","CLIENT_START","CLIENT_RUNNING", "CLIENT_END", "CLIENT_ERROR"]
logging_types = dict()
for type in logging_str:
    logging_types[type] = type

# Annonimization network types
network_types_str = ["Tor","I2P","Lokinet"] # "None" 
network_types = dict()
for type in network_types_str:
    network_types[type] = type





class OnionRTC():
    def setup_session(self):
        
        load_dotenv()

        client_config = os.environ.get("CLIENT_CONFIG","None")
        print("CLIENT_CONFIG: ", client_config)

        parser = argparse.ArgumentParser(description='Run a WebRTC session on "https://thomsen-it.dk" using Selenium, optionally using onion routing.')

        # Positional arguments, meaning they are not required but can be used.
        # If you want to set the last one, then you need to set the previous ones as well.
        # Example: './OnionRTC.py "Torben" "bfe386e8-b93b-4f2b-874a-b9494481e45a" "Room42" 10'
        # Results in: 'Namespace(client_username='Torben', test_id='bfe386e8-b93b-4f2b-874a-b9494481e45a', room_id='Room42', session_length_seconds=10, proxy=False, headless=True, verbose=False)'
        parser.add_argument('client_username', metavar="client_username", nargs='?', type=str, default="client_username", help='The username of the client')
        parser.add_argument('test_id', metavar="test_id",nargs='?', type=str, default="test_id",  help='The test id that the client should use')
        parser.add_argument('room_id', metavar="room_id",nargs='?', type=str, default="room_id",  help='The room id that the client should join')
        parser.add_argument('scenario_type', metavar="scenario_type",nargs='?', type=str, default="scenario_type",  help='The session scenario type that the run is a part of.')
        parser.add_argument('session_length_seconds', metavar='N', type=int, nargs='?', default=60,
                            help='Sets the number of seconds a session should be running for')

        # Optional arguments
        parser.add_argument('-p','--proxy', action='store_const',
                            const=True, default=True,
                            help='Whether the browser should use the onion routing proxy [Default True]')
        parser.add_argument('-r',metavar="int", type=int, dest="session_setup_retries", default=4,
                            help='How many times the session setup should be retried before failing the test')
        parser.add_argument("-c", dest="client_config", help="Sets a client config string. Defaults to env var $CLIENT_CONFIG", default=client_config)
        
        # Debug arguments
        parser.add_argument('-hl','--headless', action='store_const',
                            const=False, default=True,
                            help='Whether the browser should run in headless mode')
        parser.add_argument("-v", "--verbose", help="Print debug messages into debug.log file",
                            action="store_true", default=False)           
        
        
        args = parser.parse_args()
        print(args)
        self.vars = args
        #self.vars.client_config = os.environ.get("CLIENT_CONFIG","NOT_SET")

        # How many ticks are there in rounds of waiting before reloading the page to do a new session setup
        # Related to session_setup_retries, which is default 4 and is the amount of rounds
        self.waiting_counter_max = 4

        self.vars.state = states["setup_client"]  
         

        logging_level = logging.INFO
        # Set the threshold for selenium to WARNING
        from selenium.webdriver.remote.remote_connection import LOGGER as seleniumLogger
        seleniumLogger.setLevel(logging.INFO)
        # Set the threshold for urllib3 to WARNING
        logging.getLogger("urllib3").setLevel(logging.CRITICAL)

        if args.verbose:
            logging_level = logging.DEBUG
            logging.getLogger("urllib3").setLevel(logging.INFO)





        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)


        color_codes = {
        'RED': '\033[41m',
        'GREEN': '\033[42m',
        'PINK': '\033[45m',
        'BLUE': '\033[44m'
        }

        

        if "Tor" in client_config:
            color_code = color_codes["RED"]
        elif "I2P" in client_config:
            color_code = color_codes["BLUE"]
        elif "Lokinet" in client_config:
            color_code = color_codes["GREEN"]
        else:
            color_code = color_codes["PINK"]
        
        color_end = "\033[1;0m"

        logging.basicConfig(
                format=f'%(asctime)s {color_code}{socket.gethostname()}{color_end} %(levelname)-8s %(message)s ',
                level=logging_level,
                datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[
                    TimedRotatingFileHandler('./debug.log', when="midnight", backupCount=60), # Rotate every midnight and keep 60 days worth of logs
                    # RotatingFileHandler('./debug.log', maxBytes=268435456, backupCount=10), # 256MB max bytes
                    # logging.FileHandler("debug.log"), # Without rotation
                    #logging.StreamHandler(), # Show everything on console
                    console_handler # Only show INFO and above on console
                ])
        
        logging.addLevelName( logging.WARNING, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
        logging.addLevelName( logging.ERROR, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.ERROR))


        webdriverOptions = Options()
        webdriverOptions.headless = self.vars.headless
        webdriverOptions.set_preference("media.navigator.permission.disabled", True)
        webdriverOptions.set_preference("media.peerconnection.ice.relay_only", True)

        # Setup error report template, if we fail
        data = {'client_username':self.vars.client_username,
        "client_type": self.vars.client_config,
        "room_id": self.vars.room_id,
        "test_id": self.vars.test_id, # str(uuid.uuid4())
        "scenario_type": self.vars.scenario_type,
        "logging_type": logging_types["CLIENT_ERROR"],
        "state" : states["setup_client"]}

        # Setup the client_config string by appending the proxy flag
        if any(net_type in self.vars.client_config for net_type in network_types_str):
            if self.vars.proxy:
                self.vars.client_config += ":Proxy"
            else:
                self.vars.client_config += ":NoProxy"
        



        # Setup Socks Proxy
        # https://stackoverflow.com/questions/60000480/how-to-use-only-socks-proxy-in-firefox-using-selenium
        if self.vars.proxy and "None" not in self.vars.client_config :

            if network_types["Tor"] in self.vars.client_config:


                # Check if Tor proxy is running
                try:
                    setup_controller(logging)
                    if not is_tor_ready():
                        raise ConnectionRefusedError("Tor proxy was not ready yet")

                except Exception as e:
                    
                    type = ""
                    if hasattr(e,"__module__"):
                        type = e.__module__ 
                    data["error"] = f"Exception {type}: {e}"
                    create_client_report(data,logging)
                    raise e


                webdriverOptions.set_preference("network.proxy.type", 1)
                webdriverOptions.set_preference("network.proxy.socks", "localhost")
                webdriverOptions.set_preference("network.proxy.socks_port", 9050)
                #webdriverOptions.update_preferences()
            elif network_types["Lokinet"] in self.vars.client_config:
                #logging.error("Lokinet is not supported yet!")
                # The Lokinet client is like a VPN and does not need a proxy to be setup
                # Run the command "systemctl show lokinet.service --property=StatusText"

                try:
                    #Example: 'active' or 'inactive'
                    is_active = subprocess.run(["systemctl","is-active","lokinet"], stdout=subprocess.PIPE)
                    if is_active.stdout.decode("utf-8").strip() != "active":
                        # Not active
                        raise ConnectionRefusedError("Lokinet was not active")
                except Exception as e:
                    data["error"] = f"Exception: {e}"
                    create_client_report(data,logging)
                    raise e

                try:
                    #Example: 'StatusText=v0.9.11 client | known/connected: 1750/4 | paths/endpoints 21/1'
                    # or
                    status_text = subprocess.run(["systemctl","show","lokinet","--property=StatusText"], stdout=subprocess.PIPE)
                    if status_text.stdout.decode("utf-8").strip() != "StatusText=\n":
                        # Could not parse the status text
                        pass
                    else:
                        data["LokiNetStatusText"] = status_text.stdout.decode("utf-8").strip().split("=")[1]

                except Exception as e:
                    # Example: FileNotFoundError: [Errno 2] No such file or directory: 'systemctl' if the command is not found

                    data["error"] = f"Exception: {e}"
                    create_client_report(data,logging)
                    raise e                
            
                pass
            elif network_types["I2P"] in self.vars.client_config:
                logging.error("I2P is not supported yet!")
                # FIXME: Do I2P setup and checking here
                pass
            else:
                e = f"No valid annonymity network type was was found in the client_config string: '{self.vars.client_config}'"
                data["error"] = f"Exception: {e}"
                create_client_report(data,logging)
                raise Exception(e)

        try:
            browser = webdriver.Firefox(service=Service("/usr/bin/geckodriver"),options=webdriverOptions)
            driver = selenium_wrapper(browser)
            driver.implicitly_wait(60)
            driver.set_page_load_timeout(60)
            self.vars.driver = driver
        except Exception as e:
            data["error"] = f"Exception: {e}"
            logging.error(f"Exception: {e}")
            create_client_report(data,logging)

            raise e

        
        return self.vars







    def clean_up(self):
        if self.vars.state != states["error"]:
            self.vars.state = states["teardown"]

        if self.vars.headless:
            # Wait a bit before we close the connection to the other client to account for different registered start times
            time.sleep(3)            
            self.vars.driver.quit()
        
        close_mongo_connection()
        
        logging.info("Test clean up complete")
        self.vars.state = states["done"]

        

    def run_session(self):
        self.vars.client_id = "client_id_not_set"
        data = {'client_username':self.vars.client_username,
        "client_id": self.vars.client_id,
        "client_type": self.vars.client_config,
        "room_id": self.vars.room_id,
        "test_id": self.vars.test_id, # str(uuid.uuid4())
        "scenario_type": self.vars.scenario_type,
        "logging_type": logging_types["NOT_SET"]}

        self.vars.state = states["check_media"]
        
        self.vars.driver.get("about:webrtc")
        self.vars.driver.set_window_size(int(1765/2), int(1158/2))

        video_info = self.vars.driver.execute_script("a = navigator.mediaDevices.getUserMedia({ video: true}).then(function (stream) { if (stream.getVideoTracks().length > 0 ){ return stream.getVideoTracks() } else { return 0 }}).catch(function (error) { return error}); return a")
        time.sleep(1)
        logging.debug(f"Returned by JS: {video_info}")

        try:
        
            video_info = str(video_info) # Given as a list, but we want a string, so we can use the "in" operator
            if video_info == "0":
                logging.error("No video device found")
                raise Exception("No video device found")
            elif "ABORT_ERR" in video_info:
                logging.warning("getUserMedia failed with error. Was not able to verify that the webcam worked!")
                raise IOError("Can't verify that the webcam works")
            elif "'kind': 'video', 'label': 'Dummy video device (0x0000)'" in video_info and "'enabled': True" in video_info:
                logging.info("getUserMedia returned a video track, which is enabled. This means that the webcam works!")



            audio_info = self.vars.driver.execute_script("a = navigator.mediaDevices.getUserMedia({ audio: true}).then(function (stream) { if (stream.getAudioTracks().length > 0){ return stream.getAudioTracks() } else { return 0 }}).catch(function (error) { return error}); return a")
            time.sleep(1)
            logging.debug(f"Returned by JS: {audio_info}")
            
            audio_info = str(audio_info)
            if audio_info == "0":
                logging.error("No audio device found")
                raise Exception("No audio device found")
            elif "ABORT_ERR" in audio_info:
                logging.warning("getUserMedia failed with error. Was not able to verify that the webcam mic worked!")
                raise IOError("Can't verify that the webcam mic works")
            elif "'kind': 'audio', 'label': 'virtual_mic'" in audio_info and "'enabled': True" in audio_info:
                logging.info("getUserMedia returned a audio track, which is enabled. This means that the webcam mic works!")
        except Exception as e:
            logging.error(f"Exception: {e}")
            data["logging_type"] = logging_types["CLIENT_ERROR"]
            data["error"] = f"Exception: {e}"
            data["state"] = self.vars.state
            create_client_report(data,logging)

            raise e
        
        self.vars.state = states["check_webrtc_settings"]

        if self.vars.driver.title == 'WebRTC Internals':
            # We are on the webRTC page
            ice_relay_only_str = "media.peerconnection.ice.relay_only"
            permission_disabled_str = "media.navigator.permission.disabled"

            relay_only , permissions = False, False

            if ice_relay_only_str in self.vars.driver.page_source:
                relay_only = ice_relay_only_str+": true" in self.vars.driver.page_source
            
            if permission_disabled_str in self.vars.driver.page_source:
                permissions = permission_disabled_str+": true" in self.vars.driver.page_source
            
            if permissions and relay_only:
                logging.info("Browser settings OK")
            else:
                logging.warning("Browser settings should be 'True':"+ice_relay_only_str+":"+str(relay_only)+" - "+permission_disabled_str+":"+str(permissions))
        else:
            logging.warning("Was not able to go to about:webrtc to check permissions!!!")
            


        URL = f"https://stage.thomsen-it.dk/#/call/{self.vars.client_username}/{self.vars.room_id}"
        self.vars.state = states["starting_session"]
        data["state"] = self.vars.state
        logging.info(f"Starting session by navigating to '{URL}'")
        
        try:
            self.vars.driver.get(f"{URL}")
        except Exception as e:
            #logging.error(f"Exception: {e}")
            data["logging_type"] = logging_types["CLIENT_ERROR"]
            data["error"] = f"Exception: {e}"
            
            create_client_report(data,logging)

            raise e

        if self.vars.driver.title == 'React App':
            # We are on the webRTC application page
            logging.info("We are on the webRTC application page")

            # Find client id in text
            if "Client Id:" in self.vars.driver.page_source:
                self.vars.client_id = self.vars.driver.page_source.split("Client Id: ")[1].split("</label>")[0]
                data['client_id'] = self.vars.client_id



                
            data["logging_type"] = logging_types["CLIENT_START"]
            create_client_report(data,logging)
            

            # Starting test
            try:
                WebDriverWait(self.vars.driver, 30).until(
                    expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, ".ip > .value")))
                WebDriverWait(self.vars.driver, 30).until(
                    expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, ".country > .value")))
                self.vars.iplocation = dict()
                self.vars.iplocation["wanIp"] = self.vars.driver.find_element(
                    By.CSS_SELECTOR, ".ip > .value").text
                self.vars.iplocation["country"] = self.vars.driver.find_element(
                    By.CSS_SELECTOR, ".country > .value").text
                self.vars.iplocation["region"] = self.vars.driver.find_element(
                    By.CSS_SELECTOR, ".region > .value").text
                self.vars.iplocation["city"] = self.vars.driver.find_element(
                    By.CSS_SELECTOR, ".city > .value").text
                self.vars.iplocation["isp"] = self.vars.driver.find_element(
                    By.CSS_SELECTOR, ".isp > .value").text


                #logging.info(self.vars.iplocation)
            except Exception as e:
                #logging.error(f"Exception: {e}")
                data["logging_type"] = logging_types["CLIENT_ERROR"]
                data["error"] = f"Exception: {e}"
                
                create_client_report(data,logging)

                raise e            




            retry_counter = 0
            waiting_counter = 0
            session_setup_retries = self.vars.session_setup_retries

            self.vars.state = states["waiting_for_call"]
            data["state"] = self.vars.state

            # If we have set the proxy and the client knows that it is a Tor Client
            if self.vars.proxy and "Tor" in self.vars.client_config:
                logging.info("Starting Tor circuit subscriber")
                setup_event_streamer(self.vars,logging)
                logging.info("Done starting Tor circuit subscriber")
                
            # Waiting for the call to start by checking if the video element is visible
            try:
                while "connected" not in self.vars.driver.find_element(By.CSS_SELECTOR, ".connectionState").text:
                    logging.info(f"Waiting for the call to start.. #{waiting_counter} out of {self.waiting_counter_max}")
                    time.sleep(5)
                    

                    if "failed" in self.vars.driver.find_element(By.CSS_SELECTOR, ".connectionState").text:
                        logging.warning("Connection state is failed. This means that the connection failed to start. Refreshing the page and trying again")
                        self.vars.driver.refresh()
                        waiting_counter = 0


                    waiting_counter += 1
                    
                    if waiting_counter > self.waiting_counter_max:
                        waiting_counter = 0
                        logging.info(f"Refreshing the page to check if the call just needed a restart! #{retry_counter} out of {session_setup_retries}")
                        self.vars.driver.refresh()
                        retry_counter += 1
                        if retry_counter > session_setup_retries:
                            data["logging_type"] = logging_types["CLIENT_ERROR"]
                            data["error"] = f"Call did not start after {session_setup_retries} retries! Session failed!"
                            raise Exception(f"Call did not start after {session_setup_retries} retries! Session failed!")
                            
            except KeyboardInterrupt:
                logging.info("Skipping waiting for call to start caused by keyboard interrupt")
            except Exception as e:
                data["error"] = f"Exception: {e}"
                create_client_report(data,logging)
                raise e

            self.vars.state = states["call_in_progress"]
            data["state"] = self.vars.state
            data["logging_type"] = logging_types["CLIENT_RUNNING"]
            create_client_report(data,logging)

            logging.info(f"Waiting for {self.vars.session_length_seconds} seconds to see if the call is working.. Press CTRL+C to end the test early!")
            # Implement while loop with time.sleep(1) and check if the call is still working
            # Check if session_length_seconds is overdue.
            try:
                updates = 0
                for i in range(self.vars.session_length_seconds):
                    time.sleep(1)
                    finished = 100*(i/self.vars.session_length_seconds)
                    if divmod(finished, 10) == (updates, 0):
                        updates += 1
                        logging.info(f'Finished waiting {i} seconds out of {self.vars.session_length_seconds} seconds\t({int(finished)}%)')                    
                    
                    # Explanation of the states: https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection/connectionstatechange_event
                    if "failed" in self.vars.driver.find_element(By.CSS_SELECTOR, ".connectionState").text \
                    and self.vars.session_length_seconds > i+10: 
                        # If the session is less than 10 seconds from finishing, we don't fail the session, due to a non synchronized start of the call

                        data["error"] = f"Connection state failed. This means that the connection failed after {i} seconds out of {self.vars.session_length_seconds} ({int(finished)}/100%) during the call."
                        logging.error(data["error"])
                        data["logging_type"] = logging_types["CLIENT_ERROR"]

                        data.update(self.vars.__dict__)
                        data.pop("driver") # Take out the driver object from selenium, since it can't be serialized

                        # Remove irrelevant keys for the logging report
                        entries_to_remove = ('client_config', 'headless','verbose','session_setup_retries','session_length_seconds','proxy')
                        for k in entries_to_remove:
                            data.pop(k, None)

                        try:
                            # Close the Tor event listener and save the data reported from the last session
                            if self.vars.proxy and "Tor" in self.vars.client_config:
                                self.vars.latest_circuit = close_event_streamer()                        
                        except Exception as e:
                            pass

                        create_client_report(data,logging)
                        raise Exception(data["error"])
                

            except KeyboardInterrupt:
                logging.info("Skipping waiting for call to end caused by keyboard interrupt")
            except Exception as e:
                raise e
            

            self.vars.state = states["call_ended"]
            data["state"] = self.vars.state
            data["logging_type"] = logging_types["CLIENT_END"] # CLIENT_ERROR CLIENT_RUNNING
            data.update(self.vars.__dict__)
            data.pop("driver") # Take out the driver object from selenium, since it can't be serialized

            # Remove irrelevant keys for the logging report
            entries_to_remove = ('client_config', 'headless','verbose','session_setup_retries','session_length_seconds','proxy')
            for k in entries_to_remove:
                data.pop(k, None)

        else:
            logging.warning("Was not able to confirm that we are on the React App!!!")
            data["logging_type"] = logging_types["CLIENT_ERROR"]
            data["error"] = f"Could not go to the React App page. Title was '{self.vars.driver.title}'"

        try:
            # Close the Tor event listener and save the data reported from the last session
            if self.vars.proxy and "Tor" in self.vars.client_config:
                self.vars.latest_circuit = close_event_streamer()
        except (Exception) as e:
            logging.error(f"Exception close_event_streamer: {e}")
            data["logging_type"] = logging_types["CLIENT_ERROR"]
            data["error"] = f"Exception: {e}"

        data["state"] = self.vars.state
        create_client_report(data,logging)

        return self.vars



if __name__ == "__main__":
    result = pyfiglet.figlet_format("OnionRTC")
    print(result)

    o = OnionRTC()

    try:
        o.setup_session()
        o.run_session()

    except TimeoutException as e:
        # TimeoutException is raised when the http call for the WebRTC page took too long and after one retry
        logging.error(f"Exception {o.vars.state}: {e}")
        o.vars.state = states["error"]
        o.vars.exception = e
        exit(5)
        
    
    except ConnectionRefusedError as e:
        # Anonymity network is not running/ready
        logging.error(f"Exception {o.vars.state}: {e}")
        o.vars.state = states["error"]
        o.vars.exception = e
        exit(3)    
    except ConnectionError as e:
        # SSH connection error
        logging.error(f"Exception {o.vars.state}: {e}")
        o.vars.state = states["error"]
        o.vars.exception = e
        exit(2)
    except (Exception,KeyboardInterrupt) as e:
        logging.error(f"Exception {o.vars.state}: {traceback.format_exc()}")
        o.vars.state = states["error"]
        o.vars.exception = e
        exit(1)
    finally:
        try:
            o.clean_up()
            logging.info(f"Printing variables: {o.vars}")
        except:
            pass
        

    logging.info(f"Printing variables: {o.vars}")
    exit(0)
    
