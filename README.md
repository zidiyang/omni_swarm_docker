# Omni_swarm docker

### 介绍
A fully compiled executable Omni-swarm Docker project with the sync_bag_player tool.

### 使用说明

#### 1. Docker镜像拉取

在原始的Omni-swarm docker（TAG is xuhao1/swarm2020:pc）的基础上完成了项目的完整编译，形成了可直接运行的docker环境，TAG：blueberryfaygo/fullws_omniswarm:pc，通过以下命令拉取：

```bash
docker pull blueberryfaygo/fullws_omniswarm:pc
```

#### 2. 数据集获取与配置修改

[国外下载链接](https://www.dropbox.com/sh/w5yagas06a9r14d/AACdKgMfCCg07M6jr6Ipmus1a?dl=0)

[国内下载链接](https://pan.baidu.com/s/1qeQ-NllqrElAl8Cd-ULDRw?pwd=8xnn) 提取码: 8xnn 

**修改config_all.yaml配置文件**:

将<u>workspace</u>的值修改为<u>空</u>

将<u>image_name</u>的值修改为<u>blueberryfaygo/fullws_omniswarm:pc</u>

```bash
workspace: ""
image_name: "blueberryfaygo/fullws_omniswarm:pc"
```

#### 3. 环境配置与编译

于主机（非docker）配置ROS与Python环境，安装以下库：

```bash
pip install pyyaml lcm readchar
```

编译ROS项目sync_bag_player：

```bash
cd your~workspace~/src/
git clone https://gitee.com/blueberryfaygo/omni_swarm_docker.git
cd .. && catkin_make
```

#### 4. 运行

```bash
rosrun sync_bag_player environment_setup.sh
rosrun sync_bag_player docker_swarm_test.py path~to~/config_all.yaml
```

