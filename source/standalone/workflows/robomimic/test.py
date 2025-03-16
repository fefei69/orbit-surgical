# Copyright (c) 2022-2024, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Script to an environment with random action agent."""

"""Launch Isaac Sim Simulator first."""

import argparse

from omni.isaac.lab.app import AppLauncher

# add argparse arguments
parser = argparse.ArgumentParser(description="Random agent for Isaac Lab environments.")
parser.add_argument(
    "--disable_fabric", action="store_true", default=False, help="Disable fabric and use USD I/O operations."
)
parser.add_argument("--num_envs", type=int, default=None, help="Number of environments to simulate.")
parser.add_argument("--task", type=str, default='Isaac-Lift-Needle-PSM-IK-Abs-v0', help="Name of the task.")
# parser.add_argument("--size", type=float, default=1.5, help="Side-length of cuboid")
# SimulationApp arguments https://docs.omniverse.nvidia.com/py/isaacsim/source/isaacsim.simulation_app/docs/index.html?highlight=simulationapp#isaacsim.simulation_app.SimulationApp
# append AppLauncher cli args
AppLauncher.add_app_launcher_args(parser)
# parse the arguments
args_cli = parser.parse_args()

# launch omniverse app
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

"""Rest everything follows."""

import gymnasium as gym
import torch
import numpy as np

import omni.isaac.lab_tasks  # noqa: F401
from omni.isaac.lab_tasks.utils import parse_env_cfg

import orbit.surgical.tasks  # noqa: F401

from omni.isaac.lab.assets import RigidObject
from omni.isaac.lab.assets.rigid_object.rigid_object_data import RigidObjectData
from omni.isaac.lab.utils.math import subtract_frame_transforms

# from omni.isaac.lab.sensors import Camera, CameraCfg #, TiledCamera, TiledCameraCfg
# import omni.isaac.lab.sim as sim_utils
# import isaacsim
# print(dir(isaacsim))
# import pdb; pdb.set_trace()


def main():
    """Random actions agent with Isaac Lab environment."""
    # create environment configuration
    env_cfg = parse_env_cfg(
        args_cli.task, device=args_cli.device, num_envs=args_cli.num_envs, use_fabric=not args_cli.disable_fabric
    )
    # create environment
    env = gym.make(args_cli.task, cfg=env_cfg)

    # print info (this is vectorized environment)
    print(f"[INFO]: Gym observation space: {env.observation_space}")
    print(f"[INFO]: Gym action space: {env.action_space}")
    # reset environment
    env.reset()
    # simulate environment
    while simulation_app.is_running():
        # run everything in inference mode
        with torch.inference_mode():
            # observations
            robot: RigidObject = env.scene["robot"]
            # sample actions from -1 to 1
            actions = 2 * torch.rand(env.action_space.shape, device=env.unwrapped.device) - 1
             # -- object frame
            object_data: RigidObjectData = env.unwrapped.scene["object"].data
            # import pdb; pdb.set_trace()
            images = np.stack([env.unwrapped.scene["tiled_camera_front"].data.output["rgb"].squeeze().cpu().numpy().astype("uint8"),
                               env.unwrapped.scene["tiled_camera_back"].data.output["rgb"].squeeze().cpu().numpy().astype("uint8"),
                               env.unwrapped.scene["tiled_camera_left"].data.output["rgb"].squeeze().cpu().numpy().astype("uint8"),
                               env.unwrapped.scene["tiled_camera_right"].data.output["rgb"].squeeze().cpu().numpy().astype("uint8")], axis=0)
            # Camera data
            print("Received shape of rgb front image: ", env.unwrapped.scene["tiled_camera_front"].data.output["rgb"].shape)
            print("Received shape of rgb back image: ", env.unwrapped.scene["tiled_camera_back"].data.output["rgb"].shape)
            print("Received shape of rgb left image: ", env.unwrapped.scene["tiled_camera_left"].data.output["rgb"].shape)
            print("Received shape of rgb right image: ", env.unwrapped.scene["tiled_camera_right"].data.output["rgb"].shape)

            # print("Robot states (1,13): ", robot.data.root_state_w) # (1,13)
            # print("Object states (1,3): ", object_data.root_pos_w) # (1,3)
            # apply actions
            env.step(actions)

    # close the simulator
    env.close()


if __name__ == "__main__":
    # run the main function
    main()
    # close sim app
    simulation_app.close()
