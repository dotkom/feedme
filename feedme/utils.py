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
    """
    Get the Group objects with Permission to use feedme
    :return: A list of Group objects
    :rtype: Group
    """
    order_ctype = ContentType.objects.get_for_model(Order)
    permission = Permission.objects.get(codename='view_order', content_type=order_ctype)
    return [g for g in Group.objects.all() if permission in g.permissions.all()]


def get_or_create_balance(user):
    return Balance.objects.get_or_create(user=user)[0]


def validate_user_funds(user, amount):
    """
    Make sure that a User can pay the given amount given their Balance.
    :param user: The User to validate
    :param amount: The amount to validate
    :return: Whether the User can complete the Transaction or not.
    :rtype: bool
    """
    get_or_create_balance(user)
    return user.balance.get_balance() >= amount


def pay(user, amount):
    """
    Pay a given amount for a given user.
    :param user: The User to pay for.
    :param amount: The amount to pay.
    :return: None
    :rtype: None
    """
    balance = get_or_create_balance(user)
    balance.withdraw(amount)  # This returns True/False whether or not the payment was possible.
    balance.save()


def handle_deposit(data):
    """
    Handles depositing funds using a generic data object.
    :param data: A Generic data object.
    :return: None
    :rtype: None
    """
    balance = get_or_create_balance(data['user'])
    print('updating %s' % balance)
    amount = data['amount']
    if amount >= 0:
        balance.deposit(amount)
    else:
        balance.withdraw(amount)


# yes
def get_next_tuesday():
    """
    Gets the next Tuesday (useful to automatically populate the "Poll deadline" form field).
    :return: A datetime for the next Tuesday
    :rtype: date
    """
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
    """
    Gets the next Wednesday (useful to automatically populate the "Order deadline" form field).
    :return: A datetime for the next Wednesday
    :rtype: date
    """
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
    """
    Defines if the user in the request is an administrator for the Order
    :param request: Django HTTP Request Object
    :return: Whether the User is administrator or not.
    :rtype: bool
    """
    return request.user.has_perm('feedme.change_order')


def get_order(group=None):
    """
    Get the latest active Order.
    :param group: A Group to get the latest active Order for.
    :return: An active Order
    :rtype: Order
    """
    if Order.objects.filter(group=group):
        orders = Order.objects.filter(group=group).order_by('-id')
        for order in orders:
            if order.active:
                return order
    else:
        return None


def get_poll(group=None):
    """
    Get the latest active Poll.
    :param group: A Group to get the latest active Poll for.
    :return: An active Poll
    :rtype: Poll
    """
    if Poll.objects.filter():
        if Poll.objects.filter(group=group, active=True).count() >= 1:
            return Poll.objects.filter(group=group, active=True).order_by('-id')[0]
        else:
            return None


def manually_parse_users(form):
    """
    A hacky way to find out which users are in the Orderline, to do Orderline validation on.
    :param form: An HTML form.
    :return: The Users partaking in the Orderline
    :rtype: User
    """
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


def in_other_orderline(order, user):
    """
    Checks if a User partakes in an Orderline in the given Order.
    :param order: The Order to verify against.
    :param user: The User to check.
    :return: Whether the User is in another Orderline or not.
    :rtype: bool
    """
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
    """
    Get the OrderLine for a User and an Order.
    :param order: The Order to get an Orderline from.
    :param creator: The User who created the Order.
    :return: An Orderline as well as a Boolean if a new Order was created.
    :rtype: OrderLine
    """
    created = True
    try:
        orderline = OrderLine.objects.get(order=order, creator=creator)
        created = False
    except OrderLine.DoesNotExist:
        orderline = OrderLine()
        orderline.creator = creator
    return orderline, created


def validate_users_funds(users, price):
    """
    Validate if a given set of Users can pay a given price.
    :param users: A list of Users
    :param price: A price to pay
    :return: A list of Users not being able to pay.
    :rtype: User
    """
    # Temporarily calculate price to pay per user, check if all users have sufficient funds
    price /= len(users)
    unsufficient_funds_users = []
    for user in users:
        if not validate_user_funds(user, price):
            unsufficient_funds_users.append(user)
    return unsufficient_funds_users


def check_orderline(group, creator, price, buddies=None):
    """
    Health check an Orderline.
    :param group: The Group to validate the Orderline for.
    :param creator: The Orderline creator.
    :param price: The price of the Orderline.
    :param buddies: The buddy Users for the Orderline.
    :return: Whether the Orderline passed the health checks.
    :rtype: bool
    """
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


def handle_payment(request, order):
    """
    Do what's required to pay for an Order.
    :param request: Django HTTP Request Object.
    :param order: The Order to process payment for.
    :return: Three lists: Users paid for, Users already having paid and Users who now have a negative Balance.
    :rtype User, User, User
    """
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
