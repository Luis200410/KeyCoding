from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    LANG_CHOICES = [
        ('python','Python'), ('javascript','JavaScript'), ('typescript','TypeScript'), ('java','Java'),
        ('csharp','C#'), ('cpp','C++'), ('go','Go'), ('rust','Rust'), ('php','PHP'), ('ruby','Ruby'),
        ('swift','Swift'), ('kotlin','Kotlin'), ('scala','Scala'), ('dart','Dart'), ('r','R'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    avatar = models.FileField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    company = models.CharField(max_length=150, blank=True)
    job_title = models.CharField(max_length=150, blank=True)
    location = models.CharField(max_length=150, blank=True)
    website = models.URLField(blank=True)
    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    primary_language = models.CharField(max_length=32, choices=LANG_CHOICES, blank=True)
    interests = models.TextField(blank=True)

    def __str__(self):
        return f"Profile({self.user.username})"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

