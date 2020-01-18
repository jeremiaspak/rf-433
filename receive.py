#!/usr/bin/env python3

import argparse
import signal
import sys
import time
import logging
import paho.mqtt.publish

from rpi_rf import RFDevice

rfdevice = None

# pylint: disable=unused-argument
def exithandler(signal, frame):
  rfdevice.cleanup()
  sys.exit(0)

def publish(topic, payload):
  paho.mqtt.publish.single(
    topic=topic,
    payload=payload,
    qos=2,
    hostname='localhost',
    port=1883
    # client_id='[clientid]'
  )

logging.basicConfig(
  level=logging.INFO,
  datefmt='%Y-%m-%d %H:%M:%S',
  format='%(asctime)-15s - [%(levelname)s] %(module)s: %(message)s',
)

parser = argparse.ArgumentParser(description='Receives a decimal code via a 433/315MHz GPIO device')
parser.add_argument('-g', dest='gpio', type=int, default=27, help="GPIO pin (Default: 27)")
args = parser.parse_args()

signal.signal(signal.SIGINT, exithandler)
rfdevice = RFDevice(args.gpio)
rfdevice.enable_rx()
timestamp = None
logging.info("Listening for codes on GPIO " + str(args.gpio))
while True:
  if rfdevice.rx_code_timestamp != timestamp:
    timestamp = rfdevice.rx_code_timestamp
    publish("test/message", str(rfdevice.rx_code))
    logging.info(
      str(rfdevice.rx_code) +
      " [pulselength " + str(rfdevice.rx_pulselength) +
      ", protocol " + str(rfdevice.rx_proto) +
      "]"
    )
  time.sleep(0.01)
rfdevice.cleanup()
