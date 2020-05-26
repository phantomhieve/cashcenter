from djongo import models
from django.contrib.auth.models import User

class UserGroup(models.Model):
    primary_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='primary_user', null=True)
    main_user    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='main_user', null=True)
    shop         = models.CharField(max_length=50)