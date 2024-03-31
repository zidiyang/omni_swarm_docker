#!/bin/bash
sudo route add -net 224.0.0.0 netmask 240.0.0.0 dev docker0
sudo xhost +local:root