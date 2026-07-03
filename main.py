import os
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from starlette.middleware.sessions import SessionMiddleware

# 1. إعداد قاعدة البيانات والاتصال بـ Neon
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL variable is not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. نماذج الجداول (Models)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  
    role = Column(String, nullable=False)  # 'Teacher' أو 'Student'

class StudentRecord(Base):
    __tablename__ = "student_records"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    course = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

# 3. إعداد التطبيق والـ Session
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="secure_students_key_2026")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. الـ CSS المطور والمعدل لحل مشكلة أزرار الهاتف
CSS_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');
    * { box-sizing: border-box; font-family: 'Cairo', sans-serif; margin: 0; padding: 0; }
    
    body { 
        background-color: #0b111e; 
        color: #f3f4f6; 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        min-height: 100vh; 
        padding: 15px; 
        direction: rtl;
        animation: fadeInBody 0.6s ease-out;
    }
    
    @keyframes fadeInBody {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .container, .dashboard-container { 
        background-color: #111827; 
        border: 1px solid #1f2937; 
        border-radius: 16px; 
        padding: 25px; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.4);
    }
    .container { width: 100%; max-width: 450px; }
    .dashboard-container { max-width: 950px; width: 100%; overflow-x: hidden; }
    
    h1 { color: #60a5fa; text-align: center; margin-bottom: 10px; font-size: 24px; font-weight: 700; }
    h2 { color: #9ca3af; text-align: center; font-size: 13px; margin-bottom: 25px; font-weight: 400; line-height: 1.6; }
    
    .form-group { margin-bottom: 18px; text-align: right; }
    label { display: block; margin-bottom: 8px; color: #9ca3af; font-size: 14px; }
    
    input, select { 
        width: 100%; 
        padding: 12px 16px; 
        background-color: #1f2937; 
        border: 1px solid #374151; 
        border-radius: 8px; 
        color: #fff; 
        font-size: 15px; 
        transition: all 0.25s ease; 
        outline: none; 
        text-align: right; 
    }
    input:focus, select:focus { 
        border-color: #3b82f6; 
        box-shadow: 0 0 0 3px rgba(59,130,246,0.25);
    }
    
    .btn { 
        width: 100%; 
        padding: 12px; 
        background-color: #2563eb; 
        border: none; 
        border-radius: 8px; 
        color: #fff; 
        font-size: 16px; 
        font-weight: 600; 
        cursor: pointer; 
        transition: all 0.2s ease; 
        margin-top: 10px; 
    }
    .btn:hover { 
        background-color: #1d4ed8; 
        transform: translateY(-2px);
    }
    
    /* تنسيق أزرار التعديل والحذف لمنع التداخل */
    .actions-cell {
        display: flex;
        flex-direction: column;
        gap: 8px;
        justify-content: center;
        align-items: center;
        white-space: nowrap;
    }
    
    .btn-action {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        max-width: 90px;
        padding: 6px 10px;
        font-size: 13px;
        font-weight: 600;
        border-radius: 6px;
        color: white;
        text-decoration: none;
        border: none;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .btn-edit { background-color: #059669; }
    .btn-edit:hover { background-color: #047857; transform: scale(1.05); }
    
    .btn-danger { background-color: #dc2626; }
    .btn-danger:hover { background-color: #b91c1c; transform: scale(1.05); }

    /* جعل الجدول متجاوب تماماً في الموبايل */
    .table-responsive {
        width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        margin-top: 20px;
        border-radius: 8px;
        border: 1px solid #28334e;
    }

    table { width: 100%; border-collapse: collapse; background-color: #171e2e; min-width: 600px; }
    th, td { padding: 12px; text-align: right; border-bottom: 1px solid #28334e; font-size: 14px; }
    th { background-color: #1f2937; color: #60a5fa; font-weight: 600; white-space: nowrap; }
    
    .user-header { display: flex; justify-content: space-between; align-items: center; background-color: #1f2937; padding: 12px 20px; border-radius: 8px; margin-bottom: 25px; border: 1px solid #374151; }
    .logout-btn { background-color: #dc2626; padding: 6px 12px; border-radius: 6px; color: white; text-decoration: none; font-size: 13px; font-weight: 600; }
    
    .badge { padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; margin-right: 8px; }
    .badge-teacher { background-color: #1e3a8a; color: #93c5fd; }
    .badge-student { background-color: #064e3b; color: #6ee7b7; }

    /* الـ Modal المنبثق للتعديل */
    .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.6); justify-content: center; align-items: center; backdrop-filter: blur(4px); }
    .modal-content { background-color: #111827; border: 1px solid #1f2937; border-radius: 16px; padding: 25px; width: 90%; max-width: 450px; animation: modalOpen 0.3s ease; }
    @keyframes modalOpen { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }
    .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #1f2937; padding-bottom: 10px; }
    .close-btn { color: #9ca3af; font-size: 24px; cursor: pointer; }
</style>
"""

# 5. واجهات الدخول والإنشاء
@app.get("/login", response_class=HTMLResponse)
def login_page(error: str = None):
    error_div = f'<div class="alert">{error}</div>' if error else ''
    return f"""
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تسجيل الدخول - منصة تسجيل الطلاب السحابية</title>
        {CSS_STYLE}
    </head>
    <body>
        <div class="container">
            <h1>منصة تسجيل الطلاب السحابية</h1>
            <h2>كلية علوم الحاسوب وتقانة المعلومات</h2>
            {error_div}
            <form action="/login" method="post">
                <div class="form-group">
                    <label>البريد الإلكتروني</label>
                    <input type="email" name="email" required placeholder="name@example.com">
                </div>
                <div class="form-group">
                    <label>كلمة المرور</label>
                    <input type="password" name="password" required placeholder="••••••••">
                </div>
                <button type="submit" class="btn">تسجيل الدخول</button>
            </form>
            <div class="link-text">
                ليس لديك حساب؟ <a href="/signup">أنشئ حساب جديد الآن</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or user.password != password:
        return RedirectResponse(url="/login?error=البريد الإلكتروني أو كلمة المرور غير صحيحة", status_code=status.HTTP_303_SEE_OTHER)
    
    request.session["user_id"] = user.id
    request.session["user_name"] = user.full_name
    request.session["user_role"] = user.role
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/signup", response_class=HTMLResponse)
def signup_page(error: str = None):
    error_div = f'<div class="alert">{error}</div>' if error else ''
    return f"""
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>إنشاء حساب جديد</title>
        {CSS_STYLE}
    </head>
    <body>
        <div class="container">
            <h1>منصة تسجيل الطلاب السحابية</h1>
            <h2>كلية علوم الحاسوب وتقانة المعلومات</h2>
            {error_div}
            <form action="/signup" method="post">
                <div class="form-group">
                    <label>الاسم كاملاً</label>
                    <input type="text" name="full_name" required placeholder="أدخل اسمك الثلاثي">
                </div>
                <div class="form-group">
                    <label>البريد الإلكتروني</label>
                    <input type="email" name="email" required placeholder="name@example.com">
                </div>
                <div class="form-group">
                    <label>نوع الحساب (الصلاحية)</label>
                    <select name="role" required>
                        <option value="Student">طالب / مسجل (عرض البيانات فقط)</option>
                        <option value="Teacher">دكتور / مدرس (مسموح له بالإدارات والتعديل)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>كلمة المرور</label>
                    <input type="password" name="password" required placeholder="••••••••">
                </div>
                <button type="submit" class="btn">إنشاء الحساب</button>
            </form>
            <div class="link-text">
                لديك حساب بالفعل؟ <a href="/login">تسجيل الدخول</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/signup")
def signup(full_name: str = Form(...), email: str = Form(...), role: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return RedirectResponse(url="/signup?error=هذا البريد الإلكتروني مسجل بالفعل", status_code=status.HTTP_303_SEE_OTHER)
    
    new_user = User(full_name=full_name, email=email, role=role, password=password)
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

# 6. الصفحة الرئيسية مع معالجة الاستجابة وعزل الأزرار بشكل مرتب
@app.get("/", response_class=HTMLResponse)
def index_page(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login")
    
    user_name = request.session.get("user_name")
    user_role = request.session.get("user_role")
    
    students = db.query(StudentRecord).all()
    
    table_rows = ""
    if not students:
        table_rows = f"<tr><td colspan='{'5' if user_role == 'Teacher' else '4'}' style='text-align:center; color:#9ca3af;'>لا يوجد طلاب مسجلين حتى الآن</td></tr>"
    else:
        for s in students:
            actions_td = ""
            if user_role == "Teacher":
                actions_td = f"""
                <td>
                    <div class="actions-cell">
                        <button class="btn-action btn-edit" onclick="openEditModal({s.id}, '{s.name}', '{s.email}', '{s.course}')">تعديل ✏️</button>
                        <a href="/delete_student/{s.id}" class="btn-action btn-danger" onclick="return confirm('هل أنت متأكد من حذف هذا الطالب؟')">حذف 🗑️</a>
                    </div>
                </td>
                """
            table_rows += f"""
            <tr>
                <td>{s.id}</td>
                <td style="font-weight: 600;">{s.name}</td>
                <td>{s.email}</td>
                <td>{s.course}</td>
                {actions_td}
            </tr>
            """
            
    if user_role == "Teacher":
        add_student_section = """
        <div style="background-color: #171e2e; padding: 20px; border-radius: 12px; border: 1px solid #1f2937; margin-bottom: 30px;">
            <h3 style="color: #60a5fa; margin-bottom: 15px; font-size: 18px;">➕ إضافة طالب جديد</h3>
            <form action="/add_student" method="post">
                <div class="form-group">
                    <label>اسم الطالب كاملاً</label>
                    <input type="text" name="name" required placeholder="أدخل اسم الطالب">
                </div>
                <div class="form-group">
                    <label>البريد الإلكتروني</label>
                    <input type="email" name="email" required placeholder="student@example.com">
                </div>
                <div class="form-group">
                    <label>الكورس / التخصص</label>
                    <input type="text" name="course" required placeholder="مثال: علوم حاسوب - المستوى الرابع">
                </div>
                <button type="submit" class="btn">حفظ البيانات</button>
            </form>
        </div>
        """
    else:
        add_student_section = """
        <div style="background-color: #1c2538; padding: 15px; border-radius: 8px; border: 1px solid #2e3b52; color: #9ca3af; font-size: 14px; text-align: center; margin-bottom: 30px;">
            🔒 نموذج إدارة وبناء الطلاب متاح فقط لـ <strong>الدكاترة والمدرسين</strong>. حسابك مخصص للاستعراض.
        </div>
        """

    role_badge = f'<span class="badge badge-teacher">دكتور / مدرس</span>' if user_role == "Teacher" else f'<span class="badge badge-student">طالب / مسجل</span>'
    table_header_action = "<th>العمليات الإدارية</th>" if user_role == "Teacher" else ""

    return f"""
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>منصة تسجيل الطلاب السحابية</title>
        {CSS_STYLE}
    </head>
    <body>
        <div class="dashboard-container">
            <h1>منصة تسجيل الطلاب السحابية</h1>
            <h2 style="margin-bottom: 15px;">مشروع إدارة الطلاب - كلية علوم الحاسوب وتقانة المعلومات</h2>
            
            <div class="user-header">
                <div>
                    <span>مرحباً بك: <strong>{user_name}</strong></span>
                    {role_badge}
                </div>
                <a href="/logout" class="logout-btn">تسجيل الخروج</a>
            </div>

            {add_student_section}

            <h3 style="color: #60a5fa; margin-bottom: 15px; font-size: 18px;">🎓 قائمة الطلاب المسجلين</h3>
            
            <!-- حاوية الجدول المتجاوبة من أجل الهواتف -->
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>المعرف</th>
                            <th>الاسم</th>
                            <th>الإيميل</th>
                            <th>الكورس</th>
                            {table_header_action}
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- نافذة التعديل المنبثقة -->
        <div id="editModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h3 style="color: #60a5fa;">✏️ تعديل بيانات الطالب</h3>
                    <span class="close-btn" onclick="closeEditModal()">&times;</span>
                </div>
                <form action="/edit_student" method="post">
                    <input type="hidden" id="edit_id" name="id">
                    <div class="form-group">
                        <label>اسم الطالب كاملاً</label>
                        <input type="text" id="edit_name" name="name" required>
                    </div>
                    <div class="form-group">
                        <label>البريد الإلكتروني</label>
                        <input type="email" id="edit_email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label>الكورس / التخصص</label>
                        <input type="text" id="edit_course" name="course" required>
                    </div>
                    <button type="submit" class="btn" style="background-color: #059669;">تحديث البيانات الآن</button>
                </form>
            </div>
        </div>

        <script>
            function openEditModal(id, name, email, course) {{
                document.getElementById('edit_id').value = id;
                document.getElementById('edit_name').value = name;
                document.getElementById('edit_email').value = email;
                document.getElementById('edit_course').value = course;
                document.getElementById('editModal').style.display = 'flex';
            }}
            function closeEditModal() {{
                document.getElementById('editModal').style.display = 'none';
            }}
            window.onclick = function(event) {{
                var modal = document.getElementById('editModal');
                if (event.target == modal) {{
                    modal.style.display = 'none';
                }}
            }}
        </script>
    </body>
    </html>
    """

# 7. مسارات الإدارة
@app.post("/add_student")
def add_student(request: Request, name: str = Form(...), email: str = Form(...), course: str = Form(...), db: Session = Depends(get_db)):
    if request.session.get("user_role") != "Teacher":
        raise HTTPException(status_code=403, detail="غير مصرح لك")
    new_student = StudentRecord(name=name, email=email, course=course)
    db.add(new_student)
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/edit_student")
def edit_student(request: Request, id: int = Form(...), name: str = Form(...), email: str = Form(...), course: str = Form(...), db: Session = Depends(get_db)):
    if request.session.get("user_role") != "Teacher":
        raise HTTPException(status_code=403, detail="غير مصرح لك")
    student = db.query(StudentRecord).filter(StudentRecord.id == id).first()
    if student:
        student.name = name
        student.email = email
        student.course = course
        db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/delete_student/{id}")
def delete_student(request: Request, id: int, db: Session = Depends(get_db)):
    if request.session.get("user_role") != "Teacher":
        raise HTTPException(status_code=403, detail="غير مصرح لك")
    student = db.query(StudentRecord).filter(StudentRecord.id == id).first()
    if student:
        db.delete(student)
        db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login")
