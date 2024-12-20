# Omni_swarm docker

### Introduction

A fully compiled runnable Omni-swarm Docker project with the sync_bag_player tool, Intended to make it easier to evaluate the multi-robot datasets on single PC.

### Usage

#### 1. Docker image pull

Based on the original Omni-swarm Docker (https://github.com/HKUST-Aerial-Robotics/Omni-swarm, TAG is xuhao1/swarm2020:pc), a runnable Docker image is created with Omni-swarm code fully compiled. TAG is blueberryfaygo/compiled_omniswarm:pc, which can be pulled with the following command:

```bash
docker pull blueberryfaygo/compiled_omniswarm:pc
```

No need to create a container after pulling is completed.

#### 2. Datasets and config

[Download on dropbox](https://www.dropbox.com/sh/w5yagas06a9r14d/AACdKgMfCCg07M6jr6Ipmus1a?dl=0)

or [Download on Baidu Netdisk](https://pan.baidu.com/s/1qeQ-NllqrElAl8Cd-ULDRw?pwd=8xnn) with the extraction code: 8xnn 

**Modify the config_all.yaml in Dataset**:

Replace the  value of **workspace** with **void**

Replace the  value of **image_name** with **blueberryfaygo/compiled_omniswarm:pc**

```bash
workspace: ""
image_name: "blueberryfaygo/compiled_omniswarm:pc"
```

#### 3. Build

Configure ROS and Python environment on **host** machine, install the following libraries:

```bash
pip install pyyaml lcm readchar
```

Build sync_bag_player with ROS：

```bash
cd your~workspace~/src/
git clone https://github.com/zidiyang/omni_swarm_docker.git
cd .. && catkin_make
```

#### 4. Run on a single PC.

Running on **host** machine：

```bash
rosrun sync_bag_player environment_setup.sh
rosrun sync_bag_player docker_swarm_test.py /path~to~/config_all.yaml
```

#### 5. Evaluation

Replace the path in 'bag_read' function in 'DataAnalysis/loop_accurate_analyze.ipynb' with the path of your 'output' folder generated under the dataset directory.

Run 'loop_accurate_analyze.ipynb' to obtain accuracy evaluation on position, attitude, distance and relative pose.
