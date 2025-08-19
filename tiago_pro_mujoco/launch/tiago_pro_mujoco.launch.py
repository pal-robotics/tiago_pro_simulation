# Copyright (c) 2024 PAL Robotics S.L. All rights reserved.
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


import os
import yaml
import tempfile
from os import environ, pathsep
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    SetLaunchConfiguration,
    OpaqueFunction,
)
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration

from launch_pal.include_utils import (
    include_scoped_launch_py_description,
)
from launch_pal.actions import CheckPublicSim

from launch_pal.arg_utils import LaunchArgumentsBase
from launch_pal.robot_arguments import CommonArgs
from tiago_pro_description.launch_arguments import TiagoProArgs
from dataclasses import dataclass
from launch_ros.actions import Node

from launch_pal.param_utils import merge_param_files


@dataclass(frozen=True)
class LaunchArguments(LaunchArgumentsBase):
    base_type: DeclareLaunchArgument = TiagoProArgs.base_type
    arm_type_right: DeclareLaunchArgument = TiagoProArgs.arm_type_right
    arm_type_left: DeclareLaunchArgument = TiagoProArgs.arm_type_left
    end_effector_right: DeclareLaunchArgument = TiagoProArgs.end_effector_right
    end_effector_left: DeclareLaunchArgument = TiagoProArgs.end_effector_left
    ft_sensor_right: DeclareLaunchArgument = TiagoProArgs.ft_sensor_right
    ft_sensor_left: DeclareLaunchArgument = TiagoProArgs.ft_sensor_left
    tool_changer_right: DeclareLaunchArgument = TiagoProArgs.tool_changer_right
    tool_changer_left: DeclareLaunchArgument = TiagoProArgs.tool_changer_left
    wrist_model_right: DeclareLaunchArgument = TiagoProArgs.wrist_model_right
    wrist_model_left: DeclareLaunchArgument = TiagoProArgs.wrist_model_left
    camera_model: DeclareLaunchArgument = TiagoProArgs.camera_model
    laser_model: DeclareLaunchArgument = TiagoProArgs.laser_model
    moveit: DeclareLaunchArgument = CommonArgs.moveit
    tuck_arm: DeclareLaunchArgument = CommonArgs.tuck_arm
    is_public_sim: DeclareLaunchArgument = CommonArgs.is_public_sim
    mujoco: DeclareLaunchArgument = CommonArgs.mujoco
    mj_control: DeclareLaunchArgument = CommonArgs.mj_control
    mj_simulate: DeclareLaunchArgument = CommonArgs.mj_simulate


def declare_actions(launch_description: LaunchDescription, launch_args: LaunchArguments):

    # Set use_sim_time to True
    set_sim_time = SetLaunchConfiguration("use_sim_time", "True")
    launch_description.add_action(set_sim_time)

    set_mujoco = SetLaunchConfiguration('mujoco', 'true')
    launch_description.add_action(set_mujoco)

    set_end_effector_left = SetLaunchConfiguration('end_effector_left','pal-pro-gripper')
    launch_description.add_action(set_end_effector_left)

    set_end_effector_right = SetLaunchConfiguration('end_effector_right','pal-pro-gripper')
    launch_description.add_action(set_end_effector_right)

    set_wrist_model_left = SetLaunchConfiguration('wrist_model_left','spherical-wrist')
    launch_description.add_action(set_wrist_model_left)

    set_wrist_model_right = SetLaunchConfiguration('wrist_model_right','spherical-wrist')
    launch_description.add_action(set_wrist_model_right)

    set_arm_type_right = SetLaunchConfiguration('arm_type_right','tiago-pro')
    launch_description.add_action(set_arm_type_right)

    set_arm_type_left = SetLaunchConfiguration('arm_type_left','tiago-pro')
    launch_description.add_action(set_arm_type_left)

    # Shows error if is_public_sim is not set to True when using public simulation
    public_sim_check = CheckPublicSim()
    launch_description.add_action(public_sim_check)

    robot_name = "tiago_pro"

    tiago_pro_controller_path = os.path.join(get_package_share_directory('tiago_pro_controller_configuration'))
    head_controller_path = os.path.join(get_package_share_directory('tiago_pro_head_controller_configuration'))
    arm_controller_path = os.path.join(get_package_share_directory('pal_sea_arm_controller_configuration'))
    base_controller_path = os.path.join(get_package_share_directory('omni_base_controller_configuration'))
    gripper_controller_path= os.path.join(get_package_share_directory('pal_pro_gripper_controller_configuration'))

    controller_manager_config_yaml = os.path.join(tiago_pro_controller_path, 'config', 'mujoco_controller_manager_cfg.yaml')
    torso_controller_yaml = os.path.join(tiago_pro_controller_path, 'config', 'torso_controller.yaml')
    joint_state_broadcaster_yaml = os.path.join(tiago_pro_controller_path, 'config', 'joint_state_broadcaster.yaml')
    head_controller_yaml = os.path.join(head_controller_path, 'config', 'head_controller.yaml')
    arm_controller_yaml = os.path.join(arm_controller_path, 'config', 'arm_controller.yaml')
    base_controller_yaml = os.path.join(base_controller_path, 'config', 'mobile_base_controller.yaml')
    gripper_controller_yaml = os.path.join(gripper_controller_path, 'config', 'gripper_controller.yaml')

    arm_left_controller_yaml, arm_right_controller_yaml = generate_arm_controller_configs(arm_controller_yaml, arm_controller_path)
    gripper_left_controller_yaml,gripper_right_controller_yaml = generate_gripper_controller_configs(gripper_controller_yaml, gripper_controller_path)
    
    merged_yaml = merge_param_files([
                                    controller_manager_config_yaml,
                                    arm_right_controller_yaml, 
                                    arm_left_controller_yaml, 
                                    gripper_left_controller_yaml,
                                    gripper_right_controller_yaml,
                                    base_controller_yaml,
                                    head_controller_yaml, 
                                    joint_state_broadcaster_yaml, 
                                    torso_controller_yaml ])

    launch_description.add_action(OpaqueFunction(
        function=mujoco_model_publisher))

    node_mujoco_ros2_control = Node(
        package='mujoco_ros2_control',
        executable='mujoco_ros2_control',
        output='screen',
        parameters=[merged_yaml, {'use_sim_time': True}],
    ) 
    launch_description.add_action(node_mujoco_ros2_control)

    move_group = include_scoped_launch_py_description(
        pkg_name="tiago_pro_moveit_config",
        paths=["launch", "move_group.launch.py"],
        launch_arguments={
            "robot_name": robot_name,
            "use_sim_time": LaunchConfiguration("use_sim_time"),
            "base_type": launch_args.base_type,
            "arm_type_right": launch_args.arm_type_right,
            "arm_type_left": launch_args.arm_type_left,
            "wrist_model_right": launch_args.wrist_model_left,
            "wrist_model_left": launch_args.wrist_model_right,
            "end_effector_right": launch_args.end_effector_right,
            "end_effector_left": launch_args.end_effector_left,
            "ft_sensor_right": launch_args.ft_sensor_right,
            "ft_sensor_left": launch_args.ft_sensor_left
        },
        condition=IfCondition(LaunchConfiguration("moveit")))

    launch_description.add_action(move_group)

    tiago_bringup = include_scoped_launch_py_description(
        pkg_name="tiago_pro_bringup", paths=["launch", "tiago_pro_bringup.launch.py"],
        launch_arguments={
            "use_sim_time": LaunchConfiguration("use_sim_time"),
            "arm_type_right": launch_args.arm_type_right,
            "arm_type_left": launch_args.arm_type_left,
            "end_effector_right": launch_args.end_effector_right,
            "end_effector_left": launch_args.end_effector_left,
            "wrist_model_right": launch_args.wrist_model_left,
            "wrist_model_left": launch_args.wrist_model_right,
            "ft_sensor_right": launch_args.ft_sensor_right,
            "ft_sensor_left": launch_args.ft_sensor_left,
            "tool_changer_right": launch_args.tool_changer_right,
            "tool_changer_left": launch_args.tool_changer_left,
            "wrist_model_right": launch_args.wrist_model_right,
            "wrist_model_left": launch_args.wrist_model_left,
            "laser_model": launch_args.laser_model,
            "camera_model": launch_args.camera_model,
            "base_type": launch_args.base_type,
            "is_public_sim": launch_args.is_public_sim,
            "mujoco": launch_args.mujoco,
            "mj_control": launch_args.mj_control,
            "mj_simulate": launch_args.mj_simulate,
            }  
    )

    launch_description.add_action(tiago_bringup)

    tuck_arm = Node(
        package="tiago_pro_gazebo",
        executable="tuck_arm.py",
        emulate_tty=True,
        output="both",
        condition=IfCondition(LaunchConfiguration('tuck_arm'))
    )

    launch_description.add_action(tuck_arm)

    return

def mujoco_model_publisher(context, *args, **kwargs):
    xacro_input_args = {
            "robot_name": "tiago_pro",
            "mujoco": LaunchConfiguration("mujoco").perform(context),
            "mj_control": LaunchConfiguration("mj_control").perform(context),
            "mj_simulate": LaunchConfiguration("mj_simulate").perform(context),
            "base_type": LaunchConfiguration("base_type"),
            "end_effector_left": LaunchConfiguration("end_effector_left"),
            "end_effector_right": LaunchConfiguration("end_effector_right"),
            "arm_type_left": LaunchConfiguration("arm_type_left"),
            "arm_type_right": LaunchConfiguration("arm_type_right"),
            "wrist_model_left": LaunchConfiguration("wrist_model_left"),
            "wrist_model_right": LaunchConfiguration("wrist_model_right"),
    }
    
    model_pub = Node(
        package='pal_mujoco_model_loader_ros',
        executable='publisher',
        parameters=[xacro_input_args],
        output='screen'
    )
    
    return [model_pub]

def generate_arm_controller_configs(arm_controller_yaml, arm_controller_path):

    with open(arm_controller_yaml, 'r') as file:
        content = file.read()

    left_content = content.replace('${ARM_SIDE_PREFIX}', 'arm_left')
    arm_left_controller_yaml = os.path.join(arm_controller_path, 'config', 'arm_left_controller.yaml')
    
    with open(arm_left_controller_yaml, 'w') as left_file:
        left_file.write(left_content)

    right_content = content.replace('${ARM_SIDE_PREFIX}', 'arm_right')
    arm_right_controller_yaml = os.path.join(arm_controller_path, 'config', 'arm_right_controller.yaml')
    
    with open(arm_right_controller_yaml, 'w') as right_file:
        right_file.write(right_content)

    return arm_left_controller_yaml, arm_right_controller_yaml

def generate_gripper_controller_configs(gripper_controller_yaml, gripper_controller_path):
    with open(gripper_controller_yaml, 'r') as file:
            content = file.read()

    left_content = content.replace('${EE_SIDE_PREFIX}', f'gripper_left_inner')
    gripper_left_controller_yaml = os.path.join(gripper_controller_path, 'config', f'gripper_left_controller.yaml')
    
    with open(gripper_left_controller_yaml, 'w') as left_file:
        left_file.write(left_content)
    
    right_content = content.replace('${EE_SIDE_PREFIX}', f'gripper_right_inner')
    gripper_right_controller_yaml = os.path.join(gripper_controller_path, 'config', f'gripper_right_controller.yaml')
    
    with open( gripper_right_controller_yaml, 'w') as right_file:
        right_file.write(right_content)
    
    return gripper_left_controller_yaml, gripper_right_controller_yaml

def generate_launch_description():

    # Create the launch description
    ld = LaunchDescription()

    launch_arguments = LaunchArguments()

    launch_arguments.add_to_launch_description(ld)

    declare_actions(ld, launch_arguments)

    return ld
