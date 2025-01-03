from flask import Flask, render_template, request, send_from_directory
from rembg import remove
import os
from PIL import Image
import io

# إعداد التطبيق
app = Flask(__name__)

# مسار لحفظ الصور في بيئة الاستضافة (مثل Render)
UPLOAD_FOLDER = '/tmp/uploads'
OUTPUT_FOLDER = '/tmp/output'

# تعيين مجلدات الحفظ في التطبيق
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# تأكد من وجود المجلدات
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# الصفحة الرئيسية
@app.route('/')
def index():
    return render_template('index.html')

# وظيفة رفع الصورة وإزالة الخلفية
@app.route('/remove_background', methods=['POST'])
def remove_background():
    if 'file' not in request.files:
        return "لم يتم اختيار ملف!"
    file = request.files['file']
    if file.filename == '':
        return "لم يتم اختيار ملف!"
    
    # حفظ الصورة المدخلة
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(input_path)
    print(f"تم رفع الصورة: {file.filename}")

    # إزالة الخلفية
    try:
        with open(input_path, 'rb') as input_file:
            input_data = input_file.read()
            output_data = remove(input_data)
        
        # تحويل البيانات الناتجة إلى صورة PNG باستخدام PIL للتأكد من صيغة الصورة
        output_image = Image.open(io.BytesIO(output_data))

        # حفظ الصورة الناتجة
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'output_image.png')
        output_image.save(output_path, 'PNG')

        print(f"تم إزالة الخلفية بنجاح")
        print(f"مسار الصورة الناتجة: {output_path}")

        # إرسال الصورة الناتجة للمستخدم
        return send_from_directory(app.config['OUTPUT_FOLDER'], 'output_image.png')

    except Exception as e:
        return f"حدث خطأ أثناء إزالة الخلفية: {e}"

# تشغيل التطبيق على الشبكة المحلية
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
