#!/usr/bin/env python2
from __future__ import print_function
import rospy
import cv2
import sys
from sensor_msgs.msg import CompressedImage, Image
import numpy as np
from cv_bridge import CvBridge
bridge = CvBridge()
pub = None
depth_header_size = 12

def decompress_image(msg):
    # image = np.asarray(bytearray(msg.data), dtype="uint8")
    # img = cv2.imdecode(image, cv2.IMREAD_ANYDEPTH)
    global bridge
    cv_image = bridge.compressed_imgmsg_to_cv2(msg)
    
    raw_data = msg.data[depth_header_size:]
    depth_img_raw = cv2.imdecode(np.fromstring(msg.data, np.uint8), cv2.IMREAD_ANYDEPTH)
    
    # print(cv_image.dtype, cv_image.shape)
    # print(depth_img_raw.dtype, depth_img_raw.shape)

    cv2.imshow("compress", cv_image)
    cv2.waitKey(30)
    # bridge = bridge.cv2_to_imgmsg(msg)
    # print(cv_image)
    # pub.publish(cv_image)

if __name__ == "__main__":
    rospy.init_node("decompress_image")
    pub = rospy.Publisher(sys.argv[2], Image, queue_size=10)
    rospy.Subscriber(sys.argv[1], CompressedImage, decompress_image)
    rospy.spin()