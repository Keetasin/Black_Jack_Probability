import cv2
import os

# ตั้งค่าโฟลเดอร์
input_folder = 'btemplate'  # โฟลเดอร์ที่มีรูปภาพ
output_folder = 'template'  # โฟลเดอร์สำหรับบันทึกภาพใหม่

# สร้างโฟลเดอร์ output หากยังไม่มี
os.makedirs(output_folder, exist_ok=True)

# ขนาดที่ต้องการ
target_width = 70
target_height = 125

# วนลูปไฟล์ในโฟลเดอร์
for filename in os.listdir(input_folder):
    input_path = os.path.join(input_folder, filename)
    
    # ตรวจสอบว่าไฟล์เป็นรูปภาพหรือไม่
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
        # อ่านรูปภาพ
        img = cv2.imread(input_path)

        if img is not None:
            # ปรับขนาดรูป
            resized_img = cv2.resize(img, (target_width, target_height))

            # บันทึกรูปภาพในโฟลเดอร์ output
            output_path = os.path.join(output_folder, filename)
            cv2.imwrite(output_path, resized_img)
            print(f"Resized and saved: {output_path}")
        else:
            print(f"Failed to load image: {input_path}")
    else:
        print(f"Skipped non-image file: {filename}")

print("Finished resizing all images.")
