from django.http import HttpResponseNotFound, JsonResponse, HttpResponseBadRequest
from .models import Courier, Order
from datetime import datetime, timezone
from django.utils.dateparse import parse_datetime
from json import loads
import pytz


def load_couriers(request):
    GOOD_PARAMS = ['courier_id', 'courier_type', 'regions', 'working_hours']
    bad = {
        "validation_error": {
            "couriers": []
        }
    }
    validated = {"couriers": []}
    try:
        data = loads(request.body)["data"]

        for curdict in data:
            if len(curdict) != 4:
                bad["validation_error"]["couriers"].append(
                    {'id': curdict['courier_id']}
                )

            else:
                for key, val in curdict.items():
                    if key not in GOOD_PARAMS:
                        bad["validation_error"]["couriers"].append(
                            {'id': curdict['courier_id']}
                        )
                        break

                if curdict['courier_type'] != 'car' and curdict['courier_type'] != 'foot' and curdict['courier_type'] != 'bike':
                    bad["validation_error"]["couriers"].append(
                        {'id': curdict['courier_id']}
                    )
                else:
                    validated["couriers"].append({'id': curdict['courier_id']})

        if bad["validation_error"]["couriers"]:
            return JsonResponse(bad, reason="HTTP 400 Bad request", status=400)

        for curdict in data:
            temp_regions = (
                ';'.join(map(str, curdict['regions'])) if curdict['regions'] else ''
            )
            temp_working_hours = (';'.join(curdict['working_hours'])
                                  if curdict['working_hours'] else '')

            current_courier = Courier(courier_id=curdict['courier_id'],
                                      courier_type=curdict['courier_type'],
                                      regions=temp_regions,
                                      working_hours=temp_working_hours)

            current_courier.save()

        return JsonResponse(validated, status=201)
    except Exception as excp:
        return HttpResponseNotFound(excp)


def process_couriers(request, need_id):
    GOOD_PARAMS = ['courier_type', 'regions', 'working_hours']
    try:
        if request.method == "PATCH":
            data = loads(request.body)

            for key in data.keys():
                if key not in GOOD_PARAMS:
                    return HttpResponseBadRequest('HTTP 400 Bad Request')

                if isinstance(data[key], list):
                    data[key] = (';'.join(map(str, data[key]))
                                 if data[key] else '')

            courier = Courier.objects.get(courier_id=need_id)
            courier.save(dict_update=data)

            new_orders = []
            weight = courier.max_possible_weight()

            for order_id in courier.orders.split(';'):
                if not order_id:
                    continue
                order = Order.objects.get(order_id=int(order_id))
                if not order.check_courier(courier) or weight - order.weight < 0:
                    order.courier = None
                    order.save()
                else:
                    new_orders.append(order_id)
                    weight -= order.weight

            courier.orders = (';'.join(new_orders) if new_orders else '')
            courier.save()

            return JsonResponse(courier.transform(), status=200)
        elif request.method == "GET":
            courier = Courier.objects.get(courier_id=need_id)
            answer = courier.transform()
            if courier.completed_orders:
                answer['rating'] = (3600 - min(courier.min_average_delivery_time(), 3600)) / 3600 * 5
            answer['earnings'] = 0
            for transport in courier.completed_orders.split(';'):
                C = 0
                if transport == "foot":
                    C = 2
                elif transport == 'bike':
                    C = 5
                elif transport == 'car':
                    C = 9
                answer['earnings'] += 500 * C
            return JsonResponse(answer, status=200)
        else:
            raise Exception('No support for this method')
    except Exception as excp:
        return HttpResponseNotFound(excp)


def load_orders(request):
    GOOD_PARAMS = ['order_id', 'weight', 'region', 'delivery_hours']
    bad = {
        "validation_error": {
            "orders": []
        }
    }
    validated = {"orders": []}
    try:
        if request.method != "POST":
            raise Exception
        data = loads(request.body)["data"]

        for curdict in data:
            if len(curdict) != 4:
                bad["validation_error"]["orders"].append(
                    {'id': curdict['order_id']}
                )

            else:
                for key, val in curdict.items():
                    if key not in GOOD_PARAMS:
                        bad["validation_error"]["orders"].append(
                            {'id': curdict['order_id']}
                        )
                        break

                if curdict['weight'] < 0.01 or curdict['weight'] > 50:
                    bad["validation_error"]["orders"].append(
                        {'id': curdict['order_id']}
                    )
                else:
                    validated["orders"].append({'id': curdict['order_id']})

        if bad["validation_error"]["orders"]:
            return JsonResponse(bad, status=400)

        for curdict in data:
            temp_delivery_hours = (';'.join(curdict['delivery_hours'])
                                   if curdict['delivery_hours'] else '')
            current_order = Order(order_id=curdict['order_id'],
                                  weight=curdict['weight'],
                                  region=curdict['region'],
                                  delivery_hours=temp_delivery_hours)
            current_order.save()

        return JsonResponse(validated, status=201)
    except Exception as excp:
        return HttpResponseNotFound(excp)


def assign_orders(request):
    result = {
        "orders": [],
    }
    try:
        if request.method != "POST":
            raise Exception
        courier_id = loads(request.body)['courier_id']

        courier = Courier.objects.get(courier_id=courier_id)
        if courier.orders:
            orders = courier.orders.split(';')
            for order in orders:
                result['orders'].append({'id': int(order)})
            result['assign_time'] = str(courier.assign_time)
            return JsonResponse(result, status=200)

        regions = list(map(int, courier.regions.split(';')))
        temp_objects_set = (Order.objects
                            .filter(region__in=regions)
                            .filter(courier__isnull=True))
        weight = courier.max_possible_weight()
        for order in temp_objects_set:
            if order.check_courier(courier) and weight - order.weight >= 0:
                result["orders"].append({"id": order.order_id})
                weight -= order.weight

        if result["orders"]:
            result["assign_time"] = (datetime.now()
                                        .replace(tzinfo=timezone.utc)
                                        .isoformat())
            for id_dict in result["orders"]:
                order_id = id_dict['id']
                order = Order.objects.get(order_id=order_id)
                order.assign_time = result["assign_time"]
                order.courier = courier
                order.save(force_update=True)
    
                symbol = (';' if courier.orders else '')
                courier.orders += symbol + str(order_id)
            courier.assign_type = courier.courier_type
            courier.last_time = result["assign_time"]
            courier.assign_time = result["assign_time"]
            courier.save()

        return JsonResponse(result, status=200)
    except Courier.DoesNotExist:
        return HttpResponseBadRequest('HTTP 400 Bad Request')
    except Exception as excp:
        return HttpResponseNotFound(excp)


def complete_order(request):
    try:
        if request.method != "POST":
            raise Exception
        data = loads(request.body)

        courier = Courier.objects.get(courier_id=data['courier_id'])
        order = Order.objects.get(order_id=data['order_id'])

        if order.courier != courier:
            return HttpResponseBadRequest('HTTP 400 Bad Request')

        orders = list(map(int, courier.orders.split(';')))

        if not order.is_completed:
            orders.remove(data['order_id'])

            if not orders:
                symbol = (';' if courier.completed_orders else '')
                courier.completed_orders = symbol + str(courier.assign_type)

            order.complete_time = (parse_datetime(data['complete_time'])
                                   .replace(tzinfo=pytz.utc))
            courier.orders = (';'.join(map(str, orders)) if orders else '')

            seconds_spent = int(
                (order.complete_time - courier.last_time).total_seconds()
            )

            symbol = ''
            if courier.complete_times:
                symbol = ';'
            courier.complete_times += symbol + str(seconds_spent) + ',' + str(order.region)
            courier.last_time = order.complete_time
            order.is_completed = True

            order.save()
            courier.save()
        return JsonResponse({"order_id": data['order_id']}, status=200)
    except IndexError:
        return HttpResponseBadRequest('HTTP 400 Bad Request')
    except Exception as excp:
        return HttpResponseNotFound(excp)
