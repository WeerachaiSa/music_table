import cv2
import numpy as np

# ช่วงของสีใน HSV (ปรับตามต้องการ)
color_ranges = {
    "red": [(0, 50, 50), (10, 255, 255)],
    "orange": [(11, 50, 50), (25, 255, 255)],
    "yellow": [(26, 50, 50), (35, 255, 255)],
    "green": [(36, 50, 50), (85, 255, 255)],
    "blue": [(86, 50, 50), (125, 255, 255)],
    "indigo": [(126, 50, 50), (140, 255, 255)],
    "pink": [(141, 50, 50), (170, 255, 255)],
}

def detect_color(hsv_frame, x, y):
    # วนลูปตรวจจับสีในช่วงที่กำหนด
    for color, (lower, upper) in color_ranges.items():
        mask = cv2.inRange(hsv_frame, np.array(lower), np.array(upper))
        if mask[y, x]:  # ตรวจสอบพิกเซลที่ตำแหน่งเส้นกวาด
            return color
    return None

def adjust_brightness_contrast(image):
    # ใช้ CLAHE เพื่อปรับ contrast
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

# เริ่มต้นการจับภาพจาก webcam
cap = cv2.VideoCapture(1)
x_position = 0  # ตำแหน่งเริ่มต้นของเส้นกวาด

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # ปรับความสว่างและ contrast
    frame = adjust_brightness_contrast(frame)

    # แปลงภาพเป็น HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # ตำแหน่ง y ของเส้นกวาด
    line_y = frame.shape[0] // 2

    # ตรวจจับสีในพิกเซลที่ตำแหน่ง (x_position, line_y)
    color_detected = detect_color(hsv_frame, x_position, line_y)

    # แสดงเส้นกวาด
    cv2.line(frame, (x_position, 0), (x_position, frame.shape[0]), (255, 255, 255), 2)

    # แสดงสีที่ตรวจจับได้
    if color_detected:
        cv2.putText(frame, f"Detected Color: {color_detected}", (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # แสดงภาพ
    cv2.imshow("Color Detection", frame)

    # อัปเดตตำแหน่งของเส้นกวาด
    x_position += 2  # เลื่อนเส้นกวาดช้าลงทีละ 2 พิกเซล
    if x_position >= frame.shape[1]:  # ถ้าเส้นถึงขอบขวา ให้เริ่มใหม่ที่ซ้าย
        x_position = 0

    # ออกจากลูปเมื่อกดปุ่ม 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
