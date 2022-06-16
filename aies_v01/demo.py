#!/usr/bin/env python3

from pathlib import Path
from HandTrackerRenderer import HandTrackerRenderer
from HandTracker import HandTracker


SCRIPT_DIR = Path(__file__).resolve().parent
PALM_DETECTION_MODEL = str(SCRIPT_DIR / "models/palm_detection_sh4.blob")
LANDMARK_MODEL_FULL = str(SCRIPT_DIR / "models/hand_landmark_full_sh4.blob")
LANDMARK_MODEL_LITE = str(SCRIPT_DIR / "models/hand_landmark_lite_sh4.blob")
LANDMARK_MODEL_SPARSE = str(SCRIPT_DIR / "models/hand_landmark_sparse_sh4.blob")


tracker = HandTracker(
            input_src="rgb",                            # 사용할 카메라
            pd_model=PALM_DETECTION_MODEL,              # PALM_DETECTION 을 시작으로 하는 HAND_TRACKING_MODEL
            pd_score_thresh=0.5, pd_nms_thresh=0.5,     # PALM_DETECTION 임계값, NMS 알고리즘 임계값
            use_lm=True,                                # landmark model 사용여부(안쓰면 PALM_DETECTION 만 진행)
            lm_model="full",                            # landmark model 종류
            lm_score_thresh=0.5,                        # landmark model 임계값
            use_world_landmarks=False,                  # 3D landmark model 사용여부
            solo=True,                                  # 한손모드
            xyz=True,                                   # 위치 값 사용여부
            crop=False,                                 # 크롭 이미지 사용여부
            internal_fps=30,                            # fps 설정
            resolution="full",                          # 해상도 설정
            internal_frame_height=640,                  # 프리뷰 크기 설정
            use_gesture=True,                           # 제스처 사용여부
            use_handedness_average=False,               # 오른손 왼손 구분여부
            single_hand_tolerance_thresh=10,            # 두손모드 사용 시 디텍여부
            lm_nb_threads=2,                            # landmark model DETECTION에 사용할 쓰레드 수?
            stats=True,                                 # ??
            trace=0,                                    # detection 디버깅 메시지
            )

renderer = HandTrackerRenderer(
        tracker=tracker,
        output=None)

while True:
    # Run hand tracker on next frame
    # 'bag' contains some information related to the frame 
    # and not related to a particular hand like body keypoints in Body Pre Focusing mode
    # Currently 'bag' contains meaningful information only when Body Pre Focusing is used
    frame, hands, bag = tracker.next_frame()
    if frame is None: break
    # Draw hands
    frame = renderer.draw(frame, hands, bag)
    key = renderer.waitKey(delay=1)
    if key == 27 or key == ord('q'):
        break
renderer.exit()
tracker.exit()
