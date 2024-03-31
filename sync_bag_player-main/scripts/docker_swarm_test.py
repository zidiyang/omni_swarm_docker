#!/usr/bin/env python3
import argparse
import yaml
from os import system
import subprocess
import pathlib
import time
from sync_rosplay_cmd import SyncCtrl
import random
from datetime import datetime

def kill_docker(name):
    cmd = f"docker container kill {name}"
    system(cmd)

def launch_docker(name, config, config_path, token, terminator):
    print(f"Launching docker {name}")
    dataset_path = pathlib.Path(config_path).parent.resolve()
    current_dir = pathlib.Path(__file__).parent.resolve()

    _id = config["dataset"][name]["id"]
    workspace = config["workspace"]
    output_path = dataset_path.joinpath(config["output_path"] + f"/swarm{_id}")
    swarm_config_path = dataset_path.joinpath(config["dataset"][name]["config_path"])
    bag_path = config["dataset"][name]["bag"]
    image_name = config["image_name"]
    container_name = f"{name}_{token}"
    if "entry_point" in config:
        entry_point_path = dataset_path.joinpath(config["entry_point"])
    else:
        if "entry_point_script" in config:
            entry_point_path = (f"/tmp/{container_name}_entry_point.sh")
            with open(entry_point_path, "w") as stream:
                stream.write(config["entry_point_script"])
                stream.close()
        else:
            print("No entry_point or entrypoint_script, exiting...")
            exit(-1)

    if bag_path == "":
        docker_entry_point = current_dir.joinpath("docker_entrypoint_sim.sh")
    else:
        docker_entry_point = current_dir.joinpath("docker_entrypoint.sh")
    ws_name = pathlib.Path(workspace).name
    if workspace == "":
        workspace_mount = ""
        cmd = f"""docker run --name {container_name} --gpus all --rm -it \
-v {output_path}:/root/output/ \
-v {swarm_config_path}:/root/SwarmConfig/ \
-v {config_path}:/root/config.yaml \
-v {dataset_path}:/root/bags/ \
-v {entry_point_path}:/root/entry_point.sh \
-v {docker_entry_point}:/root/docker_entrypoint.sh \
--env='DRONE_ID={_id}' \
--env='DISPLAY' --volume='/tmp/.X11-unix:/tmp/.X11-unix:rw' \
--privileged \
{image_name} /root/docker_entrypoint.sh /root/bags/{bag_path} {token}"""
    else:
        workspace_mount = workspace+"/:/root/swarm_ws/"
        cmd = f"""docker run --name {container_name} --gpus all --rm -it \
-v {workspace_mount} \
-v {output_path}:/root/output/ \
-v {swarm_config_path}:/root/SwarmConfig/ \
-v {config_path}:/root/config.yaml \
-v {dataset_path}:/root/bags/ \
-v {entry_point_path}:/root/entry_point.sh \
-v {docker_entry_point}:/root/docker_entrypoint.sh \
--env='DRONE_ID={_id}' \
--env='DISPLAY' --volume='/tmp/.X11-unix:/tmp/.X11-unix:rw' \
--privileged \
{image_name} /root/docker_entrypoint.sh /root/bags/{bag_path} {token}"""

# -v {workspace}:/root/swarm_ws/ \
    
    
    print(cmd)
    if terminator:
        p_docker = subprocess.Popen(f'terminator -T {container_name} -x "{cmd}"', shell=True, stderr=subprocess.STDOUT)
    else:
        p_docker = subprocess.Popen(cmd, shell=True, stderr=subprocess.STDOUT)
    return p_docker, container_name

def run_swarm_docker_evaluation(config, enable_zsh, config_path, token, terminator):
    pids = {}
    pids_zsh = {}
    for name in config["dataset"]:
        pid, container_name = launch_docker(name, config, config_path, token, terminator)
        pids[container_name] = pid

    if enable_zsh:
        time.sleep(2.0)
        for name in config["dataset"]:
            cmd = f'terminator -T {name}_bash -x docker exec -it {container_name} /bin/bash'
            pids_zsh[name] =  subprocess.Popen(cmd, shell=True, stderr=subprocess.STDOUT)
    
    return pids, pids_zsh

if __name__ == '__main__':
    random.seed(datetime.now())
    print("Start swarm docker test")
    parser = argparse.ArgumentParser(description='Docker swarm evaluation tool.')
    parser.add_argument('config_path', metavar='config_path',
                    help='config_path for evaluation')
    parser.add_argument("-z", '--bash', action='store_true', help="Open additional bash.")
    parser.add_argument("-t", '--terminator', action='store_true', help="Open docker in terminator.")
    parser.add_argument("-n", '--nointeraction', action='store_true', help="No interaction")
    parser.add_argument("-s", '--sleep', type=float, default=3.0, help="sleep after exec command")

    token = random.randint(0, 1000000)
    args = parser.parse_args()
    with open(args.config_path, "r") as stream:
        config = yaml.safe_load(stream)
    pids, _ = run_swarm_docker_evaluation(config, args.bash, args.config_path, token, args.terminator)

    try:
        if "start_latency" in config:
            time.sleep(config["start_latency"])
        else:
            time.sleep(12)

        sync_ctrl = SyncCtrl(rate=config["rate"], t_start=config["t_start"], duration=config["duration"], 
            token=token, start_delay=1.0, drone_num=len(config["dataset"]), enable_interaction=not args.nointeraction)
        sync_ctrl.work()
        print(f"Sleep for {args.sleep} s. Ctrl-c to exit")
        time.sleep(args.sleep)
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    for p in pids:
        pids[p].terminate()
        kill_docker(p)
