import cv2
import numpy as np
import mediapipe as mp

class ImageProcessor:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            enable_segmentation=True,
            min_detection_confidence=0.5
        )
        
        self.mp_face = mp.solutions.face_detection
        self.face_detector = self.mp_face.FaceDetection(
            model_selection=1,
            min_detection_confidence=0.5
        )

    def detect_body_type(self, image):
        """Detect body shape using pose estimation"""
        results = self.pose.process(image)
        
        if not results.pose_landmarks:
            return "Unknown"
            
        # Extract key landmarks
        landmarks = results.pose_landmarks.landmark
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]
        left_ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE]
        right_ankle = landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE]
        
        # Calculate body ratios
        shoulder_width = abs(left_shoulder.x - right_shoulder.x)
        hip_width = abs(left_hip.x - right_hip.x)
        waist_height = abs((left_shoulder.y + right_shoulder.y)/2 - (left_hip.y + right_hip.y)/2)
        
        # Determine body type (simplified logic)
        if shoulder_width > hip_width * 1.1:
            return "Inverted Triangle"
        elif hip_width > shoulder_width * 1.1:
            return "Pear"
        elif abs(shoulder_width - hip_width) < 0.1 and waist_height < 0.2:
            return "Hourglass"
        else:
            return "Rectangle"

    def detect_skin_tone(self, image):
        """Detect skin tone from face region"""
        results = self.face_detector.process(image)
        
        if not results.detections:
            return "Unknown"
            
        # Get first face detection
        detection = results.detections[0]
        bbox = detection.location_data.relative_bounding_box
        ih, iw = image.shape[:2]
        
        # Extract face region
        x = int(bbox.xmin * iw)
        y = int(bbox.ymin * ih)
        w = int(bbox.width * iw)
        h = int(bbox.height * ih)
        face_region = image[y:y+h, x:x+w]
        
        # Convert to HSV and get average color
        hsv = cv2.cvtColor(face_region, cv2.COLOR_BGR2HSV)
        avg_hue = np.mean(hsv[:,:,0])
        
        # Classify skin tone (simplified)
        if avg_hue < 15:
            return "Warm"
        elif avg_hue < 30:
            return "Neutral"
        else:
            return "Cool"

    def generate_recommendations(self, body_type, skin_tone):
        """Generate fashion recommendations based on body type and skin tone"""
        recommendations = {
            'colors': [],
            'outfits': []
        }
        
        # Body type recommendations
        if body_type == "Hourglass":
            recommendations['outfits'].extend([
                "Wrap dresses",
                "Fitted jackets",
                "High-waisted pants"
            ])
        elif body_type == "Pear":
            recommendations['outfits'].extend([
                "A-line skirts",
                "Dark colored bottoms",
                "Structured tops"
            ])
            
        # Skin tone recommendations
        if skin_tone == "Warm":
            recommendations['colors'].extend([
                "Coral",
                "Gold",
                "Olive Green"
            ])
        elif skin_tone == "Cool":
            recommendations['colors'].extend([
                "Royal Blue",
                "Emerald Green",
                "Ruby Red"
            ])
            
        return recommendations
