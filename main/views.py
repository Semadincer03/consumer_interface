import redis
import json
import django.utils.crypto as crypto
from models import Hotel, Destination, Booking
from hotelspro_client.book import BookProcessor
from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

username = 'semadincer'
password = 'qwer321'
book_processor = BookProcessor('http://localhost:8001/api/v2/',
                               username, password)

redis_cache = redis.StrictRedis(host='localhost', port=6379)
sd_destination = Destination.objects.values_list()
sd_hotel = Hotel.objects.values_list()


@login_required()
def home(request):
    username = None
    if request.user.is_authenticated():
        username = request.user.username
    request.session['user'] = username
    return render(request, 'home.html', {'user': username})


@login_required()
def search(request):
    return render(request, 'search.html', {'user': request.session['user']})


@login_required()
def results(request):
    if request.method == 'GET':
        checkin = request.GET.get('checkin')
        checkout = request.GET.get('checkout')
        pax = request.GET.get('pax')
        destination = request.GET.get('destination')

        request.session['checkin'] = checkin
        request.session['checkout'] = checkout
        request.session['pax'] = pax
        request.session['destination'] = destination

        for item in sd_destination:
            if item[2] == destination:
                dest_code = item[1]

        result_list = list()
        result = get_from_cache({'checkin': checkin, 'checkout':
            checkout, 'pax': pax, 'destination_code': dest_code,
                                 'client_nationality': 'tr', 'currency':
                                     'USD'})

        # result_list = [{'hotel_code': sd_hotel_code[1],
        #                 'hotel_name': sd_hotel_code[2]}
        #                for hotel in result['results']
        #                for sd_hotel_code in sd_hotel
        #                if hotel['hotel_code'] in sd_hotel_code[1]]

        for hotel in result['results']:
            for sd_hotel_code in sd_hotel:
                if hotel['hotel_code'] in sd_hotel_code[1]:
                    min_price = min(
                        [float(i['price']) for i in hotel['products']])

                    result_list.append({
                        'hotel_code': sd_hotel_code[1],
                        'hotel_name': sd_hotel_code[2],
                        'min_cost': min_price
                    })
                    # request.session['hotel_name'] = sd_hotel_code[2]
        return render_to_response('results.html', {'result_list': result_list})


@login_required()
def availability(request, hotel_code):
    session = request.session
    result = get_from_cache({'checkin': session['checkin'], 'checkout':
        session['checkout'], 'pax': session['pax'], 'hotel_code': hotel_code,
                               'client_nationality': 'tr', 'currency':
                                   'USD'})

    availability_list = list()

    request.session['hotel_name'] = [hotel for hotel in sd_hotel
                                     if hotel_code in hotel[1]][0][2]

    # for hotel in sd_hotel:
    #     if hotel_code in hotel[1]:
    #         request.session['hotel_name'] = hotel[2]

    room = 1
    for result in result['results']:
        for product in result['products']:
            availability_list.append({
                'room': room,
                'product_code': product['code'],
                'room_category': product['rooms'][0]['room_category'],
                'room_description': product['rooms'][0]['room_description'],
                'room_type': product['rooms'][0]['room_type'],
                'meal_type': product['meal_type'],
                'price': product['price'],
                'currency': product['currency']

            })
            room += 1

    sorted_room = sorted(availability_list, key=lambda k: float(k["price"]))
    return render_to_response('availability.html',
                              {'availability_list': sorted_room,
                               'hotel_name': request.session['hotel_name']})


@login_required()
def provision(request, product_code):
    pax = list()
    result_dict = dict()
    session = request.session

    result_dict['hotel'] = session['hotel_name']
    result_dict['destination'] = session['destination']

    pax_generator = xrange(int(request.session['pax']))
    result = book_processor.provision(product_code)

    if request.method == 'POST':
        name = request.POST.getlist('name')

        for name in name:
            name_list = name.split()
            last_name = name_list[-1]
            name_list.pop()
            first_name = ' '.join(name_list)
            pax.append('1,{},{},adult'.format(first_name, last_name))

        book_result = book_processor.book(result['code'], {'name': pax})

        if book_result['status'] == 'succeeded':
            bookings = book_processor.bookings(book_result['code'])

            request.session['book_code'] = book_result['code']

            room = book_result['confirmation_numbers'][0]['rooms'][0]
            booking = Booking.objects.create(
                user=request.user,
                provision_code=result['code'],
                hotel_code=book_result['hotel_code'],
                booking_code=crypto.get_random_string(length=12),
                coral_booking_code=book_result['code'],
                room_type=room['room_type'],
                room_description=room['room_description'],
                pax_count=request.session['pax'],
                pax_names=", ".join(request.POST.getlist('name')),
                price=book_result['price'],
                status=book_result['status']
            )
            booking.save()

            info = message(request, response=bookings)
            subject, to = 'Booking Info', request.POST.get('email')
            email = EmailMultiAlternatives(subject, body=info,
                                           to=[to])
            email.content_subtype = 'html'
            email.send()

            return render_to_response('book.html', {'book_result': bookings})

    else:
        result_dict['price'] = result['price']

    return render(request, 'provision.html', {'product_code': product_code,
                                              'pax_generator': pax_generator,
                                              'result_dict': result_dict})


@login_required
def bookings(request):
    registered_bookings = Booking.objects.filter(
        user=request.user,
        status='succeeded').values(
        'hotel_code', 'booking_code', 'room_type', 'room_description',
        'pax_names', 'price').order_by('-id')

    return render(request, 'bookings.html',
                  {'bookings': registered_bookings})


def get_from_cache(search_params):
    if redis_cache.get(search_params):
        result = json.loads(redis_cache.get(search_params))
    else:
        result = book_processor.search(search_params)
        redis_cache.set(search_params, json.dumps(result), ex=3600)
    return result


def message(request, response):
    return render_to_string('confirm.html',
                            {'book_response': response,
                             'hotel_name': request.session['hotel_name']})
