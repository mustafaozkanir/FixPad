import os
import json

log_dir = "run_logs"
bug_dirs = [d for d in os.listdir(log_dir) if os.path.isdir(os.path.join(log_dir, d))]

iteration_counts = []
print("Iterations per bug:")

for bug_id in sorted(bug_dirs):
    traj_path = os.path.join(log_dir, bug_id, "trajectory.json")
    if os.path.exists(traj_path):
        with open(traj_path, "r") as f:
            try:
                trajectory = json.load(f)
                num_steps = len(trajectory)
                iteration_counts.append(num_steps)
                print(f"  {bug_id}: {num_steps} steps")
            except Exception as e:
                print(f"  {bug_id}: Error reading trajectory.json → {e}")
    else:
        print(f"  {bug_id}: trajectory.json not found")

if iteration_counts:
    avg_iters = sum(iteration_counts) / len(iteration_counts)
    print(f"\n✅ Average number of iterations per bug: {avg_iters:.2f}")
else:
    print("❌ No valid trajectories found.")
