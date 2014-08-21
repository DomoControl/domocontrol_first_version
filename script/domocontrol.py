import webiopi
GPIO = webiopi.GPIO # Helper for LOW/HIGH values
HEATER = 7 # Heater plugged on the Expander Pin 7
MIN = 22 # Minimum temperature in celsius
MAX = 24 # Maximum temperature in celsius
AUTO = True

# setup function is automatically called at WebIOPi startup
def setup():
    g0 = webiopi.deviceInstance("g0") # retrieve the device named "mcp" in the configuration 
    g0.setFunction(1, GPIO.OUT)
