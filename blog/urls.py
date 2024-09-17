from django.urls import path
from blog.views import create_blog_post

urlpatterns = [
    path('new/', create_blog_post, name='blog-create'),
    # path('upload-featured-image/', upload_featured_image, name='upload_featured_image'),

]
