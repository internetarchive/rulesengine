# Generated by Django 2.1 on 2018-08-27 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rules", "0008_auto_20180824_1747"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rule",
            name="capture_date_end",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="rule",
            name="capture_date_start",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="rule",
            name="retrieve_date_end",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="rule",
            name="retrieve_date_start",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="rule",
            name="seconds_since_capture",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="rulechange",
            name="capture_date_end",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="rulechange",
            name="capture_date_start",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="rulechange",
            name="change_comment",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="rulechange",
            name="change_type",
            field=models.CharField(
                choices=[("c", "created"), ("u", "updated")], max_length=1
            ),
        ),
        migrations.AlterField(
            model_name="rulechange",
            name="change_user",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="rulechange",
            name="retrieve_date_end",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="rulechange",
            name="retrieve_date_start",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="rulechange",
            name="seconds_since_capture",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
