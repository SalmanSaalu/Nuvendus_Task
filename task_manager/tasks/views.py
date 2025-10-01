from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, DetailView, FormView,UpdateView,DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from .models import Task, Profile
from .forms import UserCreateForm,UserUpdateForm,TaskCreateForm,TaskCompletionForm
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib import messages

from .serializers import (
    TaskSerializer,
    TaskCompleteSerializer,
    RegisterSerializer,
    MyTokenObtainPairSerializer,TaskCreateSerializer
)

# --------------------------
# HTML / Template Views for Listing and main pages
# --------------------------
class LoginView(TemplateView):
    template_name = "login.html"

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # generate JWT tokens for client-side API usage and store in session temporarily
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)
            request.session["api_access_token"] = access
            request.session["api_refresh_token"] = str(refresh)
            print(refresh)
            # redirect according to role
            if hasattr(user, "profile") and user.profile.role == "superadmin":
                return redirect("dashboard_superadmin")
            elif hasattr(user, "profile") and user.profile.role == "admin":
                return redirect("dashboard_admin")
            else:
                return redirect("tasks_list_html")
        return self.render_to_response({"error": "Invalid credentials"})

class LogoutView(TemplateView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("login")

class SuperAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and hasattr(self.request.user, "profile") and self.request.user.profile.role == "superadmin"

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and hasattr(self.request.user, "profile") and self.request.user.profile.role == "admin"

class DashboardSuperAdminView(LoginRequiredMixin, SuperAdminRequiredMixin, TemplateView):
    template_name = "dashboard_superadmin.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["users"] = User.objects.all().select_related("profile")
        ctx["tasks"] = Task.objects.all()
        # supply token to template and remove from session
        ctx["api_access_token"] = self.request.session.pop("api_access_token", None)
        return ctx

class DashboardAdminView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = "dashboard_admin.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # admin sees tasks of users they manage
        # admin_user = self.request.user
        managed_users = User.objects.filter(id=self.request.user.id)
        ctx["tasks"] = Task.objects.filter(assigned_to__in=managed_users)
        ctx["api_access_token"] = self.request.session.pop("api_access_token", None)
        return ctx

class UsersListView(LoginRequiredMixin, SuperAdminRequiredMixin, TemplateView):
    template_name = "users_list.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["users"] = User.objects.all().select_related("profile")
        ctx["admins"] = User.objects.filter(profile__role="admin")
        ctx["api_access_token"] = self.request.session.pop("api_access_token", None)
        return ctx

# --------------------------
# HTML / Template Views for User operations
# --------------------------


class CreateUserView(LoginRequiredMixin, SuperAdminRequiredMixin, FormView):
    template_name = "create_user.html"
    form_class = UserCreateForm
    success_url = reverse_lazy("users_list")

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        role = form.cleaned_data["role"]
        managed_by = form.cleaned_data.get("managed_by", None)

        u = User.objects.create_user(username=username, email=email, password=password)
        profile = u.profile
        profile.role = role
        if managed_by:
            profile.managed_by = managed_by
        profile.save()
        return super().form_valid(form)
    
class UpdateUserView(LoginRequiredMixin, SuperAdminRequiredMixin, FormView):
    template_name = "update_user.html"
    form_class = UserUpdateForm

    def get_initial(self):
        user_id = self.kwargs.get("pk")
        user = get_object_or_404(User, pk=user_id)
        initial = {
            "email": user.email,
            "role": user.profile.role,
            "managed_by": user.profile.managed_by
        }
        return initial

    def form_valid(self, form):
        user_id = self.kwargs.get("pk")
        user = get_object_or_404(User, pk=user_id)
        user.email = form.cleaned_data["email"]
        user.save()

        profile = user.profile
        profile.role = form.cleaned_data["role"]
        profile.managed_by = form.cleaned_data.get("managed_by", None)
        profile.save()

        return redirect("users_list")

class DeleteUserView(LoginRequiredMixin, SuperAdminRequiredMixin, TemplateView):
    def get(self, request, pk, *args, **kwargs):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return redirect("users_list")
    

    
    
# --------------------------
# HTML / Template Views for Task operations
# --------------------------


class TasksListHTMLView(LoginRequiredMixin, TemplateView):
    template_name = "tasks_list.html"   
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        current_user = self.request.user

        # Default queryset (empty until filtered by role)
        tasks_qs = Task.objects.none()

        if hasattr(current_user, "profile"):
            if current_user.profile.role == "superadmin":
                # SuperAdmin → all tasks
                tasks_qs = Task.objects.all()
            elif current_user.profile.role == "admin":
                # Admin → tasks of managed users
                managed_users = User.objects.filter(profile__managed_by=current_user)
                tasks_qs = Task.objects.filter(assigned_to__in=managed_users)

            else:
                # Regular user → only their own tasks
                tasks_qs = Task.objects.filter(assigned_to=current_user)
        
        job=current_user.profile.role
        ctx["tasks"] = tasks_qs
        ctx["role"] = job
        ctx["api_access_token"] = self.request.session.pop("api_access_token", None)
        return ctx


class TaskDetailHTMLView(LoginRequiredMixin, TemplateView):
    template_name = "task_detail.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        task_id = kwargs.get("pk")
        tasks_qs = Task.objects.filter(pk=task_id)
        ctx["tasks"] = tasks_qs
        ctx["api_access_token"] = self.request.session.pop("api_access_token", None)
        return ctx


class CreateTaskView(LoginRequiredMixin, TemplateView):
    template_name = "create_task.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        print("kkkk")
        print(self.request.user)
        ctx["form"] = TaskCreateForm(user=self.request.user)
        return ctx

    def post(self, request, *args, **kwargs):
        form = TaskCreateForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.status = "pending"  # default
            task.save()
            return redirect("tasks_list_html")
        return self.render_to_response({"form": form})
    
class UpdateTaskView(LoginRequiredMixin, TemplateView):
    template_name = "task_update.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        task = get_object_or_404(Task, pk=self.kwargs["pk"])
        ctx["form"] = TaskCreateForm(instance=task, user=self.request.user)
        ctx["task"] = task
        return ctx

    def post(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs["pk"])
        form = TaskCreateForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("tasks_list_html")
        return self.render_to_response({"form": form, "task": task})


class TaskDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk)
        print(task)
        task.delete()
        return redirect("tasks_list_html")

class TaskCompletionView(LoginRequiredMixin, TemplateView):
    template_name = "complete_task.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        task = get_object_or_404(Task, pk=self.kwargs["pk"])

        # only allow the assigned user (or superadmin/admin) to complete
        if task.assigned_to != self.request.user and self.request.user.profile.role == "user":
            messages.warning(self.request, "You are not allowed to complete this task.")
            return redirect("tasks_list_html")

        ctx["form"] = TaskCompletionForm(instance=task)
        ctx["task"] = task
        return ctx

    def post(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs["pk"])

        if task.assigned_to != request.user and request.user.profile.role == "user":     
            messages.warning(request, "You are not allowed to complete this task.")
            return redirect("tasks_list_html")

        form = TaskCompletionForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            task.status = "completed"  # update status automatically
            task.save()
            messages.success(request, "Task marked as completed!")
            return redirect("tasks_list_html")
        return self.render_to_response({"form": form, "task": task})
# --------------------------
# API Views (DRF)
# --------------------------
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"username": user.username, "email": user.email}, status=status.HTTP_201_CREATED)
     
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TaskCreateView(APIView):
    permission_classes = [IsAuthenticated]  # only logged-in users can create

    def post(self, request):
        user = request.user
        # Only superadmin/admin can create tasks
        if not hasattr(user, "profile") or user.profile.role not in ["admin", "superadmin"]:
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        serializer = TaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # status defaults to 'pending'
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        # if admin/superadmin, they can view according to role:
        if hasattr(user, "profile") and user.profile.role == "superadmin":
            tasks = Task.objects.all()
        elif hasattr(user, "profile") and user.profile.role == "admin":
            # admin sees tasks of users they manage
            managed_users = User.objects.filter(profile__managed_by=user)
            tasks = Task.objects.filter(assigned_to__in=managed_users)
        else:
            tasks = Task.objects.filter(assigned_to=user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

class TaskUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, pk):
        user = request.user
        task = get_object_or_404(Task, pk=pk)

        # permission check: user can update their own tasks, admin/superadmin more privileges
        if hasattr(user, "profile") and user.profile.role == "superadmin":
            allowed = True
        elif hasattr(user, "profile") and user.profile.role == "admin":
            # admin allowed if assigned_to is one of their managed users
            if task.assigned_to.profile.managed_by == user:
                allowed = True
            else:
                allowed = False
        else:
            # regular user
            allowed = (task.assigned_to == user)

        if not allowed:
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        if request.data.get("status") == "completed":
            serializer = TaskCompleteSerializer(data=request.data)
            if serializer.is_valid():
                report = serializer.validated_data["completion_report"]
                worked_hours = serializer.validated_data["worked_hours"]
                task.mark_completed(report, worked_hours)
                return Response({"detail": "Task marked completed"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        status_field = request.data.get("status")
        if status_field in ["pending", "in_progress"]:
            task.status = status_field
            task.save()
            return Response({"detail": "Task status updated"}, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid update"}, status=status.HTTP_400_BAD_REQUEST)

class TaskReportView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        user = request.user
        # only admin & superadmin can view
        if not (hasattr(user, "profile") and user.profile.role in ["admin", "superadmin"]):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        task = get_object_or_404(Task, pk=pk)
        if task.status != "completed":
            return Response({"detail": "Report not available for incomplete task"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "task_id": task.id,
            "title": task.title,
            "assigned_to": task.assigned_to.username,
            "completion_report": task.completion_report,
            "worked_hours": str(task.worked_hours),
        }, status=status.HTTP_200_OK)








