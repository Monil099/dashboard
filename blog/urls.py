from django.urls import path
from .views import CreateBlogPostView, BlogListView, BlogByIdView, BlogDeleteView

urlpatterns = [
    path('new/', CreateBlogPostView.as_view(), name='blog_new'),
    path('', BlogListView.as_view(), name='blog_list'),
    path('<int:blog_id>', BlogByIdView.as_view(), name='blog_get'),
    path('delete/<int:pk>', BlogDeleteView.as_view(), name='blog_delete'),
]
