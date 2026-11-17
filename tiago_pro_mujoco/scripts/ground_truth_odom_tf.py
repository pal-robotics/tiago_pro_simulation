#!/usr/bin/env python3
# Copyright (c) 2026 PAL Robotics S.L. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Publish the TF odom -> base_footprint from the base's true pose in MuJoCo.

On the robot this TF comes from the base's odometry. In MuJoCo the base is moved by the
simulation itself (BaseVelocityPlugin), so nothing publishes it. This node takes the base's
pose from the FreeJointStatePublisherPlugin, in the MuJoCo world frame, so odom is the MuJoCo
world: perfect odometry, and the objects of the MuJoCo scene are at their true pose in odom.

Parameters
----------
topic : str
    The FreeJointStatePublisherPlugin's topic; its frame_id must be empty (world).
body : str
    The base's free-joint body, default base_footprint.
frame_id : str
    Parent frame of the TF, default odom.
child_frame_id : str
    Child frame of the TF, default the body.
planar : bool
    Publish only x, y and yaw, as a wheeled base's odometry does (default true).

"""

import math

import rclpy
from geometry_msgs.msg import TransformStamped
from mujoco_ros2_control_msgs.msg import FreeJointStateArray
from rclpy.node import Node
from tf2_ros import TransformBroadcaster


class GroundTruthOdomTf(Node):

    def __init__(self):
        super().__init__('ground_truth_odom_tf')
        topic = self.declare_parameter(
            'topic', '/free_joint_state_publisher/free_joint_states').value
        self.body = self.declare_parameter('body', 'base_footprint').value
        self.frame_id = self.declare_parameter('frame_id', 'odom').value
        self.child_frame_id = self.declare_parameter('child_frame_id', '').value or self.body
        self.planar = self.declare_parameter('planar', True).value

        self.broadcaster = TransformBroadcaster(self)
        self.warned = set()
        self.create_subscription(FreeJointStateArray, topic, self.on_states, 10)
        self.get_logger().info(
            f"Publishing {self.frame_id} -> {self.child_frame_id} from '{self.body}' on {topic}")

    def warn_once(self, key, text):
        if key not in self.warned:
            self.warned.add(key)
            self.get_logger().warn(text)

    def on_states(self, msg):
        if msg.header.frame_id:
            self.warn_once('frame', f"Poses are relative to '{msg.header.frame_id}', not the "
                           "MuJoCo world: set the plugin's frame_id to \"\"")
            return
        state = next((s for s in msg.free_joints if s.name == self.body), None)
        if state is None:
            self.warn_once('body', f"No free joint '{self.body}' in the free joint states")
            return

        tf = TransformStamped()
        tf.header.stamp = msg.header.stamp
        tf.header.frame_id = self.frame_id
        tf.child_frame_id = self.child_frame_id
        p = state.pose.pose.position
        q = state.pose.pose.orientation
        tf.transform.translation.x = p.x
        tf.transform.translation.y = p.y
        if self.planar:
            yaw = math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))
            tf.transform.rotation.z = math.sin(yaw / 2.0)
            tf.transform.rotation.w = math.cos(yaw / 2.0)
        else:
            tf.transform.translation.z = p.z
            tf.transform.rotation = q
        self.broadcaster.sendTransform(tf)


def main():
    rclpy.init()
    node = GroundTruthOdomTf()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
