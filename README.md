# Omni_swarm docker

### Introduction
A fully compiled runnable Omni-swarm Docker project with the sync_bag_player tool, Intended to make it easier to evaluate the multi-robot datasets on single PC.

### Usage

#### 1. Docker image pull

Based on the original Omni-swarm Docker (https://github.com/HKUST-Aerial-Robotics/Omni-swarm, TAG is xuhao1/swarm2020:pc), a runnable Docker image is created with Omni-swarm code fully compiled. TAG is blueberryfaygo/fullws_omniswarm:pc, which can be pulled with the following command:

```bash
docker pull blueberryfaygo/fullws_omniswarm:pc
```

#### 2. Datasets and config

[Download on dropbox](https://www.dropbox.com/sh/w5yagas06a9r14d/AACdKgMfCCg07M6jr6Ipmus1a?dl=0)

[Download on Baidu Netdisk](https://pan.baidu.com/s/1qeQ-NllqrElAl8Cd-ULDRw?pwd=8xnn) with the extraction code: 8xnn 

**Modify the config_all.yaml**:

Replace the  value of <u>workspace</u> with <u>void</u>

Replace the  value of <u>image_name</u> with <u>blueberryfaygo/fullws_omniswarm:pc</u>

```bash
workspace: ""
image_name: "blueberryfaygo/fullws_omniswarm:pc"
```

#### 3. Build

Configure ROS and Python environment on **host** machine, install the following libraries:

```bash
pip install pyyaml lcm readchar
```

Build sync_bag_player with ROS：

```bash
cd your~workspace~/src/
git clone https://gitee.com/blueberryfaygo/omni_swarm_docker.git
cd .. && catkin_make
```

#### 4. Evalution on single PC for multi-robot datasets

Running on **host** machine：

```bash
rosrun sync_bag_player environment_setup.sh
rosrun sync_bag_player docker_swarm_test.py path~to~/config_all.yaml
```

