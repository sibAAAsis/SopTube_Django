from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import json
import datetime

# Create your views here.
def store(request):
	if request.user.is_authenticated:
		customer=request.user.coustomer
		order,created=Order.objects.get_or_create(coustomer=customer,complete=False)
		items=order.orderitem_set.all()
		cartitems=order.get_cart_items
	else:
		items=[]
		order={'get_cart_total':0,'get_cart_items':0,'shipping':False}
		cartitems=order['get_cart_items']

	products=Product.objects.all()
	context = {'products':products,'cartitems':cartitems}
	return render(request, 'store.html', context)

def cart(request):
	if request.user.is_authenticated:
		customer=request.user.coustomer
		order,created=Order.objects.get_or_create(coustomer=customer,complete=False)
		items=order.orderitem_set.all()
		cartitems=order.get_cart_items
	else:
		try:
			cart=json.loads(request.COOKIES['cart'])
		except:
			cart={}
		print("cart",cart)
		items=[]
		order={'get_cart_total':0,'get_cart_items':0,'shipping':False}
		cartitems=order['get_cart_items']
		
		for i in cart :
			cartitems+=cart[i]['quantity']
			product=Product.objects.get(id=i)
			total=(product.price*cart[i]['quantity'])
			order['get_cart_total']+=total
			order['get_cart_items']+=cart[i]['quantity']
			item={
				'product':{
					'id':product.id,
					'name':product.name,
					'nprice':product.price,
					'imageURL':product.imageURL,

				},
				'quantity':cart[i]['quantity'],
				'get_total':total,
				
			}

	context = {'items':items,'order':order,'cartitems':cartitems}
	return render(request, 'cart.html', context)



def checkout(request):

	if request.user.is_authenticated:
		customer=request.user.coustomer
		order,created=Order.objects.get_or_create(coustomer=customer,complete=False)
		items=order.orderitem_set.all()
		cartitems=order.get_cart_items
	else:
		items=[]
		order={'get_cart_total':0,'get_cart_items':0,'shipping':False}
		cartitems=order['get_cart_items']

	context = {'items':items,'order':order,'cartitems':cartitems}
	return render(request, 'checkout.html', context)
def about(request):
	context = {}
	return render(request, 'about.html', context)


def updateItem(request):
	data=json.loads(request.body)
	productId=data['productId']
	action=data['action']
	print('action',action)
	print('productId',productId)

	customer=request.user.coustomer
	product=Product.objects.get(id=productId)
	order,created=Order.objects.get_or_create(coustomer=customer,complete=False)

	orderItem,created=OrderItem.objects.get_or_create(order=order,product=product)

	if action=='add':
		orderItem.quantity=(orderItem.quantity+1)
	elif action=='remove':
		orderItem.quantity=(orderItem.quantity-1)

	orderItem.save()

	if orderItem.quantity<= 0:
		orderItem.delete()
	

	return JsonResponse('Item was added' ,safe=False)

# from django.views.decorators.csrf import csrf_exempt
# @csrf_exempt
def processOrder(request):
	transaction_id=datetime.datetime.now().timestamp()
	data=json.loads(request.body)
	if request.user.is_authenticated:
	
		customer=request.user.coustomer
		order,created=Order.objects.get_or_create(coustomer=customer,complete=False)
		total=float(data['form']['total'])
		order.transaction_id= transaction_id

		if total== order.get_cart_total:
			order.complete=True
		order.save()
		if order.shipping==True:
			ShippingAddress.objects.create(
				coustomer=customer,
				order=order,
				address=data['shipping']['address'],
				city=data['shipping']['city'],
				state=data['shipping']['state'],
				zipcode=data['shipping']['zipcode'],

			)
	else:
			print("Not loged In")

	return JsonResponse("Payment Complete..",safe=False)


def product(request,id):
	products=Product.objects.filter(id=id)
	print(products)
	context = {'products':products}
	return render(request, 'product.html', context)