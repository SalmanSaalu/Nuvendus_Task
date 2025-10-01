# 📝 Task Management Web Application

A **Django + Django REST Framework** web application for task management with role-based access control.  
Supports **SuperAdmin**, **Admin**, and **User** roles, task assignment, completion reports, and JWT API integration.

---

## 🔹 Features

- Role-based dashboards: SuperAdmin, Admin, and User
- User management (create, update, delete)
- Task management (create, assign, update, complete)
- Task completion report with worked hours
- JWT authentication for API access
- Admins can manage only their assigned users
- Responsive and clean HTML templates

---

## 📦 Tech Stack

- Python  
- Django REST Framework  
- Simple JWT for API authentication  
- SQLite (default database)  
- HTML, CSS (minimal styling for templates)

---

## ⚡ Prerequisites

git clone https://github.com/SalmanSaalu/Nuvendus_Task.git
cd task_manager
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver


## To view the home page - http://127.0.0.1:8000/tasks/login

