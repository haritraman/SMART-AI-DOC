AI-Powered Document & Presentation Generator

SMART AI DOC is a full-stack Flask application that allows users to:

✔ Register & log in  
✔ Create projects (Word / PPTX)  
✔ Define document structure (sections/slides)  
✔ Generate content using Google Gemini API  
✔ Refine content using prompts  
✔ Add comments & feedback  
✔ Export final files as **.docx** or **.pptx**  
✔ View generated content anytime  
✔ Manage all projects via a clean dashboard  

---

## 🚀 Live Demo
👉 **Demo Video 
https://drive.google.com/file/d/1vYHeAtQajhBzl9vDsBoGXR-YNYKv73lx/view?usp=sharing

---

## 📦 Features

### 🔐 Authentication
- User registration  
- JWT-based login  
- Session handling on frontend  

### 📁 Project Management
- Create projects with:
  - Title  
  - Document type (**Word / PowerPoint**)  
  - Main topic/prompt  
- Dashboard showing:
  - Status (configured / generated)
  - Direct links to content and comments

### 🧩 Structure Builder
- Add, remove, reorder sections/slides  
- Save structure  
- Reset content + comments when structure changes  

### 🤖 AI Generation (Google Gemini)
- Generate section-wise content  
- Regenerate specific sections  
- Local refinements (make formal, shorten, etc.)

### 💬 Comments & Feedback
- Add comments per section  
- View all comments grouped by section  
- Automatically cleared when the structure resets  

### 📤 Export
- Export complete project as:
  - **Word (.docx)**  
  - **PowerPoint (.pptx)**  

---

## 🛠️ Tech Stack

### **Backend**
- Python 3.13  
- Flask + Flask-JWT-Extended  
- SQLAlchemy ORM  
- PostgreSQL  
- python-docx  
- python-pptx  
- gunicorn (for production)

### **Frontend**
- HTML, CSS, Vanilla JS  
- Fetch API  
- LocalStorage auth tokens

### **AI**
- Google Gemini API (`v1beta`)  
- Model: `gemini-2.5-flash`  

---

# ⚙️ Installation

## **1. Clone the Repository**
```bash
[[git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
](https://github.com/haritraman/SMART-AI-DOC.git)](https://github.com/haritraman/SMART-AI-DOC.git)
