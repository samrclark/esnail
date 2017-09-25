import random
import string
import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from .forms import FileAttachmentForm
from .forms import TagForm
from .forms import FilePackageForm
from .models import Tag, FilePackage, FileAttachment
from django.contrib.auth.decorators import login_required
from cauth.models import User
from django.conf import settings
from django.forms.models import modelformset_factory
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test

def is_org(user):
        return user.groups.filter(name__startswith='org_').exists()

def getpackageforuser(pid, user):
    ugroups = user.groups.all()
    fpacks=FilePackage.objects.filter(
    Q(id=pid) & (
    Q(accessiblebyusers = user) |
    Q(accessiblebygroups__in = ugroups))).distinct()
    return fpacks

# Create your views here.

@login_required
@user_passes_test(is_org, login_url='home')
def PackageCreation(request):
    if request.method == 'POST':
        packageform = FilePackageForm(request.POST)
        attachform = FileAttachmentForm(request.POST, request.FILES)
        files = request.FILES.getlist('afile')
        if attachform.is_valid() and packageform.is_valid():

            #possibly need to sterilize the provnum/fye before saving?
            tpnum = packageform.cleaned_data['pprovnum']
            tpfye = packageform.cleaned_data['pfye'].strftime('%m%d%Y')
            rousername = tpnum + '_' + tpfye + '_' + '1'
            tuser = User.objects.filter(username=rousername)
            tcnt = 1
            while tuser:
                rousername = tpnum + '_' + tpfye + '_' + str(tcnt)
                tcnt = tcnt + 1
                tuser = User.objects.filter(username=rousername)
            randpw = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
            
            rouser = User.objects.create_user(rousername, '', randpw)
            rouser.save()
            
            rogroup = Group.objects.get(name='viewonly')
            rogroup.user_set.add(rouser)

            newpack = FilePackage(
                pprovnum = packageform.cleaned_data['pprovnum'],
                pfye = packageform.cleaned_data['pfye'],
                ptitle = packageform.cleaned_data['ptitle'],
                pdescription = packageform.cleaned_data['pdescription'],
                created_by = request.user,
            )
            newpack.save()
            newpack.accessiblebyusers.add(rouser)
            
            for g in request.user.groups.all():
                if g.name.startswith("org_"):
                    newpack.accessiblebygroups.add(g)
            
            newpack.save()
            
            for f in files:
                newattach =FileAttachment(
                    filepackage = newpack,
                    originalfilename = f.name,
                    afile = f,
                )
                newattach.save()

            request.session['foo'] = "wew lad"
            request.session['last_pid'] = newpack.id
            request.session['last_uid'] = rousername
            request.session['last_upw'] = randpw

            return redirect('packagecreated')

    else:

            packageform = FilePackageForm()
            attachform = FileAttachmentForm()

    return render(request, 'snailfile/packagecreation.html', {
        'attachform': attachform, 'packageform': packageform})


@login_required
def home(request):
    ugroups=request.user.groups.all()
    fpacks=FilePackage.objects.filter(
        Q(accessiblebyusers = request.user) |
        Q(accessiblebygroups__in = ugroups)).distinct()

    if not is_org(request.user):
        if len(fpacks) == 1:
            return redirect('packagedetail/' + str(fpacks[0].id))
        
    return render(request, 'snailfile/home.html', {'filepacks': fpacks ,'usergroups':ugroups.first()})

@login_required
def PackageDetail(request, pid=0):
    if pid == 0:
        return redirect('home')
    ugroups = request.user.groups.all()
    
#    try:
#        fpack=FilePackage.objects.get(
#            Q(id=pid) & (
#            Q(accessiblebyusers = request.user) |
#            Q(accessiblebygroups__in = ugroups)))
#    except ObjectDoesNotExist:
#        return redirect('home')
    fpacks=FilePackage.objects.filter(
        Q(id=pid) & (
        Q(accessiblebyusers = request.user) |
        Q(accessiblebygroups__in = ugroups))).distinct()

    if not fpacks:
            return redirect('home')
    
    fpack = fpacks[0]

    fattachs = FileAttachment.objects.filter(filepackage=fpack)

    return render(request, 'snailfile/packagedetail.html', {'fpack': fpack, 'fattachs':fattachs, 'isorg': is_org(request.user)})

@login_required
@user_passes_test(is_org, login_url='home')
def PackageCreated(request):
    try:
        newpack = FilePackage.objects.get(id = request.session.get('last_pid'))
    except ObjectDoesNotExist:
        return redirect('home')

    return render(request, 'snailfile/packagecreated.html', {'newpack': newpack})

@login_required
@user_passes_test(is_org, login_url='home')
def VOCredentialPage(request):
    #Need to make some check that this has been accessed from a valid link and not direct accessed
    #maybe just checking session variables is sufficient

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'

    buffer = BytesIO()

    # Create the PDF object, using the BytesIO object as its "file."
    p = canvas.Canvas(buffer, pagesize=letter)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(72, 648, "You have a file attachment waiting for you at: websiteaddress.com")
    #p.drawString(72, 612, "websiteaddress.com")
    p.drawString(72, 576, "ID: " + request.session.get('last_uid'))
    p.drawString(72, 540, "Passcode: " + request.session.get('last_upw'))

    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    print(FilePackage.objects.filter(id=request.session.get('last_pid')).count())
    return response

@login_required
@user_passes_test(is_org, login_url='home')
def VOCRegen(request, pid=0):
    #need to check that this is accessible by users org
    if pid == 0:
        return redirect('home')

    try:
        cpack = FilePackage.objects.get(id = pid)
    except ObjectDoesNotExist:
        return redirect('home')
    tpnum = cpack.pprovnum
    tpfye = cpack.pfye.strftime('%m%d%Y')
    rousername = tpnum + '_' + tpfye + '_' + '1'
    tuser = User.objects.filter(username=rousername)
    tcnt = 2
    while tuser:
        rousername = tpnum + '_' + tpfye + '_' + str(tcnt)
        tcnt = tcnt + 1
        tuser = User.objects.filter(username=rousername)
    randpw = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
    
    rouser = User.objects.create_user(rousername, '', randpw)
    rouser.save()
    
    rogroup = Group.objects.get(name='viewonly')
    rogroup.user_set.add(rouser)
    
    cpack.accessiblebyusers.add(rouser)

    request.session['last_pid'] = cpack.id
    request.session['last_uid'] = rousername
    request.session['last_upw'] = randpw
    request.session['foo'] = "wew lad"
    return redirect('vocredentialpage')

@login_required
@user_passes_test(is_org, login_url='home')
def PackageDelete(request, pid=0):
    if pid == 0:
        return redirect('home')

    try:
        cpack = FilePackage.objects.get(id = pid)
    except ObjectDoesNotExist:
        return redirect('home')

    cpack.delete()
    return redirect('home')

@login_required
@user_passes_test(is_org, login_url='home')
def PackageEdit(request, pid=0):
    if pid==0:
            return redirect('home')
    fpacks=getpackageforuser(pid, request.user)
    if not fpacks:
            return redirect('home')
    fpack = fpacks[0]
    fattachs = FileAttachment.objects.filter(filepackage=fpack)

    if request.method == 'POST':
        packageform = FilePackageForm(request.POST, instance=fpack)
        if not fattachs:
            attachform = FileAttachmentForm(request.POST, request.FILES)
        else:
            fattach = fattachs[0]
            attachform = FileAttachmentForm(request.POST, request.FILES, instance=fattach)
        
        files = request.FILES.getlist('afile')
        if attachform.is_valid() and packageform.is_valid():
            
            for fa in fattachs:
                print(fa.afile.path)
            fpack = packageform.save()

            if 'afile' in request.FILES:
                for oldattach in fattachs:
                    delatt = FileAttachment.objects.get(id=oldattach.id)
                    delid = oldattach.id
                    delatt.delete()
            
            for f in files:
                newattach =FileAttachment(
                    filepackage = fpack,
                    originalfilename = f.name,
                    afile = f,
                )
                newattach.save()
                
            return redirect('home')
    else:
        packageform = FilePackageForm(instance=fpack)

        if not fattachs:
            attachform = FileAttachmentForm()
        else:
            fattach = fattachs[0]
            attachform = FileAttachmentForm(instance=fattach)

    return render(request, 'snailfile/packageedit.html', {
        'attachform': attachform, 'packageform': packageform})