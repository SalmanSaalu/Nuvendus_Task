from django import forms
from .models import Task
from django.contrib.auth.models import User



class TaskCreateForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label="Assign To"
    )

    class Meta:
        model = Task
        fields = ["title", "description", "assigned_to", "due_date"]

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop("user", None)  # pop user
        super().__init__(*args, **kwargs)
        print(current_user)
        if current_user:
            if current_user.profile.role == "superadmin":
                self.fields["assigned_to"].queryset = User.objects.all()
            elif current_user.profile.role == "admin":
                self.fields["assigned_to"].queryset = User.objects.filter(
                    profile__role="user", profile__managed_by=current_user
                )
            else:
                # normal users cannot assign tasks
                self.fields["assigned_to"].queryset = User.objects.none()

class TaskCompletionForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["completion_report", "worked_hours"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["completion_report"].label = "Completion Description"
        self.fields["worked_hours"].label = "Worked Hours (in hours)"

class UserCreateForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, min_length=6)
    role = forms.ChoiceField(choices=[("admin", "Admin"), ("user", "User")])
    managed_by = forms.ModelChoiceField(queryset=User.objects.filter(profile__role="admin"), required=False, help_text="Assign user to an admin (optional)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If data is present (on POST), adjust queryset based on role
        if 'role' in self.data:
            if self.data.get('role') == 'admin':
                # Disable managed_by if role is admin
                self.fields['managed_by'].queryset = User.objects.none()
                self.fields['managed_by'].disabled = True
            else:
                # Role is user → show available admins
                self.fields['managed_by'].queryset = User.objects.filter(profile__role="admin")
                self.fields['managed_by'].disabled = False


class UserUpdateForm(forms.Form):
    email = forms.EmailField(required=False)
    role = forms.ChoiceField(choices=[("admin", "Admin"), ("user", "User")])
    managed_by = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__role="admin"),
        required=False,
        help_text="Assign user to an admin (optional)"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If data is present (on POST), adjust queryset based on role
        if 'role' in self.data:
            if self.data.get('role') == 'admin':
                # Disable managed_by if role is admin
                self.fields['managed_by'].queryset = User.objects.none()
                self.fields['managed_by'].disabled = True
            else:
                # Role is user → show available admins
                self.fields['managed_by'].queryset = User.objects.filter(profile__role="admin")
                self.fields['managed_by'].disabled = False