from django.shortcuts import render, redirect
import requests
import base64
from django.contrib.auth.decorators import login_required

def create_blog_post(request):
    if request.method == 'POST':

        wordpress_user = "meetbhingradiya57@gmail.com"
        wordpress_password = "NC3Q Oqwu tc8o XN82 4Yz6 FATW"
        wordpress_credentials = f"{wordpress_user} : {wordpress_password}"
        wordpress_token = base64.b64encode(wordpress_credentials.encode())
        wordpress_header = {'Authorization': 'Basic ' + wordpress_token.decode('utf-8')}

        title = request.POST["title"]
        content = request.POST['content']
        status = request.POST['status']
        # status = request.POST["featured-image"]
        api_url = 'https://darkslateblue-capybara-608439.hostingersite.com/wp-json/wp/v2/posts'
        data = {
        'title' : title,
        'status': status,
        'slug' : 'example-post',
        'content': content,
        'featured_media': 207
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

    return render(request, 'blogs.html', {'form': form})
    # return render(request, 'blogs.html', {'form': form})

# def blog_list(request):
#     blogs = BlogPost.objects.all()
#     return render(request, 'blog/blog_list.html', {'blogs': blogs})
