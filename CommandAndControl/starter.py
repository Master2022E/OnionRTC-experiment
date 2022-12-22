from datetime import datetime, timedelta
import logging


def _saveSessionTime(time: datetime) -> None:
    '''
    Saves the current time to the session.txt file.
    '''

    with open("session.txt", "w") as f:
        timeNow = time.strftime("%Y-%m-%d %H:%M:%S")
        f.write(timeNow)
        logging.info("Session start saved to file: " + timeNow)

def _readSessionTime() -> datetime:
    '''
    Reads the last session time from the session.txt file.
    '''

    try:
        with open("session.txt", "r") as f:
            lines = f.readlines()

            line = lines[0].strip()
            time = datetime.strptime(line, "%Y-%m-%d %H:%M:%S")

            return time
            
    except:
        logging.info("Could not read session.txt, Creates a new file")
        # create date from year 1970
        now = datetime.fromtimestamp(0)
        try:
            _saveSessionTime(now)
        except:
            raise("Could not create session.txt")
        return now

def startSession(timeBetweenSessions = [0, 0, 10]) -> bool:
    '''
    Reads the last session time from the session.txt file. and checks if the last session was more than some time delta ago.

    The delta is defined in the timeBetweenSessions variable [hours, minutes, seconds].
    '''
    try:
        time = _readSessionTime()

        # Check if the last session was more than 5 minutes ago
        delta = timedelta(hours   = timeBetweenSessions[0],
                          minutes = timeBetweenSessions[1],
                          seconds = timeBetweenSessions[2])
        if(time + delta < datetime.now()):
            logging.info("Last session was more than " + str(delta) + " ago, starting a new session")
            _saveSessionTime(datetime.now())
            return True
        else:
            return False
            
    except:
        logging.error("File exception error")
        raise("Could not read/write session.txt")