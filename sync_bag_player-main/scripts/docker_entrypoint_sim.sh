#!/bin/bash
source /opt/ros/noetic/setup.bash
source /root/swarm_ws/devel/setup.bash
echo "Run bag replay for drone",$DRONE_ID, "with bag", $1
route add -net 224.0.0.0 netmask 240.0.0.0 dev eth0
chmod a+x /root/entry_point.sh
/root/entry_point.sh 2>&1 | tee /root/output/logs.txt 
echo "Will end bag record"
pkill -TERM record
sleep 10000