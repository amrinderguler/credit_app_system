import json
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from .models import *
from rest_framework.response import  Response
from .serializers import *
import datetime

# Create your views here.
@api_view(['POST'])
def register(request):
    try:
        phone_no=request.data['phone_no']
        customer_exist=Customer.objects.filter(phone_no=phone_no).exists()
        if not customer_exist:
            first_name=request.data['first_name']
            last_name=request.data['last_name']
            age=request.data['age']
            monthly_salary=request.data['monthly_salary']
            monthly_salary=(monthly_salary/100000)*100000
            approved_limit=36*monthly_salary
            user=Customer.objects.create(phone_no=phone_no,first_name=first_name,last_name=last_name,age=age,monthly_salary=monthly_salary,approved_limit=approved_limit)
            # specify serializer to be used
            serializer_class = CustomerSerializers(user, context={'request': request})
            return Response(serializer_class.data)
        else:
            return JsonResponse({"message":"This Customer is already registered."},status=409)
    except Exception as e:
        return JsonResponse({"message":f"Error Occured: {e}"})

def calculate_credit_score(customer_id):
    # Calculate credit score based on the given components
    credit_score = 0
    
    customer_past=Loan.objects.filter(end_date__lt=datetime.datetime.now(), customer_id__customer_id=customer_id).count()
    customer_total=Loan.objects.filter(customer_id__customer_id=customer_id).count()
    approved_loan=Loan.objects.filter(end_date__gte=datetime.datetime.now(),customer_id__customer_id=customer_id)
    approved_loan_ammount=0
    ongoing_emi=0
    for i in approved_loan:
        approved_loan_ammount=approved_loan_ammount+i.loan_amount
        ongoing_emi+=i.emi
        
    customer=Customer.objects.get(customer_id=customer_id)
    # Check if sum of current loans exceeds approved limit
    if approved_loan_ammount >=  customer.approved_limit or ongoing_emi>customer.monthly_salary/2:
        return credit_score

    # Calculate credit rating (out of 100)
    monthly_salary=customer.monthly_salary
    approved_limit=customer.approved_limit
    loan_obj=Loan.objects.filter(customer_id__customer_id=customer_id)
    total_emiontime=0
    total_tenure=0
    loan_approved=0
    for loan in loan_obj:
        total_emiontime+=loan.emi_ontime
        total_tenure+=loan.tenure
        loan_approved+=loan.loan_amount
    
    pemi=(total_emiontime/total_tenure)*100
    ploan_inpast=(customer_past/customer_total)*100
    ploan_cy=((monthly_salary-ongoing_emi)/monthly_salary)*100
    ploan_app=((approved_limit-loan_approved)/approved_limit)*100
    
    credit_score=(pemi+ploan_inpast+ploan_cy+ploan_app)/4
    return credit_score

    


@api_view(['POST'])
def check_eligibility(request):
    customer_id=request.data['customer_id']
    credit_score=calculate_credit_score(customer_id)
    loan_amount=request.data['loan_amount']
    interest_rate=request.data['interest_rate']
    tenure=request.data['tenure']
    approval=False
    monthly_installment=0
    # Apply loan approval rules
    if credit_score > 50:
        approval=True
        corrected_interest_rate = 8
        ir=corrected_interest_rate/1200
        monthly_installment=loan_amount*((ir*(1+ir)**(tenure))/((1+ir)**(tenure)-1))
    elif 50 > credit_score > 30:
        corrected_interest_rate = 12
        approval=True
        monthly_installment=loan_amount*((ir*(1+ir)**(tenure))/((1+ir)**(tenure)-1))
    elif 30 > credit_score > 10:
        corrected_interest_rate = 16
        approval=True
        monthly_installment=loan_amount*((ir*(1+ir)**(tenure))/((1+ir)**(tenure)-1))
    else:
        corrected_interest_rate=None
        
    dic={"Customer ID":customer_id,"Approval":approval,"Interest Rate":interest_rate,"Corrected Interest Rate":corrected_interest_rate,"Tenure":tenure,"Monthly Installement":monthly_installment}
    return Response(dic)

@api_view(['POST'])
def create_loan(request):    
    customer_id=request.data['customer_id']
    credit_score=calculate_credit_score(customer_id)
    loan_amount=request.data['loan_amount']
    interest_rate=request.data['interest_rate']
    tenure=request.data['tenure']
    approval=False
    monthly_installment=0
    if credit_score > 50:
        approval=True
        corrected_interest_rate = 8
        ir=corrected_interest_rate/1200
        monthly_installment=loan_amount*((ir*(1+ir)**(tenure))/((1+ir)**(tenure)-1))
    elif 50 > credit_score > 30:
        corrected_interest_rate = 12
        approval=True
        monthly_installment=loan_amount*((ir*(1+ir)**(tenure))/((1+ir)**(tenure)-1))
    elif 30 > credit_score > 10:
        corrected_interest_rate = 16
        approval=True
        monthly_installment=loan_amount*((ir*(1+ir)**(tenure))/((1+ir)**(tenure)-1))
    else:
        corrected_interest_rate=None
        
    if approval==True:
        days=tenure*30
        customer=Customer.objects.get(pk=customer_id)
        loan_obj=Loan.objects.create(customer_id=customer,loan_amount=loan_amount,tenure=tenure,interest_rate=corrected_interest_rate,emi=monthly_installment,doa=datetime.datetime.now(),end_date=datetime.datetime.now()+datetime.timedelta(days=days))
        loan_id=loan_obj.loan_id
        dct={"Loan ID":loan_id,"Customer ID":customer_id,"Loan Approved":approval,"Message":"Loan Approved Sucessfully","Monthly Installement":monthly_installment}
        return Response(dct)

    dct={"Loan ID": None,"Customer Id":customer_id,"Loan Approved":approval,"Message":"Approval Limit Exhausted","Monthly Installement":None}
    return Response(dct)

@api_view(['GET'])
def view_loan(request,loan_id):
    loan_obj=Loan.objects.filter(loan_id=loan_id)
    dct={"Loan ID":loan_id,
        "Customer":{"Customer ID":loan_obj[0].customer_id.customer_id,
                    "First Name":loan_obj[0].customer_id.first_name,
                    "Last Name":loan_obj[0].customer_id.last_name,
                    "Phone Number":loan_obj[0].customer_id.phone_no,
                    "Age":loan_obj[0].customer_id.age
                    },
        "Loan Amount":loan_obj[0].loan_amount,
        "Interest Rate":loan_obj[0].interest_rate,
        "Monthly Installement":loan_obj[0].emi,
        "Tenure":loan_obj[0].tenure
        }
    return Response(dct)

@api_view(['GET'])
def view_customer_loan(request,customer_id):
    loan_list=[]
    loan_obj=Loan.objects.filter(customer_id__customer_id=customer_id)
    for loan in loan_obj:
        repay_left=loan.end_date-datetime.datetime.now().date()
        dct={
            "Loan ID":loan.loan_id,
            "Loan Amount":loan.loan_amount,
            "Interest Rate":loan.interest_rate,
            "Monthly Installement":loan.emi,
            "Repayment left":int((repay_left.days-1)/30)+1
            }
        loan_list.append(dct)
    
    return Response(loan_list)