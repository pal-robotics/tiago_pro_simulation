^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Changelog for package tiago_pro_gazebo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Forthcoming
-----------
* stores_server log level
* separate advanced docking
* Contributors: antoniobrandi

1.16.0 (2026-03-30)
-------------------
* Add gz bridge
* New gazebo
* Contributors: thomaspeyrucain

1.15.0 (2026-03-18)
-------------------
* Add support for short-wrist
* Contributors: Noel Jimenez

1.14.1 (2026-02-05)
-------------------
* uncomment tuck arm
* remove end effectors teleop station - add wrist
* Contributors: ileniaperrella

1.14.0 (2026-02-02)
-------------------
* add end_effectors_teleop in the gazebo launch
* fix launch file typos
* fix missing comma
* add TiagoProArgs ee teleop
* add ft sensors in sim
* add teleop in simulation
* Contributors: ileniaperrella

1.13.1 (2025-12-15)
-------------------
* missing deps
* Contributors: antoniobrandi

1.13.0 (2025-12-11)
-------------------
* Point Cloud filter pipeline
* Contributors: antoniobrandi

1.12.2 (2025-10-28)
-------------------
* Add condition for allegro hand on public simulation
* Contributors: Noel Jimenez

1.12.1 (2025-10-28)
-------------------
* Add condition for allegro_hand dependency
* Contributors: Noel Jimenez

1.12.0 (2025-10-28)
-------------------
* Revert "Merge branch 'feat/aca/missing-dep-public-sim' into 'humble-devel'"
  This reverts merge request !49
* Contributors: antoniobrandi

1.11.2 (2025-10-27)
-------------------
* added missing dep for public sim
* Contributors: andreacapodacqua

1.11.1 (2025-10-14)
-------------------
* allegro hand dep released
* fix deps
* cosmetic
* added public navigation
* Contributors: andreacapodacqua

1.11.0 (2025-10-09)
-------------------
* added gzclient and rviz args
* Contributors: martinaannicelli

1.10.1 (2025-06-05)
-------------------
* Add pal_urdf_utils as env var path for gazebo
* Contributors: Aina

1.10.0 (2025-05-07)
-------------------
* add use_sim_time to robot_info
* Contributors: antoniobrandi

1.9.0 (2025-05-06)
------------------
* fix slam launch_args
* Contributors: antoniobrandi

1.8.0 (2025-05-06)
------------------
* rviz use_sim_time
* Contributors: antoniobrandi

1.7.2 (2025-05-05)
------------------
* fix deps
* Contributors: andreacapodacqua

1.7.1 (2025-04-17)
------------------
* Add allegro dependency
* Açdd allegro-hand as possible end-effector
* Contributors: Aina

1.7.0 (2025-04-03)
------------------
* store robot_info in tmp
* Contributors: antoniobrandi

1.6.0 (2025-04-03)
------------------
* Adopt pal configuration
* Contributors: antoniobrandi

1.5.0 (2025-01-16)
------------------
* Merge branch 'tpe/simplify-3d-model' into 'humble-devel'
  remove laptop tray option
  See merge request robots/tiago_pro_simulation!32
* remove laptop tray option
* Contributors: thomas.peyrucain, thomaspeyrucain

1.4.0 (2024-12-02)
------------------
* Remove unnecesary controller_configuration dependency
* Add space to add distinction between robot info and other params as it already was
* Add again camera arg
* Update packages for gz and remove camera model as argument
* Contributors: Aina

1.3.0 (2024-12-02)
------------------
* Merge branch 'abr/feat/deps-and-specs' into 'humble-devel'
  nav deps and specifics
  See merge request robots/tiago_pro_simulation!31
* always start docking with adv navigation
* nav deps and specifics
* Merge branch 'omm/removable_tray' into 'humble-devel'
  Added arguments for supporting the removable tray
  See merge request robots/tiago_pro_simulation!26
* Added arguments for supporting the removable tray
* Contributors: antoniobrandi, davidterkuile, oscarmartinez

1.2.0 (2024-10-16)
------------------
* Merge branch 'man/feat/advanced-nav' into 'humble-devel'
  added advanced nav to navigation
  See merge request robots/tiago_pro_simulation!28
* added advanced nav to navigation
* Contributors: antoniobrandi, martinaannicelli

1.1.0 (2024-09-19)
------------------
* Added tool changer args
* Contributors: oscarmartinez

1.0.9 (2024-07-23)
------------------
* added tuck arm argument
* Contributors: sergiacosta

1.0.8 (2024-07-08)
------------------
* Merge branch 'fix/use_common_slam_arg' into 'humble-devel'
  Use slam from CommonArgs
  See merge request robots/tiago_pro_simulation!23
* Add missing navigation related launch arguments
* Use slam from CommonArgs
* Merge branch 'abr/feat/advanced-navigation' into 'humble-devel'
  added advanced navigation
  See merge request robots/tiago_pro_simulation!22
* added advanced navigation
* Contributors: Noel Jimenez, antoniobrandi, davidterkuile

1.0.7 (2024-06-26)
------------------
* Merge branch 'dtk/move-robot-args' into 'humble-devel'
  Change import for launch args
  See merge request robots/tiago_pro_simulation!21
* Change import for launch args
* Merge branch 'feat/auto-generated_srdf_files' into 'humble-devel'
  add arguments for moveit launch file
  See merge request robots/tiago_pro_simulation!20
* add arguments for moveit launch file
* Contributors: Aina Irisarri, David ter Kuile, davidterkuile

1.0.6 (2024-04-19)
------------------
* Merge branch 'omm/fix/missing_bringup_dep' into 'humble-devel'
  Added missing bringup dep
  See merge request robots/tiago_pro_simulation!19
* Added missing bringup dep
* Contributors: Oscar, davidterkuile

1.0.5 (2024-04-18)
------------------
* Merge branch 'omm/feat/public_sim_check' into 'humble-devel'
  is_public_sim launch support
  See merge request robots/tiago_pro_simulation!18
* is_public_sim launch support
* Merge branch 'omm/feat/tuck_arm' into 'humble-devel'
  Added tuck arm script
  See merge request robots/tiago_pro_simulation!17
* Added tuck arm script
* Merge branch 'fix/renamed-params' into 'humble-devel'
  removed laser pipeline
  See merge request robots/tiago_pro_simulation!16
* removed laser pipeline
* Merge branch 'dtk/feat/public_sim_check' into 'humble-devel'
  Show error when public sim is used without the is_public_sim arg set to true
  See merge request robots/tiago_pro_simulation!15
* Show error when public sim is used without the is_public_sim arg set to true
* Contributors: David ter Kuile, Oscar, andreacapodacqua, davidterkuile

1.0.4 (2024-03-27)
------------------
* Merge branch 'dtk/fix/missing-nav-dependency' into 'humble-devel'
  Add missing 2dnav dependency
  See merge request robots/tiago_pro_simulation!14
* Add missing 2dnav dependency
* Contributors: davidterkuile

1.0.3 (2024-03-26)
------------------
* Merge branch 'feat/ros2-navigation' into 'humble-devel'
  Feat/ros2 navigation
  See merge request robots/tiago_pro_simulation!13
* linters
* using robot_name
* private simulation for navigation and mapping
* Contributors: andreacapodacqua

1.0.2 (2024-03-22)
------------------
* Merge branch 'dtk/fix/add-movit-config' into 'humble-devel'
  Add dependency tiago-pro-moveit-config
  See merge request robots/tiago_pro_simulation!12
* Add dependency tiago-pro-moveit-config
* Contributors: Noel Jimenez, davidterkuile

1.0.1 (2024-03-22)
------------------
* Merge branch 'dtk/fix/restructure' into 'humble-devel'
  restructure launch files
  See merge request robots/tiago_pro_simulation!10
* Change to double quotes
* Update copyright year
* Change common param to is_public_sim
* restructure launch files
* Merge branch 'dtk/fix/add-linter-tests' into 'humble-devel'
  Dtk/fix/add linter tests
  See merge request robots/tiago_pro_simulation!9
* Fix linter formatting issues
* Add tests packages to package.xml
* Add linter testing
* Merge branch 'feat/launch_moveit_by_default' into 'humble-devel'
  Launch MoveIt 2 by default
  See merge request robots/tiago_pro_simulation!8
* Launch MoveIt 2 by default
* Contributors: David ter Kuile, Jordan Palacios, Noel Jimenez, davidterkuile

1.0.0 (2024-01-30)
------------------
* Merge branch 'ros2-migration' into 'humble-devel'
  Ros2 migration
  See merge request robots/tiago_pro_simulation!5
* add the world_name param
* remove pal_hardware_gazebo depend
* update to 3.8 the cmake_minimum_required Version
* update launch files
* integration launch file for simulation
* delete find_package(catkin REQUIRED)
* migration to ROS2 CMakeLists and package.xml
* Merge branch 'change_name' into 'master'
  Change tiago_v2_prototype to tiago_pro
  See merge request robots/tiago_pro_simulation!3
* Change tiago_v2_prototype to tiago_pro
* Contributors: Adria Roig, Jordan Palacios, ileniaperrella, thomaspeyrucain
