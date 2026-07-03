
from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

# قراءة رابط قاعدة البيانات من إعدادات Render
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is missing!")

# إعداد الـ SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# تعريف جدول الطلاب
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    course = Column(String)

# إنشاء الجداول في قاعدة البيانات السحابية
Base.metadata.create_all(bind=engine)

app = FastAPI()

# دالة للحصول على جلسة قاعدة البيانات
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# عرض الواجهة الرئيسية وقراءة الطلاب من القاعدة
@app.get("/", response_class=HTMLResponse)
async def read_root(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    
    # قراءة ملف الـ HTML
    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # بناء جدول الطلاب ديناميكياً داخل الـ HTML
    table_rows = ""
    for student in students:
        table_rows += f"""
        <tr class="border-b border-slate-700 hover:bg-slate-700/50 transition">
            <td class="px-6 py-4">{student.id}</td>
            <td class="px-6 py-4 font-semibold text-white">{student.name}</td>
            <td class="px-6 py-4 text-slate-300">{student.email}</td>
            <td class="px-6 py-4 text-blue-400">{student.course}</td>
        </tr>
        """
    
    # استبدال المكان المخصص في الـ HTML بالجدول الحقيقي
    if "<!-- STUDENTS_PLACEHOLDER -->" in html_content:
        html_content = html_content.replace("<!-- STUDENTS_PLACEHOLDER -->", table_rows)
    else:
        html_content = html_content.replace("</tbody>", f"{table_rows}</tbody>")
        
    return html_content

# إضافة طالب جديد
@app.post("/add_student")
async def add_student(
    name: str = Form(...), 
    email: str = Form(...), 
    course: str = Form(...), 
    db: Session = Depends(get_db)
):
    db_student = db.query(Student).filter(Student.email == email).first()
    if db_student:
        raise HTTPException(status_code=400, detail="البريد الإلكتروني مسجل مسبقاً")
    
    new_student = Student(name=name, email=email, course=course)
    db.add(new_student)
    db.commit()
    return RedirectResponse(url="/", status_code=303)
