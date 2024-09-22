from django.db import models
from wp_site.models import WpSite
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class WpBlog(models.Model):
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blogs_created')  # Unique related_name for create_by
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blogs_updated') # Unique related_name for updated_by
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class WpBlogSite(models.Model):
    blog = models.ForeignKey(WpBlog, on_delete=models.CASCADE)
    site = models.ForeignKey(WpSite, on_delete=models.CASCADE)
    wp_blog_id = models.BigIntegerField()
