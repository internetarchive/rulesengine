# Generated by Django 2.1 on 2018-08-09 22:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rules", "0002_auto_20180809_2229"),
    ]

    operations = [
        migrations.RenameField(
            model_name="rule",
            old_name="capture_end",
            new_name="date_end",
        ),
        migrations.RenameField(
            model_name="rule",
            old_name="capture_start",
            new_name="date_start",
        ),
        migrations.RenameField(
            model_name="rulechange",
            old_name="capture_end",
            new_name="date_end",
        ),
        migrations.RenameField(
            model_name="rulechange",
            old_name="capture_start",
            new_name="date_start",
        ),
        migrations.RemoveField(
            model_name="rule",
            name="retrieval_end",
        ),
        migrations.RemoveField(
            model_name="rule",
            name="retrieval_start",
        ),
        migrations.RemoveField(
            model_name="rule",
            name="seconds_since_capture",
        ),
        migrations.RemoveField(
            model_name="rulechange",
            name="retrieval_end",
        ),
        migrations.RemoveField(
            model_name="rulechange",
            name="retrieval_start",
        ),
        migrations.RemoveField(
            model_name="rulechange",
            name="seconds_since_capture",
        ),
    ]
