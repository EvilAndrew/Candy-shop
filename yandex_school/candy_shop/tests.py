from unittest import TestCase
from .models import Courier, Order
from .test_constants import *
from datetime import datetime, timezone
from django.utils.dateparse import parse_datetime
from time import sleep
import requests
import json


class CreatingCouriersTestCase(TestCase):
    def setUp(self):
        Courier.objects.all().delete()

    def test_creating_couriers_1(self):
        res = requests.post(
            'http://{0}:{1}/couriers'.format(URL, HOST), json=COURIERS)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.content.decode(), json.dumps(
            {"couriers": [{"id": 1}, {"id": 2}, {"id": 3}]}
        ))

        courier = Courier.objects.get(courier_id=1)
        self.assertEqual(courier.working_hours, "11:35-14:05;09:00-11:00")
        self.assertEqual(courier.regions, "1;12;22")

        courier = Courier.objects.get(courier_id=2)
        self.assertEqual(courier.working_hours, "09:00-18:00")
        self.assertEqual(courier.regions, "22")

        courier = Courier.objects.get(courier_id=3)
        self.assertEqual(courier.working_hours, "")
        self.assertEqual(courier.regions, "12;22;23;33")

        self.assertEqual(len(Courier.objects.all()), 3)

    def test_creating_couriers_2(self):
        res = requests.post(
            'http://{0}:{1}/couriers'.format(URL, HOST), json=COURIERS_2)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.content.decode(), json.dumps(
            {"couriers": [{"id": 5}, {"id": 10}]}
        ))

        courier = Courier.objects.get(courier_id=5)
        self.assertEqual(courier.working_hours, "11:00-11:02")
        self.assertEqual(courier.regions, "1;2;3")

        courier = Courier.objects.get(courier_id=10)
        self.assertEqual(courier.working_hours, "00:00-00:30;01:00-02:00")
        self.assertEqual(courier.regions, "3")

        self.assertEqual(len(Courier.objects.all()), 2)

    def test_creating_wrong_couriers(self):
        res = requests.post(
            'http://{0}:{1}/couriers'.format(URL, HOST), json=WRONG_COURIERS)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.content.decode(), json.dumps({
            "validation_error": {
                "couriers": [{"id": 1}]
            }
        }))

        self.assertEqual(len(Courier.objects.all()), 0)

    def tearDown(self):
        Courier.objects.all().delete()


class PatchingTestCase(TestCase):
    def setUp(self):
        Courier.objects.all().delete()
        self.updated_couriers = {
            "regions": [1, 2, 3, 4, 7],
            "working_hours": ["11:35-14:05", "09:00-11:00", "14:10-23:57"]
        }
        self.wrong_updated_couriers = {
            "regions": [1, 2, 3, 4, 7],
            "working_hours": ["11:35-14:05", "09:00-11:00", "14:10-23:57"],
            "some_text": "somewhat"
        }

    def test_patching_couriers(self):
        requests.post(
            'http://{0}:{1}/couriers'.format(URL, HOST), json=COURIERS)

        res = requests.patch(
            'http://{0}:{1}/couriers/1'.format(URL, HOST), json=self.updated_couriers)
        self.assertEqual(res.status_code, 200)

        courier = Courier.objects.get(courier_id=1)

        # only regions and working_hours must change
        self.assertEqual(courier.regions, "1;2;3;4;7")
        self.assertEqual(
            courier.working_hours,
            "11:35-14:05;09:00-11:00;14:10-23:57"
        )
        self.assertEqual(courier.courier_type, "foot")

        # nothing else must be created
        self.assertEqual(len(Courier.objects.all()), 3)

    def test_wrong_patching_couriers(self):
        requests.post(
            'http://{0}:{1}/couriers'.format(URL, HOST), json=COURIERS)

        res = requests.patch(
            'http://{0}:{1}/couriers/1'.format(URL, HOST), json=self.wrong_updated_couriers)
        self.assertEqual(res.status_code, 400)

        courier = Courier.objects.get(courier_id=1)

        # nothing must change
        self.assertEqual(courier.regions, "1;12;22")
        self.assertEqual(courier.working_hours, "11:35-14:05;09:00-11:00")
        self.assertEqual(courier.courier_type, "foot")

        # nothing else must be created
        self.assertEqual(len(Courier.objects.all()), 3)

    def tearDown(self):
        Courier.objects.all().delete()


class CreatingOrdersTestCase(TestCase):
    def setUp(self):
        Order.objects.all().delete()

    def test_creating_orders(self):
        res = requests.post(
            'http://{0}:{1}/orders'.format(URL, HOST), json=ORDERS)

        self.assertEqual(res.content.decode(), json.dumps({
            "orders": [{"id": 1}, {"id": 2}, {"id": 3}]
        }))

        self.assertEqual(res.status_code, 201)
        self.assertEqual(len(Order.objects.all()), 3)

        order = Order.objects.get(order_id=1)
        self.assertEqual(order.weight, 0.23)
        self.assertEqual(order.region, 12)
        self.assertEqual(order.delivery_hours, "09:00-18:00")

        order = Order.objects.get(order_id=2)
        self.assertEqual(order.weight, 15)
        self.assertEqual(order.region, 1)
        self.assertEqual(order.delivery_hours, "09:00-18:00")

        order = Order.objects.get(order_id=3)
        self.assertEqual(order.weight, 0.01)
        self.assertEqual(order.region, 22)
        self.assertEqual(order.delivery_hours, "09:00-12:00;16:00-21:30")

    def test_creating_wrong_orders(self):
        res = requests.post(
            'http://{0}:{1}/orders'.format(URL, HOST), json=WRONG_ORDERS)

        self.assertEqual(res.content.decode(), json.dumps({
            "validation_error": {
                "orders": [{"id": 5}, {"id": 7}, {"id": 11}, {"id": 25}]
            }
        }))

        self.assertEqual(res.status_code, 400)
        self.assertEqual(len(Order.objects.all()), 0)

    def tearDown(self):
        Order.objects.all().delete()


class AssigningOrdersWithoutPatchingTestCase(TestCase):
    def setUp(self):
        Courier.objects.all().delete()
        Order.objects.all().delete()

    def test_asssignment(self):
        requests.post(
            'http://{0}:{1}/couriers'.format(URL, HOST), json=COURIERS)
        requests.post(
            'http://{0}:{1}/orders'.format(URL, HOST), json=ORDERS)

        res = requests.post(
            'http://{0}:{1}/orders/assign'.format(URL, HOST), json={"courier_id": 1})
        self.assertEqual(res.status_code, 200)

        returned = json.loads(res.content.decode())
        self.assertEqual(returned['orders'], [{'id': 1}, {'id': 3}])

        assign_time = returned['assign_time']
        courier = Courier.objects.get(courier_id=1)

        self.assertEqual(courier.assign_type, "foot")
        self.assertEqual(courier.assign_time
                         .replace(tzinfo=timezone.utc)
                         .isoformat(),
                         assign_time
                         )
        self.assertEqual(courier.last_time
                         .replace(tzinfo=timezone.utc)
                         .isoformat(),
                         assign_time
                         )
        self.assertEqual(courier.orders, "1;3")

        for i in [1, 3]:
            order = Order.objects.get(order_id=i)

            self.assertEqual(order.is_completed, False)
            self.assertEqual(order.courier, courier)

    def test_idempotency(self):
        requests.post(
            'http://{0}:{1}/couriers'.format(URL, HOST), json=COURIERS)
        requests.post(
            'http://{0}:{1}/orders'.format(URL, HOST), json=ORDERS)
        res = requests.post(
            'http://{0}:{1}/orders/assign'.format(URL, HOST), json={"courier_id": 1})

        returned = json.loads(res.content.decode())
        assign_time = returned['assign_time']

        courier = Courier.objects.get(courier_id=1)

        res = requests.post(
            'http://{0}:{1}/orders/assign'.format(URL, HOST), json={"courier_id": 1})
        self.assertEqual(res.status_code, 200)

        returned = json.loads(res.content.decode())
        self.assertEqual(returned['orders'], [{'id': 1}, {'id': 3}])

        self.assertEqual(
            parse_datetime(returned['assign_time']),
            parse_datetime(assign_time)
        )

    def test_empty_assignment(self):
        requests.post(
            'http://{0}:{1}/couriers'.format(URL, HOST), json=COURIERS)
        requests.post(
            'http://{0}:{1}/orders'.format(URL, HOST), json=ORDERS)
        requests.post(
            'http://{0}:{1}/orders/assign'.format(URL, HOST), json={"courier_id": 1})

        res = requests.post(
            'http://{0}:{1}/orders/assign'.format(URL, HOST), json={"courier_id": 3})

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content.decode(), json.dumps({"orders": []}))

    def test_unexistent_id_assignment(self):
        requests.post(
            'http://{0}:{1}/couriers'.format(URL, HOST), json=COURIERS)
        requests.post(
            'http://{0}:{1}/orders'.format(URL, HOST), json=ORDERS)

        res = requests.post(
            'http://{0}:{1}/orders/assign'.format(URL, HOST), json={"courier_id": 2281337})

        self.assertEqual(res.status_code, 400)

    def test_single_order_to_many(self):
        requests.post(
            'http://{0}:{1}/couriers'.format(URL, HOST), json=COURIERS)
        requests.post(
            'http://{0}:{1}/orders'.format(URL, HOST), json=ORDERS)
        requests.post(
            'http://{0}:{1}/orders/assign'.format(URL, HOST), json={"courier_id": 1})

        res = requests.post(
            'http://{0}:{1}/orders/assign'.format(URL, HOST), json={"courier_id": 2})

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content.decode(), json.dumps({"orders": []}))

    def tearDown(self):
        Courier.objects.all().delete()
        Order.objects.all().delete()


class AssigningOrdersWithPatchingTestCase(TestCase):
    def setUp(self):
        Courier.objects.all().delete()
        Order.objects.all().delete()

    def tearDown(self):
        Courier.objects.all().delete()
        Order.objects.all().delete()

    def test_patched_courier_reassignment(self):
        requests.post(
            'http://{0}:{1}/couriers'.format(URL, HOST), json=COURIERS)
        requests.post(
            'http://{0}:{1}/orders'.format(URL, HOST), json=ORDERS)
        requests.post(
            'http://{0}:{1}/orders/assign'.format(URL, HOST), json={"courier_id": 1})

        res = requests.patch(
            'http://{0}:{1}/couriers/1'.format(URL, HOST), json={"working_hours": []})

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content.decode(), json.dumps({
            "courier_id": 1,
            "courier_type": "foot",
            "regions": [1, 12, 22],
            "working_hours": []
        }))

        courier = Courier.objects.get(courier_id=1)
        self.assertEqual(courier.orders, "")
        self.assertEqual(courier.regions, "1;12;22")
        self.assertEqual(courier.working_hours, "")

        for i in [1, 3]:
            order = Order.objects.get(order_id=i)
            self.assertEqual(order.courier, None)

        res = requests.post(
            'http://{0}:{1}/orders/assign'.format(URL, HOST), json={"courier_id": 2})

        returned = json.loads(res.content.decode())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(returned['orders'], [{'id': 3}])

        courier = Courier.objects.get(courier_id=2)
        self.assertEqual(Order.objects.get(order_id=3).courier, courier)
        self.assertEqual(courier.orders, "3")


class CompletingOrderTestCase(TestCase):
    def setUp(self):
        Courier.objects.all().delete()
        Order.objects.all().delete()

    def tearDown(self):
        Courier.objects.all().delete()
        Order.objects.all().delete()

    def test_completing_single_order(self):
        requests.post(
            'http://{0}:{1}/couriers'.format(URL, HOST), json=COURIERS)
        requests.post(
            'http://{0}:{1}/orders'.format(URL, HOST), json=ORDERS)
        res = requests.post(
            'http://{0}:{1}/orders/assign'.format(URL, HOST), json={"courier_id": 1})

        complete_time = datetime.now().replace(tzinfo=timezone.utc).isoformat()

        res = requests.post(
            'http://{0}:{1}/orders/complete'.format(URL, HOST), json={
            "courier_id": 1,
            "order_id": 1,
            "complete_time": complete_time
        })

        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.content.decode()), {"order_id": 1})

        courier = Courier.objects.get(courier_id=1)

        self.assertEqual(courier.orders, "3")
        self.assertEqual(courier.last_time, parse_datetime(complete_time))
        self.assertEqual(len(courier.complete_times.split(';')), 1)

        order = Order.objects.get(order_id=1)
        self.assertTrue(order.is_completed)
        self.assertEqual(order.complete_time, parse_datetime(complete_time))

    def test_idempotency(self):
        requests.post(
            'http://{0}:{1}/couriers'.format(URL, HOST), json=COURIERS)
        requests.post(
            'http://{0}:{1}/orders'.format(URL, HOST), json=ORDERS)
        res = requests.post(
            'http://{0}:{1}/orders/assign'.format(URL, HOST), json={"courier_id": 1})

        complete_time = datetime.now().replace(tzinfo=timezone.utc).isoformat()

        res = requests.post(
            'http://{0}:{1}/orders/complete'.format(URL, HOST), json={
            "courier_id": 1,
            "order_id": 1,
            "complete_time": complete_time
        })

        sleep(1)  # to make sure other times are different
        complete_time2 = datetime.now().replace(tzinfo=timezone.utc).isoformat()

        res = requests.post(
            'http://{0}:{1}/orders/complete'.format(URL, HOST), json={
            "courier_id": 1,
            "order_id": 1,
            "complete_time": complete_time2
        })

        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.content.decode()), {"order_id": 1})

        courier = Courier.objects.get(courier_id=1)

        self.assertEqual(courier.orders, "3")
        self.assertEqual(courier.last_time, parse_datetime(complete_time))
        self.assertEqual(len(courier.complete_times.split(';')), 1)

        order = Order.objects.get(order_id=1)
        self.assertTrue(order.is_completed)
        self.assertEqual(order.complete_time, parse_datetime(complete_time))

    def test_wrong_courier(self):
        requests.post(
            'http://{0}:{1}/couriers'.format(URL, HOST), json=COURIERS)
        requests.post(
            'http://{0}:{1}/orders'.format(URL, HOST), json=ORDERS)
        res = requests.post(
            'http://{0}:{1}/orders/assign'.format(URL, HOST), json={"courier_id": 1})

        complete_time = datetime.now().replace(tzinfo=timezone.utc).isoformat()

        res = requests.post(
            'http://{0}:{1}/orders/complete'.format(URL, HOST), json={
            "courier_id": 2,
            "order_id": 1,
            "complete_time": complete_time
        })

        self.assertEqual(res.status_code, 400)

    def test_completing_whole_delivery(self):
        requests.post(
            'http://{0}:{1}/couriers'.format(URL, HOST), json=COURIERS)
        requests.post(
            'http://{0}:{1}/orders'.format(URL, HOST), json=ORDERS)
        res = requests.post(
            'http://{0}:{1}/orders/assign'.format(URL, HOST), json={"courier_id": 1}
        )

        sleep(1)  # to make sure other times are different
        complete_time = datetime.now().replace(tzinfo=timezone.utc).isoformat()

        res = requests.post('http://{0}:{1}/orders/complete'.format(URL, HOST), json={
            "courier_id": 1,
            "order_id": 1,
            "complete_time": complete_time
        })

        sleep(1)  # to make sure other times are different
        complete_time = datetime.now().replace(tzinfo=timezone.utc).isoformat()

        res = requests.post('http://{0}:{1}/orders/complete'.format(URL, HOST), json={
            "courier_id": 1,
            "order_id": 3,
            "complete_time": complete_time
        })

        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.content.decode()), {"order_id": 3})

        courier = Courier.objects.get(courier_id=1)

        self.assertEqual(courier.orders, "")
        self.assertEqual(courier.last_time, parse_datetime(complete_time))
        self.assertEqual(len(courier.complete_times.split(';')), 2)

        order = Order.objects.get(order_id=3)
        self.assertTrue(order.is_completed)

        # differs from 2 seconds deduced from sleep no more than for 20%
        seconds = (parse_datetime(complete_time) - courier.assign_time).total_seconds()
        self.assertTrue(0.80 * 2 <= seconds <= 1.20 * 2)

        # must not differ from 1 second for more than 20% as well
        seconds = courier.min_average_delivery_time()
        self.assertTrue(0.80 * 1 <= seconds <= 1.20 * 1)


class GettingCourierInfoTestCase(TestCase):
    def setUp(self):
        Courier.objects.all().delete()
        Order.objects.all().delete()

    def tearDown(self):
        Courier.objects.all().delete()
        Order.objects.all().delete()

    # nothing must change
    def test_empty_courier_info(self):
        requests.post(
            'http://{0}:{1}/couriers'.format(URL, HOST), json=COURIERS)

        res = requests.get(
            'http://{0}:{1}/couriers/1'.format(URL, HOST), json=COURIERS)

        self.assertEqual(res.status_code, 200)

        returned = json.loads(res.content.decode())

        self.assertTrue('courier_id' in returned)
        self.assertTrue('courier_type' in returned)
        self.assertTrue('working_hours' in returned)
        self.assertTrue('earnings' in returned)
        self.assertTrue('rating' not in returned)
        self.assertEqual(returned['courier_id'], 1)
        self.assertEqual(returned['courier_type'], "foot")
        self.assertEqual(returned['regions'], [1, 12, 22])
        self.assertEqual(
            returned['working_hours'],
            ["11:35-14:05", "09:00-11:00"]
        )
        self.assertEqual(returned['earnings'], 0)

    # nothing must change
    def test_assigned_courier_info(self):
        requests.post(
            'http://{0}:{1}/couriers'.format(URL, HOST), json=COURIERS)
        requests.post(
            'http://{0}:{1}/orders'.format(URL, HOST), json=ORDERS)
        requests.post(
            'http://{0}:{1}/orders/assign'.format(URL, HOST), json={"courier_id": 1})

        res = requests.get(
            'http://{0}:{1}/couriers/1'.format(URL, HOST), json=COURIERS)

        self.assertEqual(res.status_code, 200)

        returned = json.loads(res.content.decode())

        self.assertTrue('courier_id' in returned)
        self.assertTrue('courier_type' in returned)
        self.assertTrue('working_hours' in returned)
        self.assertTrue('earnings' in returned)
        self.assertTrue('rating' not in returned)
        self.assertEqual(returned['courier_id'], 1)
        self.assertEqual(returned['courier_type'], "foot")
        self.assertEqual(returned['regions'], [1, 12, 22])
        self.assertEqual(
            returned['working_hours'], 
            ["11:35-14:05", "09:00-11:00"]
        )
        self.assertEqual(returned['earnings'], 0)

    # nothing must change
    def test_completed_single_order_courier_info(self):
        requests.post(
            'http://{0}:{1}/couriers'.format(URL, HOST), json=COURIERS)
        requests.post(
            'http://{0}:{1}/orders'.format(URL, HOST), json=ORDERS)
        requests.post(
            'http://{0}:{1}/orders/assign'.format(URL, HOST), json={"courier_id": 1})

        complete_time = datetime.now().replace(tzinfo=timezone.utc).isoformat()

        requests.post('http://{0}:{1}/orders/complete'.format(URL, HOST), json={
            "courier_id": 1,
            "order_id": 1,
            "complete_time": complete_time
        })

        res = requests.get(
            'http://{0}:{1}/couriers/1'.format(URL, HOST), json=COURIERS)

        self.assertEqual(res.status_code, 200)

        returned = json.loads(res.content.decode())

        self.assertTrue('courier_id' in returned)
        self.assertTrue('courier_type' in returned)
        self.assertTrue('working_hours' in returned)
        self.assertTrue('earnings' in returned)
        self.assertTrue('rating' not in returned)
        self.assertEqual(returned['courier_id'], 1)
        self.assertEqual(returned['courier_type'], "foot")
        self.assertEqual(returned['regions'], [1, 12, 22])
        self.assertEqual(
            returned['working_hours'], 
            ["11:35-14:05", "09:00-11:00"]
        )
        self.assertEqual(returned['earnings'], 0)

    # must change
    def test_completed_delivery_courier_info(self):
        requests.post(
            'http://{0}:{1}/couriers'.format(URL, HOST), json=COURIERS)
        requests.post(
            'http://{0}:{1}/orders'.format(URL, HOST), json=ORDERS)
        requests.post(
            'http://{0}:{1}/orders/assign'.format(URL, HOST), json={"courier_id": 1})

        sleep(1)
        complete_time = datetime.now().replace(tzinfo=timezone.utc).isoformat()

        requests.post('http://{0}:{1}/orders/complete'.format(URL, HOST), json={
            "courier_id": 1,
            "order_id": 1,
            "complete_time": complete_time
        })

        sleep(1)
        complete_time = datetime.now().replace(tzinfo=timezone.utc).isoformat()

        requests.post('http://{0}:{1}/orders/complete'.format(URL, HOST), json={
            "courier_id": 1,
            "order_id": 3,
            "complete_time": complete_time
        })

        res = requests.get(
            'http://{0}:{1}/couriers/1'.format(URL, HOST), json=COURIERS)

        self.assertEqual(res.status_code, 200)

        returned = json.loads(res.content.decode())

        self.assertTrue('courier_id' in returned)
        self.assertTrue('courier_type' in returned)
        self.assertTrue('working_hours' in returned)
        self.assertTrue('earnings' in returned)
        self.assertTrue('rating' in returned)
        self.assertEqual(returned['courier_id'], 1)
        self.assertEqual(returned['courier_type'], "foot")
        self.assertEqual(returned['regions'], [1, 12, 22])
        self.assertEqual(
            returned['working_hours'],
            ["11:35-14:05", "09:00-11:00"]
        )
        self.assertEqual(returned['earnings'], 500 * 2)

        # delivery times are always 1 second because of sleep(1)
        # but since there may be precision errors
        # it is better to assume the value should not differ for more than 20%
        lower_bound = (3600 - min(1.2 * 1, 3600)) / 3600 * 5
        upper_bound = (3600 - min(0.8 * 1, 3600)) / 3600 * 5

        self.assertTrue(lower_bound <= returned['rating'] <= upper_bound)
