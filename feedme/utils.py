# -*- coding: utf-8 -*-

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from datetime import date, timedelta
import logging

from feedme.models import Balance, Order, OrderLine, Poll

logger = logging.getLogger(__name__)
try:
    # Django 1.7 way for importing custom user
    from django.contrib.auth import AUTH_USER_MODEL
    User = AUTH_USER_MODEL
except ImportError:
    # Django 1.6 way for importing custom user, will crash in Django 1.7
    from django.contrib.auth import get_user_model
    User = get_user_model()


def get_feedme_groups():
    order_ctype = ContentType.objects.get_for_model(Order)
    permission = Permission.objects.get(codename='view_order', content_type=order_ctype)
    return [g for g in Group.objects.all() if permission in g.permissions.all()]


# Get or create balance for a user
def get_or_create_balance(user):
    return Balance.objects.get_or_create(user=user)[0]


# Check that the user has enough funds
def validate_user_funds(user, amount):
    get_or_create_balance(user)
    return user.balance.get_balance() >= amount


# The actual function for payment
def pay(user, amount):
    balance = get_or_create_balance(user)
    balance.withdraw(amount)  # This returns True/False whether or not the payment was possible.
    balance.save()


# Deposit of funds
def handle_deposit(data):
    balance = get_or_create_balance(data['user'])
    print('updating %s' % balance)
    amount = data['amount']
    if amount >= 0:
        balance.deposit(amount)
    else:
        balance.withdraw(amount)


# yes
def get_next_tuesday():
    today = date.today()
    day = today.weekday()
    if day < 1:
        diff = timedelta(days=(1 - day))
    elif day > 1:
        diff = timedelta(days=(7 - day + 1))
    else:
        diff = timedelta(days=0)

    return today + diff


def get_next_wednesday():
    today = date.today()
    day = today.weekday()
    if day < 2:
        diff = timedelta(days=(2 - day))
    elif day > 2:
        diff = timedelta(days=(7 - day + 2))
    else:
        diff = timedelta(days=0)

    return today + diff


def is_admin(request):
    return request.user.has_perm('feedme.change_order')


# Gets latest active order
def get_order(group=None):
    if Order.objects.filter(group=group):
        orders = Order.objects.filter(group=group).order_by('-id')
        for order in orders:
            if order.active:
                return order
    else:
        return None


# Gets latest active poll
def get_poll(group=None):
    if Poll.objects.filter():
        if Poll.objects.filter(group=group, active=True).count() >= 1:
            return Poll.objects.filter(group=group, active=True).order_by('-id')[0]
        else:
            return None


# Manually parses users to validate user funds on buddy-add on initial orderline creation
def manually_parse_users(form):
    li = str(form).split('<select')
    potential_users = li[1].split('<option')
    user_ids = []
    for user in potential_users:
        if 'selected' in user:
            user_ids.append(user.split('value="')[1].split('"')[0])
    users = []
    for i in user_ids:
        users.append(User.objects.get(pk=i))
    return users


# Checks if user is in another orderline
def in_other_orderline(order, user):
    r1 = ""
    r2 = ""
    if order:
        if order.orderline_set:
            if order.orderline_set.filter(creator=user.id):
                r1 = user == order.orderline_set.filter(creator=user.id)[0].creator
            if order.orderline_set.filter(users=user.id):
                r2 = user in order.orderline_set.filter(users=user.id)[0].users.all()
    return r1 or r2


def get_orderline_for_order_and_creator(order, creator):
    created = True
    try:
        orderline = OrderLine.objects.get(order=order, creator=creator)
        created = False
    except OrderLine.DoesNotExist:
        orderline = OrderLine()
        orderline.creator = creator
    return orderline, created


def validate_users_funds(users, price):
    # Temporarily calculate price to pay per user, check if all users have sufficient funds
    price /= len(users)
    unsufficient_funds_users = []
    for user in users:
        if not validate_user_funds(user, price):
            unsufficient_funds_users.append(user)
    return unsufficient_funds_users


# Validation of orderline
def check_orderline(group, creator, price, buddies=None):
    order = get_order(group)

    orderline, created = get_orderline_for_order_and_creator(order, creator)

    logger.debug('Validating %s orderline for "%s" (%.2f kr) by "%s".' %
                 ("new" if created else "existing", order, price, creator))

    # Update users
    users = [orderline.creator]
    users.extend(buddies)

    unsufficient_funds_users = validate_users_funds(users, price)

    if order.use_validation and unsufficient_funds_users:
        logger.debug("Validation failed. Users unable to join orderline: %s" % unsufficient_funds_users)
        return False
    else:
        logger.debug("Validation successful.")
        return True


# Handle payment
def handle_payment(request, order):
    orderlines = order.orderline_set.all()

    # Initialize empty lists for users
    paid = []
    already_paid = []
    negatives = []

    # Go through each orderline, paying it for each user
    for orderline in orderlines:
        if not orderline.paid_for:
            amount = orderline.get_price_to_pay()
            logger.info('Paying orderline for "%s" (%.2f kr, %.2f kr ea) for "%s".'
                        % (orderline.order, orderline.price, amount, orderline.users.all()))
            # Pay for each user
            for user in orderline.users.all():
                pay(user, amount)
                paid.append(user.get_username())
                if user.balance.get_balance() < 0:
                    negatives.append(user.get_username())
            orderline.paid_for = True
            orderline.save()

        else:
            # Tell that these have already been paid
            already_paid.append(orderline.creator.get_username())
            if orderline.users.all().count() > 0:
                for user in orderline.users.all():
                    if user == orderline.creator:
                        logger.warn('Creator (%s) both in users and creator for orderline #%i' % (user, orderline.id))
                    else:
                        already_paid.append(user.get_username())

    # Disable the order
    order.active = False
    order.save()

    return paid, already_paid, negatives
