import face_recognition
import numpy as np
import pickle
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.db.models import FaceEmbedding, Student
from app.core.config import settings


class FaceLogic:
    @staticmethod
    def process_image(image_bytes: bytes) -> List[np.ndarray]:
        """
        Decodes image bytes to numpy array and finds face encodings.
        Returns a list of 128-d embeddings found in the image.
        """
        import cv2

        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Convert to RGB (face_recognition uses RGB)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Detect faces (using HOG by default, or CNN if GPU available)
        # For production/speed, we use HOG. 'cnn' needs GPU.
        boxes = face_recognition.face_locations(rgb_img, model="hog")
        encodings = face_recognition.face_encodings(rgb_img, boxes)

        return encodings

    @staticmethod
    def identify_face(
        embedding: np.ndarray,
        db: Session,
        threshold: float = settings.SIMILARITY_THRESHOLD,
    ) -> Tuple[Student, float]:
        """
        Compares the given embedding against ALL student embeddings in DB.
        Returns (Student, Distance) if match found, else (None, Distance).
        """
        # Load all embeddings from DB
        # OPTIMIZATION: In production, load this into memory (FAISS or cache)
        # instead of querying DB every frame.
        # For MVP/School Class (~50 students * 10 images = 500 vectors),
        # DB query -> Python list is fine.

        all_embeddings = db.query(FaceEmbedding).all()
        if not all_embeddings:
            return None, 1.0

        known_encodings = [pickle.loads(e.embedding_bytes) for e in all_embeddings]
        known_ids = [e.student_id for e in all_embeddings]

        # Compare
        distances = face_recognition.face_distance(known_encodings, embedding)

        min_distance_idx = np.argmin(distances)
        min_distance = distances[min_distance_idx]

        if min_distance < threshold:
            student_id = known_ids[min_distance_idx]
            student = db.query(Student).get(student_id)
            return student, min_distance

        return None, min_distance

    @staticmethod
    def check_liveness_basic(embedding_history: List[np.ndarray]) -> bool:
        """
        Simple consistency check.
        If we have N consecutive frames, the embeddings should be very close
        but NOT identical.
        Identical embeddings (dist=0) usually means the exact same image
        frame was sent (e.g. video replay of a static photo).
        """
        if len(embedding_history) < 2:
            return True

        # Ensure some variance exists (it's a live video, noise exists)
        # If variance is 0.0 -> Suspicious (Static Image Attack)
        # If variance is too high -> Suspicious (Different person?)

        return True  # Placeholder for advanced logic
