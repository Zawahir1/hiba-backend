from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import BlogsCategories, Blogs, BlogImages, News, Bookings,Calculators, CalculatorQuestions, CalculatorResults, CalculatorScores
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)  # Get the original token response

        user = self.user  # Get user instance
        data.update({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": getattr(user, "phone", None),  # Prevents AttributeError if 'phone' isn't present
            "first_name": user.first_name,
            "last_name": user.last_name,
        })

        return data
    
class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "email", "phone", "role", "password", "first_name", "last_name"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)  # Hash password
        user.save()
        return user

    def to_representation(self, instance):
        """Customize response to include tokens"""
        refresh = RefreshToken.for_user(instance)
        return {
            "user": {
                "id": instance.id,
                "username": instance.username,
                "email": instance.email,
                "phone": instance.phone,
                "role": instance.role,
                "first_name": instance.first_name,
                "last_name": instance.last_name,
            },
            "access": str(refresh.access_token),
        }

    
class TherapistSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'role',
            'therapist_expertise', 'therapist_experience',
            'therapist_description', 'therapist_img',
            'therapist_popUp', 'therapist_fee', "first_name", "last_name"
        ]


class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogsCategories
        fields = '__all__'

class BlogImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogImages
        fields = '__all__'


class BlogsTherapistSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',  'role',
            'therapist_expertise', 'therapist_experience',
             'therapist_img',
             'therapist_fee', "first_name", "last_name"
        ]
class BlogSerializer(serializers.ModelSerializer):
    category = BlogCategorySerializer(read_only=True)
    images = BlogImageSerializer(source='blogimages_set', many=True, read_only=True)
    owner = BlogsTherapistSerializer(read_only=True)  # Use the nested UserSerializer


    class Meta:
        model = Blogs
        fields = ['id', 'category', 'title', 'content', 'created_at', 'owner', 'images']
        
class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'
        

class UserSerializer(serializers.ModelSerializer):
    """Serializer to return full therapist details"""
    class Meta:
        model = User
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    therapist = UserSerializer(read_only=True)  # For GET request
    therapist_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="therapist"),
        source="therapist",
        write_only=True
    )  # Allow therapist selection in POST request

    class Meta:
        model = Bookings
        fields = ['id', 'user', 'therapist', 'therapist_id', 'date', 'time', 'created_at', 'status', "payment_method", "paid"]
        extra_kwargs = {
            'user': {'read_only': True},  # User should be auto-set from the request
            'created_at': {'read_only': True},
            'status': {'read_only': True}  # Default is 'pending'
        }
        
# For listing all calculators
class CalculatorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calculators
        fields = ["name", "desc", "img"]  # Only these fields

# For detailed calculator view
class CalculatorQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalculatorQuestions
        fields = "__all__"

class CalculatorResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalculatorResults
        fields = ["min", "max", "result"]

class CalculatorDetailSerializer(serializers.ModelSerializer):
    calculator_questions = CalculatorQuestionSerializer(many=True, read_only=True)
    calculator_results = CalculatorResultSerializer(many=True, read_only=True)

    class Meta:
        model = Calculators
        fields = "__all__"  # Include all fields in response

# For user scores
class UserLatestScoreSerializer(serializers.ModelSerializer):
    calculator_name = serializers.CharField(source="calculator.name")

    class Meta:
        model = CalculatorScores
        fields = ["calculator_name", "score", "created_at"]

# For saving user scores
class SaveCalculatorScoreSerializer(serializers.Serializer):
    calculator_name = serializers.CharField()
    score = serializers.IntegerField()