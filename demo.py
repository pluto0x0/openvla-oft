import pickle
from openvla_oft.experiments.robot.openvla_utils import (
    get_action_head,
    get_processor,
    get_proprio_projector,
    get_vla,
    get_vla_action,
)
from prismatic.vla.constants import NUM_ACTIONS_CHUNK, PROPRIO_DIM

#
# from experiments.robot.libero.run_libero_eval import GenerateConfig
#
# (this is removed, to prevent requiring the full Libero evaluation codebase)
# (instead, directly import GenerateConfig)
from openvla_oft import GenerateConfig

# Instantiate config (see class GenerateConfig in experiments/robot/libero/run_libero_eval.py for definitions)
cfg = GenerateConfig(
    pretrained_checkpoint="moojink/openvla-7b-oft-finetuned-libero-spatial",
    use_l1_regression=True,
    use_diffusion=False,
    use_film=False,
    num_images_in_input=2,
    use_proprio=True,
    load_in_8bit=False,
    load_in_4bit=False,
    center_crop=True,
    num_open_loop_steps=NUM_ACTIONS_CHUNK,
    unnorm_key="libero_spatial_no_noops",
)

# Load OpenVLA-OFT policy and inputs processor
vla = get_vla(cfg)
processor = get_processor(cfg)

# Load MLP action head to generate continuous actions (via L1 regression)
action_head = get_action_head(cfg, llm_dim=vla.llm_dim)

# Load proprio projector to map proprio to language embedding space
proprio_projector = get_proprio_projector(cfg, llm_dim=vla.llm_dim, proprio_dim=PROPRIO_DIM)

# Load sample observation:
#   observation (dict): {
#     "full_image": primary third-person image,
#     "wrist_image": wrist-mounted camera image,
#     "state": robot proprioceptive state,
#     "task_description": task description,
#   }

with open("src/openvla_oft/experiments/robot/libero/sample_libero_spatial_observation.pkl", "rb") as file:
    observation = pickle.load(file)
observation["task_description"] = "open the drawer and put the ramekin in it"

# Generate robot action chunk (sequence of future actions)
actions = get_vla_action(
    cfg, vla, processor, observation, observation["task_description"], action_head, proprio_projector
)
print("Generated action chunk:")
for act in actions:
    print(act)
