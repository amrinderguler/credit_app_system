from django.db import models

# Create your models here.
class Customer(models.Model):
    def __str__(self):
        return str(self.customer_id)
    
    customer_id=models.AutoField(unique=True,primary_key=True)
    first_name=models.CharField(max_length=200)
    last_name=models.CharField(max_length=200)
    age=models.IntegerField()
    phone_no=models.CharField(unique=True,max_length=15,null=False,blank=False)
    monthly_salary=models.IntegerField(default=0)
    approved_limit=models.IntegerField(default=0)
    current_debt=models.IntegerField(default=0)
    
class Loan(models.Model):
    def __str__(self):
        return str(self.customer_id)
    
    customer_id=models.ForeignKey(Customer,on_delete=models.CASCADE)
    loan_id=models.AutoField(primary_key=True)
    loan_amount=models.IntegerField()
    tenure=models.IntegerField()
    interest_rate=models.FloatField()
    emi=models.IntegerField()
    emi_ontime=models.IntegerField(default=0)
    doa=models.DateField()
    end_date=models.DateField()