from django import forms
from django.forms.models import ModelChoiceField
from django.forms.widgets import DateInput, Select
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.urls import reverse, reverse_lazy

class DateInput(forms.DateInput):
    input_type = 'date'
    
class RegisterNewUserForm(UserCreationForm):
    name = forms.CharField(widget= forms.TextInput
                        (attrs={'placeholder':'Enter your name'}))
    email = forms.CharField(widget= forms.EmailInput
                        (attrs={'placeholder':'Enter your email'}))
    identity_number = forms.CharField(widget= forms.TextInput
                        (attrs={'placeholder':'Enter your identity number'}))
    
    class Meta:
        model = Register
        fields = ('name', 'email', 'identity_number')
        
class NominationForm(forms.ModelForm):   
    full_name = forms.CharField(widget= forms.TextInput
                                (attrs={'placeholder':'Enter your name'}), label="Full Name")    
    ic_num = forms.CharField(widget= forms.TextInput
                                (attrs={'placeholder':'Enter your NRIC'}), label="NRIC")    
    share_num = forms.CharField(widget= forms.TextInput
                                (attrs={'placeholder':'Percentage Shared Sum'}),label="Share (%)")    
    mobile_number = forms.CharField(widget= forms.TextInput
                                (attrs={'placeholder':'+60-123456789 '}),label="Mobile Number")   

     
    class Meta:
        model = NomineeDetails
        fields = ('__all__')
        widgets = {
            'date_of_birth': DateInput()
        }
        exclude = ('user_policy',)
        
class PolicyForm(forms.ModelForm):   
    policy_number = forms.CharField(widget= forms.TextInput
                                (attrs={'placeholder':'Enter Policy Number'})) 
    insured_name = forms.CharField(widget= forms.TextInput
                                (attrs={'placeholder':'Name of Insurer'})) 
    basic_product = forms.CharField(widget= forms.TextInput
                                (attrs={'placeholder':'Product Name'})) 
    class Meta:
        model = PolicyDetails
        fields = ('__all__')
        widgets = {
            'request_date': DateInput()
        }

class MSVRChangeForm(forms.ModelForm):
    agreement = forms.BooleanField(label=_("Terms and Conditions"))
    class Meta:
        model = MSVRChange
        fields = ('__all__')
        exclude = ('msvr_id',)
        
    def __init__(self, *args, **kwargs):
        super(MSVRChangeForm, self).__init__(*args, **kwargs)
        terms_and_conditions = 'https://myzurichlife.com.my/Landing/tnc'
        self.fields['agreement'].label = mark_safe(_("I accept and agree that I have read and understood the "
                                                      "<a href='%s'>Terms and Conditions</a>")) % (terms_and_conditions)
        
        
class MSVRForm(forms.ModelForm):
    
    class Meta:
        model = MSVR
        fields =('__all__')
        widgets = {
            'policy_effective_date': DateInput(),
            'request_date': DateInput()
        }
        exclude = ('user_policy',)
        
class RequestChangeForm(forms.ModelForm):
    
    policy = ModelChoiceField(queryset=UserPolicy.objects.all(), widget=Select(attrs={'style': 'background_color:#F5F8EC'}))
    class Meta:
        model = ChangeRequest
        fields = ('__all__')
        exclude = ('user_policy',)
    
