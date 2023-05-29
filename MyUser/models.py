from django.contrib.auth import get_user_model
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db import models
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "MyUserManager.create_user: email is None")
            raise ValueError('Users must have an email address.')

        user = self.model(**kwargs)
        email = self.normalize_email(email)
        user.email = email
        user.set_password(password)
        user.save(using=self._db)
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"MyUserManager.create_user: user created = {user}")
        return user

    def create_superuser(self, email, password, **kwargs):
        u = self.create_user(email, password, **kwargs)
        u.is_admin = True
        u.is_active = True
        u.save(using=self._db)
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"MyUserManager.create_superuser: superuser created = {u}")
        return u


class MyUser(AbstractBaseUser):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=255, unique=True)
    credit = models.IntegerField(default=1)
    rooyesh = models.IntegerField(default=3)
    post_address = models.CharField(max_length=100, default='', blank=True)
    phone_number = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_vip = models.BooleanField(default=False)
    vip_end_date = models.DateTimeField(blank=True, null=True)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone_number']

    def update_vip_status(self):
        if self.vip_end_date is None:
            return
        if self.vip_end_date < timezone.now():
            self.is_vip = False
            self.save(update_fields=['is_vip'])
            logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"MyUser.update_vip_status: user vip status updated = {self}")

    def is_user_vip(self):
        if self.vip_end_date is None:
            return False
        self.update_vip_status()
        return self.is_vip

    def set_vip(self, days):
        self.vip_end_date = timezone.now() + timezone.timedelta(days=days)
        self.is_vip = True
        self.save(update_fields=['vip_end_date', 'is_vip'])
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"MyUser.set_vip: user {self} vip status updated, vip_end_date = {self.vip_end_date}")

    @property
    def is_staff(self):
        return self.is_admin

    def change_credit(self, value):
        self.credit = max(self.credit + int(value), 1)
        self.save(update_fields=['credit'])
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"MyUser.change_credit: user {self} credit updated, credit = {self.credit}")
        return self.credit

    def change_rooyesh(self, value):
        self.rooyesh = max(self.rooyesh + int(value), 0)
        self.save(update_fields=['rooyesh'])
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"MyUser.change_rooyesh: user {self} rooyesh updated, rooyesh = {self.rooyesh}")
        return self.rooyesh
    
    def __str__(self):
        return self.email


class EmailToken(models.Model):
    token = models.CharField(max_length=30)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

