
import time

# Threading
from threading import Thread, Lock

#################################################
# Threading - Flasher
#################################################

class Flasher(Thread):
    """Flash something.

    Keep calling state_function() at a frequency specified by delay
    until the timeout expires, or the stop() function is called. If
    auto is False, start() must be called explicitly before it starts.
    """

    def __init__(self, state_function, lock, *, delay = 0.5, timeout = 0, auto = True):
        """Initialize."""

        Thread.__init__(self)

        # The callback
        self.state_function = state_function
        # How long to wait on a state on/off
        self.delay = delay
        # How long to flash before we return
        self.timeout = timeout
        # Allow manual termination
        self.running = True
        # Make sure only one pin instance is flashed at a time
        self.lock = lock
        # Daemonize the thread so it dies with parent
        self.daemon = True

        if auto:
            self.start()

    def run(self):
        """Do work."""

        if self.lock.acquire(blocking=False):

            state = True
            time_spent = 0
            while self.running and (time_spent <= self.timeout):
                # Set state
                self.state_function(state)
    
                # Toggle state
                if state:
                    state = False
                else:
                    state = True
    
                # Wait a bit
                time.sleep(self.delay)
    
                # Time is disabled if zero
                if self.timeout:
                    time_spent += self.delay

            # Release
            self.lock.release()

    def stop(self):
        """Stop the flasher."""

        self.running = False
        self.join()
        self.state_function(False)

#################################################
# Threading - MQTT Event
#################################################

class Event(Thread):
    """Publish an event.

    While state_get() returns True, keep calling state_function()
    at a frequency specified by delay. Terminate when the state
    change to false.
    """

    def __init__(self, state_get, state_function, lock, *, delay = 1, auto = True):
        """Initialize."""

        Thread.__init__(self)

	# Get current state
        self.state_get = state_get
        # The callback
        self.state_function = state_function
        # How long to raise the event
        self.delay = delay
        # Make sure only one event type at a time
        self.lock = lock
        # Daemonize the thread so it dies with parent
        self.daemon = True

        if auto:
            self.start()

    def run(self):
        """Do work."""

        if self.lock.acquire(blocking=False):

            # Set state
            self.state_function(True)

            # Wait a bit
            time.sleep(self.delay)
       
            while self.state_get():
                # Set state
                self.state_function(True)

                # Wait a bit
                time.sleep(self.delay)

            # Set state
            self.state_function(True)
           
            # Set state
            self.state_function(False)
            
            # Release
            self.lock.release()
    
