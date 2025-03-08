from django.contrib import admin
from django.utils.html import format_html
from .models import User, BlogsCategories, Blogs, BlogImages, News, Bookings, Calculators, CalculatorResults, CalculatorQuestions

# Customizing User Admin
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone', 'role', 'therapist_expertise', 'therapist_experience')
    list_filter = ('role',)
    search_fields = ('username', 'email', 'phone')

# Blog Categories Admin
@admin.register(BlogsCategories)
class BlogsCategoriesAdmin(admin.ModelAdmin):
    list_display = ('name', "description", 'category_image')
    search_fields = ('name',)  # Add this line


    def category_image(self, obj):
        if obj.img:
            return format_html('<img src="{}" width="50" height="50" />'.format(obj.img.url))
        return "-"

# Blogs Admin
@admin.register(Blogs)
class BlogsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'owner', 'created_at')
    list_filter = ('category', 'owner')
    
    search_fields = ('title', 'content')
    autocomplete_fields = ('owner', 'category')

# Blog Images Admin
@admin.register(BlogImages)
class BlogImagesAdmin(admin.ModelAdmin):
    list_display = ('blog', 'blog_image')

    def blog_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />'.format(obj.image.url))
        return "-"

# News Admin
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'content')

# Bookings Admin
@admin.register(Bookings)
class BookingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'therapist', 'date', 'time', 'status', 'created_at')
    list_filter = ('status', 'date')
    search_fields = ('user__username', 'therapist__username')
    autocomplete_fields = ('user', 'therapist')

@admin.register(Calculators)
class CalculatorAdmin(admin.ModelAdmin):
    list_display = ("name", "desc", "scoring_name", "leveling_name")
    search_fields = ("name", "desc")
    list_filter = ("scoring_name", "leveling_name")
    ordering = ("name",)

# Customizing Foreign Key Display for CalculatorQuestions
class CalculatorQuestionsAdmin(admin.ModelAdmin):
    list_display = ("question", "calculator_name_display")  # Display calculator name
    search_fields = ("question", "calculator__name")
    
    def calculator_name_display(self, obj):
        return obj.calculator.name
    calculator_name_display.short_description = "Calculator"

# Customizing Foreign Key Display for CalculatorResults
class CalculatorResultsAdmin(admin.ModelAdmin):
    list_display = ("min", "max", "result", "calculator_name_display")
    search_fields = ("result", "calculator__name")
    
    def calculator_name_display(self, obj):
        return obj.calculator.name
    calculator_name_display.short_description = "Calculator"

# Registering models with their custom admin classes
admin.site.register(CalculatorQuestions, CalculatorQuestionsAdmin)
admin.site.register(CalculatorResults, CalculatorResultsAdmin)