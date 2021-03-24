URL = "127.0.0.1"
HOST = "8080"

COURIERS = {
    "data": [
        {
            "courier_id": 1,
            "courier_type": "foot",
            "regions": [1, 12, 22],
            "working_hours": ["11:35-14:05", "09:00-11:00"]
            },
        {
            "courier_id": 2,
            "courier_type": "bike",
            "regions": [22],
            "working_hours": ["09:00-18:00"]
            },
        {
            "courier_id": 3,
            "courier_type": "car",
            "regions": [12, 22, 23, 33],
            "working_hours": []
            },
    ]
}

COURIERS_2 = {
    "data": [
        {
            "courier_id": 5,
            "courier_type": "foot",
            "regions": [1, 2, 3],
            "working_hours": ["11:00-11:02"]
        },
        {
            "courier_id": 10,
            "courier_type": "car",
            "regions": [3],
            "working_hours": ["00:00-00:30", "01:00-02:00"]
        }
    ]
}

WRONG_COURIERS = {
    "data": [
        {
            "courier_id": 1,
            "some_wrong_text": "somewhat",
            "courier_type": "foot"
        },
        {
            "courier_id": 2,
            "courier_type": "bike",
            "regions": [22],
            "working_hours": ["09:00-18:00"]
        }
    ]
}

ORDERS = {
    "data": [
        {
            "order_id": 1,
            "weight": 0.23,
            "region": 12,
            "delivery_hours": ["09:00-18:00"]
        },
        {
            "order_id": 2,
            "weight": 15,
            "region": 1,
            "delivery_hours": ["09:00-18:00"]
        },
        {
            "order_id": 3,
            "weight": 0.01,
            "region": 22,
            "delivery_hours": ["09:00-12:00", "16:00-21:30"]
        },
    ]
}

WRONG_ORDERS = {
    "data": [
        {
            "order_id": 5,
            "weight": 0.001,
            "region": 12,
            "delivery_hours": ["09:00-18:00"]
        },
        {
            "order_id": 7,
            "weight": 15,
            "some_text": "somewhat",
            "region": 1,
            "delivery_hours": ["09:00-18:00"]
        },
        {
            "order_id": 11,
            "weight": 0.01,
            "region": 22,
        },
        { # good one
            "order_id": 27,
            "weight": 0.01,
            "region": 22,
            "delivery_hours": ["09:00-12:00", "16:00-21:30"]        
        },
        {
            "order_id": 25,
            "weight": 50.1,
            "region": 12,
            "delivery_hours": ["01:00-18:00"]            
        }
    ]
}