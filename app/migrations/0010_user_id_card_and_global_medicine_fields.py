from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0009_alter_sharepost_medicine_audit_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="id_card",
            field=models.CharField(blank=True, max_length=18, verbose_name="身份证号"),
        ),
        migrations.AddField(
            model_name="globalmedicine",
            name="approval_number",
            field=models.CharField(blank=True, max_length=60, verbose_name="批准文号"),
        ),
        migrations.AddField(
            model_name="globalmedicine",
            name="manufacturer",
            field=models.CharField(blank=True, max_length=120, verbose_name="生产厂家"),
        ),
        migrations.AddField(
            model_name="globalmedicine",
            name="rx_otc",
            field=models.CharField(
                choices=[("RX", "处方药"), ("OTC", "非处方药")],
                default="OTC",
                max_length=3,
                verbose_name="药品类型",
            ),
        ),
        migrations.AddField(
            model_name="globalmedicine",
            name="specification",
            field=models.CharField(blank=True, max_length=120, verbose_name="规格"),
        ),
    ]
