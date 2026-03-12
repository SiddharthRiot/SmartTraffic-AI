from ultralytics import YOLO

model = YOLO("yolov8n.pt")

vehicle_classes = [2,3,5,7]

def detect_vehicles(frame):

    results = model(frame)

    count = 0

    for r in results:
        for box in r.boxes:
            cls = int(box.cls)

            if cls in vehicle_classes:
                count += 1

    return count