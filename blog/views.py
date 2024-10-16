from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from rest_framework import views
from django.views.generic import CreateView, ListView, UpdateView
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from .models import WpBlog, WpSite, WpBlogSite
import base64
import requests
from blog.categories import categories_list
from django.utils.text import slugify
from datetime import datetime


def home_view(request):
    return render(request, 'blog_list.html')

class CreateBlogPostView(LoginRequiredMixin, CreateView):
    model = WpBlog
    template_name = 'blog_upload.html'
    fields = ['title', 'content', 'status']  # Define fields for the form

    def get_context_data(self, **kwargs):
        # Add additional context (like available sites) to the template
        context = super().get_context_data(**kwargs)
        context['sites'] = WpSite.objects.all().values("id", "name")
        return context

    def form_valid(self, form):
        user = self.request.user
        form.instance.created_by = user
        form.instance.updated_by = user
        self.object = form.save()  # Save the blog post to the database
        sites = self.request.POST.getlist('sites')
        categories = self.request.POST.get("categories")
        category_id = None
        for category, id in categories_list.items():
            if category == categories:
                category_id = id
        result = {}
        for site_id in sites:
            site = WpSite.objects.filter(id=int(site_id)).first()

            # Make the request to the WordPress site
            wordpress_url = site.url
            wordpress_user = site.wp_username
            wordpress_password = site.wp_password
            wordpress_credentials = f"{wordpress_user}:{wordpress_password}"
            wordpress_token = base64.b64encode(wordpress_credentials.encode())
            wordpress_header = {'Authorization': 'Basic ' + wordpress_token.decode('utf-8')}
            post_date = datetime.now().isoformat()

            api_url = f'{wordpress_url}/wp-json/wp/v2/posts'
            data = {
                'title': form.cleaned_data['title'],
                'status': form.cleaned_data['status'],
                'content': form.cleaned_data['content'],
                "categories": category_id,
                'slug': slugify(form.cleaned_data['title']),
                'date': post_date
            }

            response = requests.post(api_url, headers=wordpress_header, json=data)

            # Handle the response and update the result context
            if response.status_code != 201:
                result = {"msg-error": f"Failed to upload blog to {wordpress_url}"}

            else:
                blog_json = response.json()
                wp_blog_id = blog_json["id"]
                wp_blog_url = blog_json['guid']['rendered']
                result = {"msg": f"Successfully uploaded blog to {wordpress_url}", "url": wp_blog_url}
                # Save the relationship between the blog and the sites
                WpBlogSite.objects.get_or_create(blog=self.object, site_id=int(site_id), wp_blog_id=wp_blog_id)

        return self.render_to_response(self.get_context_data(form=form, result=result))


class BlogListView(ListView):
    model = WpBlog
    template_name = 'blog_list.html'
    context_object_name = 'blogs'

    def get_queryset(self):
        # Use prefetch_related to fetch related site names efficiently
        return WpBlog.objects.prefetch_related('wpblogsite_set__site').order_by('-id').all()


class BlogByIdView(LoginRequiredMixin, View):
    def get(self, request, blog_id, *args, **kwargs):
        # Fetch the blog post by its ID
        blog = get_object_or_404(WpBlog, id=blog_id)
        
        sites = WpSite.objects.all().values("id", "name")
        selected_sites = list(WpBlogSite.objects.filter(blog_id=blog_id).values_list("site__id", flat=True))

        # Return the blog details as a context for a template
        return render(request, 'blog_detail.html', {'blog': blog, 'sites': sites, 'selected_sites': selected_sites})

class BlogUpdateView(views.View):
    def post(self, request, pk, *args, **kwargs):
        user = self.request.user
        blog = get_object_or_404(WpBlog, id=int(pk))
        title = request.POST.get('title', blog.title)
        content = request.POST.get('content', blog.content)
        status = request.POST.get('status', blog.status)

        # Update the blog locally
        blog.title = title
        blog.content = content
        blog.status = status
        blog.updated_by = user
        blog.save()

        sites = self.request.POST.getlist('sites')  # Get the selected sites from the form
        result = {}  # To store the result of each site's response

        for site_id in sites:
            site = get_object_or_404(WpSite, id=int(site_id))  # Fetch the site
            wordpress_url = site.url
            wordpress_user = site.wp_username
            wordpress_password = site.wp_password
            wordpress_credentials = f"{wordpress_user}:{wordpress_password}"
            wordpress_token = base64.b64encode(wordpress_credentials.encode())
            wordpress_header = {'Authorization': 'Basic ' + wordpress_token.decode('utf-8')}

            # Get the blog-site relationship
            blog_site, created = WpBlogSite.objects.get_or_create(blog=blog, site=site)
            wordpress_post_id = blog_site.wp_blog_id

            # Prepare the categories (Assuming you have a categories list in your form)
            categories = self.request.POST.get("categories")
            category_id = None
            for category, id in categories_list.items():
                if category == categories:
                    category_id = id

            # Prepare the data for WordPress API request
            api_url = f'{wordpress_url}/wp-json/wp/v2/posts/{wordpress_post_id}'
            data = {
                'title': title,
                'status': status,
                'content': content,
                "categories": category_id,
                'slug': slugify(title),
            }

            # Make the request to the WordPress site
            response = requests.post(api_url, headers=wordpress_header, json=data)

            # Handle the response and update the result context
            if response.status_code != 200:
                result[site_id] = {"msg-error": f"Failed to upload blog to {wordpress_url}"}
            else:
                blog_json = response.json()
                wp_blog_id = blog_json["id"]
                wp_blog_url = blog_json['guid']['rendered']
                result[site_id] = {"msg": f"Successfully uploaded blog to {wordpress_url}", "url": wp_blog_url}
                # Update the wp_blog_id in case it's newly created
                blog_site.wp_blog_id = wp_blog_id
                blog_site.save()

        # Pass the result to the context and redirect
        self.request.session['result'] = result  # Store the result in session for display
        return redirect('blog_list')  # Redirect to the detail page or another view



class BlogDeleteView(views.View):
    def get(self, request, pk, *args, **kwargs):
        blog  = get_object_or_404(WpBlog, id=pk)
        result = {}

        if blog:
            wp_sites = WpBlogSite.objects.filter(blog=blog).all()
            for wp_site in wp_sites:
                # Make the request to the WordPress site
                wordpress_blog_id = wp_site.wp_blog_id
                wordpress_url = wp_site.site.url
                wordpress_user = wp_site.site.wp_username
                wordpress_password = wp_site.site.wp_password
                wordpress_credentials = f"{wordpress_user}:{wordpress_password}"
                wordpress_token = base64.b64encode(wordpress_credentials.encode())
                wordpress_header = {'Authorization': 'Basic ' + wordpress_token.decode('utf-8')}

                api_url = f'{wordpress_url}/wp-json/wp/v2/posts/{wordpress_blog_id}'

                response = requests.delete(api_url, headers=wordpress_header)

                wp_site.delete()

                # Handle the response and update the result context
                if response.status_code != 200:
                    result = {"msg-error": f"Failed to delete blog to {wordpress_url}"}
                else:
                    result = {"msg": "Successfully blog deleted"}
        blog.delete()
        return redirect('blog_list')