import numpy as np

def face_locations(img, model="hog"):
    return [(0, 0, 100, 100)]

def face_encodings(img, boxes=None):
    # Return a random 128-d vector
    return [np.random.rand(128)]

def face_distance(face_encodings, face_to_compare):
    # Return random distances
    return np.random.rand(len(face_encodings))
