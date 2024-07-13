# Generated by Django 5.0.7 on 2024-07-13 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djaframe", "0005_remove_staging_x_pos_remove_staging_z_pos"),
    ]

    operations = [
        migrations.AddField(
            model_name="scene",
            name="image",
            field=models.ImageField(
                blank=True, null=True, upload_to="uploads/djaframe/scene/"
            ),
        ),
        migrations.AlterField(
            model_name="staging",
            name="position",
            field=models.CharField(
                default="0 0 0",
                help_text="Left/Right - Up/Down - In/Out",
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="staging",
            name="rotation",
            field=models.CharField(
                default="0 0 0", help_text="Pitch - Yaw - Roll", max_length=50
            ),
        ),
        migrations.AlterField(
            model_name="staging",
            name="scale",
            field=models.CharField(
                default="1 1 1", help_text="Width - Heigth - Depth", max_length=50
            ),
        ),
    ]
