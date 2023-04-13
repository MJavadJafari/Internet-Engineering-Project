from django.db import models

# Create your models here.


class Transaction(models.Model):
    # days: price
    VIP_OPTIONS = {
        7: 10000,
        30: 35000,
        90: 75000,
        180: 120000,
        365: 200000,
    }

    PENDING = 'pending'
    SUCCESS = 'success'
    FAILED = 'failed'
    STATUS_CHOICES = (
        (PENDING, 'pending'),
        (SUCCESS, 'success'),
        (FAILED, 'failed'),
    )

    transaction_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('MyUser.MyUser', on_delete=models.CASCADE)
    tracking_code = models.CharField(max_length=100, null=True)
    amount = models.IntegerField()
    vip_duration = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)


    def __str__(self):
        return str(self.transaction_id)
