import cv2
import os

video_path = 'WeeklyProductPulseandFeeExplainer.mov'
output_dir = 'extracted_frames'
os.makedirs(output_dir, exist_ok=True)

cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = total_frames / fps

print(f"FPS: {fps}, Total Frames: {total_frames}, Duration: {duration:.2f}s")

# Extract frame every 30 seconds
for sec in range(0, int(duration), 30):
    frame_idx = int(sec * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    ret, frame = cap.read()
    if ret:
        output_path = os.path.join(output_dir, f"frame_{sec}s.png")
        cv2.imwrite(output_path, frame)
        print(f"Saved: {output_path}")

# Also extract the very last frame
cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
ret, frame = cap.read()
if ret:
    output_path = os.path.join(output_dir, "frame_last.png")
    cv2.imwrite(output_path, frame)
    print(f"Saved: {output_path}")

cap.release()
print("Done!")
