import factory
from factory.django import DjangoModelFactory
from models import Client, Delivery_In, Delivery_Out, Manager

def dt():
	Company= factory.Faker("name")
	Phone = factory.Faker("phone_number")
	Location = factory.Faker("location")
	print(Company)
	



#if __name__ == "__main__":
#	print("run from internal")