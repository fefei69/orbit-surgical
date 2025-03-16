# Datra collection with robomimic
${IsaacLab_PATH}/isaaclab.sh -p source/standalone/workflows/robomimic/lift_needle_sm.py --num_envs 1 --num_demos 1200 --filename 1200demos_4cam --enable_cameras --livestream 2
# ${IsaacLab_PATH}/isaaclab.sh -p source/standalone/workflows/robomimic/tools/inspect_demonstrations.py logs/robomimic/Isaac-Lift-Needle-PSM-IK-Abs-v0/5demos_4cam.hdf5
# inspect dataset
# ${IsaacLab_PATH}/isaaclab.sh -p source/standalone/workflows/robomimic/tools/inspect_demonstrations.py logs/robomimic/Isaac-Lift-Needle-PSM-IK-Abs-v0/test50_hdf5.hdf5
# split dataset
# ${IsaacLab_PATH}/isaaclab.sh -p source/standalone/workflows/robomimic/tools/split_train_val.py logs/robomimic/Isaac-Lift-Needle-PSM-IK-Abs-v0/test50_hdf5.hdf5 --ratio 0.1
# Train
# ${IsaacLab_PATH}/isaaclab.sh -p source/standalone/workflows/robomimic/train.py --task Isaac-Lift-Needle-PSM-IK-Abs-v0 --algo bc --dataset logs/robomimic/Isaac-Lift-Needle-PSM-IK-Abs-v0/test50_hdf5.hdf5 
# Play the trained agents
# ${IsaacLab_PATH}/isaaclab.sh -p source/standalone/workflows/robomimic/play.py --task Isaac-Lift-Needle-PSM-IK-Abs-v0 --checkpoint logs/robomimic/Isaac-Lift-Needle-PSM-IK-Abs-v0/bc/20250215014826/models/model_epoch_200.pth --livestream 2
# execute from the root directory of the repository
# ${IsaacLab_PATH}/isaaclab.sh -p -m tensorboard.main --logdir=logs/robomimic/Isaac-Lift-Needle-PSM-IK-Abs-v0/bc/20250210085716/logs




# ${IsaacLab_PATH}/isaaclab.sh -p source/standalone/workflows/robomimic/camera_test.py --livestream 2
# ${IsaacLab_PATH}/isaaclab.sh -p source/standalone/workflows/robomimic/camera_test.py \
# --task Isaac-Cartpole-v0 --num_tiled_cameras 100 \
# --task_num_cameras_per_env 2 \
# --tiled_camera_data_types rgb \
# --livestream 2
