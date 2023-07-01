#!/bin/sh
python3 speedtest.py --mqtt-server $MQTT_SERVER --mqtt-port $MQTT_PORT --mqtt-username $MQTT_USERNAME --mqtt-password $MQTT_PASSWORD --mqtt-topic $MQTT_TOPIC --mqtt-secure --service $TEST_SERVICE --test-time $TEST_TIME
