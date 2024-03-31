#!/usr/bin/env python3
from __future__ import print_function
import rospy
import rosbag
import sys
from rosgraph_msgs.msg import Clock
import time
import lcm
from SyncBagCtrl import *
from TimeSync import *
from PlayerStats import *
import threading
import yaml

class SyncBagPlayer:
    def __init__(self, bag_path, play_t0_sys=None, start = 0, rate=1.0, autostart=False, drone_id = 1, token=0, exclude_topics=set()):
        self.bag = rosbag.Bag(bag_path)
        self.play_t0_sys = play_t0_sys
        self.bag_t0 = None
        self.r = rospy.Rate(10000)
        self.start_bag_duration = start
        self.total_time = self.bag.get_end_time() - self.bag.get_start_time()
        self.rate = rate
        self.is_bag_playing = autostart
        self.is_terminated = False
        self.drone_id = drone_id
        self.autostart = autostart
        self.exclude_topics = exclude_topics
        self.token = token

        self.lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")
        self.ctrl_sub = self.lc.subscribe("CTRL_PLAYER", self.sync_bag_ctrl_handle)
        self.ctrl_sub = self.lc.subscribe("TIME_SYNC_CTRL", self.handle_time_sync)
        self.prepare_publishers()
        self.t = threading.Thread(target = self.lcm_thread)
        self.t.start()
    
        time.sleep(2.0)    
        self.send_time_sync(self.play_t0_sys, self.bag_t0)

    def lcm_thread(self):
        while not self.is_terminated:
            self.lc.handle_timeout(10)
    
    def sync_bag_ctrl_handle(self, channel, msg):
        msg = SyncBagCtrl.decode(msg)
        if msg.token != self.token:
            return
        if msg.cmd == 1:
            self.is_bag_playing = True
            self.play_t0_sys = msg.system_time
            self.duration = msg.duration
            self.rate = msg.rate
            self.start_bag_duration = msg.start_t
        if msg.cmd == 2:
            self.is_bag_playing = True
            self.play_t0_sys = msg.system_time
        elif msg.cmd < 0:
            print("[SyncBagPlayer] Player cancelled by LCM, exiting.")
            self.is_bag_playing = False
            self.is_terminated = True
            sys.stdout.flush()
        elif msg.cmd == 0:
            print("[SyncBagPlayer] Player paused by LCM.")
            self.is_bag_playing = False
        
    def prepare_publishers(self):
        bag = self.bag
        topics = bag.get_type_and_topic_info()[1]
        publishers = {}
        #Prepare publishers for bag
        for topic, msg, t in bag.read_messages():
            if self.bag_t0 is None:
                self.bag_t0 = t.to_sec()
            if topic not in publishers:
                publishers[topic] = rospy.Publisher(topic, type(msg), queue_size=10)
            if len(topics) == len(publishers):
                break
        print("[SyncBagPlayer] Topics", publishers.keys(), "Excluded", self.exclude_topics)
        print("[SyncBagPlayer] SYS_T0", self.play_t0_sys, "BAG_T0", self.bag_t0, "Start bag", self.start_bag_duration)

        self.publishers = publishers
        self.clock_pub = rospy.Publisher("/clock", Clock, queue_size=10)
    
    def send_player_stats(self, tsys, tplayedsys, tplayedbag, t_bag):
        t_sync = PlayerStats()
        t_sync.system_time = tsys
        t_sync.played_time_sys = tplayedsys
        t_sync.played_time_bag = tplayedbag
        t_sync.rate = self.rate
        t_sync.bag_time_abs = t_bag.to_sec()
        t_sync.drone_id = self.drone_id
        t_sync.token = self.token
        self.lc.publish("PLAYER_STATS", t_sync.encode())
    
    def send_end_stats(self):
        print("\n\nSending end stats\n")
        t_sync = PlayerStats()
        t_sync.played_time_bag = -1
        t_sync.rate = self.rate
        t_sync.drone_id = self.drone_id
        t_sync.token = self.token
        self.lc.publish("PLAYER_STATS", t_sync.encode())
    
    def send_time_sync(self, play_t0_sys, bag_t0):
        t_sync = TimeSync()
        t_sync.drone_id = self.drone_id
        t_sync.system_time0 = play_t0_sys
        t_sync.bag_time0 = bag_t0
        t_sync.token = self.token

        self.lc.publish("TIME_SYNC_CTRL", t_sync.encode())
    
    def handle_time_sync(self, channel, msg):
        msg = TimeSync.decode(msg)
        if msg.token != self.token:
            return
        if self.bag_t0 > msg.bag_time0:
            self.bag_t0 = msg.bag_time0
        print("[SyncBagPlayer] Updated SYS_T0", self.play_t0_sys, "BAG_T0", self.bag_t0, "Start bag", self.start_bag_duration)

    def play(self):
        count = 0
        all_msgs = self.bag.read_messages()
        print("[SyncBagPlayer] Ready.")
        while not rospy.is_shutdown() and not self.is_terminated:
            if not self.is_bag_playing:
                time.sleep(0.001)
                continue
            try:
                topic, msg, t_bag  = next(all_msgs)

                t_system = time.time()
               
                if self.play_t0_sys is None:
                    self.play_t0_sys = t_system

                t_played_time_sys = t_system - self.play_t0_sys
                t_bag_played = t_bag.to_sec() - self.bag_t0 - self.start_bag_duration

                if t_bag_played < 0 or topic in self.exclude_topics:
                    continue
                if t_bag_played > self.duration:
                    print(f"[SyncBagPlayer] Finish {t_bag_played}. Exiting.")
                    self.send_end_stats()
                    return

                while t_played_time_sys*self.rate < t_bag_played:
                    t_system = time.time()
                    t_played_time_sys = t_system - self.play_t0_sys
                    time.sleep(0.0001)

                self.send_player_stats(t_system, t_played_time_sys, t_bag_played, t_bag)

                self.publishers[topic].publish(msg)
                sim_clock = Clock()
                sim_clock.clock = t_bag
                self.clock_pub.publish(sim_clock)
                if count % 100 == 0:
                    t_ = (time.time()- self.play_t0_sys)*self.rate
                    progress = t_ / self.total_time * 100
                    if self.autostart:
                        print("Time {:5.2f}/{:5.2f} Progress {:3.2f}% Count {}".format(t_, self.total_time, progress, count), end="\r")
                    # else:
                        # print("Time {:5.2f}/{:5.2f} Progress {:3.2f}% Count {}".format(t_, self.total_time, progress, count), end="\n")
                    sys.stdout.flush()
                count += 1
            except Exception as e:
                print("[SyncBagPlayer] Exiting.", e)
                self.send_end_stats()
                return
        self.send_end_stats()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Play bags synchronously from dockers')
    
    parser.add_argument('--path', type=str,
                    help='bagpath')

    parser.add_argument('--syst', type=float,
                    default=time.time() + 1,
                    help='start time')
    
    parser.add_argument('--rate', type=float,
                    default=1.0,
                    help='play rate')
        
    parser.add_argument('--start', type=float,
                    default=0.0,
                    help='start')

    parser.add_argument('--drone-id', type=int,
                    default=1,
                    help='start')

    parser.add_argument('--autostart', type=bool,
                    default=False,
                    help='automatics start play at spec system time')
    
    parser.add_argument('--config-path', type=str,
                    default="",
                    help='Config path')

    parser.add_argument('--token', type=int,
                    default=0,
                    help='Control token')
    
    args = parser.parse_args()

    exclude_topics = set()
    try:
        with open(args.config_path, "r") as stream:
            config = yaml.safe_load(stream)
            for topic in config["exclude_topics"]:
                exclude_topics.add(topic)
    except:
        print("Error while reading exclude topics")

    rospy.init_node("player")
    player = SyncBagPlayer(args.path, args.syst, args.start, args.rate, args.autostart, args.drone_id, args.token, exclude_topics)
    player.play()
    print("Exiting...")