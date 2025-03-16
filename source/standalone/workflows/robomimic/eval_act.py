
import argparse

from omni.isaac.lab.app import AppLauncher

# add argparse arguments
parser = argparse.ArgumentParser(description="Random agent for Isaac Lab environments.")
parser.add_argument(
    "--disable_fabric", action="store_true", default=False, help="Disable fabric and use USD I/O operations."
)
parser.add_argument("--num_envs", type=int, default=None, help="Number of environments to simulate.")
parser.add_argument("--task", type=str, default='Isaac-Lift-Needle-PSM-IK-Abs-v0', help="Name of the task.")
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


# Lerobot
from pathlib import Path

import gymnasium as gym
import imageio
import numpy
import torch

from lerobot.common.policies.act.modeling_act import ACTPolicy
from orbit.surgical.tasks.surgical.lift.lift_env_cfg import LiftEnvCfg


def process_images(image: torch.Tensor):
    '''
    Process the cam images for the policy
    '''
    image = image.to(torch.float32) / 255.0
    image = image.permute(2, 0, 1)
    return image

def main():
    """Random actions agent with Isaac Lab environment."""
    # create environment configuration
    env_cfg: LiftEnvCfg = parse_env_cfg(
        "Isaac-Lift-Needle-PSM-IK-Abs-v0",
        device=args_cli.device,
        num_envs=args_cli.num_envs,
        use_fabric=not args_cli.disable_fabric,
    )

    # modify configuration such that the environment runs indefinitely
    # until goal is reached
    env_cfg.terminations.time_out = None
    # set the resampling time range to large number to avoid resampling
    env_cfg.commands.object_pose.resampling_time_range = (1.0e9, 1.0e9)

    # we want to have the terms in the observations returned as a dictionary
    # rather than a concatenated tensor
    env_cfg.observations.policy.concatenate_terms = False

    # Select your device
    device = "cuda"

    pretrained_policy_path = "outputs/train/act_needle_reaching_1000demos/checkpoints/080000/pretrained_model"  # 100000. 020000. 040000. 060000
    policy = ACTPolicy.from_pretrained(pretrained_policy_path, map_location=device)

    # create environment
    env = gym.make(args_cli.task, cfg=env_cfg)

    # We can verify that the shapes of the features expected by the policy match the ones from the observations
    # produced by the environment
    print(policy.config.input_features)
    print(f"[INFO]: Gym observation space: {env.observation_space}")

    # Similarly, we can check that the actions produced by the policy will match the actions expected by the
    # environment
    print(policy.config.output_features)
    print(f"[INFO]: Gym action space: {env.action_space}")
    # reset environment
    obs_dict, _ = env.reset()
    # reset policy
    policy.reset()
    # create observation dictionary
    observation ={}
    # simulate environment
    while simulation_app.is_running():
        # run everything in inference mode
        with torch.inference_mode():
            # -- observations
            joint_pos = obs_dict["policy"]["joint_pos"]
            joint_vel = obs_dict["policy"]["joint_vel"]
            image_front = process_images(env.unwrapped.scene["tiled_camera_front"].data.output["rgb"].squeeze())
            image_back = process_images(env.unwrapped.scene["tiled_camera_back"].data.output["rgb"].squeeze())
            image_left = process_images(env.unwrapped.scene["tiled_camera_left"].data.output["rgb"].squeeze())
            image_right = process_images(env.unwrapped.scene["tiled_camera_right"].data.output["rgb"].squeeze())
            # import pdb; pdb.set_trace()
            # Create the policy input dictionary
            observation = {
                    "observation.state": joint_pos,
                    "observation.velocity": joint_vel,
                    "observation.image.tiled_camera_front": image_front,
                    "observation.image.tiled_camera_back": image_back,
                    "observation.image.tiled_camera_left": image_left,
                    "observation.image.tiled_camera_right": image_right,
                }
            # -- actions
            actions = policy.select_action(observation)
       
            # -- robot
            robot: RigidObject = env.scene["robot"]
            # sample actions from -1 to 1
             # -- object frame
            object_data: RigidObjectData = env.unwrapped.scene["object"].data
            
            # apply actions
            obs_dict, rewards, terminated, truncated, info = env.step(actions)
            dones = terminated | truncated

    # close the simulator
    env.close()


if __name__ == "__main__":
    # run the main function
    main()
    # close sim app
    simulation_app.close()
