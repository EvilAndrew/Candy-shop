from django.db import models


class Courier(models.Model):
    courier_id = models.IntegerField(primary_key=True)
    courier_type = models.CharField(max_length=4)
    # there is no array-like field, so TextField with semicolon delimiter is
    # used instead (ex: "1;6;22" is considered the same way as[1, 6, 22])
    regions = models.TextField()
    working_hours = models.TextField()
    orders = models.TextField(blank=True, default="")

    # Used in the following average-time calculations 
    # the format is "time1,region1;time2,region2;..."
    complete_times = models.TextField(blank=True, default="")

    # Used for calculation of completion time
    last_time = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    assign_time = models.DateTimeField(
        null=True, blank=True, auto_now_add=True)
    assign_type = models.TextField(blank=True, default="")
    completed_orders = models.TextField(blank=True, default="")

    # HH:MM-HH:MM format
    def get_minutes_from_string(self, temp):
        return (int(temp[:2]) * 60 + int(temp[3:5]),
                int(temp[6:8]) * 60 + int(temp[9:]))

    # Getting list of working hours in [(L_1, R_1), (L_2, R_2), ...] format
    def get_hours(self):
        return [self.get_minutes_from_string(item) for item in self.working_hours.split(';')]

    def save(self, *args, **kwargs):

        if 'dict_update' in kwargs:
            for key, val in kwargs['dict_update'].items():
                setattr(self, key, val)
            kwargs.pop('dict_update')

        super().save(*args, *kwargs)

    # Useful for debug purposes
    def __str__(self):
        return 'id: {0}\ntype: {1}\nregions: {2}\nworking_hours: {3}\n'.format(
            str(self.courier_id), self.courier_type, self.regions, self.working_hours)

    def max_possible_weight(self):
        if self.courier_type == "foot":
            return 10
        return 15 if self.courier_type == "bike" else 50

    def transform(self):
        return {
            'courier_id': self.courier_id,
            'courier_type': self.courier_type,
            'regions': list(map(int, self.regions.split(';'))),
            'working_hours': (self.working_hours.split(';') if self.working_hours else [])
        }

    def min_average_delivery_time(self):
        sum_region = {}
        cnt_region = {}

        for i in self.complete_times.split(';'):
            seconds, region = map(int, i.split(','))
            sum_region[region] = sum_region.get(region, 0) + seconds
            cnt_region[region] = cnt_region.get(region, 0) + 1

        t = -1
        flag = False
        for key in sum_region.keys():
            avg = sum_region[key] / cnt_region[key]
            t = (avg if not flag else min(avg, t))
            flag = True

        return t


class Order(models.Model):
    order_id = models.IntegerField(primary_key=True)
    weight = models.FloatField()
    region = models.IntegerField()

    # there is no array-like field, so TextField with semicolon delimiter is
    # used instead (ex: "1;6;22" is considered the same way as[1, 6, 22])
    delivery_hours = models.TextField()
    courier = models.ForeignKey(
        Courier,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None)
    complete_time = models.DateTimeField(blank=True, auto_now_add=True)
    is_completed = models.BooleanField(default=False, blank=True, null=True)

    # HH:MM-HH:MM format
    def get_minutes_from_string(self, temp):
        return (int(temp[:2]) * 60 + int(temp[3:5]),
                int(temp[6:8]) * 60 + int(temp[9:]))

    # Getting list of delivery hours in [(L_1, R_1), (L_2, R_2), ...] format
    def get_hours(self):
        return [self.get_minutes_from_string(
            item) for item in self.delivery_hours.split(';')]

    # Useful for debug purposes
    def __str__(self):
        return 'id: {0}\n weight: {1}\nregion: {2}\ndelivery_hours: {3}\ncourier:{4}\n'.format(
            str(self.order_id),
            str(self.weight),
            str(self.region),
            self.delivery_hours,
            str(self.courier) if self.courier else "NULL")

    def check_courier(self, courier):
        if not courier.working_hours or not self.delivery_hours:
            return False
        courier_minutes, delivery_minutes = courier.get_hours(), self.get_hours()

        # Although the complexity is quadratic, one can clearly reduce it to
        # O(size_1 * log(size_1) + size_2 * log(size_2)) with sorting ("sweep line techique")
        for i in courier_minutes:
            for j in delivery_minutes:
                if max(i[0] + 1, j[0] + 1) <= min(i[1] - 1, j[1] - 1):
                    return True

        return self.region in map(int, courier.region.split(';'))
