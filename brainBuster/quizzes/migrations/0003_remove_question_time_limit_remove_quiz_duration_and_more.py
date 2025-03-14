# Generated by Django 5.1.7 on 2025-03-11 19:50

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0002_alter_quiz_code'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='time_limit',
        ),
        migrations.RemoveField(
            model_name='quiz',
            name='duration',
        ),
        migrations.AddField(
            model_name='quiz',
            name='icon',
            field=models.CharField(default='question-circle', max_length=50),
        ),
        migrations.AddField(
            model_name='quiz',
            name='time_limit_per_question',
            field=models.IntegerField(default=30, help_text='Time limit in seconds'),
        ),
        migrations.AlterUniqueTogether(
            name='participation',
            unique_together={('user', 'quiz')},
        ),
    ]
