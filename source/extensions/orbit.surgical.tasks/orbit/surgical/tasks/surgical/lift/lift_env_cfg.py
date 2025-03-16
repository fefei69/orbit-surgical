# Copyright (c) 2024, The ORBIT-Surgical Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import MISSING

from orbit.surgical.assets import ORBITSURGICAL_ASSETS_DATA_DIR

import omni.isaac.lab.sim as sim_utils
from omni.isaac.lab.assets import ArticulationCfg, AssetBaseCfg, RigidObjectCfg
from omni.isaac.lab.envs import ManagerBasedRLEnvCfg
from omni.isaac.lab.managers import CurriculumTermCfg as CurrTerm
from omni.isaac.lab.managers import EventTermCfg as EventTerm
from omni.isaac.lab.managers import ObservationGroupCfg as ObsGroup
from omni.isaac.lab.managers import ObservationTermCfg as ObsTerm
from omni.isaac.lab.managers import RewardTermCfg as RewTerm
from omni.isaac.lab.managers import SceneEntityCfg
from omni.isaac.lab.managers import TerminationTermCfg as DoneTerm
from omni.isaac.lab.scene import InteractiveSceneCfg
from omni.isaac.lab.sensors.frame_transformer.frame_transformer_cfg import FrameTransformerCfg
from omni.isaac.lab.sim.spawners.from_files.from_files_cfg import GroundPlaneCfg, UsdFileCfg
from omni.isaac.lab.utils import configclass

from omni.isaac.lab.sensors import Camera, CameraCfg, TiledCamera, TiledCameraCfg
# import omni.isaac.core.utils.prims as prim_utils
# import pdb; pdb.set_trace()

from . import mdp

##
# Scene definition
##


# def create_camera_base(
#     camera_cfg: type[CameraCfg | TiledCameraCfg],
#     num_cams: int,
#     data_types: list[str],
#     height: int,
#     width: int,
#     prim_path: str | None = None,
#     instantiate: bool = True,
# ) -> Camera | TiledCamera | CameraCfg | TiledCameraCfg | None:
#     """Generalized function to create a camera or tiled camera sensor with a complete prim hierarchy."""
#     # Determine the camera type name (e.g. "Camera" or "TiledCamera")
#     name = camera_cfg.class_type.__name__

#     if instantiate:
#         # For each camera instance, create both the parent transform and the child camera prim
#         for idx in range(num_cams):
#             base_path = f"/World/{name}_{idx:02d}"
#             # Create the parent transform prim
#             prim_utils.create_prim(base_path, "Xform")
#             # Create the child prim that actually holds the camera asset configuration
#             prim_utils.create_prim(f"{base_path}/{name}", "Camera")

#     # Use a default prim_path pattern if none is provided, matching the hierarchy above
#     if prim_path is None:
#         prim_path = f"/World/{name}_.*/{name}"

#     # If valid parameters are provided, construct the camera configuration
#     if num_cams > 0 and len(data_types) > 0 and height > 0 and width > 0:
#         cfg = camera_cfg(
#             prim_path=prim_path,
#             update_period=0,
#             height=height,
#             width=width,
#             data_types=data_types,
#             spawn=sim_utils.PinholeCameraCfg(
#                 focal_length=24,
#                 focus_distance=400.0,
#                 horizontal_aperture=20.955,
#                 clipping_range=(0.1, 1e4)
#             ),
#         )
#         if instantiate:
#             return camera_cfg.class_type(cfg=cfg)
#         else:
#             return cfg
#     else:
#         return None


@configclass
class ObjectTableSceneCfg(InteractiveSceneCfg):
    """Configuration for the lift scene with a robot and a object.
    This is the abstract base implementation, the exact scene is defined in the derived classes
    which need to set the target object, robot and end-effector frames
    """

    # robots: will be populated by agent env cfg
    robot: ArticulationCfg = MISSING
    # end-effector sensor: will be populated by agent env cfg
    ee_frame: FrameTransformerCfg = MISSING
    # target object: will be populated by agent env cfg
    object: RigidObjectCfg = MISSING

    # Table
    table = AssetBaseCfg(
        prim_path="{ENV_REGEX_NS}/Table",
        init_state=AssetBaseCfg.InitialStateCfg(pos=(0.0, 0.0, -0.457)),
        spawn=UsdFileCfg(usd_path=f"{ORBITSURGICAL_ASSETS_DATA_DIR}/Props/Table/table.usd"),
    )

    # plane
    plane = AssetBaseCfg(
        prim_path="/World/GroundPlane",
        init_state=AssetBaseCfg.InitialStateCfg(pos=(0, 0, -0.95)),
        spawn=GroundPlaneCfg(),
    )

    # lights
    light = AssetBaseCfg(
        prim_path="/World/light",
        spawn=sim_utils.DomeLightCfg(color=(0.75, 0.75, 0.75), intensity=3000.0),
    )

    ### Add a camera to the scene 

    # def create_tiled_cameras(
    # num_cams: int = 2, data_types: list[str] | None = None, height: int = 100, width: int = 120
    # ) -> TiledCamera | None:
    #     if data_types is None:
    #         data_types = ["rgb", "depth"]
    #     """Defines the tiled camera sensor to add to the scene."""
    #     return create_camera_base(
    #         camera_cfg=TiledCameraCfg,
    #         num_cams=num_cams,
    #         data_types=data_types,
    #         height=height,
    #         width=width,
    # )

    # tiled_camera = create_tiled_cameras()
    tiled_camera_front = TiledCameraCfg(
        prim_path="/World/robot/base/front_cam", 
        update_period=0.1,
        width=224, # 480
        height=224, # 640
        data_types=["rgb"],
        spawn=sim_utils.PinholeCameraCfg(
            focal_length=24.0*1.2, focus_distance=400.0, horizontal_aperture=20.955, clipping_range=(0.1, 20) # (0.1, 1.0e5)
        ),
        offset=TiledCameraCfg.OffsetCfg(pos=(0.5, 0.0, 0.2), rot=(0.0, -0.1736482, 0, 0.9848078), convention="world"),
    )

    tiled_camera_back: TiledCameraCfg = TiledCameraCfg(
        prim_path="/World/robot/base/back_cam",  
        update_period=0.1,  
        width=224,
        height=224,
        data_types=["rgb"],
        spawn=sim_utils.PinholeCameraCfg(
            focal_length=24.0*1.2, focus_distance=400.0, horizontal_aperture=20.955, clipping_range=(0.1, 20.0)
        ),
        offset=TiledCameraCfg.OffsetCfg(pos=(-0.5, 0.0, 0.2), rot=(0.9914449, 0, 0.1305262, 0), convention="world"),
        )
    
    tiled_camera_left: TiledCameraCfg = TiledCameraCfg(
        prim_path="/World/envs/env_.*/Camera",
        update_period=0.1,  
        width=224,
        height=224,
        data_types=["rgb"],
        spawn=sim_utils.PinholeCameraCfg(
            focal_length=24.0*1.2, focus_distance=400.0, horizontal_aperture=20.955, clipping_range=(0.1, 20.0)
        ),
        offset=TiledCameraCfg.OffsetCfg(pos=(0.0, 0.5, 0.2), rot=(0.7010574, 0.092296, 0.092296, -0.7010574), convention="world"),
        )
    
    tiled_camera_right: TiledCameraCfg = TiledCameraCfg(
        prim_path="/World/robot/base/camera",
        update_period=0.1,  
        width=224,
        height=224,
        data_types=["rgb"],
        spawn=sim_utils.PinholeCameraCfg(
            focal_length=24.0*1.2, focus_distance=400.0, horizontal_aperture=20.955, clipping_range=(0.1, 20.0)
        ),
        offset=TiledCameraCfg.OffsetCfg(pos=(0.0, -0.5, 0.2), rot=(0.7010574, -0.092296, 0.092296, 0.7010574), convention="world"),
        )
    

    
    
    # name = CameraCfg.class_type.__name__
    # idx = 1
    # prim_utils.create_prim(f"/World/{name}_{idx:02d}", "Xform")
    # name = TiledCameraCfg.class_type.__name__  # "Camera"
    # idx = 1
    # parent_path = f"/World/{name}_{idx:02d}"
    # # prim_utils.create_prim(parent_path, "Xform")
    # # Create the child prim that will have the actual Camera asset config
    # child_path = f"{parent_path}/{name}"
    # # prim_utils.create_prim(child_path, "Camera")
    # tiled_camera_2: TiledCameraCfg = TiledCameraCfg(
    #     prim_path="{ENV_REGEX_NS}/Robot/base/rear_cam",#f"/World/{name}_.*/{name}",
    #     offset=TiledCameraCfg.OffsetCfg(pos=(1.0, 0.0, 1.0), rot=(0.9945, 0.0, 0.1045, 0.0), convention="world"),
    #     data_types=["rgb"],
    #     spawn=sim_utils.PinholeCameraCfg(
    #         focal_length=24.0, focus_distance=400.0, horizontal_aperture=20.955, clipping_range=(0.1, 20.0)
    #     ),
    #         width=480,
    #         height=640,
    #     )


##
# MDP settings
##


@configclass
class CommandsCfg:
    """Command terms for the MDP."""

    object_pose = mdp.UniformPoseCommandCfg(
        asset_name="robot",
        body_name=MISSING,  # will be set by agent env cfg
        resampling_time_range=(1.0, 1.0),
        debug_vis=False,
        ranges=mdp.UniformPoseCommandCfg.Ranges(
            pos_x=(-0.05, 0.05),
            pos_y=(-0.05, 0.05),
            pos_z=(-0.12, -0.12),
            roll=(0.0, 0.0),
            pitch=(0.0, 0.0),
            yaw=(0.0, 0.0),
        ),
    )
    # set the scale of the visualization markers to (0.01, 0.01, 0.01)
    object_pose.goal_pose_visualizer_cfg.markers["frame"].scale = (0.01, 0.01, 0.01)
    object_pose.current_pose_visualizer_cfg.markers["frame"].scale = (0.01, 0.01, 0.01)


@configclass
class ActionsCfg:
    """Action specifications for the MDP."""

    # will be set by agent env cfg
    body_joint_pos: mdp.JointPositionActionCfg = MISSING
    finger_joint_pos: mdp.BinaryJointPositionActionCfg = MISSING


@configclass
class ObservationsCfg:
    """Observation specifications for the MDP."""

    @configclass
    class PolicyCfg(ObsGroup):
        """Observations for policy group."""

        joint_pos = ObsTerm(func=mdp.joint_pos_rel)
        joint_vel = ObsTerm(func=mdp.joint_vel_rel)
        object_position = ObsTerm(func=mdp.object_position_in_robot_root_frame)
        target_object_position = ObsTerm(func=mdp.generated_commands, params={"command_name": "object_pose"})
        action = ObsTerm(func=mdp.last_action)

        def __post_init__(self):
            self.enable_corruption = True
            self.concatenate_terms = True

    # observation groups
    policy: PolicyCfg = PolicyCfg()


@configclass
class EventCfg:
    """Configuration for events."""

    reset_all = EventTerm(func=mdp.reset_scene_to_default, mode="reset")

    reset_object_position = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "pose_range": {"x": (-0.03, 0.03), "y": (-0.03, 0.03), "z": (0.0, 0.0)},
            "velocity_range": {},
            "asset_cfg": SceneEntityCfg("object", body_names="Object"),
        },
    )


@configclass
class RewardsCfg:
    """Reward terms for the MDP."""

    reaching_object = RewTerm(func=mdp.object_ee_distance, params={"std": 0.1}, weight=1.0)

    lifting_object = RewTerm(func=mdp.object_is_lifted, params={"minimal_height": 0.02}, weight=15.0)

    object_goal_tracking = RewTerm(
        func=mdp.object_goal_distance,
        params={"std": 0.3, "minimal_height": 0.02, "command_name": "object_pose"},
        weight=16.0,
    )

    object_goal_tracking_fine_grained = RewTerm(
        func=mdp.object_goal_distance,
        params={"std": 0.05, "minimal_height": 0.02, "command_name": "object_pose"},
        weight=5.0,
    )

    # action penalty
    action_rate = RewTerm(func=mdp.action_rate_l2, weight=-1e-3)

    joint_vel = RewTerm(
        func=mdp.joint_vel_l2,
        weight=-1e-4,
        params={"asset_cfg": SceneEntityCfg("robot")},
    )


@configclass
class TerminationsCfg:
    """Termination terms for the MDP."""

    time_out = DoneTerm(func=mdp.time_out, time_out=True)

    object_dropping = DoneTerm(
        func=mdp.root_height_below_minimum, params={"minimum_height": -0.05, "asset_cfg": SceneEntityCfg("object")}
    )


@configclass
class CurriculumCfg:
    """Curriculum terms for the MDP."""

    action_rate = CurrTerm(
        func=mdp.modify_reward_weight, params={"term_name": "action_rate", "weight": -1e-1, "num_steps": 10000}
    )

    joint_vel = CurrTerm(
        func=mdp.modify_reward_weight, params={"term_name": "joint_vel", "weight": -1e-1, "num_steps": 10000}
    )


##
# Environment configuration
##


@configclass
class LiftEnvCfg(ManagerBasedRLEnvCfg):
    """Configuration for the lifting environment."""

    # Scene settings
    scene: ObjectTableSceneCfg = ObjectTableSceneCfg(num_envs=4096, env_spacing=2.5)
    # Basic settings
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    commands: CommandsCfg = CommandsCfg()
    # MDP settings
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    events: EventCfg = EventCfg()
    curriculum: CurriculumCfg = CurriculumCfg()

    def __post_init__(self):
        """Post initialization."""
        # general settings
        self.decimation = 4
        self.sim.render_interval = self.decimation
        self.episode_length_s = 2.0
        # simulation settings
        self.sim.dt = 1.0 / 200.0
        self.viewer.eye = (0.2, 0.2, 0.1)
        self.viewer.lookat = (0.0, 0.0, 0.04)
