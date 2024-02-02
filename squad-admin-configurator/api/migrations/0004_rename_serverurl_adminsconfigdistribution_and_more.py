# Generated by Django 4.2.7 on 2024-02-02 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server_admins', '0001_initial'),
        ('api', '0003_alter_rolewebhook_request_sender'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ServerUrl',
            new_name='AdminsConfigDistribution',
        ),
        migrations.AlterField(
            model_name='rolewebhook',
            name='hmac_hash_type',
            field=models.CharField(blank=True, choices=[('blake2b', 'blake2b'), ('blake2s', 'blake2s'), ('md5', 'md5'), ('md5-sha1', 'md5-sha1'), ('sha1', 'sha1'), ('sha224', 'sha224'), ('sha256', 'sha256'), ('sha384', 'sha384'), ('sha3_224', 'sha3_224'), ('sha3_256', 'sha3_256'), ('sha3_384', 'sha3_384'), ('sha3_512', 'sha3_512'), ('sha512', 'sha512'), ('sha512_224', 'sha512_224'), ('sha512_256', 'sha512_256'), ('shake_128', 'shake_128'), ('shake_256', 'shake_256'), ('sm3', 'sm3')], help_text='Обычно предоставляется тем, кто будет вызывать вебхук, например sha256 для Battlemetrics', max_length=64, verbose_name='Тип хеша в HMAC'),
        ),
    ]
