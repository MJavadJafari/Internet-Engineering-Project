from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db import models


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have an email address.')

        user = self.model(**kwargs)
        email = self.normalize_email(email)
        user.email = email
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **kwargs):
        u = self.create_user(email, password, **kwargs)
        u.is_admin = True
        u.is_active = True
        u.save(using=self._db)
        return u


class MyUser(AbstractBaseUser):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=255, unique=True)
    credit = models.IntegerField(default=0)
    rooyesh = models.IntegerField(default=3)
    biography = models.CharField(max_length=1003, default='', blank=True)
    picture = models.ImageField(upload_to='user/profile/', blank=True)

    phone_number = models.CharField(max_length=50)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone_number']

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def change_credit(self, value):
        self.credit = max(self.credit + int(value), 0)
        self.save(update_fields=['credit'])
        return self.credit

    def change_rooyesh(self, value):
        self.rooyesh = max(self.rooyesh + int(value), 0)
        self.save(update_fields=['credit'])
        return self.rooyesh
