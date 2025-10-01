from django.urls import path


from tasks import views
from tasks.views import RegisterView
from .views import (
    LoginView, LogoutView,
    DashboardSuperAdminView, DashboardAdminView,
    UsersListView, CreateUserView,
    TasksListHTMLView, TaskDetailHTMLView,
    MyTokenObtainPairView, RegisterView,
    TaskListView, TaskUpdateView, TaskReportView,UpdateUserView,DeleteUserView,
    CreateTaskView,TaskCreateView,TaskDeleteView,UpdateTaskView,TaskCompletionView
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


urlpatterns = [

    # API endpoints (Templates rendering)
    path("login/", LoginView.as_view(), name="login"),#ok
    path("logout/", LogoutView.as_view(), name="logout"),#ok
    path("dashboard/superadmin/", DashboardSuperAdminView.as_view(), name="dashboard_superadmin"),
    path("dashboard/admin/", DashboardAdminView.as_view(), name="dashboard_admin"),
    path("users/", UsersListView.as_view(), name="users_list"),#ok
    path("users/create/", CreateUserView.as_view(), name="create_user"),#ok
    path("tasks/html/", TasksListHTMLView.as_view(), name="tasks_list_html"),
    path("tasks/<int:pk>/detail/", TaskDetailHTMLView.as_view(), name="task_detail_html"),
    path("tasks/<int:pk>/update/", UpdateTaskView.as_view(), name="task-update"),
    path("tasks/<int:pk>/delete/", TaskDeleteView.as_view(), name="task-delete"),
    path("tasks/<int:pk>/completion/", TaskCompletionView.as_view(), name="task-completion"),
    path("tasks/create/", CreateTaskView.as_view(), name="create_task"),
    path("users/<int:pk>/update/", UpdateUserView.as_view(), name="update_user"),#ok
    path("users/<int:pk>/delete/", DeleteUserView.as_view(), name="delete_user"),#ok



    # API endpoints (JWT-protected)
    path("api/token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/register/", RegisterView.as_view(), name="api_register"),#ok
    path("api/tasks/", TaskListView.as_view(), name="api_get_tasks"),#ok
    path("api/tasks/<int:pk>/", TaskUpdateView.as_view(), name="api_update_task"),
    path("api/tasks/<int:pk>/report/", TaskReportView.as_view(), name="api_get_task_report"),
    path("api/tasks/create/", TaskCreateView.as_view(), name="api_create_task"),


     
]