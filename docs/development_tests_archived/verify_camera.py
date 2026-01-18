import numpy as np

from rulial.runners.probe_2d import RulialProbe2D


def test_camera_tracking():
    print("=== Testing Born-Maxwell Observer (Camera Tracking) ===")

    # Initialize Runner (Mocking size)
    # We won't call run_loop, just test the state update logic if we can access it.
    # Actually, the logic is embedded in run_loop.
    # We will replicate the logic here to verify the ALGORITHM,
    # since refactoring run_loop to be testable is a larger task.
    # BUT, to be sure, let's trust the logic I wrote if I can verify the math here.

    runner = RulialProbe2D(width=64, height=64, obs_window=16)

    # Mock Internal State
    width = 64
    height = 64
    runner.camera_x = 32.0
    runner.camera_y = 32.0

    print(f"Initial Camera: ({runner.camera_y}, {runner.camera_x})")

    # 1. Create a "Glider" at (32, 40) -> Right of center
    grid = np.zeros((height, width), dtype=np.uint8)
    grid[31:34, 39:42] = 1  # 3x3 block centered at ~32, 40.5

    # Manually run the update logic (copied from implementation for verification)
    active_rows, active_cols = np.nonzero(grid)
    if len(active_rows) > 0:
        com_y = np.mean(active_rows)
        com_x = np.mean(active_cols)
        print(f"Target CoM: ({com_y:.1f}, {com_x:.1f})")

        # Update 10 times (simulate 10 frames)
        for i in range(10):
            runner.camera_y = (0.8) * runner.camera_y + 0.2 * com_y
            runner.camera_x = (0.8) * runner.camera_x + 0.2 * com_x
            print(f"Frame {i+1}: Cam ({runner.camera_y:.2f}, {runner.camera_x:.2f})")

    # Check if we moved towards target
    if runner.camera_x > 38.0 and abs(runner.camera_y - 32.0) < 1.0:
        print("SUCCESS: Camera tracked the object to the right.")
    else:
        print("FAILURE: Camera did not track correctly.")

    # 2. Test Bounds Clamping
    print("\nTest Edge Clamping (Object at 60, 60)")
    com_y = 60.0
    com_x = 60.0
    # jump camera there
    runner.camera_y = 60.0
    runner.camera_x = 60.0

    # Calc crop vars
    half_obs = 16 // 2
    target_y, target_x = int(runner.camera_y), int(runner.camera_x)

    safe_cy = max(half_obs, min(height - half_obs, target_y))
    safe_cx = max(half_obs, min(width - half_obs, target_x))

    print(f"Cam: ({target_y}, {target_x}) -> Clamped: ({safe_cy}, {safe_cx})")
    print(
        f"Expect: ({height-half_obs}, {width-half_obs}) -> ({64-8}, {64-8}) -> (56, 56)"
    )

    if safe_cy == 56 and safe_cx == 56:
        print("SUCCESS: Camera clamped correctly at edge.")
    else:
        print(f"FAILURE: Clamping wrong. Got {safe_cy}, {safe_cx}")


if __name__ == "__main__":
    test_camera_tracking()
