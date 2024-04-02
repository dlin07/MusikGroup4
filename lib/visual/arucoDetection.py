import cv2 as cv
from cv2 import aruco
import numpy as np

markerPositions = []
for i in range(0, 6):
    markerPositions.append((0, 0))
# print(markerPositions)

marker_dict = aruco.getPredefinedDictionary(aruco.DICT_5X5_50)
param_markers = aruco.DetectorParameters()
detector = aruco.ArucoDetector(marker_dict, param_markers)

cap = cv.VideoCapture(1)

calibration = cv.imread('defaultAruco.png')
calibrationR = cv.resize(calibration, (int(1920/1.25), int(1080/1.25)))
cv.imshow('calibration', calibrationR)

def transformCalibrationDisplay(mPos):
    global calibrationR
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
    srcTri = np.array([[mPos[0][0], mPos[0][1]],[mPos[1][0], mPos[1][1]],[mPos[2][0], mPos[2][1]]]).astype(np.float32)
    dstTri = np.array([[actualTlShrunk[0], actualTlShrunk[1]],[actualTrShrunk[0],actualTrShrunk[1]],[actualBlShrunk[0], actualBlShrunk[1]]]).astype(np.float32)

    print(srcTri)
    print(dstTri)
    warp_mat = cv.getAffineTransform(srcTri, dstTri)

    warpedImg = cv.warpAffine(calibrationR, warp_mat, (calibrationR.shape[1], calibrationR.shape[0]))

    # translate
    translation_matrix = np.float32([ [1,0,center[0] - displayCenter[0]], [0,1,center[1] - displayCenter[1]] ])   
    warpedImg = cv.warpAffine(warpedImg, translation_matrix, (warpedImg.shape[1], warpedImg.shape[0]))
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
cap.release()
cv.destroyAllWindows()

    