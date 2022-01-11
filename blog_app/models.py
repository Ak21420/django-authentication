from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from PIL import Image


class PostManager(models.Manager):
    def like_toggle(self, user, post_obj):
        if user in post_obj.liked.all():
            is_liked = False
            post_obj.liked.remove(user)
        else:
            is_liked = True
            post_obj.liked.add(user)
        return is_liked


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    liked = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='liked')
    date_posted = models.DateTimeField(default=timezone.now)
    delete_status = models.BooleanField(default=False, null=True)
    private = models.BooleanField(default=False, null=True)

    objects = PostManager()

    class Meta:
        ordering = ('-date_posted', )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})

    # def save(self, *args, **kwargs):
    #     super(Post, self).save(*args, **kwargs)

    #     img = Image.open(self.image.path)

    #     if img.height > 300 or img.width > 300:
    #         output_size = (300, 300)
    #         img.thumbnail(output_size)
    #         img.save(self.image.path)


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=True)

    def approve(self):
        self.approved_comment = True
        self.save()

    def get_absolute_url(self):
        return reverse("post_list")

    def __str__(self):
        return self.author


# Create your models here.
# class Post(models.Model):
#     title = models.CharField(max_length=255)
#     author = models.ForeignKey(User, on_delete=models.CASCADE)
#     content = models.TextField()
#     image_file = models.FileField(upload_to='images/', null=True)
#     delete_status = models.BooleanField(blank=True, null=True)
#     created_user_id = models.CharField(max_length=100)
#     created_at = models.DateTimeField(blank=True, null=True)
#     updated_user_id = models.CharField(max_length=100)
#     updated_at = models.DateTimeField(blank=True, null=True)

#     def __str__(self):
#         return self.title + ' | ' + str(self.author)