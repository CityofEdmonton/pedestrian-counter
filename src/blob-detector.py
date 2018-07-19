class BlobDetector:

    minArea = 5

    filterByCircularity = False
    minCircularity = 0.1

    filterByConvexity = False
    minConvexity = 0.87

    __init__ (self,
            minThreshold = 10,
            maxThreshold = 255,
            filterByArea = True,
            minArea = 5,
            filterByCircularity = True,
            minCircularity = 0.1,
            filterByConvexity = False,
            minConvexity = 0.87,
            filterByInertia = False,
            minInertiaRatio = 0.01):
        params = cv2.SimpleBlobDetector_Params()
        params.minThreshold = minThreshold
        params.maxThreshold = maxThreshold
        params.filterByArea = filterByArea
        params.minArea = minArea
        params.filterByCircularity = filterByCircularity
        params.minCircularity = minCircularity
        params.filterByConvexity = filterByConvexity
        params.minConvexity = minConvexity
        params.filterByInertia = filterByInertia
        params.minInertiaRatio = minInertiaRatio
        self.detector = cv2.SimpleBlobDetector_create(params)

    def detect(self, img):
        keypoints = detector.detect(img)
        return keypoints
    
