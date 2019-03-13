from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return 'Profile for user {}'.format(self.user.username)

    class Meta:
        db_table = 'profiles'
