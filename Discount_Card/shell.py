from Discount_Card.models import User
user = User.objects.get(username='MG')
print(user.member)  # Should not be None
print(user.member.active_subscription())  # Should be True for active subscription
