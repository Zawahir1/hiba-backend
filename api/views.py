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

    def get_queryset(self):
        category_name = self.kwargs['category_name']
        category_id = BlogsCategories.objects.get(name=category_name).id
        blogs = Blogs.objects.filter(category_id=category_id).order_by('-created_at')
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