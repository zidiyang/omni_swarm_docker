# rosrun sync_bag_player docker_swarm_test.py ~/bags/swarm_raw_parallel_noyaw_2021-11-12/config_no_map.yaml -n
# sleep 2
# rosrun sync_bag_player docker_swarm_test.py  ~/bags/swarm_raw_parallel_yaw_2021-11-16/config_no_dis.yaml -n
# sleep 2
# rosrun sync_bag_player docker_swarm_test.py  ~/bags/swarm_raw_parallel_yaw_2021-11-16/config_no_det.yaml -n
# sleep 2
# rosrun sync_bag_player docker_swarm_test.py  ~/bags/swarm_raw_parallel_yaw_2021-11-16/config_no_map.yaml -n

sleep 2
rosrun sync_bag_player docker_swarm_test.py  ~/bags/swarm_raw_random_2_2021-11-23/config_no_dis.yaml -n
sleep 2
rosrun sync_bag_player docker_swarm_test.py  ~/bags/swarm_raw_random_2_2021-11-23/config_no_det.yaml -n
sleep 2
rosrun sync_bag_player docker_swarm_test.py  ~/bags/swarm_raw_random_2_2021-11-23/config_no_map.yaml -n
