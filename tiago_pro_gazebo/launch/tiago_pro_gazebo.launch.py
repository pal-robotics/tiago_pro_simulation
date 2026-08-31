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
from os import environ, pathsep
from ament_index_python.packages import get_package_prefix

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    SetEnvironmentVariable,
    SetLaunchConfiguration,
    OpaqueFunction,
)
from launch.conditions import IfCondition
from launch.substitutions import (
    LaunchConfiguration,
    AndSubstitution,
    NotSubstitution,
)
from launch_pal.include_utils import (
    include_scoped_launch_py_description,
)
from launch_pal.actions import CheckPublicSim

from launch_pal.arg_utils import LaunchArgumentsBase, read_launch_argument
from launch_pal.robot_arguments import CommonArgs
from launch_pal.conditions import UnlessNodeRunning
from tiago_pro_description.launch_arguments import TiagoProArgs
from dataclasses import dataclass
from launch_ros.actions import Node


@dataclass(frozen=True)
class LaunchArguments(LaunchArgumentsBase):
    base_type: DeclareLaunchArgument = TiagoProArgs.base_type
    arm_type_right: DeclareLaunchArgument = TiagoProArgs.arm_type_right
    arm_type_left: DeclareLaunchArgument = TiagoProArgs.arm_type_left
    end_effector_right: DeclareLaunchArgument = TiagoProArgs.end_effector_right
    end_effector_left: DeclareLaunchArgument = TiagoProArgs.end_effector_left
    ft_sensor_right: DeclareLaunchArgument = TiagoProArgs.ft_sensor_right
    ft_sensor_left: DeclareLaunchArgument = TiagoProArgs.ft_sensor_left
    ft_sensor_teleop_left: DeclareLaunchArgument = TiagoProArgs.ft_sensor_teleop_left
    ft_sensor_teleop_right: DeclareLaunchArgument = TiagoProArgs.ft_sensor_teleop_right
    tool_changer_right: DeclareLaunchArgument = TiagoProArgs.tool_changer_right
    tool_changer_left: DeclareLaunchArgument = TiagoProArgs.tool_changer_left
    wrist_model_right: DeclareLaunchArgument = TiagoProArgs.wrist_model_right
    wrist_model_left: DeclareLaunchArgument = TiagoProArgs.wrist_model_left
    camera_model: DeclareLaunchArgument = TiagoProArgs.camera_model
    laser_model: DeclareLaunchArgument = TiagoProArgs.laser_model
    has_teleop_arms: DeclareLaunchArgument = TiagoProArgs.has_teleop_arms
    has_wrist_camera: DeclareLaunchArgument = TiagoProArgs.has_wrist_camera

    navigation: DeclareLaunchArgument = CommonArgs.navigation
    advanced_navigation: DeclareLaunchArgument = CommonArgs.advanced_navigation
    slam: DeclareLaunchArgument = CommonArgs.slam
    docking: DeclareLaunchArgument = CommonArgs.docking
    moveit: DeclareLaunchArgument = CommonArgs.moveit
    world_name: DeclareLaunchArgument = CommonArgs.world_name
    tuck_arm: DeclareLaunchArgument = CommonArgs.tuck_arm
    is_public_sim: DeclareLaunchArgument = CommonArgs.is_public_sim
    namespace: DeclareLaunchArgument = CommonArgs.namespace
    rviz: DeclareLaunchArgument = CommonArgs.rviz
    gzclient: DeclareLaunchArgument = CommonArgs.gzclient
    gazebo_version: DeclareLaunchArgument = CommonArgs.gazebo_version
    play_motion2: DeclareLaunchArgument = DeclareLaunchArgument(
        "play_motion2",
        default_value="True",
        description="Launch play_motion2",
        choices=["True", "False"],
    )


def generate_launch_description():

    # Create the launch description and populate
    ld = LaunchDescription()
    launch_arguments = LaunchArguments()

    launch_arguments.add_to_launch_description(ld)

    declare_actions(ld, launch_arguments)

    return ld


def start_gazebo(context, *args, **kwargs):
    world_name = read_launch_argument('world_name', context)
    gzclient = read_launch_argument('gzclient', context)
    gazebo_version = read_launch_argument('gazebo_version', context)
    is_public_sim = read_launch_argument('is_public_sim', context)

    packages = ['tiago_pro_description', 'pal_sea_arm_description',
                'omni_base_description', 'pal_pro_gripper_description',
                'tiago_pro_head_description', 'pal_urdf_utils',
                'pal_atc_description']

    if not is_public_sim == 'True':
        packages.append('allegro_hand_description')

    model_path = get_model_paths(packages)

    if gazebo_version == 'gazebo':
        PATH = 'GZ_SIM_RESOURCE_PATH'
    else:
        PATH = 'GAZEBO_MODEL_PATH'

    if PATH in environ:
        model_path += pathsep + environ[PATH]

    gazebo_model_path_env_var = SetEnvironmentVariable(PATH, model_path)

    gazebo = include_scoped_launch_py_description(
        pkg_name='pal_gazebo_worlds',
        paths=['launch', 'pal_gazebo.launch.py'],
        env_vars=[gazebo_model_path_env_var],
        launch_arguments={
            "world_name":  world_name,
            "model_paths": packages,
            "resource_paths": packages,
            "gzclient": gzclient,
            'gazebo_version': gazebo_version,
        },
        condition=UnlessNodeRunning("gazebo")
    )

    return [gazebo]


def declare_actions(
    launch_description: LaunchDescription, launch_args: LaunchArguments
):
    # Set use_sim_time to True
    set_sim_time = SetLaunchConfiguration('use_sim_time', 'True')
    launch_description.add_action(set_sim_time)

    # Shows error if is_public_sim is not set to True when using public simulation
    public_sim_check = CheckPublicSim()
    launch_description.add_action(public_sim_check)

    robot_name = 'tiago_pro'

    launch_description.add_action(OpaqueFunction(function=start_gazebo))

    public_navigation_launch = include_scoped_launch_py_description(
        condition=IfCondition(AndSubstitution(
            LaunchConfiguration('is_public_sim'), LaunchConfiguration('navigation'))
        ),
        pkg_name='tiago_pro_gazebo',
        paths=['launch', 'navigation_public_sim.launch.py'],
        launch_arguments={
            'world_name': launch_args.world_name,
            'slam': launch_args.slam,
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'rviz': launch_args.rviz,
        },
    )
    launch_description.add_action(public_navigation_launch)

    private_navigation_launch = include_scoped_launch_py_description(
        condition=IfCondition(AndSubstitution(
            NotSubstitution(LaunchConfiguration('is_public_sim')),
            LaunchConfiguration('navigation'))
        ),
        pkg_name='tiago_pro_gazebo',
        paths=['launch', 'navigation_private_sim.launch.py'],
        launch_arguments={
            'namespace': launch_args.namespace,
            'camera_model': launch_args.camera_model,
            'base_type': launch_args.base_type,
            'laser_model': launch_args.laser_model,
            'docking': launch_args.docking,
            'slam': launch_args.slam,
            'advanced_navigation': launch_args.advanced_navigation,
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'rviz': launch_args.rviz,
        },
    )
    launch_description.add_action(private_navigation_launch)

    move_group = include_scoped_launch_py_description(
        pkg_name='tiago_pro_moveit_config',
        paths=['launch', 'move_group.launch.py'],
        launch_arguments={
            'robot_name': robot_name,
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'base_type': launch_args.base_type,
            'arm_type_right': launch_args.arm_type_right,
            'arm_type_left': launch_args.arm_type_left,
            'end_effector_right': launch_args.end_effector_right,
            'end_effector_left': launch_args.end_effector_left,
            'ft_sensor_right': launch_args.ft_sensor_right,
            'ft_sensor_left': launch_args.ft_sensor_left,
            'ft_sensor_teleop_right': launch_args.ft_sensor_teleop_right,
            'ft_sensor_teleop_left': launch_args.ft_sensor_teleop_left,
            'has_teleop_arms': launch_args.has_teleop_arms,
            'wrist_model_right': launch_args.wrist_model_right,
            'wrist_model_left': launch_args.wrist_model_left,
        },
        condition=IfCondition(LaunchConfiguration('moveit')))

    launch_description.add_action(move_group)

    robot_spawn = include_scoped_launch_py_description(
        pkg_name='tiago_pro_gazebo',
        paths=['launch', 'robot_spawn.launch.py'],
        launch_arguments={
            'robot_name': robot_name,
            'gazebo_version': LaunchConfiguration('gazebo_version'),
        }
    )

    launch_description.add_action(robot_spawn)

    tiago_bringup = include_scoped_launch_py_description(
        pkg_name='tiago_pro_bringup', paths=['launch', 'tiago_pro_bringup.launch.py'],
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'arm_type_right': launch_args.arm_type_right,
            'arm_type_left': launch_args.arm_type_left,
            'end_effector_right': launch_args.end_effector_right,
            'end_effector_left': launch_args.end_effector_left,
            'ft_sensor_right': launch_args.ft_sensor_right,
            'ft_sensor_left': launch_args.ft_sensor_left,
            'tool_changer_right': launch_args.tool_changer_right,
            'ft_sensor_teleop_right': launch_args.ft_sensor_teleop_right,
            'ft_sensor_teleop_left': launch_args.ft_sensor_teleop_left,
            'tool_changer_left': launch_args.tool_changer_left,
            'wrist_model_right': launch_args.wrist_model_right,
            'wrist_model_left': launch_args.wrist_model_left,
            'laser_model': launch_args.laser_model,
            'camera_model': launch_args.camera_model,
            'base_type': launch_args.base_type,
            'is_public_sim': launch_args.is_public_sim,
            'gazebo_version': launch_args.gazebo_version,
            'has_teleop_arms': launch_args.has_teleop_arms,
            'has_wrist_camera': launch_args.has_wrist_camera,
            'play_motion2': LaunchConfiguration('play_motion2')}
    )

    launch_description.add_action(tiago_bringup)

    tuck_arm = Node(
        package='tiago_pro_gazebo',
        executable='tuck_arm.py',
        emulate_tty=True,
        output='both',
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

    return model_paths
