# Generated by Django 5.1.7 on 2025-03-17 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0007_remove_participation_time_taken_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='quiz',
            old_name='time_limit_per_question',
            new_name='time_limit',
        ),
        migrations.AddField(
            model_name='quiz',
            name='time_limit_type',
            field=models.CharField(choices=[('per_question', 'Per Question'), ('overall', 'Overall Quiz')], default='per_question', max_length=20),
        ),
    ]
