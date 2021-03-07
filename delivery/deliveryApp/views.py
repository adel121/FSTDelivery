from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from .models import Manager, Bill,Client,Delivery_In,Delivery_Out
from django.db import models
from django.utils import timezone
import datetime
from django.urls import reverse
from .forms import LoginForm,ViewDeliveryOutForm, ManagerForm,Delivery_OutForm,ViewClientForm, ViewDeliveryInForm, ClientForm, Delivery_InForm, BillForm
from datetime import date as DATE
from django.shortcuts import render
from django.shortcuts import get_object_or_404 
import json
from django.http import HttpResponse
from django.views.generic.edit import UpdateView, DeleteView
import xlwt
from django.db.models import Q
def index(request, category='None', year=0, month=0, day=0, phone='0'):
	if request.method=='POST':

		if request.is_ajax():
			if request.POST.get("operation") == "postpone":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)
				bill.Date += datetime.timedelta(days=1)
				bill.save()
				dt = str(bill.Date.date())
				block=bill.Id+"_item"
				if year!=0:
					remove=True
				else:
					remove=False
				ctx = {'content_id':bill.Id, 'new_date':dt, 'id':bill.Id+"_date", 'remove':remove, 'block':block}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
			elif request.POST.get("operation") == "done":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)
				bill.Done=True
				bill.Date_Done=datetime.datetime.now()
				bill.save()
				block=bill.Id+"_notdone"
				remove1 = bill.Id+"_donebutton"
				remove2 = bill.Id+"_postponebutton"
				ctx = {'content_id':bill.Id, 'block':block, 'rem1':remove1, 'rem2':remove2}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
			elif request.POST.get("operation") == "sent":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)
				if (bill.Status == "pending"):
					bill.Status="sent"
					bill.Hidden_Status="sent"
					bill.Date_Sent = datetime.datetime.now()
					bill.delivery_out=Delivery_Out.objects.get(pk = request.POST.get("deliveryout",None))
					bill.save()
					Id=bill.Id+"_sentbutton"
					statusid = bill.Id+"_status"
					billid=bill.Id
					newId=bill.Id+"_paidbutton"
					ctx = {'content_id':bill.Id, 'Id':Id, 'newId':newId,'statusid':statusid, 'billid':billid}	
					v = HttpResponse(json.dumps(ctx),content_type='application/json')
				else: 
					v = HttpResponse(json.dumps({}),content_type='application/json')
				return v
			elif request.POST.get("operation") == "done_refunding":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)			
				bill.Done_Refunding = True
				bill.Date_Sent = None
				bill.save()
				Id=bill.Id+"_donerefundingbutton"
				statusid = bill.Id+"_notdonerefunding"
				billid=bill.Id
				ctx = {'content_id':bill.Id, 'Id':Id,'statusid':statusid, 'billid':billid}	
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
			elif request.POST.get("operation") == "paid":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)
				bill.Status="paid"
				bill.Date_Paid=datetime.datetime.now()
				bill.Hidden_Status="paid"
				bill.Date_Paid=datetime.datetime.now()
				bill.save()
				Id=bill.Id+"_paidbutton"
				statusid = bill.Id+"_status"
				billid=bill.Id
				ctx = {'content_id':bill.Id, 'Id':Id,'statusid':statusid, 'billid':billid}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
		if(len(request.POST['requested_date'])==0):
			datelist=[0,0,0]
		else:
			datelist=request.POST['requested_date'].split('-')
		
		if datelist[0]!="No Date Specified":
			year=int(datelist[0])
			month=int(datelist[1])
			day=int(datelist[2])
		phone=request.POST['requested_phone']
		if phone == "All Phone Numbers":
			phone = "0"
	if category=="paid":
		lst = Bill.objects.all().filter(Status="paid")
	elif category=="pending":
		lst = Bill.objects.all().filter(Status="pending")
	elif category=="sent":
		lst = Bill.objects.all().filter(Status="sent")
	else:
		lst = Bill.objects.all()
	if year!=0:
		date=datetime.date(int(year),int(month),int(day))
	else:
		date='0-0-0'
	if phone!='0':
		lst = lst.filter(endClientNumber=phone)	
		#date=date.today()
	
	return render(request, 'index.html', {'bills':lst, 'date':date, 'category':category, 'phone':phone, 'deliveryouts':Delivery_Out.objects.all()})



def bill_details(request, bill_id=0, status=0,date='0-0-0', category='all'):

	if request.method == "GET" and request.GET.get('id'):
		bill_id = request.GET.get('id')

		if not Bill.objects.filter(Id=bill_id).exists():
			return render(request,'thanks.html',{'Message': "Bill With Id "+bill_id+" Doesn't Exist :("})
	bill = Bill.objects.get(Id=bill_id)
	if bill.Hidden_Status == "refunded" and bill.Status!="refunded":
		bill.Done_Refunding=False
	if bill.Status != "refunded":
		bill.Done_Refunding = False
	if bill.Hidden_Status != "sent" and bill.Status=="sent":
		bill.Date_Sent = datetime.datetime.now()
	if bill.Hidden_Status != "paid" and bill.Status=="paid":
		bill.Date_Paid=datetime.datetime.now()
	if bill.Status == "pending":
		bill.Date_Sent = None
	if bill.Status != "paid":
		bill.Done=False
		bill.Date_Done=None
		bill.Date_Paid = None
	if not bill.Done:
		bill.Date_Done = None
	if bill.Hidden_Status == "paid" and bill.Status != "paid":
		bill.Done=False
		bill.Date_Done=None
	bill.Hidden_Status=bill.Status
	bill.save()
	return render(request, 'bill_details.html', {'bill':bill})
	
def end_bill(request, bill_id, date='0-0-0', category='all'):
	bill = Bill.objects.get(Id=bill_id)
	bill.Date_Done=datetime.datetime.now()
	bill.Done=True
	bill.save()
	lst = Bill.objects.all()
	datelist=date.split('-')
	if datelist[0]!="No Date Specified":
		year=int(datelist[0])
		month=int(datelist[1])
		day=int(datelist[2])
	return HttpResponseRedirect(reverse('index',args=(category,year,month,day)))


def postpone_bill(request, bill_id, date='0-0-0', category='all'):
	bill = Bill.objects.get(Id=bill_id)
	bill.Date += datetime.timedelta(days=1)
	bill.save()
	lst = Bill.objects.all()
	datelist=date.split('-')
	if datelist[0]!="No Date Specified":
		year=int(datelist[0])
		month=int(datelist[1])
		day=int(datelist[2])
	return HttpResponseRedirect(reverse('index',args=(category,year,month,day)))



def add_manager(request):
	if request.method=='POST':
		form=ManagerForm(request.POST)
		if form.is_valid():
			data=form.cleaned_data
			manager=Manager()
			manager.Name=data['Name']
			manager.Location=data['Location']
			manager.save()
			return render(request,'thanks.html',{'Message': "Manager Added Successfully"})
	else:
		form=ManagerForm()
	return render(request,'add_manager.html',{'form':form})

def add_deliveryout(request):
	if request.method=='POST':
		form = Delivery_OutForm(request.POST)
		if form.is_valid():
			data=form.cleaned_data
			delivery_out=Delivery_Out()
			delivery_out.Name=data['Name']
			#delivery_out.Location=data['Location']
			delivery_out.Phone=data['Phone']
			delivery_out.save()
			return render(request,'thanks.html',{'Message': "Delivery Out Added Successfully"})
	else:
		form=Delivery_OutForm()
	return render(request,'add_deliveryout.html',{'form':form})

def add_client(request):
	if request.method=='POST':
		form = ClientForm(request.POST)
		if form.is_valid():
			data=form.cleaned_data
			client=Client()
			#client.Name=data['Name']
			client.Location=data['Location']
			client.Phone=data['Phone']
			client.Company=data['Company'].replace("'","")
			client.save()
			return render(request,'thanks.html',{'Message': "Client Added Successfully"})
	else:
		form=ClientForm()
	return render(request,'add_client.html',{'form':form})

def add_deliveryin(request):
	if request.method=='POST':
		form=Delivery_InForm(request.POST)
		if form.is_valid():
			data=form.cleaned_data
			deliveryin=Delivery_In()
			deliveryin.Name=data['Name']
			#deliveryin.Location=data['Location']
			deliveryin.Phone=data['Phone']
			#deliveryin.client=Client.objects.get(pk=data['client'])
			deliveryin.save()
			return render(request,'thanks.html',{'Message': "Delivery In Added Successfully"})
	else:
		form=Delivery_InForm()
	return render(request,'add_deliveryin.html',{'form':form})


def add_bill(request):
	if request.method=='POST':
		form=BillForm(request.POST)
		if form.is_valid():
			data=form.cleaned_data
			print(data)
			bill=Bill()
			bill.Id=str(data['Id'])
			bill.Date=datetime.datetime.now()
			bill.Date_In=datetime.datetime.now()
			bill.address=data['address']
			bill.delivery_in=Delivery_In.objects.get(pk=data['delivery_in'].pk)
			bill.delivery_out=Delivery_Out.objects.all()[0]
			bill.endClientName=data['endClientName']
			bill.endClientNumber=data['endClientNumber']
			bill.manager=Manager.objects.get(pk=data['manager'].pk)
			bill.client=Client.objects.get(pk=data['client'].pk)
			bill.Product_cost=data['Product_cost']
			bill.Delivery_cost=data['Delivery_cost']
			bill.status="pending"
			bill.Hidden_Status="pending"
			#if not str.isnumeric(bill.Id):
			#	return render(request,'add_bill.html',{'form':form})
			bill.save()
			return render(request,'thanks.html',{'Message': "Bill Added Successfully"})
	else:
		form = BillForm()
	return render(request,'add_bill.html',{'form':form})


def client_details(request, company ,year=0, month=0, day=0,bill_id=-1, operation='no operation'):
	if request.method == 'POST':
		if request.is_ajax():
			if request.POST.get("operation") == "postpone":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)
				bill.Date += datetime.timedelta(days=1)
				bill.save()
				dt = str(bill.Date.date())
				block=bill.Id+"_item"
				if year!=0:
					remove=True
				else:
					remove=False
				ctx = {'content_id':bill.Id, 'new_date':dt, 'id':bill.Id+"_date", 'remove':remove, 'block':block}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
			elif request.POST.get("operation") == "done":

				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)
				bill.Date_Done=datetime.datetime.now()
				bill.Done=True
				bill.save()
				block=bill.Id+"_notdone"
				remove1 = bill.Id+"_donebutton"
				remove2 = bill.Id+"_postponebutton"
				ctx = {'content_id':bill.Id, 'block':block, 'rem1':remove1, 'rem2':remove2}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
			elif request.POST.get("operation") == "done_refunding":

				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)			
				bill.Done_Refunding = True
				bill.Date_Sent = None
				bill.save()
				Id=bill.Id+"_donerefundingbutton"
				statusid = bill.Id+"_notdonerefunding"
				billid=bill.Id
				ctx = {'content_id':bill.Id, 'Id':Id,'statusid':statusid, 'billid':billid}	
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
			elif request.POST.get("operation") == "sent":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)
				if (bill.Status == "pending"):
					bill.Status="sent"
					bill.Hidden_Status="sent"
					bill.Date_Sent = datetime.datetime.now()
					bill.delivery_out=Delivery_Out.objects.get(pk = request.POST.get("deliveryout",None))
					bill.save()
					Id=bill.Id+"_sentbutton"
					statusid = bill.Id+"_status"
					billid=bill.Id
					newId=bill.Id+"_paidbutton"
					ctx = {'content_id':bill.Id, 'Id':Id, 'newId':newId,'statusid':statusid, 'billid':billid}	
					v = HttpResponse(json.dumps(ctx),content_type='application/json')
				else:
					v = HttpResponse(json.dumps({}),content_type='application/json')
				return v
			elif request.POST.get("operation") == "paid":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)
				bill.Status="paid"
				bill.Date_Paid=datetime.datetime.now()
				bill.Hidden_Status="paid"
				bill.save()
				Id=bill.Id+"_paidbutton"
				statusid = bill.Id+"_status"
				billid=bill.Id
				ctx = {'content_id':bill.Id, 'Id':Id,'statusid':statusid, 'billid':billid}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
	if bill_id!=-1:
		bill=Bill.objects.get(pk=bill_id)
		if operation == 'make sent':
			bill.Status='sent'
			bill.Hidden_Status="sent"
		elif operation == 'make paid':
			bill.Status='paid'
			bill.Hidden_Status="paid"
			bill.Date_Paid=datetime.datetime.now()
		elif operation == 'make done':
			bill.Date_Done=datetime.datetime.now()
			bill.Done=True
		elif operation == 'postpone':
			bill.Date += datetime.timedelta(days=1)
		bill.save()
		return HttpResponseRedirect(reverse('client_details', args=(company,year,month,day)))
	elif request.method=='POST':
		datelist=request.POST['requested_date'].split('-')
		if datelist[0]!="No Date Specified":
			year=int(datelist[0])
			month=int(datelist[1])
			day=int(datelist[2])
	lst = Bill.objects.all().filter(client = company)
	if year!=0:
		date=datetime.date(int(year),int(month),int(day))
	else:
		date='0-0-0'
	return render(request, 'client_details.html', {'bills':lst, 'date':date,  'company':company, 'deliveryouts':Delivery_Out.objects.all() })

def delivery_in_details(request, delivery_in_id ,year=0, month=0, day=0,bill_id=-1, operation='no operation'):
	if request.method == 'POST':
		if request.is_ajax():
			if request.POST.get("operation") == "postpone":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)
				bill.Date += datetime.timedelta(days=1)
				bill.save()
				dt = str(bill.Date.date())
				block=bill.Id+"_item"
				if year!=0:
					remove=True
				else:
					remove=False
				ctx = {'content_id':bill.Id, 'new_date':dt, 'id':bill.Id+"_date", 'remove':remove, 'block':block}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
			elif request.POST.get("operation") == "done":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)
				bill.Date_Done=datetime.datetime.now()
				bill.Done=True
				bill.save()
				block=bill.Id+"_notdone"
				remove1 = bill.Id+"_donebutton"
				remove2 = bill.Id+"_postponebutton"
				ctx = {'content_id':bill.Id, 'block':block, 'rem1':remove1, 'rem2':remove2}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
			elif request.POST.get("operation") == "done_refunding":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)			
				bill.Done_Refunding = True
				bill.Date_Sent = None
				bill.save()
				Id=bill.Id+"_donerefundingbutton"
				statusid = bill.Id+"_notdonerefunding"
				billid=bill.Id
				ctx = {'content_id':bill.Id, 'Id':Id,'statusid':statusid, 'billid':billid}	
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
			elif request.POST.get("operation") == "sent":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)
				if (bill.Status == "pending"):
					bill.Status="sent"
					bill.Hidden_Status="sent"
					bill.Date_Sent = datetime.datetime.now()
					bill.delivery_out=Delivery_Out.objects.get(pk = request.POST.get("deliveryout",None))
					bill.save()
					Id=bill.Id+"_sentbutton"
					statusid = bill.Id+"_status"
					billid=bill.Id
					newId=bill.Id+"_paidbutton"
					ctx = {'content_id':bill.Id, 'Id':Id, 'newId':newId,'statusid':statusid, 'billid':billid}	
					v = HttpResponse(json.dumps(ctx),content_type='application/json')
				else:
					v = HttpResponse(json.dumps({}),content_type='application/json')
				return v
			elif request.POST.get("operation") == "paid":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)
				bill.Status="paid"
				bill.Date_Paid=datetime.datetime.now()
				bill.Hidden_Status="paid"
				bill.save()
				Id=bill.Id+"_paidbutton"
				statusid = bill.Id+"_status"
				billid=bill.Id
				ctx = {'content_id':bill.Id, 'Id':Id,'statusid':statusid, 'billid':billid}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
	if bill_id!=-1:
		bill=Bill.objects.get(pk=bill_id)
		if operation == 'make sent':
			bill.Status='sent'
			bill.Hidden_Status="sent"
		elif operation == 'make paid':
			bill.Status='paid'
			bill.Date_Paid=datetime.datetime.now()
			bill.Hidden_Status="paid"
		elif operation == 'make done':
			bill.Date_Done=datetime.datetime.now()
			bill.Done=True
		elif operation == 'postpone':
			bill.Date += datetime.timedelta(days=1)
		bill.save()
		return HttpResponseRedirect(reverse('delivery_in_details', args=(delivery_in_id,year,month,day)))
	elif request.method=='POST':
		if(len(request.POST['requested_date'])==0):
			datelist=[0,0,0]
		else:
			datelist=request.POST['requested_date'].split('-')
		if datelist[0]!="No Date Specified":
			year=int(datelist[0])
			month=int(datelist[1])
			day=int(datelist[2])
	lst = Bill.objects.all().filter(delivery_in=delivery_in_id)
	if year!=0:
		date=datetime.date(int(year),int(month),int(day))
	else:
		date='0-0-0'
	delivery_in=Delivery_In.objects.get(pk=delivery_in_id)
	return render(request, 'delivery_in_details.html', {'bills':lst, 'date':date, 'delivery_in':delivery_in, 'deliveryouts':Delivery_Out.objects.all()})


def delivery_out_details(request, delivery_out_id ,year=0, month=0, day=0,bill_id=-1, operation='no operation'):
	if request.method == 'POST':
		if request.is_ajax():
			if request.POST.get("operation") == "postpone":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)
				bill.Date += datetime.timedelta(days=1)
				bill.save()
				dt = str(bill.Date.date())
				block=bill.Id+"_item"
				if year!=0:
					remove=True
				else:
					remove=False
				ctx = {'content_id':bill.Id, 'new_date':dt, 'id':bill.Id+"_date", 'remove':remove, 'block':block}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
			elif request.POST.get("operation") == "done_refunding":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)			
				bill.Done_Refunding = True
				bill.Date_Sent = None
				bill.save()
				Id=bill.Id+"_donerefundingbutton"
				statusid = bill.Id+"_notdonerefunding"
				billid=bill.Id
				ctx = {'content_id':bill.Id, 'Id':Id,'statusid':statusid, 'billid':billid}	
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
			elif request.POST.get("operation") == "done":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)
				bill.Date_Done=datetime.datetime.now()
				bill.Done=True
				bill.save()
				block=bill.Id+"_notdone"
				remove1 = bill.Id+"_donebutton"
				remove2 = bill.Id+"_postponebutton"
				ctx = {'content_id':bill.Id, 'block':block, 'rem1':remove1, 'rem2':remove2}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
			elif request.POST.get("operation") == "sent":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)
				if (bill.Status == "pending"):
					bill.Status="sent"
					bill.Hidden_Status="sent"
					bill.Date_Sent = datetime.datetime.now()
					bill.delivery_out=Delivery_Out.objects.get(pk = request.POST.get("deliveryout",None))
					bill.save()
					Id=bill.Id+"_sentbutton"
					statusid = bill.Id+"_status"
					billid=bill.Id
					newId=bill.Id+"_paidbutton"
					ctx = {'content_id':bill.Id, 'Id':Id, 'newId':newId,'statusid':statusid, 'billid':billid}	
					v = HttpResponse(json.dumps(ctx),content_type='application/json')
				else:
					v = HttpResponse(json.dumps({}),content_type='application/json')
				return v
			elif request.POST.get("operation") == "paid":
				bill_id=request.POST.get("content_id",None)
				bill=Bill.objects.get(Id=bill_id)
				bill.Status="paid"
				bill.Date_Paid=datetime.datetime.now()
				bill.Hidden_Status="paid"
				bill.save()
				Id=bill.Id+"_paidbutton"
				statusid = bill.Id+"_status"
				billid=bill.Id
				ctx = {'content_id':bill.Id, 'Id':Id,'statusid':statusid, 'billid':billid}
				v = HttpResponse(json.dumps(ctx),content_type='application/json')
				return v
	if bill_id!=-1:
		bill=Bill.objects.get(pk=bill_id)
		if operation == 'make sent':
			bill.Status='sent'
			bill.Hidden_Status='sent'
		elif operation == 'make paid':
			bill.Status='paid'
			bill.Date_Paid=datetime.datetime.now()
			bill.Hidden_Status='paid'
		elif operation == 'make done':
			bill.Done=True
			bill.Date_Done=datetime.datetime.now()
		elif operation == 'postpone':
			bill.Date += datetime.timedelta(days=1)
		bill.save()
		return HttpResponseRedirect(reverse('delivery_out_details', args=(delivery_out_id,year,month,day)))
	elif request.method=='POST':
		if(len(request.POST['requested_date'])==0):
			datelist=[0,0,0]
		else:
			datelist=request.POST['requested_date'].split('-')
		if datelist[0]!="No Date Specified":
			year=int(datelist[0])
			month=int(datelist[1])
			day=int(datelist[2])
	lst = Bill.objects.filter(
		Q(delivery_out=delivery_out_id) & ~Q(Status = 'refunded')
	)
	if year!=0:
		date=datetime.date(int(year),int(month),int(day))
	else:
		date='0-0-0'
	delivery_out=Delivery_Out.objects.get(pk=delivery_out_id)
	return render(request, 'delivery_out_details.html', {'bills':lst, 'date':date, 'delivery_out':delivery_out, 'deliveryouts':Delivery_Out.objects.all()})



def get_bill_format(bill):
	n="<br>"
	h="<hr>"
	if bill.Status == "refunded":
		string = "Bill Id: " + bill.Id +n+"End-Client Name: "+bill.endClientName+n+"End-Client Phone Number: "+bill.endClientNumber +n + "Address: " + bill.address+n+"Status: "+bill.Status+n+"Done Refunding: "
		if bill.Done_Refunding:
			string = string + "Yes" + n
		else:
			string = string + "No" + n
		"Date Done: "+str(bill.Date).split(' ')[0]+n+"Date In: "+str(bill.Date_In).split(' ')[0]+n
		string = string +"Product Cost: "+str(bill.Product_cost)+n+h	
		return str(string)
	string = "Bill Id: " + bill.Id +n+"End-Client Name: "+bill.endClientName+n+"End-Client Phone Number: "+bill.endClientNumber +n + "Address: " + bill.address+n+"Status: "+bill.Status+n+"Date Done: "+str(bill.Date).split(' ')[0]+n+"Date In: "+str(bill.Date_In).split(' ')[0]+n
	string = string +"Product Cost: "+str(bill.Product_cost)+n+h	
	return str(string)

def extract_client_report(request,company):
	client = Client.objects.get(pk=company)
	
	date = str(datetime.datetime.now()).split(' ')[0]
	
	response = HttpResponse(content_type='application/ms-excel')
	response['Content-Disposition'] = 'attachment; filename='+company+"_"+str(date)+'.xls'
	wb = xlwt.Workbook(encoding='utf-8')
	ws = wb.add_sheet('Client Report')
	row_num = 0

	font_style = xlwt.easyxf('font: bold on, color black;\
                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;\
                     pattern: pattern solid, fore_color white;align: horiz center;')
	ws.write(0,2,'FST Delivery',font_style)
	ws.write(1,2,'Client:',font_style)
	ws.write(2,2,'Report Date:',font_style)
	ws.write(1,3,client.Company)
	ws.write(2,3,str(date))
	columns = ['Id','Region','Phone Number', 'Product Cost', 'Delivery Cost', 'Status']
	for col_num in range(len(columns)):
		ws.write(4, col_num+1, columns[col_num], font_style)
	paid_rows = bills = Bill.objects.filter(
		Q(client = company) &  ~Q(Done = True) & Q(Status = 'paid'))
	print(paid_rows)
	font_style = xlwt.XFStyle()
	row_num=4
	totalprod=0
	totaldel=0
	font_style=xlwt.easyxf("pattern: pattern solid, fore_color white; font: color black; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,left thin, right thin, top thin, bottom thin;")
	
	for row in paid_rows:
		row_num += 1
		print("check :",row.Id)
		totalprod+=row.Product_cost
		totaldel+=row.Delivery_cost
		row.Date_Done=datetime.datetime.now()
		row.Done=True
		row.save()
		ws.write(row_num,1,row.Id,font_style)
		ws.write(row_num,2,row.address,font_style)
		ws.write(row_num,3,row.endClientNumber,font_style)
		ws.write(row_num,4,row.Product_cost,font_style)
		ws.write(row_num,5,row.Delivery_cost,font_style)
		ws.write(row_num,6,"Received",font_style)
	font_style = xlwt.easyxf('font: bold on, color black;\
                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;\
                     pattern: pattern solid, fore_color yellow;align: horiz center;')
	
	row_num+=1
	
	ws.write(row_num,5,'Total Product Cost:',font_style)
	ws.write(row_num,6,str(totalprod)+' L.L', font_style)
	row_num+=1
	ws.write(row_num,5,'Total Delivery Cost:',font_style)
	ws.write(row_num,6,str(totaldel)+' L.L', font_style)
	row_num+=1
	ws.write(row_num,5,'Total Combined Cost:',font_style)
	ws.write(row_num,6,str(totalprod+totaldel)+' L.L', font_style)
	row_num+=3

	font_style = xlwt.easyxf('font: bold on, color black;\
                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;\
                     pattern: pattern solid, fore_color white;align: horiz center;')
	columns = ['Id','Region','Phone Number', 'Product Cost', 'Delivery Cost', 'Status']
	for col_num in range(len(columns)):
		ws.write(row_num, col_num+1, columns[col_num], font_style)
	paid_rows = bills = Bill.objects.filter(
		Q(client = company) &  ~Q(Done_Refunding = True) & Q(Status = 'refunded'))
	print(paid_rows)
	totalprod=0
	totaldel=0
	font_style=xlwt.easyxf("pattern: pattern solid, fore_color white; font: color black; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,left thin, right thin, top thin, bottom thin;")
	
	for row in paid_rows:
		row_num += 1
		print("check :",row.Id)
		totalprod+=row.Product_cost
		totaldel+=row.Delivery_cost
		row.Done_Refunding=True
		row.save()
		ws.write(row_num,1,row.Id,font_style)
		ws.write(row_num,2,row.address,font_style)
		ws.write(row_num,3,row.endClientNumber,font_style)
		ws.write(row_num,4,row.Product_cost,font_style)
		ws.write(row_num,5,row.Delivery_cost,font_style)
		ws.write(row_num,6,"Refunded",font_style)
	font_style = xlwt.easyxf('font: bold on, color black;\
                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;\
                     pattern: pattern solid, fore_color yellow;align: horiz center;')
	
	row_num+=1
	
	ws.write(row_num,5,'Total Product Cost:',font_style)
	ws.write(row_num,6,str(totalprod)+' L.L', font_style)
	row_num+=1
	ws.write(row_num,5,'Total Delivery Cost:',font_style)
	ws.write(row_num,6,str(totaldel)+' L.L', font_style)
	row_num+=1
	ws.write(row_num,5,'Total Combined Cost:',font_style)
	ws.write(row_num,6,str(totalprod+totaldel)+' L.L', font_style)
	
	wb.save(response)
	return response

	


def extract_delivery_out_report(request,id):
	deliveryout = Delivery_Out.objects.get(pk=id)
	date = str(datetime.datetime.now()).split(' ')[0]
	response = HttpResponse(content_type='application/ms-excel')
	response['Content-Disposition'] = 'attachment; filename='+deliveryout.Name+"_"+str(date)+'.xls'
	wb = xlwt.Workbook(encoding='utf-8')
	ws = wb.add_sheet('Delivery_Out Report')
	row_num = 0

	font_style = xlwt.easyxf('font: bold on, color black;\
                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;\
                     pattern: pattern solid, fore_color white;align: horiz center;')
	ws.write(0,2,'FST Delivery',font_style)
	ws.write(1,2,'Driver Out:',font_style)
	ws.write(2,2,'Report Date:',font_style)
	ws.write(1,3,deliveryout.Name)
	ws.write(2,3,str(date))
	columns = ['Id','Region','Phone Number', 'Product Cost', 'Delivery Cost', 'Status']
	for col_num in range(len(columns)):
		ws.write(4, col_num+1, columns[col_num], font_style)
	print("cgevhjwqdqw/:",deliveryout.pk)
	paid_rows = Bill.objects.filter(
		Q( delivery_out = id) &  ~Q(Done = True) & Q(Status = 'paid'))
	print(paid_rows)
	font_style = xlwt.XFStyle()
	row_num=4
	totalprod=0
	totaldel=0
	font_style=xlwt.easyxf("pattern: pattern solid, fore_color white; font: color black; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,left thin, right thin, top thin, bottom thin;")
	
	for row in paid_rows:
		row_num += 1
		print("check :",row.Id)
		totalprod+=row.Product_cost
		totaldel+=row.Delivery_cost
		ws.write(row_num,1,row.Id,font_style)
		ws.write(row_num,2,row.address,font_style)
		ws.write(row_num,3,row.endClientNumber,font_style)
		ws.write(row_num,4,row.Product_cost,font_style)
		ws.write(row_num,5,row.Delivery_cost,font_style)
		ws.write(row_num,6,"Received",font_style)
	font_style = xlwt.easyxf('font: bold on, color black;\
                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;\
                     pattern: pattern solid, fore_color yellow;align: horiz center;')
	row_num+=1
	
	ws.write(row_num,5,'Total Product Cost:',font_style)
	ws.write(row_num,6,str(totalprod)+' L.L', font_style)
	row_num+=1
	ws.write(row_num,5,'Total Delivery Cost:',font_style)
	ws.write(row_num,6,str(totaldel)+' L.L', font_style)
	row_num+=1
	ws.write(row_num,5,'Total Combined Cost:',font_style)
	ws.write(row_num,6,str(totalprod+totaldel)+' L.L', font_style)
	wb.save(response)
	return(response)
	

def extract_delivery_in_report(request,id,year,month,day):
	date=datetime.date(int(year),int(month),int(day))
	deliveryin = Delivery_In.objects.get(pk=id)
	
	response = HttpResponse(content_type='application/ms-excel')
	response['Content-Disposition'] = 'attachment; filename='+deliveryin.Name+"_"+str(date)+'.xls'
	wb = xlwt.Workbook(encoding='utf-8')
	ws = wb.add_sheet('Delivery_In Report')
	row_num = 0
	pre_date = datetime.datetime(int(year), int(month), int(day)-1, 23, 50, 55) 
	post_date = datetime.datetime(int(year), int(month), int(day)+1, 0, 0, 1) 
	font_style = xlwt.easyxf('font: bold on, color black;\
                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;\
                     pattern: pattern solid, fore_color white;align: horiz center;')
	ws.write(0,2,'FST Delivery',font_style)
	ws.write(1,2,'Client:',font_style)
	ws.write(2,2,'Report Date:',font_style)
	ws.write(1,3,deliveryin.Name)
	ws.write(2,3,str(date))
	columns = ['Id','Region','Phone Number', 'Product Cost', 'Delivery Cost', 'Status']
	for col_num in range(len(columns)):
		ws.write(4, col_num+1, columns[col_num], font_style)
	paid_rows = bills = Bill.objects.filter(
		Q(delivery_in = id) &  Q(Date_In__lt = post_date) & Q(Date_In__gt = pre_date))
	print("paid: ",post_date, pre_date)
	font_style = xlwt.XFStyle()
	row_num=4
	totalprod=0
	totaldel=0
	font_style=xlwt.easyxf("pattern: pattern solid, fore_color white; font: color black; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,left thin, right thin, top thin, bottom thin;")
	
	for row in paid_rows:
		row_num += 1
		print("check :",row.Id)
		totalprod+=row.Product_cost
		totaldel+=row.Delivery_cost
		ws.write(row_num,1,row.Id,font_style)
		ws.write(row_num,2,row.address,font_style)
		ws.write(row_num,3,row.endClientNumber,font_style)
		ws.write(row_num,4,row.Product_cost,font_style)
		ws.write(row_num,5,row.Delivery_cost,font_style)
		ws.write(row_num,6,row.Status,font_style)
	font_style = xlwt.easyxf('font: bold on, color black;\
                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;\
                     pattern: pattern solid, fore_color yellow;align: horiz center;')
	
	row_num+=1
	
	ws.write(row_num,5,'Total Product Cost:',font_style)
	ws.write(row_num,6,str(totalprod)+' L.L', font_style)
	row_num+=1
	ws.write(row_num,5,'Total Delivery Cost:',font_style)
	ws.write(row_num,6,str(totaldel)+' L.L', font_style)
	row_num+=1
	ws.write(row_num,5,'Total Combined Cost:',font_style)
	ws.write(row_num,6,str(totalprod+totaldel)+' L.L', font_style)
	row_num+=3
	wb.save(response)
	return response
	

def extract_all_data(request,year=0,month=0,day=0):
	post_date = datetime.datetime(int(year),int(month),int(day)+1)
	pre_date  = datetime.datetime(int(year),int(month),int(day)-1)
	date  = datetime.date(int(year),int(month),int(day))
	bills = Bill.objects.filter(
		Q(Status = 'paid') & Q(Date_Paid__lt = post_date) & Q(Date_Paid__gt = pre_date) 
		)
	response = HttpResponse(content_type='application/ms-excel')
	response['Content-Disposition'] = 'attachment; filename='+"Daily Report" +"_"+str(date)+'.xls'
	wb = xlwt.Workbook(encoding='utf-8')
	ws = wb.add_sheet('Daily Report')
	row_num = 0
	font_style = xlwt.easyxf('font: bold on, color black;\
                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;\
                     pattern: pattern solid, fore_color white;align: horiz center;')
	ws.write(0,2,'FST Delivery',font_style)
	ws.write(1,2,'Daily Report',font_style)
	ws.write(2,2,'Report Date:',font_style)
	ws.write(2,3,str(date))
	columns = ['Id','Region','Phone Number', 'Product Cost', 'Delivery Cost', 'Status']
	for col_num in range(len(columns)):
		ws.write(4, col_num+1, columns[col_num], font_style)

	font_style = xlwt.XFStyle()
	row_num=4
	totalprod=0
	totaldel=0
	totalprodpaid=0
	totaldelpaid=0
	totalproddone=0
	totaldeldone=0
	font_style=xlwt.easyxf("pattern: pattern solid, fore_color white; font: color black; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,left thin, right thin, top thin, bottom thin;")
	
	for row in bills:
		if not row.Done:
			row_num += 1
			totalprodpaid+=row.Product_cost
			totaldelpaid+=row.Delivery_cost
			ws.write(row_num,1,row.Id,font_style)
			ws.write(row_num,2,row.address,font_style)
			ws.write(row_num,3,row.endClientNumber,font_style)
			ws.write(row_num,4,row.Product_cost,font_style)
			ws.write(row_num,5,row.Delivery_cost,font_style)
			ws.write(row_num,6,"Received",font_style)

	font_style = xlwt.easyxf('font: bold on, color black;\
                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;\
                     pattern: pattern solid, fore_color yellow;align: horiz center;')
	row_num+=1
	
	ws.write(row_num,5,'Total Product Cost:',font_style)
	ws.write(row_num,6,str(totalprodpaid)+' L.L', font_style)
	row_num+=1
	ws.write(row_num,5,'Total Delivery Cost:',font_style)
	ws.write(row_num,6,str(totaldelpaid)+' L.L', font_style)
	row_num+=1
	ws.write(row_num,5,'Total Combined Cost:',font_style)
	ws.write(row_num,6,str(totalprodpaid+totaldelpaid)+' L.L', font_style)
	font_style=xlwt.easyxf("pattern: pattern solid, fore_color white; font: color black; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,left thin, right thin, top thin, bottom thin;")
	
	row_num+=3

	font_style = xlwt.easyxf('font: bold on, color black;\
                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;\
                     pattern: pattern solid, fore_color white;align: horiz center;')
	columns = ['Id','Region','Phone Number', 'Product Cost', 'Delivery Cost', 'Status']
	for col_num in range(len(columns)):
		ws.write(row_num, col_num+1, columns[col_num], font_style)
	font_style=xlwt.easyxf("pattern: pattern solid, fore_color white; font: color black; align: horiz center; borders: top_color black, bottom_color black, right_color black, left_color black,left thin, right thin, top thin, bottom thin;")
		
	for row in bills:
		if row.Done:
			row_num += 1
			totalproddone+=row.Product_cost
			totaldeldone+=row.Delivery_cost
			ws.write(row_num,1,row.Id,font_style)
			ws.write(row_num,2,row.address,font_style)
			ws.write(row_num,3,row.endClientNumber,font_style)
			ws.write(row_num,4,row.Product_cost,font_style)
			ws.write(row_num,5,row.Delivery_cost,font_style)
			ws.write(row_num,6,"Finished",font_style)

	font_style = xlwt.easyxf('font: bold on, color black;\
                     borders: top_color black, bottom_color black, right_color black, left_color black,\
                              left thin, right thin, top thin, bottom thin;\
                     pattern: pattern solid, fore_color yellow;align: horiz center;')
	row_num+=1
	
	ws.write(row_num,5,'Total Product Cost:',font_style)
	ws.write(row_num,6,str(totalproddone)+' L.L', font_style)
	row_num+=1
	ws.write(row_num,5,'Total Delivery Cost:',font_style)
	ws.write(row_num,6,str(totaldeldone)+' L.L', font_style)
	row_num+=1
	ws.write(row_num,5,'Total Combined Cost:',font_style)
	ws.write(row_num,6,str(totalproddone+totaldeldone)+' L.L', font_style)
	totalprod = totalproddone + totalproddone
	totaldel = totaldelpaid + totaldeldone
	wb.save(response)
	return response


def find_client(request):
	if request.method == 'POST':
		form = ViewClientForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			client=data['client'].pk
			return HttpResponseRedirect(reverse('client_details',args=(client,)))
	else:
		form=ViewClientForm()
	return render(request,'find_client.html',{'form':form})

def find_delivery_in(request):
	if request.method == 'POST':
		form = ViewDeliveryInForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			delivery_in=data['delivery_in'].pk
			
			return HttpResponseRedirect(reverse('delivery_in_details',args=(delivery_in,)))
	else:
		form=ViewDeliveryInForm()
	return render(request,'find_delivery_in.html',{'form':form})


def find_delivery_out(request):
	if request.method == 'POST':
		form = ViewDeliveryOutForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			delivery_out=data['delivery_out'].pk
			return HttpResponseRedirect(reverse('delivery_out_details',args=(delivery_out,)))
	else:
		form=ViewDeliveryOutForm()
	return render(request,'find_delivery_out.html',{'form':form})


def request_extract_all_data(request):
	if request.method == 'POST':
		data=request.POST
		date=data['date']
		if (len(date)==0):
			date="0-0-0"
		date=date.split('-')
		year=date[0]			
		month=date[1]
		day=date[2]
		return HttpResponseRedirect(reverse('extract_all_data',args=(year,month,day)))
	return render(request,'extract_all_data.html')




class BillUpdate(UpdateView):
    model = Bill
    fields = ['Id','Date_In','Date_Sent', 'Done', 'address', 'delivery_in','delivery_out','endClientName','endClientNumber','manager','client','Product_cost','Delivery_cost','Status','Done_Refunding']
    #template_name_suffix = '_update'


class BillDelete(DeleteView): 
    model = Bill
    success_url ="/confirm_delete/"

def deletionComplete(request):
	return render(request, 'thanks.html', {'Message':'Deletion Performed Successfully'})

class ClientDelete(DeleteView): 
    model = Client
    success_url ="/confirm_delete/"

class DeliveryInDelete(DeleteView): 
    model = Delivery_In
    success_url ="/confirm_delete/"

class DeliveryOutDelete(DeleteView): 
    model = Delivery_Out
    success_url ="/confirm_delete/"
