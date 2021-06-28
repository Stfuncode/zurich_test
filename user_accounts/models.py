from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models.deletion import CASCADE
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator, MaxValueValidator


class CustomUserManager(BaseUserManager):
    
    use_in_migrations = True
    
    def create_user(self,username, email, identity_number, password):

        if not email:
            raise ValueError(_('The Email must be set'))
        
        email = self.normalize_email(email)
        user = self.model(
            username = username,
            email=email, 
            identity_number=identity_number,
            password=password,
        )      
        user.is_staff = True
        user.is_superuser = False
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, identity_number, password):
        user = self.create_user(
            username = username ,
            email=self.normalize_email(email),
            identity_number=identity_number,
            password=password,
        )
        
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    
# Create your models here.
class Register(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, default="")
    identity_number = models.CharField(default="", max_length=14)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','identity_number']

    objects = CustomUserManager()
    
    def __str__(self):
        return self.name

class PolicyDetails(models.Model):
    policy_number = models.CharField(primary_key=True, max_length=20, verbose_name=u'Policy Number')
    policy_status = models.CharField(max_length=20, verbose_name=u'Policy Status')
    insured_name = models.CharField(max_length=200, validators=[RegexValidator('^[A-Z_]*$',
                               'Only uppercase letters and underscores allowed.')], verbose_name=u'Insured Name')
    basic_product = models.CharField(max_length=5, verbose_name=u'Basic Product')
    request_date = models.DateField(auto_now=False, verbose_name=u'Requested Date')

class UserPolicy(models.Model):
    user_id = models.ForeignKey(Register, on_delete=CASCADE)
    policy_details = models.ForeignKey(PolicyDetails, to_field='policy_number', on_delete=CASCADE)

    def __str__(self):
        return str(self.policy_details)
    
class NomineeDetails(models.Model):
    RELATIONSHIP = [
        ('Please Select','Please Select'),
        ('Parent', 'Parent'),
        ('Child', 'Child'),
        ('Sibling', 'Sibling'),
        ('Grandparent', 'Grandparent'),
        ('GrandChild', 'GrandChild'),
    ]
    
    GENDER = [
        ('Please Select','Please Select'),
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    
    NOMINATION = [
        ('Please Select','Please Select'),
        ('A','A'),
        ('B','B'),
        ('C','C'),
    ]
    
    user_policy = models.ForeignKey(UserPolicy, on_delete=CASCADE)
    full_name = models.CharField(max_length=200, validators=[RegexValidator('^[A-Z_]*$',
                               'Only uppercase letters and underscores allowed.')])
    ic_num = models.CharField(max_length=14, validators=[RegexValidator('^[0-9]*-[0-1][0-9]-[0-9]*',
                               'Please follow standard NRIC formatting.')])
    share_num = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP, default='Please Select')
    gender = models.CharField(max_length=20, choices=GENDER, default='Please Select')
    date_of_birth = models.DateField(auto_now=False, verbose_name=u'Date Of Birth')
    mobile_number = models.CharField(max_length=18, validators=[RegexValidator('^(\+\d{1,3})?,?\s?\d{8,13}',
                                    'Please follow standard global mobile number formatting')])
    nomination_type = models.CharField(max_length=30, choices=NOMINATION, default='Please Select', verbose_name=u'Nomination Type' )
    
    def __str__(self):
        return self.full_name
    
class MSVR(models.Model):
    user_policy = models.ForeignKey(UserPolicy, on_delete=CASCADE)
    policy_effective_date = models.DateField(auto_now=False)
    request_date = models.DateField(auto_now=False)
    basic_plan = models.CharField(max_length=8)
    premium = models.DecimalField(max_digits=12, decimal_places=2)
    sum_insured = models.DecimalField(max_digits=12, decimal_places=2)
    
class MSVRChange(models.Model):
    PREMIUM = [
        ('Please Select','Please Select'),
        ('Monthly Mode', 'M'),
        ('Yearly Mode', 'Y')
    ]
    msvr_id = models.ForeignKey(MSVR, on_delete=CASCADE)
    current_premium = models.CharField(max_length=50, verbose_name='Current MSVR Premium', choices=PREMIUM)
    new_premium = models.PositiveIntegerField(default=0, verbose_name='New MSVR Premium', )
    agreement = models.BooleanField(default=False)
    
class ChangeRequest(models.Model):
    REQUEST_TYPE = [
        ('Nomination', 'Nomination'),
        ('MSVR', 'MSVR')
    ]  
    user_policy = models.ForeignKey(UserPolicy, on_delete=CASCADE)
    request_type = models.CharField(max_length=50, verbose_name='Type of Request', choices=REQUEST_TYPE)

    def __str__(self):
        return self.policy

class UnicodeSpaceUsernameValidator(UnicodeUsernameValidator):
    """ validator to allow spaces in username """

    regex = r"^[\w\.@+\- ]+$"