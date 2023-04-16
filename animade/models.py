from django.contrib.auth.models import User
from django.db import models

from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    email_plaintext_message = "{}?token={}".format(reverse('password_reset:reset-password-request'), reset_password_token.key)

    send_mail(
        # title:
        "Password Reset for {title}".format(title="Some website title"),
        # message:
        email_plaintext_message,
        # from:
        "noreply@somehost.local",
        # to:
        [reset_password_token.user.email]
    )

class Profile(models.Model):
    class PlanLevel(models.TextChoices):
        FREE = 'Free', 'Free'
        BASIC = 'Basic', 'Basic'
        STANDARD = 'Standard', 'Standard'
        PREMIUM = 'Premium', 'Premium'
        UNLIMITED = 'Unlimited', 'Unlimited'

    user = models.OneToOneField(User , null= True ,on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(default=None, blank=True, null=True, upload_to="images/", max_length=1000)
    address = models.CharField(max_length=255, default=None, null=True, blank=True)
    pro_status = models.BooleanField(default=False)
    pro_code = models.IntegerField(default=0)
    numberdesigns = models.IntegerField(default=0)
    paymentvertfication = models.BooleanField(default=False)
    trial_status = models.CharField(max_length = 10, choices = PlanLevel.choices, default=PlanLevel.FREE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

    def can_create_design(self):
        """
        Check if the user can create a new design based on their plan level.
        """
        if self.trial_status == self.PlanLevel.FREE:
            return self.numberdesigns < 30
        elif self.trial_status == self.PlanLevel.BASIC:
            return self.numberdesigns < 100
        elif self.trial_status == self.PlanLevel.STANDARD:
            return self.numberdesigns < 500
        elif self.trial_status == self.PlanLevel.PREMIUM:
            return self.numberdesigns < 1250
        elif self.trial_status == self.PlanLevel.UNLIMITED:
            return True
        else:
            return False


# show how we want it to be displayed
class CreatedDesign(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    desc = models.TextField()
    number = models.IntegerField()
    image = models.CharField(max_length=1000)

    def __str__(self):
      return str(self.id)
    
    def clean(self):
        """
        Check if the user can create a new design before saving it.
        """
        if not self.user.profile.can_create_design():
            raise ValidationError("You have reached the maximum number of designs for your plan level.")


class SavedDesign(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    design = models.ForeignKey(CreatedDesign, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "design",)

    def __str__(self):
        return f"{self.user.first_name} - {self.status}"