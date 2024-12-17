import cv2
import os

# โฟลเดอร์ที่เก็บภาพต้นฉบับ
input_folder = "rank"
# โฟลเดอร์ที่ใช้เก็บภาพผลลัพธ์
output_folder = "template"

# ตรวจสอบว่าโฟลเดอร์ผลลัพธ์มีอยู่แล้วหรือไม่ ถ้าไม่มีจะสร้างใหม่
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# ตั้งค่าความเข้มแสง (threshold) และค่าสีสูงสุด
threshold_value = 128
max_value = 255

# อ่านไฟล์ภาพทั้งหมดในโฟลเดอร์ต้นฉบับ
for file_name in os.listdir(input_folder):
    # ตรวจสอบว่าเป็นไฟล์ภาพหรือไม่ (รองรับไฟล์ .jpg, .png, .jpeg)
    if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
        # สร้าง path ของภาพต้นฉบับและภาพผลลัพธ์
        input_path = os.path.join(input_folder, file_name)
        output_path = os.path.join(output_folder, f"{file_name}")

        # โหลดภาพในโหมด Grayscale
        image = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)

        if image is not None:
            # แปลงภาพเป็น Binary
            _, binary_image = cv2.threshold(image, threshold_value, max_value, cv2.THRESH_BINARY)

            # บันทึกภาพผลลัพธ์
            cv2.imwrite(output_path, binary_image)
            print(f"แปลงสำเร็จ: {file_name} -> {output_path}")
        else:
            print(f"ไม่สามารถโหลดภาพได้: {file_name}")

print("การแปลงภาพทั้งหมดเสร็จสิ้น!")
