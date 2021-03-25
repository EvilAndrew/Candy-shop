
# Candy-shop

## The description

This is a REST-service written on Python 3 and Django.
Its idea is to manage is to simulate couriers-orders system.
Totally the application has 6 handlers:
#### 1. POST /couriers

One has to send a **JSON** file to the input, and it must have the following structure:
```html
{
	"data": [
		{
			"courier_id": courier_id,
			"courier_type": courier_type,
			"regions": [reg1, reg2, ...],
			"working_hours": [time1, time2, ...]
		}
		{
			"courier_id": ...,
			...
		},
		...
	]
}
```

**courier_id** is an **integer**
**courier_type** is a **string** equal to **"foot"**, **"car"** or **"bike"**
**regions** is a **list of integers**
**working_hours** is a **list of strings**, and their format is strictly **HH:MM-HH:MM**
**courier_id** must be unique for all couriers
**regions** are used later for assigning appropriate orders
**working**_hours are used later for assigning appropriate orders
**courier_type** is responsible for maximum possible weight courier can have:
	10 kilo in case of "foot",
	15 kilo in case of "bike",
	50 kilo in case of "car"
**Note:** If the whole data is not validated, for example, if there is any field not equal to one of there four, then the whole query is canceled, nothing is added, and **HTTP 400 Bad Request** is returned. Otherwise **HTTP 201 Created** is returned and everything is saved to the database.
In case of success the following-like **JSON** object of all IDs is returned:
```html
{
	"couriers": [{"id": courier_id_1}, {"id": courier_id_2}, ...]
}
```
Otherwise the following-like **JSON** object of all _bad_ IDs is returned:
```html
{
	"validation_error": {
		"couriers": [{"id": courier_id_1}, {"id": courier_id_2}, ...]
	}
}
```
********************
#### 2. PATCH /couriers/$courier_id

One has to send a **JSON** file to the input, and it must have the following structure:
```html
{
	"regions": [...],
	"courier_type": ...,
	"working_hours": [...]
}
```

Any of {"regions", "courier_type", "working_hours"} may not be in the request, and those, if absent, will not be changed, for example, this is still a correct query:

```html
{
	"regions": [...]
}
```

In case the request is validated, the following **JSON** object of updated information is returned:
```html
{
	"courier_id": courier_id,
	"courier_type": courier_type,
	"regions": [...],
	"working_hours": [...]
}
```

**Note:** if there is any field not equal to one of there four, the whole query is canceled, nothing is added, and **HTTP 400 Bad Request** is returned. Otherwise **HTTP 200 OK** is returned and the database is updated. If the courier has a delivery in the moment, and some parameters are now changed, there may occur to be orders which can't be handled anymore. There orders become free and may be assigned later to someone else. In this case those are deleted from the delivery (it is important that if the assigned orders become empty after the patching, the delivery is not counted as a completed one, regardless of whether it was already partially completed before)
********************
#### 3. POST /orders

Similar to the first **POST** query, new orders are created via a **JSON** file:

```html
{
	"data": [
		{
			"order_id": order_id,
			"weight": order_weight,
			"regions": [...],
			"delivery_hours": [...]
		}
		{
			"order_id": ...,
			...
		},
		...
	]
}
```

**order_id** is an **integer** (must be unique for all orders)
**weight** is a **float between 0.01 and 50**
**regions** is a **list of integers**
**delivery_hours** is a **list of strings**, and their format is strictly **HH:MM-HH:MM**

**Note:** If the whole data is not validated, for example, if there is any field not equal to one of there four, then the whole query is canceled, nothing is added, and **HTTP 400 Bad Request** is returned. Otherwise **HTTP 201 Created** is returned and everything is saved to the database.
The return is similar to the first **POST** query: (in case of **HTTP 400**)
```html
{
	"validation_error": {
		"orders": [...]
	}
}
```
and, in case of success:
```html
{
	"orders": [...]
}
```
********************
#### 4. POST /orders/assign

The input is **JSON** object:

```html
{
	"courier_id": id
}
```
If the **id** is not existent, **HTTP 400 Bad Requst** is returned.
Otherwise, **HTTP 200 OK** and the following objects are returned:
```html
{
	"orders": [{"id": order_id_1}, {"id": order_id_2}, ...]
	"assign_time": assign_time
}
```
assign_time is the current server time in **UTC RFC 3339** format

The handler is idempotent, i.e. **assign_time** will only change in case it is the first calling or the previous delivery is fully completed. Otherwise, **orders** is the current delivery and **assign_time** is the time the orders were firstly assigned.

**Note:** ***order X*** may be assigned to a courier if: 
1. Current assigned orders' weight + ***X***'s weight <= total weight of the courier (dependent on the courier's type)
2. ***X*** has not been assigned to any other courier by the moment of the handler's calling
3. There is a mutual region
4. Some of ***X***'s delivery_hours and some of the courier's working_hours intersect. It is important that **12:00-13:00** does not have an intersection with **11:30-12:00** and with **13:00-13:47**, because the borders are not considered

********************
#### 5. POST /orders/complete

The input is **JSON** object:

```html
{
	"courier_id": courier_id,
	"order_id": order_id,
	"complete_time": complete_time
}
```

**complete_time** must be in the format of **RFC 3339**
In case **order_id** is not in the current courier's delivery, or any of the IDs is not existent, **HTTP 400 Bad Request** is returned.
Otherwise:
```html
HTTP 200 OK
{
	"order_id": order_id
}
```

**Note:** if the order is already completed, its **complete_time** in the database will not change. Note that if the order is the last of courier's delivery, then the courier's delivery counter receives +1.

********************
### 6. GET /courier_id/$courier_id

The handler's return is an information about courier with the **courier_id**:
```html
{
	"courier_id": courier_id,
	"courier_type": ...,
	"regions": ...,
	"working_hours": ...,
	"rating": ...,
	"earnings": ...
}
```
Rating is a **float number** calculated by the next formula:
```html
5 * (3600 - min(T, 3600)) / 3600
```
***T*** is the minimum of all average times in seconds through all visited regions.
**earnings** is calculated as follows:
	```∑(500 * C_i)```, where ```C_i``` is a coefficient depending on courier's type _in the moment of assignment_ (2 for **foot**, 5 for **bike**, 9 for **car**)
A delivery time is a difference between order's **complete_time** and **assign_time** if the order is the first completed in its delivery, and between **complete_time** and the previous order's **complete_time** (**last_time** in **Courier** model is used for the purposes, check _models.py_ for the clarification).

**Note**: rating will not be returned in case a courier has not completed any delivery. Also, if there is no completed order within a certain region, the average time will not be counted to the rating at all.

## Necessary installation
The application has been tested with the following:
```
1. Python 3.8.6
2. django 3.1.7
3. requests 2.25.1
4. json 2.0.9
5. datetime (native Python library)
6. pytz 2021.1
7. time (native python library)
```
The preinstallation is necessary for the application's launch.

## Running the application

To start the application one has to run the following command:

```hmtl
python3 manage.py runserver 0.0.0.0:8080
```
The ***python*** part may differ depending on your system's settings, but ***runserver 0.0.0.0:8080*** part is independent.

```manage.py``` is located in the repository's _yandex_school_ folder

Now anyone in your network may refer to the application via your device's IP.
In your case it may look as _127.0.0.1:8080_

## Testing

Some testing is provided in the repository.

One may launch it with the command:

```html
python3 manage.py test
```
As in the previous case, ***python*** part may be different for you.

**Note:** ```runserver``` command has to be sent before the testing, i.e. the server has to be launched while testing. The whole testing procedure is written in ```tests.py```
