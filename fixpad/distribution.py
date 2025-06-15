import os
import json
import matplotlib.pyplot as plt
from collections import defaultdict

trajectory_dir = "run_logs"
included_bugs = {f"bug_{str(i).zfill(3)}" for i in range(1, 11)}

step_action_counts = defaultdict(lambda: defaultdict(int))
max_steps = 0

# Traverse trajectories
for bug_dir in os.listdir(trajectory_dir):
    if bug_dir not in included_bugs:
        continue
    traj_path = os.path.join(trajectory_dir, bug_dir, "trajectory.json")
    if os.path.exists(traj_path):
        with open(traj_path, "r") as f:
            trajectory = json.load(f)
            for step_index, step in enumerate(trajectory):
                for action in step.get("actions", []):
                    action_type = action.get("type", "unknown")
                    if action_type == "moveTo":
                        action_type = "move_to"  # Rename here
                    step_action_counts[step_index][action_type] += 1
            max_steps = max(max_steps, len(trajectory))

# Get all action types
all_action_types = sorted({atype for step in step_action_counts.values() for atype in step.keys()})

# Updated color mapping (adjust as needed)
action_color_map = {
    "click": "#2171b5",
    "highlight": "#c7e9c0",
    "hotkey": "#238b45",
    "move_to": "#c6dbef",
    "multi_select": "#fcbba1",
    "paste": "#cb181d"
}
# Fallback for unknowns
for atype in all_action_types:
    if atype not in action_color_map:
        action_color_map[atype] = "#bbbbbb"

# Prepare stacked bar data
step_indices = list(range(max_steps))
data_by_action = {atype: [] for atype in all_action_types}
for step_index in step_indices:
    for atype in all_action_types:
        data_by_action[atype].append(step_action_counts[step_index].get(atype, 0))

# Plot
fig, ax = plt.subplots(figsize=(12, 5))
bar_width = 0.4
bottom = [0] * max_steps

for atype in all_action_types:
    counts = data_by_action[atype]
    ax.bar(step_indices, counts, bottom=bottom, width=bar_width, label=atype, color=action_color_map[atype])
    bottom = [bottom[i] + counts[i] for i in range(max_steps)]

ax.set_xlabel("Step Index")
ax.set_ylabel("Count")
ax.set_title("ActionAgent Action Distribution by Step Index")
ax.set_xticks(step_indices)
ax.legend(
    title="Command",
    loc='upper right',
    bbox_to_anchor=(0.98, 0.98),
    frameon=True,
    fontsize='small',
    title_fontsize='small'
)
plt.tight_layout()
plt.savefig("action_distribution.png", bbox_inches='tight', pad_inches=0.02)
plt.show()
