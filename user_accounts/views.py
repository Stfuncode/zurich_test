# from azure.storage import blob
# from azure.storage.blob import BlobServiceClient, __version__
import requests
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .forms import *
from .models import *
# ms_identity_web = settings.MS_IDENTITY_WEB
from django.core.mail import BadHeaderError, EmailMultiAlternatives
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import get_template
from io import BytesIO
from login import settings
from django.contrib.auth.models import auth

def indexView(request):
    return render(request, 'index.html')

@login_required
def dashboardView(request):
    
    # connect_str = "DefaultEndpointsProtocol=https;AccountName=formsample;AccountKey=YJx8jQwLMmI6Qb6Ju0UHA6N5IC/9iIUUxq00xjsQZYhMtqFy/gr235jK5UcI4Ttj15lTJ+qs+I4nJzunevme6g==;EndpointSuffix=core.windows.net"
    # blob_service_client = BlobServiceClient.from_connection_string(connect_str)    
    
    # DEST_FILE = 'Insurance Sample - Zurich.fott'
    
    # try:

    #     blob_client = blob_service_client.get_blob_client(container='newersampletest', blob='Insurance Sample - Zurich.fott')
    
    #     download_file_path = r'C:\Users\jason.chao\OneDrive - Infront Consulting APAC\Desktop\FYP\Zurich\Zurich_Temp\test.txt'
    #     print("\nDownloading blob to \n\t" + download_file_path)

    #     with open(download_file_path, "wb") as download_file:
    #         download_file.write(blob_client.download_blob().readall())
        
    #     blob_client.download_blob().readall()    

    # except Exception as ex:
    #     print('lol')
    
     
    context = {
        'user_list': Register.objects.all()
    }
    return render(request, 'dashboard.html', context)

def register(request):
    if request.method == "POST":
        form = RegisterNewUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User Registered')
            return redirect('register')
    else:
        form = RegisterNewUserForm()
        
    return render(request, 'registration/register.html', {'form':form})

def homepage(request):
    return render(request, 'homepage.html')

def selfservice(request,pk):
    context = {
        'user_policy' : UserPolicy.objects.filter(user_id=pk)
    }    
    return render(request, 'selfservice.html', context)

def request_change(request):
    if request.method == "POST": 
        user_policy_val = request.POST['user_policy']
        request_type_val = request.POST['request_type']
        user_policy = UserPolicy.objects.get(policy_details=user_policy_val)
        
        if(request_type_val == 'MSVR'):
            msvr = MSVR.objects.get(user_policy=user_policy)
            return redirect('msvr', pk=msvr.id)
        else:
            nominationform = NomineeDetails.objects.get(user_policy=user_policy)
            return redirect('nominationform', pk=nominationform.id)
    else:
        return render(request, 'homepage.html')

def nominationform(request, pk):
    nominee_details = NomineeDetails.objects.get(id=pk)
    form1 = NominationForm(instance=nominee_details)
    policy_details = nominee_details.user_policy.policy_details

    context = {
        'form1': form1,
        'nominee_details': policy_details,
        'pk':pk
    }
    if request.method == "POST":
        form1 = NominationForm(request.POST, instance=nominee_details)
        if form1.is_valid():
            data = {
                'details': policy_details,
                'full_name' : form1.cleaned_data['full_name'],
                'ic_num': form1.cleaned_data['ic_num'],
                'share_num' : form1.cleaned_data['share_num'],
                'relationship' : form1.cleaned_data['relationship'],
                'gender' : form1.cleaned_data['gender'],
                'date_of_birth' : form1.cleaned_data['date_of_birth'],
                'mobile_number' : form1.cleaned_data['mobile_number'],
                'nomination_type' : form1.cleaned_data['nomination_type'],
            }
            subject = "New Nominee Details Request"
            template = get_template('pdf/nomination_form_pdf.html') 
            html  = template.render(data)
            result = BytesIO()
            pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
            pdf = result.getvalue()
            filename = 'Insurance Test App.pdf' 

            data2 = {
                'user': request.user.email,
                'details': policy_details,
            }
            template = get_template('email/submission_email.html')
            message  = template.render(data2)

            try:
                mail = EmailMultiAlternatives(subject, "New Nominee Details Request Made", settings.EMAIL_HOST_USER, ['puteri.syazzwani@infrontconsulting.com.my'], cc=[request.user.email])
                mail.attach_alternative(message, "text/html")
                mail.attach(filename, pdf, 'application/pdf')
                mail.send()
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            form1.save()
            messages.success(request, "Information updated successfully!")
            return redirect('nominationform', pk=pk)
        else:
            messages.error(request, "Information update unsuccessful!")
            return redirect('nominationform', pk=pk)
    return render(request, 'nominationform.html', context)
    
def msvr(request, pk):
    msvr = MSVR.objects.get(id=pk)
    msvr_change = MSVRChange.objects.get(msvr_id=msvr)  
    form1 = MSVRForm(instance=msvr)
    form2 = MSVRChangeForm(instance=msvr_change)
    policy_details = msvr.user_policy.policy_details
    
    context = {
        'pk':pk,
        'form1': form1,
        'form2': form2,
    }
    
    if request.method == "POST":
        form1 = MSVRForm(request.POST, instance=msvr)
        form2 = MSVRChangeForm(request.POST, instance=msvr_change) 
        if form1.is_valid() and form2.is_valid():
            data = {
                'details': policy_details,
                'policy_effective_date' : form1.cleaned_data['policy_effective_date'],
                'request_date': form1.cleaned_data['request_date'],
                'basic_plan' : form1.cleaned_data['basic_plan'],
                'premium' : form1.cleaned_data['premium'],
                'sum_insured' : form1.cleaned_data['sum_insured'],
                'current_premium'  : form2.cleaned_data['current_premium'],
                'new_premium' : form2.cleaned_data['new_premium'],
            }
            subject = "New MSVR Request"
            template = get_template('pdf/msvr_pdf.html') 
            html  = template.render(data)
            result = BytesIO()
            pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
            pdf = result.getvalue()
            filename = 'Insurance Test App.pdf' 

            data2 = {
                'user': request.user.email,
                'details' : policy_details
            }
            template = get_template('email/submission_email.html')
            message  = template.render(data2)

            try:
                mail = EmailMultiAlternatives(subject, "New MSVR Request Made", settings.EMAIL_HOST_USER, ['puteri.syazzwani@infrontconsulting.com.my'], cc=[request.user.email])
                mail.attach_alternative(message, "text/html")
                mail.attach(filename, pdf, 'application/pdf')
                mail.send()
            except BadHeaderError:
                return HttpResponse('Invalid header found.')

            form1.save()
            form2.save()
            messages.success(request, "Information updated successfully!")
            return redirect('msvr', pk=pk)  
        else:
            messages.error(request, "Information update unsuccessful!")
            return redirect('msvr', pk=pk)  
    return render(request, 'msvr.html', context)

# @ms_identity_web.login_required
# def token_details(request):
#     return render(request, 'auth/token.html')

# @ms_identity_web.login_required
# def call_ms_graph(request):
#     ms_identity_web.acquire_token_silently()
#     graph = 'https://graph.microsoft.com/v1.0/users'
#     authZ = f'Bearer {ms_identity_web.id_data._access_token}'
#     results = requests.get(graph, headers={'Authorization': authZ}).json()

#     # trim the results down to 5 and format them.
#     if 'value' in results:
#         results ['num_results'] = len(results['value'])
#         results['value'] = results['value'][:5]

#     return render(request, 'auth/call-graph.html', context=dict(results=results))
def logout(request):
    auth.logout(request)
    return redirect('login')
