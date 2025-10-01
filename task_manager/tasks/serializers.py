from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile,Task
# Token generation and Additional response fields added
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token
    
    def validate(self, attrs):

        data = super().validate(attrs)
        data.update({
            'username': self.user.username,
            'email': self.user.email,
        })

        return data
    

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        
        Profile.objects.get_or_create(user=user, role='user')
        return user
    
    # Task Serializer
class TaskSerializer(serializers.ModelSerializer):
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)
    class Meta:
        model = Task
        fields = ['id','title','description','assigned_to','assigned_to_username','due_date','status','completion_report','worked_hours','created_at','updated_at']
        read_only_fields = ['completion_report','worked_hours','created_at','updated_at']

class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["title", "description", "assigned_to", "due_date", "status"]
        read_only_fields = ["status"] 


# Serializer for marking completed (partial update)
class TaskCompleteSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['completed'])
    completion_report = serializers.CharField()
    worked_hours = serializers.DecimalField(max_digits=6, decimal_places=2)