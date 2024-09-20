from django.shortcuts import render, redirect
import requests
import base64
from django.contrib.auth.decorators import login_required
from wp_site.models import WpSite

def create_blog_post(request):
    if request.method == 'POST':


        breakpoint()
        title = request.POST["title"]
        content = request.POST['content']
        status = request.POST['status']
        featured_image = request.FILES['featured-image']
        sites = request.POST.getlist('site')

        for site in sites:
            site1 = WpSite.objects.filter(id=int(site)).first()
            wordpress_url = site1.url
            wordpress_user = site1.wp_username
            wordpress_password = site1.wp_password
            wordpress_credentials = f"{wordpress_user} : {wordpress_password}"
            wordpress_token = base64.b64encode(wordpress_credentials.encode())
            wordpress_header = {'Authorization': 'Basic ' + wordpress_token.decode('utf-8')}


            wp_api_media_url = f'{wordpress_url}/wp-json/wp/v2/media'

            media_response = requests.post(wp_api_media_url, headers=wordpress_header, files={'file': featured_image})
            featured_image_id = None
            if media_response.status_code == 201:
                media_json = media_response.json()
                featured_image_id = media_json['id']

            api_url = f'{wordpress_url}/wp-json/wp/v2/posts'
            data = {
            'title' : title,
            'status': status,
            'slug' : 'example-post',
            'content': content,
            'featured_media': featured_image_id
            }
            response = requests.post(api_url,headers=wordpress_header, json=data)
            print(response)
            print(response.json()['guid'])
            breakpoint()
        form = "BlogPostForm(request.POST)"
        if form.is_valid():
            form.save()
            return redirect('blog_list')
    else:
        form = "BlogPostForm()"

    _site = WpSite.objects.all().values("id","name")

    return render(request, 'blogs.html', {'form': form, 'sites': _site})

# def blog_list(request):
#     blogs = BlogPost.objects.all()
#     return render(request, 'blog/blog_list.html', {'blogs': blogs})
