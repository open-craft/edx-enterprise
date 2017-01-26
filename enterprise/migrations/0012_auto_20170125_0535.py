# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enterprise', '0011_enterprisecustomerentitlement_historicalenterprisecustomerentitlement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enterprisecustomeruser',
            name='enterprise_customer',
            field=models.ForeignKey(related_name='enterprise_customer_users', to='enterprise.EnterpriseCustomer'),
        ),
        migrations.AlterField(
            model_name='userdatasharingconsentaudit',
            name='user',
            field=models.ForeignKey(related_name='data_sharing_consent', to='enterprise.EnterpriseCustomerUser'),
        ),
    ]
