from typing import Tuple
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# Create your models here.

class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password):
        if not email:
            raise ValueError('User must have an email address')
        if not username:
            raise ValueError('User must have an username')
        
        user = self.model(
            email = self.normalize_email(email),
            username = email,
            first_name = first_name,
            last_name = last_name 
        )

        user.set_password(password)
        user.save(using=self._db)
        user.is_active = True
        return user 

    def create_superuser(self, first_name, last_name, email, username, password):
        user = self.create_user(
            first_name,
            last_name,
            username, 
            self.normalize_email(email), 
            password
        )

        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_supperadmin = True
        user.save(using=self._db)
        return user

class Account(AbstractBaseUser):
    first_name = models.CharField('Primeiro nome', max_length=50)
    last_name = models.CharField('Último nome', max_length=50)
    username = models.CharField('Nome de usuário', max_length=50, unique=True)
    email = models.EmailField(max_length=50, unique=True)
    phone_number = models.CharField('Número de telefone', max_length=50)


    #required
    date_joined = models.DateTimeField(auto_now_add=True)
    last_join = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager()

    def __str__(self) -> str:
        return self.email

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True
