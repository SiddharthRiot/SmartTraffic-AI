import cv2
from detection.yolo_detector import detect_vehicles

def start_stream():

    cap = cv2.VideoCapture("detection/Traffic.mp4")

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        vehicles = detect_vehicles(frame)

        print("Vehicles detected:", vehicles)

        cv2.imshow("Traffic Feed", frame)

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()