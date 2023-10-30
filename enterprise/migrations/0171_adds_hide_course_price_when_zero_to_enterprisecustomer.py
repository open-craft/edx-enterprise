from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enterprise', '0170_auto_20230301_1627'),
    ]

    operations = [
        migrations.AddField(
            model_name='enterprisecustomer',
            name='hide_course_price_when_zero',
            field=models.BooleanField(default=False, help_text='Specify whether course cost should be hidden in the landing page when the final price is zero.'),
        ),
        migrations.AddField(
            model_name='historicalenterprisecustomer',
            name='hide_course_price_when_zero',
            field=models.BooleanField(default=False, help_text='Specify whether course cost should be hidden in the landing page when the final price is zero.'),
        ),
    ]
