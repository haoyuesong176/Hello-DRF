from datetime import datetime, time, timedelta
from itertools import product

from django.utils import timezone

from .models import FieldRecord


def create_daily_records(target_date_str='2025-05-10'):
    base_date = timezone.make_aware(datetime.strptime(target_date_str, '%Y-%m-%d'))

    start_time = time(7, 0)
    end_time = time(21, 30)
    field_names = ['field1', 'field2', 'field3']
    price = 50
    status = FieldRecord.Status.AVAILABLE

    def generate_time_slots():
        current = datetime.combine(datetime.today(), start_time)
        end = datetime.combine(datetime.today(), end_time)
        while current <= end:
            yield current.time()
            current += timedelta(minutes=30)

    times = list(generate_time_slots())

    records = []
    for current_time, field_name in product(times, field_names):
        records.append(
            FieldRecord(
                date=base_date.date(),
                time=current_time,
                field_name=field_name,
                price=price,
                status=status,
            )
        )

    FieldRecord.objects.bulk_create(records)
    print(f"✅ 已成功创建 {len(records)} 条记录")