# -*- coding: utf-8 -*-

from datetime import datetime
from django.db import models
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Restaurant(models.Model):
    """Restaurant is a model for providing information about where an Order is placed."""
    restaurant_name = models.CharField(_('name'), max_length=50)
    menu_url = models.URLField(_('menu url'), max_length=250)
    phone_number = models.CharField(_('phone number'), max_length=15)
    email = models.EmailField(_('email address'), blank=True, null=True)
    buddy_system = models.BooleanField(_('Enable buddy system'), default=False)

    def __str__(self):
        return self.restaurant_name


@python_2_unicode_compatible
class Order(models.Model):
    """Order is the wrapper for multiple OrderLines for a Restaurant at a given date and time."""
    group = models.ForeignKey(Group)
    date = models.DateField(_('date'))
    restaurant = models.ForeignKey(Restaurant)
    extra_costs = models.FloatField(_('extra costs'), default=0)
    active = models.BooleanField(_('Order currently active'), default=True)
    use_validation = models.BooleanField(_('Enable funds validation'), default=True)

    @property
    def get_total_sum(self):
        """
        Gets the total price for an order, including any extra costs. This is the price that should be paid to
        the Restaurant.
        :return: The total price for this Order
        :rtype: float
        """
        s = self.orderline_set.aggregate(models.Sum('price'))['price__sum']
        if s is None:
            s = 0
        return s + self.extra_costs

    # Should rename to "get_extra_costs_for_each_user" or -each_payer
    def get_extra_costs(self):
        """
        Calculate the amount each person partaking in this order should pay of this Order.extra_costs.
        :return: The amount each person partaking in this order should pay of this Order.extra_costs
        :rtype: float
        """
        # users = self.orderline_set.aggregate(models.Sum('users'))['users__sum']
        users = 0
        for ol in self.orderline_set.all():
            users += ol.users.count()
        return self.extra_costs / users if users > 0 else self.extra_costs

    def order_users(self):
        """
        :return: A Django QuerySet containing the users available for partaking in this Order
        :rtype: list
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.filter(groups=self.group)

    def available_users(self):
        """
        Get the available users for partaking in a new (or current) OrderLine for this Order
        :return: the available users for partaking in a new (or current) OrderLine for this Order
        :rtype: list
        """
        order_users = self.order_users()
        taken_users = self.taken_users()
        available_users = order_users.exclude(id__in=taken_users)
        return available_users

    def taken_users(self):
        return self.orderline_set.values_list(_('creator'), flat=True)

    @classmethod
    def get_latest(cls):
        """
        Get the latest active Order
        :return: The latest active Order
        :rtype: Order
        """
        if Order.objects.all():
            orders = Order.objects.all().order_by('-id')
            for order in orders:
                if order.active:
                    return order
        else:
            return False

    @property
    def paid(self):
        """
        Checks if the Order and all related Orderlines are paid for.
        :return: Whether the Order is fully paid for or not.
        :rtype: bool
        """
        if self.orderline_set.all():
            for ol in self.orderline_set.all():
                if not ol.paid_for:
                    return False
            return True
        return False

    def __str__(self):
        return "%s: %s @ %s" % (self.group, self.date.strftime("%d. %B"), self.restaurant)

    class Meta:
        get_latest_by = 'date'
        permissions = (
            ('view_order', 'View Order'),
        )


@python_2_unicode_compatible
class OrderLine(models.Model):
    """The relation between a number of users (creator and users) and an Order."""
    order = models.ForeignKey(Order)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name=_('owner'))
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name=_('buddies'), blank=True)
    menu_item = models.CharField(_('menu item'), max_length=50)
    soda = models.CharField(_('soda'), blank=True, null=True, max_length=25)
    extras = models.CharField(_('extras/comments'), blank=True, null=True, max_length=50)
    price = models.IntegerField(_('price'))
    paid_for = models.BooleanField(_('paid for'), default=False)

    def get_order(self):
        """
        Get the Order for this Orderline
        :return: the Order related to this Orderline
        :rtype: Order
        """
        return self.order

    def get_users(self):
        """
        Get this Orderline's users
        :return: The users related to this Orderline
        :rtype: User
        """
        return self.users

    def get_buddies(self):
        """
        Proxy for "get_users()"
        :return: The users related to this Orderline
        :rtype: User
        """
        return self.get_users()

    def get_num_users(self):
        """
        Get the number of users in this Orderline
        :return: The number of users in this Orderline
        :rtype: int
        """
        return self.get_users().count()

    # Should rename to "get_orderline_total"
    def get_total_price(self):
        """
        Calculate the total cost for this Orderline, including extra_costs as a sum of the partaking users.
        :return: The total price of this Orderline
        :rtype: float
        """
        return self.price + (self.order.get_extra_costs() * self.get_num_users())

    def get_price_to_pay(self):
        """
        Calculate how much each person partaking in this OrderLine should pay, including extra_costs.
        :return: The price to pay for one user.
        :rtype: float
        """
        return self.get_total_price() / self.get_num_users() if self.get_num_users() > 0 else 0

    def __str__(self):
        return self.creator.get_username()

    @models.permalink
    def get_absolute_url(self):
        return 'edit', (), {'orderline_id': self.id}

    class Meta:
        verbose_name = _('Orderline')
        verbose_name_plural = _('Orderlines')


@python_2_unicode_compatible
class Transaction(models.Model):
    """Transaction is the model used for keeping a history of users actions towards their Balance,
    e.g. withdrawing money from their Balance to pay for an Order, or depositing to be able to participate
    in an upcoming Order with funds validation enabled."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    amount = models.FloatField(_('amount'), default=0)
    date = models.DateTimeField(_('transaction date'), auto_now_add=True)

    def __str__(self):
        return self.user.get_username()


@python_2_unicode_compatible
class Balance(models.Model):
    """Balance is a wrapper for a User's Transactions."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL)

    @property
    def balance(self):
        return self.get_balance()

    def get_balance(self):
        """
        Calculate the Balance of a given User. Create an initial Transaction if none exist from before.
        :return: The Balance of a given user.
        :rtype: float
        """
        if self.user.transaction_set.aggregate(models.Sum('amount'))['amount__sum'] is None:
            self.add_transaction(0)
        return self.user.transaction_set.aggregate(models.Sum('amount'))['amount__sum']

    def get_balance_string(self):
        """
        Format the Balance string
        :return: A string-formatted Balance.
        :rtype: str
        """
        return "%.2f kr" % self.get_balance()

    def add_transaction(self, amount):
        """
        Add a Transaction for the current user.
        :param amount: The value of this Transaction
        :return: True if the Transaction completed successfully.
        :rtype: bool
        """
        transaction = Transaction()
        transaction.user = self.user
        transaction.amount = amount
        transaction.save()
        return True

    def deposit(self, amount):
        """
        Proxy for add_transaction.
        :param amount: The value of this Transaction
        :return: True if the Transaction completed successfully.
        :rtype: bool
        """
        return self.add_transaction(amount)
        # print('Deprecated notice, please add new transaction objects rather than calling the Balance object')

    def withdraw(self, amount):
        """
        Proxy for add_transaction.
        :param amount: The value of this Transaction
        :return: True if the Transaction completed successfully.
        :rtype: bool
        """
        return self.add_transaction(amount * -1)
        # print('Deprecated notice, please add new transaction objects rather than calling the Balance object')

    @property
    def username(self):
        return self.user.username

    def __str__(self):
        return "%s: %s" % (self.user.username, self.get_balance())


@python_2_unicode_compatible
class Poll(models.Model):
    """Poll allows for democratic voting for a Restaurant for an Order"""
    group = models.ForeignKey(Group)
    question = models.CharField(_('question'), max_length=250)
    active = models.BooleanField(_('active'), default=True)
    due_date = models.DateTimeField(_('due date'))

    def deactivate(self):
        self.active = False
        self.save()

    def activate(self):
        if datetime.now() < self.due_date:
            self.active = True
            self.save()

    @classmethod
    def get_active(cls):
        """
        Get an active Poll, if any.
        :return: An active Poll, or None if no Polls are active.
        :rtype: Poll
        """
        if Poll.objects.count() == 0:
            return None
        if Poll.objects.latest('id').active:
            return Poll.objects.latest('id')
        else:
            return None

    def get_result(self):
        """
        Get the results of a Poll
        :return: A dict containing the Answer choices and the amount of votes for each Answer
        :rtype: dict
        """
        answers = Answer.objects.filter(poll=self)
        r = dict()
        for answer in answers:
            if answer.answer not in r:
                r[answer.answer] = 0
            r[answer.answer] += 1
        return r

    def get_winner(self):
        """
        Get the winner of a Poll
        :return: The winning Answer
        :rtype: User
        """
        winner = (None, -1)
        results = self.get_result()
        for key in results:
            if results[key] > winner[1]:
                winner = (key, results[key])
        return winner[0]

    def __str__(self):
        return "%s due %s" % (self.question, self.due_date.strftime("%x"))

    class Meta:
        permissions = (
            ('view_poll', 'View Poll'),
        )


@python_2_unicode_compatible
class Answer(models.Model):
    """Answer is used to partake in a Poll"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name=_('user'))
    poll = models.ForeignKey(Poll, related_name=_('votes'))
    answer = models.ForeignKey(Restaurant, related_name=_('answer'))

    def __str__(self):
        return "%s: %s (%s)" % (self.user, self.answer, self.poll)

    class Meta:
        permissions = (
            ('vote_poll', 'Vote Poll'),
        )


class ManageBalance(models.Model):
    user = models.ForeignKey(Balance)
    amount = models.FloatField(_('amount'), default=0)


class ManageOrders(models.Model):
    orders = models.OneToOneField(Order, related_name=_('Orders'))


class ManageUsers(models.Model):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name=_('Users'))


class ManageOrderLimit(models.Model):
    order_limit = models.IntegerField(_('Order limit'), default=100)
