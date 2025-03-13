import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessStart

from launch_ros.actions import Node



def generate_launch_description():


    package_name='ralph_7' 

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'false', 'use_ros2_control': 'true'}.items()
    )

    robot_description = Command(['ros2 param get --hide-type /robot_state_publisher robot_description'])

    controller_params_file = os.path.join(get_package_share_directory(package_name),'config','my_controllers.yaml')

    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[{'robot_description': robot_description},
                    controller_params_file]
    )

    delayed_controller_manager = TimerAction(period=3.0, actions=[controller_manager])

    diff_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_cont"],
    )

    delayed_diff_drive_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[diff_drive_spawner],
        )
    )

    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"],
    )

    delayed_joint_broad_spawner = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[joint_broad_spawner],
        )
    )

    lidar = Node(
            package='sllidar_ros2',
            executable='sllidar_node',
            name='sllidar_node',
            parameters=[{'channel_type':'serial',
                         'serial_port': '/dev/rplidar', 
                         'serial_baudrate': 115200, 
                         'frame_id': 'laser_frame',
                         'inverted': False, 
                         'angle_compensate': True}],
    )

    hardware_interface = Node(
            package='micro_ros_agent',
            executable='micro_ros_agent',
            name='hardware_interface',
            arguments=["serial", "--dev","/dev/ttyACM0"]
    )

    depth_cam = Node(
            package='realsense2_camera',
            executable='realsense2_camera_node',
            name='realsense2_node',
            parameters=[{'enable_color':'false',
                         'spatial_filter.enable': 'true', 
                         'temporal_filter.enable': 'true'}],
    )


    gps = Node(
            package='vk_162_gps',
            executable='gps',
            name='vk_162_gps_handler',
            output='screen',
            emulate_tty=True,
            parameters=[
                {'deviceName': '/dev/vkgps'}
            ]
    )

    foxglove = Node(
            package='foxglove_bridge',
            executable='foxglove_bridge',
            name='foxglove_websocket'
    )

    delayed_rplidar = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[lidar],
        )
    )

    delayed_foxglove = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=controller_manager,
            on_start=[foxglove],
        )
    )

    joy_params = os.path.join(get_package_share_directory('ralph_7'),'config','joystick.yaml')

    teleop_node = Node(
            package='teleop_twist_joy',
            executable='teleop_node',
            name='teleop_node',
            parameters=[joy_params],
            remappings=[('/cmd_vel','/diff_cont/cmd_vel_unstamped')]
         )

    return LaunchDescription([
        rsp,
        delayed_controller_manager,
        delayed_diff_drive_spawner,
        delayed_joint_broad_spawner,
        teleop_node,
        depth_cam,
        hardware_interface,
        delayed_rplidar,
        #gps,
        foxglove
    ])
