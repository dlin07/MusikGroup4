import cv2 as cv
from cv2 import aruco
import numpy as np
import os as os

markerPositions = []
for i in range(0, 6):
    markerPositions.append((0, 0))
# print(markerPositions)

marker_dict = aruco.getPredefinedDictionary(aruco.DICT_5X5_50)
param_markers = aruco.DetectorParameters()
detector = aruco.ArucoDetector(marker_dict, param_markers)

cap = cv.VideoCapture(1)

absolutePath = os.path.join(os.getcwd(), 'lib', 'visual', 'defaultAruco.png')

calibration = cv.imread(absolutePath)
calibrationR = cv.resize(calibration, (int(1920), int(1080)))

origImg = calibrationR

cv.imshow('calibration', calibrationR)
projectedTri = None
realTri = None
projectedToReal = None

def transformCalibrationDisplay(mPos):
    global calibrationR
    global projectedTri
    global realTri
    global projectedToReal
    # 0, 1, 2 = tl, tr, bl display triangle
    # 3, 4, 5 = tl, tr, bl actual triangle
    # scale actual triangle to half the size
    center = ((mPos[4][0] + mPos[5][0])/2, (mPos[4][1] + mPos[5][1])/2)
    displayCenter = ((mPos[1][0] + mPos[2][0])/2, (mPos[1][1] + mPos[2][1])/2)
    
    offset1 = ((mPos[4][0] - center[0])/2, (mPos[4][1] - center[1])/2)
    actualTrShrunk = (center[0] + offset1[0], center[1] + offset1[1])
    offset2 = ((mPos[5][0] - center[0])/2, (mPos[5][1] - center[1])/2)
    actualBlShrunk = (center[0] + offset2[0], center[1] + offset2[1])
    offset3 = ((mPos[3][0] - center[0])/2, (mPos[3][1] - center[1])/2)
    actualTlShrunk = (center[0] + offset3[0], center[1] + offset3[1])
    
    print(mPos)
    # print(calibration.shape)
    defaultTri = np.array([[480, 270], [1440, 270], [480, 810]]).astype(np.float32)
    projectedTri = np.array([[mPos[0][0], mPos[0][1]],[mPos[1][0], mPos[1][1]],[mPos[2][0], mPos[2][1]]]).astype(np.float32)
    realTri = np.array([[actualTlShrunk[0], actualTlShrunk[1]],[actualTrShrunk[0],actualTrShrunk[1]],[actualBlShrunk[0], actualBlShrunk[1]]]).astype(np.float32)
    # realTri = np.array([[mPos[3][0], mPos[3][1]],[mPos[4][0], mPos[4][1]],[mPos[5][0], mPos[5][1]]]).astype(np.float32)a 

    # print(projectedTri)
    # print(realTri)
    defaultToCamera = cv.getAffineTransform(defaultTri, projectedTri)
    cameraToDefault = cv.getAffineTransform(projectedTri, defaultTri)
    projectedToReal = cv.getAffineTransform(projectedTri, realTri)

    warpedImg = cv.warpAffine(calibrationR, defaultToCamera, (calibrationR.shape[1], calibrationR.shape[0]))
    warpedImg = cv.warpAffine(warpedImg, projectedToReal, (warpedImg.shape[1], warpedImg.shape[0]))
    warpedImg = cv.warpAffine(warpedImg, cameraToDefault, (warpedImg.shape[1], warpedImg.shape[0]))

    # translate
    # translation_matrix = np.float32([ [1,0,center[0] - displayCenter[0]], [0,1,center[1] - displayCenter[1]] ])   
    # warpedImg = cv.warpAffine(warpedImg, translation_matrix, (warpedImg.shape[1], warpedImg.shape[0]))
    cv.imshow('calibration', warpedImg)
    
    # print("hello")

# transformCalibrationDisplay([(0, 0), (10, 0), (0, 10), (0, 0), (20, 0), (0, 20)])

while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    marker_corners, marker_IDs, reject = detector.detectMarkers(gray_frame)
    # print(marker_corners)
    
    if not (projectedTri is None):
        cv.polylines(
            frame, [projectedTri.astype(np.int32)], True, (0,255,255)
        )
        cv.polylines(
            frame, [realTri.astype(np.int32)], True, (0,255,255)
        )
        # display the warped triangle and see if it matches
        transformed = cv.transform(np.array([projectedTri]), projectedToReal)
        cv.polylines(
            frame, [transformed.astype(np.int32)], True, (255,0,0)
        )

    if marker_corners:
        for ids, corners in zip(marker_IDs, marker_corners):
            cv.polylines(
                frame, [corners.astype(np.int32)], True, (0, 255, 255), 4, cv.LINE_AA
            )
            corners = corners.reshape(4, 2)
            corners = corners.astype(int)
            top_right = corners[0].ravel()
            top_left = corners[1].ravel()
            bottom_right = corners[2].ravel()
            bottom_left = corners[3].ravel()
            cv.putText(
                frame,
                f"id: {ids[0]}",
                top_right,
                cv.FONT_HERSHEY_PLAIN,
                1.3,
                (200, 100, 0),
                2,
                cv.LINE_AA,
            )
            # put the marker's center position into the array
            curPos = (0, 0)
            for i in range(0, 4):
                curPos = (curPos[0] + corners[i][0], curPos[1] + corners[i][1])
            curPos = (curPos[0] / 4, curPos[1] / 4)
            if (1 <= ids[0] and ids[0] <= 6) :
                markerPositions[ids[0]-1] = curPos
            
    cv.imshow("frame", frame)
    key = cv.waitKey(1)
    if key == ord("a"):
        transformCalibrationDisplay(markerPositions)
    elif key == ord("q"):
        break
    elif (key) == ord("s"):
        cv.imshow('calibration', origImg)
cap.release()
cv.destroyAllWindows()

"""     better organized?

import cv2 as cv
from cv2 import aruco
import numpy as np
import os as os

# Function to detect ArUco markers and calculate their positions
def detect_markers(frame, detector):
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    marker_corners, marker_IDs, _ = detector.detectMarkers(gray_frame)
    marker_positions = []
    if marker_corners:
        for corners in marker_corners:
            corners = corners.reshape(4, 2)
            marker_center = np.mean(corners, axis=0)
            marker_positions.append(marker_center)
    return marker_positions

# Function to calculate affine transformation matrix
def calculate_affine_transform(src_points, dst_points):
    src_tri = np.array(src_points).astype(np.float32)
    dst_tri = np.array(dst_points).astype(np.float32)
    return cv.getAffineTransform(src_tri, dst_tri)

# Function to apply affine transformation to an image
def apply_affine_transform(image, transform_matrix):
    return cv.warpAffine(image, transform_matrix, (image.shape[1], image.shape[0]))

# Function to draw markers and triangles on the frame
def draw_markers_and_triangles(frame, src_tri, dst_tri, transformed_tri):
    if src_tri is not None:
        cv.polylines(frame, [src_tri.astype(np.int32)], True, (0, 255, 255))
        cv.polylines(frame, [dst_tri.astype(np.int32)], True, (0, 255, 255))
        cv.polylines(frame, [transformed_tri.astype(np.int32)], True, (255, 0, 0))
    return frame

def main():
    # Initialize ArUco marker detector
    marker_dict = aruco.getPredefinedDictionary(aruco.DICT_5X5_50)
    param_markers = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(marker_dict, param_markers)

    # Open camera
    cap = cv.VideoCapture(1)

    # Load calibration image
    absolute_path = os.path.join(os.getcwd(), 'lib', 'visual', 'defaultAruco.png')
    calibration = cv.imread(absolute_path)
    calibration_r = cv.resize(calibration, (1920, 1080))

    while True:
        # Capture frame from camera
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect ArUco markers and calculate their positions
        marker_positions = detect_markers(frame, detector)
        
        # Calculate affine transformation matrix
        if len(marker_positions) >= 3:
            src_tri = marker_positions[:3]
            dst_tri = [(0, 0), (calibration_r.shape[1], 0), (0, calibration_r.shape[0])]
            warp_mat = calculate_affine_transform(src_tri, dst_tri)
        
            # Apply affine transformation to calibration image
            warped_img = apply_affine_transform(calibration_r, warp_mat)

            # Draw markers and triangles on the frame
            transformed_tri = cv.transform(np.array([src_tri]), warp_mat)
            frame = draw_markers_and_triangles(frame, src_tri, dst_tri, transformed_tri)
            
            # Display frame with markers and triangles
            cv.imshow('Frame', frame)
            cv.imshow('Warped Calibration', warped_img)
        
        # Exit loop on 'q' key press
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release camera and close windows
    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()

"""