from django.db import models
from django.contrib.auth.models import User

class UserGroup(models.Model):
    primary_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='primary_user', null=True)
    main_user    = models.OneToOneField(User, on_delete=models.CASCADE, related_name='main_user', null=True)
    shop         = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.primary_user}/{self.main_user}-\
            {self.shop}"