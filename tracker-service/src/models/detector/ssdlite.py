# SPDX-License-Identifier: Apache-2.0
"""Light person detector for the magic mirror: presence and a box, no pose.

torchvision SSDLite320-MobileNetV3-Large (COCO, BSD-3) replaces Detectron2
Keypoint R-CNN. The mirror only needs to know that someone is there (to wake up,
reset styles and let PhotoGate allow a photo), not where their head is, so no
keypoints are returned and the robot does not head-track.
"""

import torch
from constants import UNDEFINED_INSTANCE_ID
from models.detector.base import BaseDetector, DetectionResult
from torchvision.models.detection import (
    SSDLite320_MobileNet_V3_Large_Weights,
    ssdlite320_mobilenet_v3_large,
)
from torchvision.ops import nms

COCO_PERSON = 1  # torchvision's COCO label ids start at 1 (0 is background)


class SSDLiteDetector(BaseDetector):
    def __init__(
        self,
        device: str = "auto",
        confidence_threshold: float = 0.5,
        iou_threshold: float = 0.45,
    ) -> None:
        super().__init__()
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.model = (
            ssdlite320_mobilenet_v3_large(
                weights=SSDLite320_MobileNet_V3_Large_Weights.COCO_V1,
                score_thresh=min(confidence_threshold, 0.3),
            )
            .eval()
            .to(self.device)
        )

    @torch.inference_mode()
    def run(self, video: torch.Tensor) -> DetectionResult:
        assert video.shape[0] == 1, "SSDLiteDetector only supports single frame input"
        frame = video[0].to(self.device)
        # Frames arrive as uint8 RGB (helpers.utils.from_cv2_to_torch).
        frame = frame.float() if frame.is_floating_point() else frame.float() / 255.0
        out = self.model([frame])[0]
        keep = (out["labels"] == COCO_PERSON) & (
            out["scores"] >= self.confidence_threshold
        )
        boxes = out["boxes"][keep].float().cpu()
        scores = out["scores"][keep].float().cpu()
        if boxes.shape[0] > 0:
            idx = nms(boxes, scores, self.iou_threshold)
            boxes, scores = boxes[idx], scores[idx]
        n = boxes.shape[0]
        return DetectionResult(
            boxes=boxes.reshape(n, 4),
            scores=scores.reshape(n),
            instance_ids=torch.full((n,), float(UNDEFINED_INSTANCE_ID)),
            keypoints=torch.zeros((n, 0, 3)),
        )
