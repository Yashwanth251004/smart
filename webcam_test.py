import cv2

found = False
for idx in range(3):
    print(f"Trying camera index {idx}...")
    cap = cv2.VideoCapture(idx)
    if cap.isOpened():
        print(f"Camera index {idx} opened successfully!")
        found = True
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            cv2.imshow(f'Webcam Test (Camera {idx})', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
        break
    else:
        print(f"Camera index {idx} not available.")
        cap.release()
if not found:
    print("No available camera found. Please check your webcam connection and permissions.") 