from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, TherapistSerializer, BlogCategorySerializer, BlogSerializer, NewsSerializer, BookingSerializer, UserSignupSerializer, CalculatorDetailSerializer, CalculatorListSerializer, UserLatestScoreSerializer, SaveCalculatorScoreSerializer
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model  
from .models import User, BlogsCategories, Blogs, News, Bookings, Calculators, CalculatorScores
from rest_framework import  pagination
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from django.db.models import OuterRef, Subquery





from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
from rest_framework.decorators import api_view
from django.middleware.csrf import get_token
import uuid
import time
from rest_framework.response import Response

model_name = "facebook/blenderbot-400M-distill"
tokenizer = BlenderbotTokenizer.from_pretrained(model_name)
model = BlenderbotForConditionalGeneration.from_pretrained(model_name)
session_data = {}

# Remove inactive sessions (e.g., after 10 minutes)
SESSION_TIMEOUT = 10 * 60  # 10 minutes in seconds

def cleanup_sessions():
    """Delete inactive sessions to free up memory."""
    current_time = time.time()
    inactive_sessions = [sid for sid, data in session_data.items() if (current_time - data["last_active"]) > SESSION_TIMEOUT]
    
    for sid in inactive_sessions:
        del session_data[sid]  # Remove inactive session

@api_view(['POST'])
def chatbot_response(request):
    cleanup_sessions()  # Run cleanup before processing request

    session_id = request.data.get("session_id", str(uuid.uuid4()))
    user_input = request.data.get("message", "")

    if not user_input:
        return Response({"error": "No message provided"}, status=400)

    # Retrieve session history or create a new one
    if session_id not in session_data:
        session_data[session_id] = {"history": [], "last_active": time.time()}

    session_data[session_id]["history"].append({"role": "user", "message": user_input})

    # Generate chatbot response
    inputs = tokenizer([user_input], return_tensors="pt")
    reply_ids = model.generate(**inputs)
    response_text = tokenizer.batch_decode(reply_ids, skip_special_tokens=True)[0]

    session_data[session_id]["history"].append({"role": "bot", "message": response_text})
    session_data[session_id]["last_active"] = time.time()  # Update last active time

    return Response({
        "session_id": session_id,
        "response": response_text
    })


User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)  # Call parent method

        refresh_token = response.data.pop("refresh", None)  # Remove refresh from JSON response
        
        if refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,  # Secure against JavaScript access
                secure=False,  # Set to True in production (HTTPS required)
                samesite="Lax",
                path="/api/token/refresh/"  # Ensure cookie is accessible for refresh
            )

        return response

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            raise AuthenticationFailed("Refresh token not found in cookies.")

        request.data["refresh"] = refresh_token  # Inject token into request body
        return super().post(request, *args, **kwargs)
    
class UserSignupView(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = [AllowAny]  # Anyone can register

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)  # Call parent create method
        user = self.get_queryset().get(id=response.data["user"]["id"])  # Get created user

        # Generate refresh token
        refresh = RefreshToken.for_user(user)

        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,  # Secure against JS access
            secure=False,  # Set to True in production (HTTPS required)
            samesite="Lax",
            path="/api/token/refresh/"
        )

        return response
    
class TherapistListView(ListAPIView):
    queryset = User.objects.filter(role='therapist')  # Fetch only therapists
    serializer_class = TherapistSerializer
    permission_classes = [AllowAny]  # Allow anyone to access the endpoint
    

# Get all categories
class BlogCategoryListView(ListAPIView):
    queryset = BlogsCategories.objects.all()
    serializer_class = BlogCategorySerializer

# Custom pagination for 12 blogs per page
class BlogPagination(pagination.PageNumberPagination):
    page_size = 12

# Get 12 blogs of a specific category with pagination
class BlogsByCategoryView(ListAPIView):
    serializer_class = BlogSerializer
    pagination_class = BlogPagination

    # def get_queryset(self):
    #     category_name = self.kwargs['category_name']
    #     print("category_name")
    #     print(category_name)
    #     category_id = BlogsCategories.objects.get(name=category_name).id
    #     blogs = Blogs.objects.filter(category_id=category_id).order_by('-created_at')
    #     return blogs
    def get_queryset(self):
        category_name = self.kwargs.get('category_name', None)
        print("Received category_name:", category_name)  # Debugging print

        if category_name is None:
            raise ValueError("Category name is None")  # This will help detect if it's missing

        try:
            category = BlogsCategories.objects.get(name__iexact=category_name.strip())
            print("Found category:", category)  # Debugging print
        except BlogsCategories.DoesNotExist:
            print("Category not found in DB")  # Debugging print
            raise  # Re-raise the exception to see the full error

        blogs = Blogs.objects.filter(category_id=category.id).order_by('-created_at')
        return blogs
    
class BlogView(ListAPIView):
    serializer_class = BlogSerializer
    
    def get_queryset(self):
        category_name = self.kwargs["category"]
        category_id = BlogsCategories.objects.get(name=category_name)
        blog_name = self.kwargs["blog"]
        blog = Blogs.objects.filter(category=category_id, title=blog_name)
        return blog

# Get latest 4 blogs
class LatestBlogsView(ListAPIView):
    serializer_class = BlogSerializer

    def get_queryset(self):
        return Blogs.objects.order_by('-created_at')[:4]
    

class LatestNewsListView(ListAPIView):
    queryset = News.objects.order_by('-created_at')[:4]  # Get the latest 4 news
    serializer_class = NewsSerializer
    
class UserBookingsListCreateView(ListCreateAPIView):
    """Allows users to get their bookings and create new bookings"""
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Bookings.objects.filter(user=self.request.user).select_related('therapist')

    def perform_create(self, serializer):
        """Automatically assigns the logged-in user as the patient when creating a booking"""
        serializer.save(user=self.request.user)
        

# 1. List all calculators
class CalculatorListView(ListAPIView):
    queryset = Calculators.objects.all()
    serializer_class = CalculatorListSerializer

# 2. Get all details of a specific calculator (including questions & results)
class CalculatorDetailView(RetrieveAPIView):
    serializer_class = CalculatorDetailSerializer
    lookup_field = "name"
    
    def get_queryset(self):
        return Calculators.objects.prefetch_related("calculator_questions", "calculator_results")

# 3. Get latest scores per calculator for the authenticated user
class UserLatestScoresView(ListAPIView):
    serializer_class = UserLatestScoreSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        latest_scores = CalculatorScores.objects.filter(
            user=user,
            created_at=Subquery(
                CalculatorScores.objects.filter(
                    user=user,
                    calculator=OuterRef("calculator")
                )
                .order_by("-created_at")
                .values("created_at")[:1]  # Get latest created_at per calculator
            )
        )

        return latest_scores

# 4. Save user's calculator score
class SaveCalculatorScoreView(CreateAPIView):
    serializer_class = SaveCalculatorScoreSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        calculator_name = serializer.validated_data["calculator_name"]
        score = serializer.validated_data["score"]

        calculator = get_object_or_404(Calculators, name=calculator_name)

        # Save score
        CalculatorScores.objects.create(user=user, calculator=calculator, score=score)

        return Response({"message": "Score saved successfully"}, status=status.HTTP_201_CREATED)