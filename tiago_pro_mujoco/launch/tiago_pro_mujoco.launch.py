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
from ament_index_python.packages import get_package_prefix, get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    SetEnvironmentVariable,
    SetLaunchConfiguration,
    GroupAction,
    OpaqueFunction,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration

from launch_pal.include_utils import (
    include_scoped_launch_py_description,
    include_launch_py_description,
)
from launch_pal.actions import CheckPublicSim

from launch_pal.arg_utils import LaunchArgumentsBase, read_launch_argument
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

    # navigation: DeclareLaunchArgument = CommonArgs.navigation
    # advanced_navigation: DeclareLaunchArgument = CommonArgs.advanced_navigation
    # slam: DeclareLaunchArgument = CommonArgs.slam
    # docking: DeclareLaunchArgument = CommonArgs.docking
    # world_name: DeclareLaunchArgument = CommonArgs.world_name
    tuck_arm: DeclareLaunchArgument = CommonArgs.tuck_arm
    is_public_sim: DeclareLaunchArgument = CommonArgs.is_public_sim

    mujoco: DeclareLaunchArgument = DeclareLaunchArgument(
        'mujoco', default_value='true', choices=['true', 'false'], description='Mujoco tags')
    mj_position: DeclareLaunchArgument = DeclareLaunchArgument(
        'mj_position', default_value='true', choices=['true', 'false'], description='Mujoco position tags')
    mj_motor: DeclareLaunchArgument = DeclareLaunchArgument(
        'mj_motor', default_value='false', choices=['true', 'false'], description='Mujoco motor tags')
    mj_control: DeclareLaunchArgument = DeclareLaunchArgument(
        'mj_control', default_value='true', choices=['true', 'false'], description='Mujoco Ros2 control tags')
    mj_simulate: DeclareLaunchArgument = DeclareLaunchArgument(
        'mj_simulate', default_value='false', choices=['true', 'false'], description='Mujoco simulation tool tags')

# def private_navigation(context, *args, **kwargs):
#     actions = []
#     base_type = read_launch_argument('base_type', context)
#     camera_model = read_launch_argument('camera_model', context)
#     docking = read_launch_argument('docking', context)
#     advanced_navigation = read_launch_argument('advanced_navigation', context)
#     use_sim_time = read_launch_argument('use_sim_time', context)
#     rviz_cfg_pkg = base_type + '_2dnav'
#     if advanced_navigation == 'True':
#         rviz_cfg_pkg = base_type + '_advanced_2dnav'

#     robot_info = {
#         "robot_info_publisher": {
#             "ros__parameters": {
#                 "robot_type": "tiago_pro",
#                 "base_type": base_type,
#                 "laser_model": "sick-571",
#                 "camera_model": camera_model,
#                 "advanced_navigation": (advanced_navigation == 'True'),
#                 "has_dock": (docking == 'True'),
#                 "use_sim_time": (use_sim_time == 'True'),
#             }
#         }
#     }

#     temp_yaml = tempfile.mkdtemp()
#     temp_robot_info = os.path.join(temp_yaml, '99_robot_info.yaml')
#     with open(temp_robot_info, 'w') as temp_robot_info_file:
#         yaml.safe_dump(robot_info, temp_robot_info_file)

#     # Robot Info Publisher
#     robot_info_env = SetEnvironmentVariable(
#         name='ROBOT_INFO_PATH',
#         value=temp_yaml,
#     )
#     actions.append(robot_info_env)

#     robot_info_publisher = Node(
#         package='robot_info_publisher',
#         executable='robot_info_publisher',
#         name='robot_info_publisher',
#         output='screen',
#     )
#     actions.append(robot_info_publisher)

#     # Laser Sensors
#     laser_bringup_launch = include_launch_py_description(
#         pkg_name=base_type + '_laser_sensors',
#         paths=['launch', 'laser_sim.launch.py'],
#     )
#     actions.append(laser_bringup_launch)

#     # Navigation
#     nav_bringup_launch = include_launch_py_description(
#         pkg_name=base_type + '_2dnav',
#         paths=['launch', 'navigation.launch.py'],
#     )
#     actions.append(nav_bringup_launch)

#     # Localization
#     loc_bringup_launch = include_launch_py_description(
#         pkg_name=base_type + '_2dnav',
#         paths=['launch', 'localization.launch.py'],
#         condition=UnlessCondition(LaunchConfiguration('slam'))
#     )
#     actions.append(loc_bringup_launch)

#     # SLAM
#     slam_bringup_launch = include_launch_py_description(
#         pkg_name=base_type + '_2dnav',
#         paths=['launch', 'slam.launch.py'],
#         condition=IfCondition(LaunchConfiguration('slam'))
#     )
#     actions.append(slam_bringup_launch)

#     # Docking
#     docking_bringup_launch = include_launch_py_description(
#         pkg_name=base_type + '_docking',
#         paths=['launch', 'docking_sim.launch.py'],
#         condition=IfCondition(LaunchConfiguration('docking'))
#     )
#     actions.append(docking_bringup_launch)

#     # Stores Server
#     db_bringup_launch = Node(
#         package='pal_stores_server',
#         executable='pal_stores_server',
#         arguments=[os.path.join(
#             os.environ['HOME'], '.pal', 'stores.db'
#         )],
#         output='screen',
#         condition=IfCondition(LaunchConfiguration('advanced_navigation'))
#     )
#     actions.append(db_bringup_launch)

#     # Advanced Navigation
#     advanced_nav_bringup_launch = include_launch_py_description(
#         pkg_name=base_type + '_advanced_2dnav',
#         paths=['launch', 'advanced_navigation.launch.py'],
#         condition=IfCondition(LaunchConfiguration('advanced_navigation'))
#     )
#     actions.append(advanced_nav_bringup_launch)

#     # RViz
#     rviz_bringup_launch = Node(
#         package='rviz2',
#         executable='rviz2',
#         arguments=['-d', os.path.join(
#             get_package_share_directory(rviz_cfg_pkg),
#             'config',
#             'rviz',
#             'navigation.rviz',
#         )],
#         parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
#         output='screen',
#     )
#     actions.append(rviz_bringup_launch)
#     return actions


def declare_actions(launch_description: LaunchDescription, launch_args: LaunchArguments):

    # Set use_sim_time to True
    set_sim_time = SetLaunchConfiguration("use_sim_time", "True")
    launch_description.add_action(set_sim_time)

    # Shows error if is_public_sim is not set to True when using public simulation
    public_sim_check = CheckPublicSim()
    launch_description.add_action(public_sim_check)

    robot_name = "tiago_pro"

    tiago_pro_controller_path = os.path.join(get_package_share_directory('tiago_pro_controller_configuration'))
    head_controller_path = os.path.join(get_package_share_directory('tiago_pro_head_controller_configuration'))
    arm_controller_path = os.path.join(get_package_share_directory('pal_sea_arm_controller_configuration'))
    base_controller_path = os.path.join(get_package_share_directory('omni_base_controller_configuration'))
    # inference_controller_path= os.path.join(get_package_share_directory('arm_controller'))

    controller_manager_config_yaml = os.path.join(tiago_pro_controller_path, 'config', 'mujoco_controller_manager_cfg.yaml')

    torso_controller_yaml = os.path.join(tiago_pro_controller_path, 'config', 'torso_controller.yaml')
    joint_state_broadcaster_yaml = os.path.join(tiago_pro_controller_path, 'config', 'joint_state_broadcaster.yaml')
    head_controller_yaml = os.path.join(head_controller_path, 'config', 'head_controller.yaml')
    arm_controller_yaml = os.path.join(arm_controller_path, 'config', 'arm_controller.yaml')
    # arm_controller_yaml = os.path.join(inference_controller_path, 'config', 'joint_group_position_controller.yaml')
    base_controller_yaml = os.path.join(base_controller_path, 'config', 'mobile_base_controller.yaml')

    # ft_sensor_controller_yaml = os.path.join(tiago_pro_controller_path, 'config', 'ft_sensor_controller.yaml')
    
    with open(arm_controller_yaml, 'r') as file:
        content = file.read()

    left_content = content.replace('${ARM_SIDE_PREFIX}', f'arm_left')
    arm_left_controller_yaml = os.path.join(arm_controller_path, 'config', f'arm_left_controller.yaml')
    
    with open(arm_left_controller_yaml, 'w') as left_file:
        left_file.write(left_content)
    
    right_content = content.replace('${ARM_SIDE_PREFIX}', f'arm_right')
    arm_right_controller_yaml = os.path.join(arm_controller_path, 'config', f'arm_right_controller.yaml')
    
    with open( arm_right_controller_yaml, 'w') as right_file:
        right_file.write(right_content)

    
    merged_yaml = merge_param_files([
                                    controller_manager_config_yaml,
                                    arm_right_controller_yaml, 
                                    arm_left_controller_yaml, 
                                    # arm_controller_yaml,
                                    base_controller_yaml,
                                    head_controller_yaml, 
                                    joint_state_broadcaster_yaml, 
                                    torso_controller_yaml, 
                                    # imu_sensor_broadcaster_yaml
                                    #  ft_sensor_controller_yaml, 
                                    ])

    model_pub = Node(
        package='pal_mujoco_model_loader_ros',
        executable='publisher',
        parameters=[{'robot_name': 'tiago_pro'}],
        output='screen',
    )
    launch_description.add_action(model_pub)

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
            "arm_type_right":"tiago-pro",
            "arm_type_left":"tiago-pro",
            # "arm_type_right": launch_args.arm_type_right,
            # "arm_type_left": launch_args.arm_type_left,
            "end_effector_right": "no-end-effector",
            "end_effector_left": "no-end-effector",
            "wrist_model_right": "spherical-wrist",
            "wrist_model_left": "spherical-wrist",
            # "end_effector_right": launch_args.end_effector_right,
            # "end_effector_left": launch_args.end_effector_left,
            "ft_sensor_right": launch_args.ft_sensor_right,
            "ft_sensor_left": launch_args.ft_sensor_left
        },
        condition=IfCondition(LaunchConfiguration("moveit")))

    launch_description.add_action(move_group)

    tiago_bringup = include_scoped_launch_py_description(
        pkg_name="tiago_pro_bringup", paths=["launch", "tiago_pro_bringup.launch.py"],
        launch_arguments={
            "use_sim_time": LaunchConfiguration("use_sim_time"),
            # "arm_type_right": launch_args.arm_type_right,
            # "arm_type_left": launch_args.arm_type_left,
            # "end_effector_right": launch_args.end_effector_right,
            # "end_effector_left": launch_args.end_effector_left,
            "arm_type_right":"tiago-pro",
            "arm_type_left":"tiago-pro",
            "wrist_model_right": "spherical-wrist",
            "wrist_model_left": "spherical-wrist",
            "end_effector_right": "no-end-effector",
            "end_effector_left": "no-end-effector",
            "ft_sensor_right": launch_args.ft_sensor_right,
            "ft_sensor_left": launch_args.ft_sensor_left,
            "tool_changer_right": launch_args.tool_changer_right,
            "tool_changer_left": launch_args.tool_changer_left,
            # "wrist_model_right": launch_args.wrist_model_right,
            # "wrist_model_left": launch_args.wrist_model_left,
            "laser_model": launch_args.laser_model,
            "camera_model": launch_args.camera_model,
            "base_type": launch_args.base_type,
            "is_public_sim": launch_args.is_public_sim,
            "mujoco": launch_args.mujoco,
            "mj_position": launch_args.mj_position,
            "mj_motor": launch_args.mj_motor,
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

def get_model_paths(packages_names):
    model_paths = ""
    for package_name in packages_names:
        if model_paths != "":
            model_paths += pathsep

        package_path = get_package_prefix(package_name)
        model_path = os.path.join(package_path, "share")

        model_paths += model_path

    if "GAZEBO_MODEL_PATH" in environ:
        model_paths += pathsep + environ["GAZEBO_MODEL_PATH"]

    return model_paths


def get_resource_paths(packages_names):
    resource_paths = ""
    for package_name in packages_names:
        if resource_paths != "":
            resource_paths += pathsep

        package_path = get_package_prefix(package_name)
        resource_paths += package_path

    if "GAZEBO_RESOURCE_PATH" in environ:
        resource_paths += pathsep + environ["GAZEBO_RESOURCE_PATH"]

    return resource_paths


def generate_launch_description():

    # Create the launch description
    ld = LaunchDescription()

    launch_arguments = LaunchArguments()

    launch_arguments.add_to_launch_description(ld)

    declare_actions(ld, launch_arguments)

    return ld
