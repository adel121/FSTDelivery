from django.db import models
from django.urls import reverse
# Create your models here.

class Manager(models.Model):
    def __str__(self):
        return self.Name
    Name = models.CharField(max_length=50)
    Location = models.CharField(max_length=50)

class Delivery_Out(models.Model):
    def __str__(self):
        return self.Name
    Name = models.CharField(max_length=50)
    #Location = models.CharField(max_length=50)
    Phone = models.CharField(max_length=20)



class Client(models.Model):
    def __str__(self):
        return self.Company
    Location = models.CharField(max_length=50)
    Phone = models.CharField(max_length=50)
    Company = models.CharField(max_length=50,primary_key=True)

class Delivery_In(models.Model):
    def __str__(self):
        return self.Name
    Name=models.CharField(max_length=50)
    #Location = models.CharField(max_length=50)
    Phone = models.CharField(max_length=50)
    #client = models.ForeignKey(Client, on_delete=models.CASCADE)


Status_Choices = ( ('paid','PAID'), ('pending','PENDING'), ('sent','SENT'), ('refunded','REFUNDED'))



class Bill(models.Model):
    def __str__(self):
        return self.Id
    def get_absolute_url(self):
        return reverse('bill_details', args=[str(self.Id),self.Status])
    Id = models.CharField(max_length=10, primary_key=True)
    Date_In = models.DateTimeField('Date In', null=True, blank=True)
    Date_Sent = models.DateTimeField('Date Sent', null=True, blank=True,default=None)
    Date_Paid = models.DateTimeField('Date Paid', null=True, blank=True, default=None)
    Date_Done = models.DateTimeField('Date Done', null=True, blank=True, default=None)
    Done = models.BooleanField(default=False)
    address = models.CharField(max_length=100000,default="Address not found")
    delivery_in = models.ForeignKey(Delivery_In, on_delete=models.CASCADE)
    delivery_out = models.ForeignKey(Delivery_Out, on_delete=models.CASCADE)
    endClientName=models.CharField(max_length=100000,default="Unknown Name")
    endClientNumber=models.CharField(max_length=10000,default="03000000")
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=False)
    Product_cost = models.PositiveIntegerField( default=0)
    Delivery_cost = models.PositiveIntegerField(default=0)
    Status = models.CharField(max_length=99, choices=Status_Choices, default="pending" )
    Hidden_Status =  models.CharField(max_length=99, choices=Status_Choices, default="pending" )
    Done_Refunding = models.BooleanField(default=False)

