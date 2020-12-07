from django.db.models.signals import post_save

from django.contrib.auth.models import User, Group


from .models import Customer


def customer_profile(sender, instance, created, **kwargs):
    if created:
        group = Group.objects.get(name='customer')
        instance.groups.add(group)
        Customer.objects.create(
            user=instance,
            name=instance.username,
            email=instance.email,
        )
        print('*'*30)
        print('CREATE PROFILE')
        print('*'*30)


post_save.connect(customer_profile, sender=User)
