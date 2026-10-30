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


from dataclasses import dataclass
import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, SetLaunchConfiguration
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_pal.actions import CheckPublicSim
from launch_pal.arg_utils import LaunchArgumentsBase
from launch_pal.include_utils import (
    include_scoped_launch_py_description,
)

from launch_pal.robot_arguments import CommonArgs
from launch_ros.actions import Node
from tiago_pro_description.launch_arguments import TiagoProArgs


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
    moveit: DeclareLaunchArgument = CommonArgs.moveit
    world_name: DeclareLaunchArgument = CommonArgs.world_name
    is_public_sim: DeclareLaunchArgument = CommonArgs.is_public_sim
    sim_type: DeclareLaunchArgument = CommonArgs.sim_type
    mj_control: DeclareLaunchArgument = CommonArgs.mj_control
    mj_initial_pose: DeclareLaunchArgument = CommonArgs.mj_initial_pose


def declare_actions(launch_description: LaunchDescription, launch_args: LaunchArguments):

    # Check that the requested MuJoCo scene exists before the xacro is processed
    def check_world_name(context, *args, **kwargs):
        world_name = LaunchConfiguration('world_name').perform(context)
        scenes_dir = os.path.join(get_package_share_directory('pal_mujoco_scenes'), 'scenes')
        available_scenes = sorted(
            os.path.splitext(f)[0] for f in os.listdir(scenes_dir) if f.endswith('.xacro'))
        if world_name not in available_scenes:
            raise RuntimeError(
                f"MuJoCo scene '{world_name}' not found in {scenes_dir}. "
                f"Available scenes: {', '.join(available_scenes)}")
        return []
    launch_description.add_action(OpaqueFunction(function=check_world_name))

    # Set use_sim_time to True
    set_sim_time = SetLaunchConfiguration('use_sim_time', 'True')
    launch_description.add_action(set_sim_time)

    # Set simulation_type to Mujoco Ros2 Control
    set_sim_type = SetLaunchConfiguration('sim_type', 'mujoco-ros2-control')
    launch_description.add_action(set_sim_type)

    # Shows error if is_public_sim is not set to True when using public simulation
    public_sim_check = CheckPublicSim()
    launch_description.add_action(public_sim_check)

    robot_name = 'tiago_pro'

    # Use decomposed meshes for the base of the robot
    omni_base_asset_path = os.path.join(
        get_package_share_directory('omni_base_description'),
        'mujoco', 'assets'
    )
    mujoco_plugins_path = os.path.join(
        get_package_share_directory('tiago_pro_mujoco'),
        'config', 'mujoco_ros2_control_plugins.yaml'
    )

    tiago_bringup = include_scoped_launch_py_description(
        pkg_name='tiago_pro_bringup', paths=['launch', 'tiago_pro_bringup.launch.py'],
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'arm_type_right': launch_args.arm_type_right,
            'arm_type_left': launch_args.arm_type_left,
            'end_effector_right': launch_args.end_effector_right,
            'end_effector_left': launch_args.end_effector_left,
            'wrist_model_right': launch_args.wrist_model_right,
            'wrist_model_left': launch_args.wrist_model_left,
            'ft_sensor_right': launch_args.ft_sensor_right,
            'ft_sensor_left': launch_args.ft_sensor_left,
            'tool_changer_right': launch_args.tool_changer_right,
            'tool_changer_left': launch_args.tool_changer_left,
            'laser_model': launch_args.laser_model,
            'camera_model': launch_args.camera_model,
            'base_type': launch_args.base_type,
            'is_public_sim': launch_args.is_public_sim,
            'has_wrist_camera': launch_args.has_wrist_camera,
            'sim_type': LaunchConfiguration('sim_type'),
            'mj_control': LaunchConfiguration('mj_control'),
            'world_name': launch_args.world_name,
            'ft_sensor_teleop_right': launch_args.ft_sensor_teleop_right,
            'ft_sensor_teleop_left': launch_args.ft_sensor_teleop_left,
            'has_teleop_arms': launch_args.has_teleop_arms,
            'mj_initial_pose': launch_args.mj_initial_pose
        }
    )

    launch_description.add_action(tiago_bringup)

    # Launch the conversion node
    def converter_node_setup(context, *args, **kwargs):
        args_list = [
            '-p', 'mujoco_robot_description',
            '--no-fuse',
            '-f',
            '-a', omni_base_asset_path,
        ]
        return [Node(
            package='mujoco_ros2_control',
            executable='robot_description_to_mjcf.sh',
            output='both',
            emulate_tty=True,
            arguments=args_list,
        )]

    launch_description.add_action(OpaqueFunction(function=converter_node_setup))

    # Mujoco Ros2 Control Simulation
    def control_node_setup(context, *args, **kwargs):
        parameters = [
            {"use_sim_time": LaunchConfiguration("use_sim_time")},
            mujoco_plugins_path,
        ]
        # FTS gravity compensation only for the wrists with a force/torque sensor:
        # the plugin fails to load if the sensor is not in the model
        config_dir = os.path.join(get_package_share_directory('tiago_pro_mujoco'), 'config')
        for side in ('right', 'left'):
            ft_sensor = LaunchConfiguration(f'ft_sensor_{side}').perform(context)
            if ft_sensor == 'no-ft-sensor':
                continue
            # the load on the sensor depends on the end effector: one file per sensor and end effector
            end_effector = LaunchConfiguration(f'end_effector_{side}').perform(context).replace('-', '_')
            config_file = os.path.join(config_dir, f'fts_grav_comp_{side}_{ft_sensor}_{end_effector}.yaml')
            if os.path.exists(config_file):
                parameters.append(config_file)
            else:
                print(f'No FTS gravity compensation for the {side} wrist: '
                      f'{os.path.basename(config_file)} not found')
        return [Node(
            package="mujoco_ros2_control",
            executable="ros2_control_node",
            output="both",
            parameters=parameters,
        )]

    launch_description.add_action(OpaqueFunction(function=control_node_setup))

    # The TF odom -> base_footprint, from the base's true pose (nothing publishes it in MuJoCo)
    odom_tf_node = Node(
        package='tiago_pro_mujoco',
        executable='ground_truth_odom_tf.py',
        output='both',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )

    launch_description.add_action(odom_tf_node)

    move_group = include_scoped_launch_py_description(
        pkg_name='tiago_pro_moveit_config',
        paths=['launch', 'move_group.launch.py'],
        launch_arguments={
            'robot_name': robot_name,
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'base_type': launch_args.base_type,
            'arm_type_right': launch_args.arm_type_right,
            'arm_type_left': launch_args.arm_type_left,
            'wrist_model_right': launch_args.wrist_model_left,
            'wrist_model_left': launch_args.wrist_model_right,
            'end_effector_right': launch_args.end_effector_right,
            'end_effector_left': launch_args.end_effector_left,
            'ft_sensor_right': launch_args.ft_sensor_right,
            'ft_sensor_left': launch_args.ft_sensor_left,
            'ft_sensor_teleop_right': launch_args.ft_sensor_teleop_right,
            'ft_sensor_teleop_left': launch_args.ft_sensor_teleop_left,
            'has_teleop_arms': launch_args.has_teleop_arms,
        },
        condition=IfCondition(LaunchConfiguration('moveit')))

    launch_description.add_action(move_group)

    return


def generate_launch_description():

    # Create the launch description
    ld = LaunchDescription()

    launch_arguments = LaunchArguments()

    launch_arguments.add_to_launch_description(ld)

    declare_actions(ld, launch_arguments)

    return ld
