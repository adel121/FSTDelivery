from django.contrib import admin
from django.urls import path
from django.conf.urls import url,include
from . import views
from .views import BillUpdate, BillDelete, DeliveryInDelete,DeliveryOutDelete,ClientDelete
urlpatterns=[

path('',views.index,name='index'),
path('bill_details/', views.bill_details,name='bill_details'),
path('bill_details/<str:bill_id>/', views.bill_details,name='bill_details'),
path('bill_details/<str:bill_id>/<str:status>/', views.bill_details,name='bill_details'),
path('bill_details/<str:bill_id>/<str:status>/<str:date>/', views.bill_details,name='bill_details'),
path('bill_details/<str:bill_id>/<str:status>/<str:date>/<str:category>/', views.bill_details,name='bill_details'),
path('end_bill/<str:bill_id>/<str:date>/', views.end_bill, name='end_bill'),
path('end_bill/<str:bill_id>/<str:date>/<str:category>/', views.end_bill, name='end_bill'),
path('postpone_bill/<str:bill_id>/<str:date>/',views.postpone_bill,name='postpone_bill'),
path('postpone_bill/<str:bill_id>/<str:date>/<str:category>/',views.postpone_bill,name='postpone_bill'),
path('bills/',views.index,name='index'),
path('bills/<str:category>/',views.index,name='index'),
path('bills/<str:category>/<int:year>/<int:month>/<int:day>',views.index,name='index'),
path('bills/<int:year>/<int:month>/<int:day>/',views.index,name='index'),
path('bills/<str:phone>/',views.index,name='index'),
path('bills/<str:category>/<str:phone>/',views.index,name='index'),
path('bills/<str:category>/<int:year>/<int:month>/<int:day>/<str:phone>/',views.index,name='index'),
path('bills/<int:year>/<int:month>/<int:day>/<str:phone>/',views.index,name='index'),
path('add_manager',views.add_manager,name='add_manager'),
path('add_deliveryout',views.add_deliveryout,name='add_deliveryout'),
path('add_client',views.add_client,name='add_client'),
path('add_deliveryin',views.add_deliveryin,name='add_deliveryin'),
path('add_bill',views.add_bill,name='add_bill'),
path('client_details/<str:company>/<int:year>/<int:month>/<int:day>/',views.client_details,name='client_details'),
path('client_details/<str:company>/<int:year>/<int:month>/<int:day>/<str:bill_id>/<str:operation>/',views.client_details,name='client_details'),
path('client_details/<str:company>/',views.client_details,name='client_details'),
path('delivery_in_details/<int:delivery_in_id>/<int:year>/<int:month>/<int:day>/',views.delivery_in_details,name='delivery_in_details'),
path('delivery_in_details/<int:delivery_in_id>/<int:year>/<int:month>/<int:day>/<str:bill_id>/<str:operation>/',views.delivery_in_details,name='delivery_in_details'),
path('delivery_in_details/<int:delivery_in_id>/',views.delivery_in_details,name='delivery_in_details'),
path('delivery_out_details/<int:delivery_out_id>/<int:year>/<int:month>/<int:day>/',views.delivery_out_details,name='delivery_out_details'),
path('delivery_out_details/<int:delivery_out_id>/<int:year>/<int:month>/<int:day>/<str:bill_id>/<str:operation>/',views.delivery_out_details,name='delivery_out_details'),
path('delivery_out_details/<int:delivery_out_id>/',views.delivery_out_details,name='delivery_out_details'),
path('find_client/',views.find_client, name='find_client'),
path('find_delivery_in/',views.find_delivery_in, name='find_delivery_in'),
path('find_delivery_out/',views.find_delivery_out, name='find_delivery_out'),
path('extract_all_data/<int:year>/<int:month>/<int:day>/', views.extract_all_data,name='extract_all_data'),
path('extract_all_data/', views.extract_all_data,name='extract_all_data'),
path('extract_client_report/<str:company>/', views.extract_client_report,name='extract_client_report'),
path('extract_delivery_in_report/<str:id>/<int:year>/<int:month>/<int:day>/', views.extract_delivery_in_report,name='extract_delivery_in_report'),
path('extract_delivery_out_report/<str:id>/', views.extract_delivery_out_report,name='extract_delivery_out_report'),
path('extract_all_data_form/',views.request_extract_all_data, name='request_extract_all_data'),
 path('<pk>/updateBill', BillUpdate.as_view(),name="updatebill"), 
 path('<pk>/deleteBill', BillDelete.as_view(),name="deletebill"), 
 path('<pk>/deleteDeliveryIn', DeliveryInDelete.as_view(),name="delete_delivery_in"),
 path('<pk>/deleteDeliveryOut', DeliveryOutDelete.as_view(),name="delete_delivery_out"),
 path('<pk>/deleteClient', ClientDelete.as_view(),name="delete_client"), 
 path('confirm_delete/', views.deletionComplete, name="confirmDelete")
]