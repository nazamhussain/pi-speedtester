#!/usr/bin/env python

import os
import re
import ssl
import json
import argparse
import paho.mqtt.client as mqtt
from datetime import *
from time import sleep

mqtt_server = None
mqtt_port = None
mqtt_secure = False
mqtt_username = None
mqtt_password = None
mqtt_topic = None
service = None
test_time = None

regex_latency = re.compile("^.*Latency.* (.*) ms.*$")
regex_download = re.compile("^.*Download.* (.*) Mbps.*$")
regex_upload = re.compile("^.*Upload.* (.*) Mbps.*$")

### Get Command Line Arguments
def get_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("-s", "--mqtt-server", help="MQTT Server", required=True)
  parser.add_argument("-p", "--mqtt-port", help="MQTT Port", type=int, default="1883")
  parser.add_argument("-x", "--mqtt-secure", help="Enable MQTT over SSL", action="store_true")
  parser.add_argument("-U", "--mqtt-username", help="MQTT Username", required=True)
  parser.add_argument("-P", "--mqtt-password", help="MQTT Password", required=True)
  parser.add_argument("-T", "--mqtt-topic", help="MQTT Topic Prefix", required=True)
  parser.add_argument("-S", "--service", help="Service being speed-tested", required=True)
  parser.add_argument("-t", "--test-time", help="Hourly test-time", required=True)
  args = parser.parse_args()
  return args

### Spedtest Function
def speedtest(service, test_time):
  ### MQTT Connect Callback Function
  def on_connect(client, userdata, flags, rc):
    nonlocal mqtt_connected
    mqtt_connected = True
    print(f"Connected to MQTT Server - speedtester-{service}")
  ### MQTT Disconnect Callback Function
  def on_disconnect(client, userdata, rc):
    nonlocal mqtt_connected
    mqtt_connected = False
    print(f"Disconnected from MQTT Server - speedtester-{service}")

  mqtt_connected = False

  metrics = {
    'latency': None,
    'download': None,
    'upload': None
  }

  metadata = {
    'service': service,
    'hour': None,
    'day': None,
    'month': None,
    'year': None
  }

  dt = datetime.now().timetuple()
  next_test_time = datetime.strptime(f"{dt.tm_mday}/{dt.tm_mon}/{dt.tm_year} {dt.tm_hour}:{test_time}:00", '%d/%m/%Y %H:%M:%S')
  if (next_test_time < datetime.now()):
    next_test_time = next_test_time + timedelta(hours=1)

  try:
    mqtt_client = f"speedtester-{service}"
    client = mqtt.Client(mqtt_client)
    if mqtt_secure:
      client.tls_set(ca_certs='ca.crt', certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
    client.username_pw_set(mqtt_username,mqtt_password)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(mqtt_server, mqtt_port)
    client.loop_start()

    while True:
      try:
        while mqtt_connected:
          if ((next_test_time.timestamp() - datetime.now().timestamp()) > 0):
            sleep(next_test_time.timestamp() - datetime.now().timestamp())
          stream = os.popen("speedtest --accept-license --accept-gdpr --server-id=24640 --progress=no | grep 'Latency\|Download\|Upload'")
          output = stream.read()
          for line in output.split('\n'):
            if regex_latency.match(line):
              metrics['latency'] = float(re.search(regex_latency, line).group(1))
            elif regex_download.match(line):
              metrics['download'] = float(re.search(regex_download, line).group(1))
            elif regex_upload.match(line):
              metrics['upload'] = float(re.search(regex_upload, line).group(1))
          metadata['hour'] = f"{dt.tm_hour:02d}00"
          metadata['day'] = f"{dt.tm_mday}"
          metadata['month'] = f"{dt.tm_mon}"
          metadata['year'] = f"{dt.tm_year}"
          client.publish(f"{mqtt_topic}/{service}/speedtest", json.dumps([metrics, metadata]))
          next_test_time = next_test_time + timedelta(hours=1)
        sleep(60)
      except KeyboardInterrupt:
        exit()
      except Exception as e:
        print(e)
  except ConnectionRefusedError:
    print(f"MQTT Server refused the connection for speedtester-{service}")
  except Exception as e:
    print(e)


### Main Function
def main():
  args = get_args()
  global mqtt_server
  global mqtt_port
  global mqtt_secure
  global mqtt_username
  global mqtt_password
  global mqtt_topic
  global service
  global test_time
  mqtt_server = args.mqtt_server
  mqtt_port = args.mqtt_port
  mqtt_secure = args.mqtt_secure
  mqtt_username = args.mqtt_username
  mqtt_password = args.mqtt_password
  mqtt_topic = args.mqtt_topic
  service = args.service
  test_time = args.test_time

  # Speedtest
  speedtest(service, test_time)


if __name__ == "__main__":
  main()

