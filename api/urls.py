from django.urls import path
from .views import CustomTokenObtainPairView, chatbot_response, TherapistListView, BlogCategoryListView, BlogsByCategoryView,BlogView, LatestBlogsView, LatestNewsListView, UserBookingsListCreateView, CustomTokenRefreshView, UserSignupView, CalculatorDetailView, CalculatorListView, UserLatestScoresView, SaveCalculatorScoreView
from . import views

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
        path("signup/", UserSignupView.as_view(), name="signup"),

    path('therapists/', TherapistListView.as_view(), name='therapists'),
        path('categories/', BlogCategoryListView.as_view(), name='categories'),
    path('blogs/category/<str:category_name>/', BlogsByCategoryView.as_view(), name='blogs_by_category'),
    path('blogs/<str:category>/<str:blog>', BlogView.as_view(), name="blog"),
    path('blogs/latest/', LatestBlogsView.as_view(), name='latest_blogs'),
    path('news/latest/', LatestNewsListView.as_view(), name='latest_news'),
    path('bookings/', UserBookingsListCreateView.as_view(), name='user_bookings'),
    path("calculators/", CalculatorListView.as_view(), name="calculator-list"),
    path("calculators/<str:name>/", CalculatorDetailView.as_view(), name="calculator-detail"),
    path("user/scores/", UserLatestScoresView.as_view(), name="user-latest-scores"),
    path("save-score/", SaveCalculatorScoreView.as_view(), name="save-calculator-score"),
    path("chatbot/", chatbot_response, name="chatbot_response"),

        
]