from django.urls import path
from blog.views import CreateBlogPostView, BlogListView, BlogByIdView, BlogDeleteView, home_view

urlpatterns = [
    # path('', home_view, name='home'),
    path('blog/new/', CreateBlogPostView.as_view(), name='blog_new'),
    path('', BlogListView.as_view(), name='blog_list'),
    path('blog/<int:blog_id>', BlogByIdView.as_view(), name='blog_get'),
    path('blog/delete/<int:pk>', BlogDeleteView.as_view(), name='blog_delete'),
]
