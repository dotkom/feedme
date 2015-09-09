from datetime import date, timedelta

from django.contrib import messages
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.views.generic import ListView, DetailView, FormView

from feedme.models import OrderLine, Order, ManageOrderLimit, Restaurant, Balance, Transaction, Poll, Answer
from feedme.forms import OrderLineForm, OrderForm, ManageOrderForm, ManageOrderLimitForm, NewOrderForm, NewRestaurantForm, ManageBalanceForm, NewPollForm, PollAnswerForm
from feedme.utils import get_feedme_groups

try:
    # Django 1.7 way for importing custom user
    from django.contrib.auth import AUTH_USER_MODEL
    User = get_user_model()
except ImportError:
    try:
        # Django 1.6 way for importing custom user, will crash in Django 1.7
        from django.contrib.auth import get_user_model
        User = get_user_model()
    except AppRegistryNotReady:
        # If all else fails, import default user model -- please report this bug
        from django.contrib.auth.models import User


# Index
def index(request):
    r = dict(
        is_admin=is_admin(request),
        feedme_groups=[g for g in get_feedme_groups() if request.user in g.user_set.all()],
    )
    return render(request, 'feedme/index.html', r)


@login_required()
def index_new(request, group=None):
    groups = get_feedme_groups()
    group = get_object_or_404(Group, name=group) if request.user in get_object_or_404(Group, name=group).user_set.all() else None
    order = get_order(group) if group else None
    poll = get_poll(group) if group else None
    r = dict()
    r['group'] = group
    r['order'] = order
    r['restaurants'] = Restaurant.objects.all()
    r['is_admin'] = is_admin(request)
    r['can_join'] = not in_other_orderline(request.user)
    r['feedme_groups'] = [g for g in get_feedme_groups() if request.user in g.user_set.all()]

    a_id = None
    if str(request.user) != 'AnonymousUser':
        if Answer.objects.filter(poll=poll, user=request.user).count() == 1:
            a_id = Answer.objects.get(poll=poll, user=request.user)

    if request.method == 'POST':
        if request.POST['act'] == 'vote':
            if a_id is not None:
                form = PollAnswerForm(request.POST, instance=a_id)
            else:
                form = PollAnswerForm(request.POST)
            if form.is_valid():
                answer = form.save(commit=False)
                answer.user = request.user
                answer.poll = poll
                answer.save()
                messages.success(request, 'Voted for %s' % answer.answer)
                return redirect('feedme:feedme_index_new', group)

    if poll is not None:
        r['poll'] = poll
        if a_id is None:
            r['answer'] = PollAnswerForm()
        else:
            r['answer'] = PollAnswerForm(instance=a_id)
        r['results'] = poll.get_result()

    return render(request, 'feedme/index.html', r)


# View order
@login_required()
def orderview(request, order_id=None, group=None):
    if order_id:
        order = get_object_or_404(Order, pk=order_id)
    else:
        order = Order()

    group = get_object_or_404(Group, name=group)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form = form.save(commit=False)
            form.creator = request.user
            form.order_line = get_order(group)
            form.save()
            messages.success(request, 'Orderline added')
            return redirect('feedme:feedme_index_new', group)

        form = OrderForm(request.POST)
    else:
        form = OrderForm(instance=order)

    r = dict()
    r['feedme_groups'] = [g for g in get_feedme_groups() if request.user in g.user_set.all()]
    r['group'] = group
    r['form'] = form
    r['is_admin'] = is_admin(request)

    return render(request, 'feedme/orderview.html', r)


# New / edit order line
def orderlineview(request, orderline_id=None, group=None):
    new_or_existing_orderline = 'new'
    if orderline_id is None:
        orderline = OrderLine()
        creator = None
    else:
        orderline = get_object_or_404(OrderLine, pk=orderline_id)
        new_or_existing_orderline = 'existing'
        creator = orderline.creator

    group = get_object_or_404(Group, name=group)

    if request.method == 'POST':
        form = OrderLineForm(request.POST, instance=orderline)
        if form.is_valid():
            new_orderline = form.save(commit=False)
            if creator is not None:
                new_orderline.creator = creator
            else:
                new_orderline.creator = request.user
            new_orderline.order = get_order(group)
            users = manually_parse_users(form)
            if check_orderline(request, new_orderline, orderline_id, buddies=users, group=group):
                new_orderline.save()
                form.save_m2m()  # Manually save the m2m relations when using commit=False
                if new_or_existing_orderline == 'new':
                    messages.success(request, "Orderline added")
                else:
                    messages.success(request, "Orderline edited")
                new_orderline.users.add(new_orderline.creator)
                return redirect('feedme:feedme_index_new', group)
            else:
                messages.error(request, "Orderline validation failed, please verify your data and try again.")  # @ToDo More useful errors
                new_orderline = OrderLineForm(request.POST, auto_id=True)
        else:
            new_orderline = OrderLineForm(request.POST, auto_id=True)
    else:
        form = OrderLineForm(instance=orderline)
        form.fields["users"].queryset = get_order(group).available_users().exclude(id=request.user.id)

    r = dict()
    r['feedme_groups'] = [g for g in get_feedme_groups() if request.user in g.user_set.all()]
    r['group'] = group
    r['form'] = form
    r['is_admin'] = is_admin(request)

    return render(request, 'feedme/orderview.html', r)


class OrderlineDetail(DetailView):
    model = OrderLine

    template_name = 'feedme/orderview.html'

    def get_queryset(self):
        print(self.args)
        self.orderline = get_object_or_404(OrderLine, pk=self.args[0])
        return self.orderline


def create_orderline(request, group=None):
    r = dict()
    group = get_object_or_404(Group, name=group)

    if request.method == 'POST':
        form = OrderLineForm(request.POST)
        if form.is_valid():
            new_orderline = form.save(commit=False)
            new_orderline.creator = request.user
            new_orderline.order = get_order(group)
            users = manually_parse_users(form)
            if check_orderline(request, new_orderline, buddies=users, group=group):
                new_orderline.save()
                form.save_m2m()  # Manually save the m2m relations when using commit=False
                new_orderline.users.add(new_orderline.creator)
                messages.success(request, 'Added orderline')
                return redirect('feedme:feedme_index_new', group)
            else:
                messages.error(request, 'Failed to add orderline')
    else:
        form = OrderLineForm()
        form.fields["users"].queryset = get_order(group).available_users().exclude(id=request.user.id)

    r['feedme_groups'] = [g for g in get_feedme_groups() if request.user in g.user_set.all()]
    r['group'] = group
    r['form'] = form
    r['is_admin'] = is_admin(request)

    return render(request, 'feedme/orderview.html', r)


# Edit order line
def edit_orderline(request, group, orderline_id):
    orderline = get_object_or_404(OrderLine, pk=orderline_id)
    group = get_object_or_404(Group, name=group)
    if not is_in_current_order('orderline', group, orderline_id):
        messages.error(request, 'you can not edit orderlines from old orders')
    elif request.user != orderline.creator and request.user not in orderline.users.all():
        messages.error(request, 'You need to be the creator')
        return redirect('feedme:feedme_index_new', group)
    return orderlineview(request, orderline_id=orderline_id, group=group)


# Delete order line
def delete_orderline(request, group, orderline_id):
    orderline = get_object_or_404(OrderLine, pk=orderline_id)
    group = get_object_or_404(Group, name=group)
    if not is_in_current_order('orderline', group, orderline_id):
        messages.error(request, 'You can not delete orderlines from old orders')
    elif orderline.creator == request.user:
        orderline.delete()
        messages.success(request, 'Orderline deleted')
    else:
        messages.error(request, 'You need to be the creator or the buddy')
    return redirect('feedme:feedme_index_new', group)


@login_required()
def join_orderline(request, group, orderline_id):
    orderline = get_object_or_404(OrderLine, pk=orderline_id)
    group = get_object_or_404(Group, name=group)
    # @TODO if not buddy system enabled, disable join
    if not is_in_current_order('orderline', group, orderline_id):
        messages.error(request, 'You can not join orderlines from old orders')
    elif in_other_orderline(request.user):
        messages.error(request, 'You cannot be in multiple orderlines')
    elif orderline.order.use_validation and not validate_user_funds(request.user, (orderline.price / (orderline.users.count() + 1))):  # Adds us to the test aswell
        messages.error(request, 'You need cashes')
    else:
        orderline.users.add(request.user)
        orderline.save()
        messages.success(request, 'Joined orderline')
    return redirect('feedme:feedme_index_new', group)


@login_required()
def leave_orderline(request, group, orderline_id):
    orderline = get_object_or_404(OrderLine, pk=orderline_id)
    group = get_object_or_404(Group, name=group)
    if not is_in_current_order('orderline', group, orderline_id):
        messages.error(request, 'You cannot leave old orders')
    elif request.user not in orderline.users.all():
        messages.error(request, 'You cannot leave since you are not in the users')
    else:
        orderline.users.remove(request.user)
        orderline.save()
        messages.success(request, 'Left orderline')
    return redirect('feedme:feedme_index_new', group)


@login_required
def order_history(request):
    user_orders = OrderLine.objects.filter(Q(creator=request.user) | Q(users=request.user))
    return render(request, 'feedme/order_history.html', {'order_history': user_orders})

# ADMIN


# New order
@permission_required('feedme.add_order', raise_exception=True)
def new_order(request, group=None):
    print('DEPRECATED - STOP USING THIS')
    group = get_object_or_404(Group, name=group)
    if request.method == 'POST':
        form = NewOrderForm(request.POST)
        if form.is_valid():
            form.save()
            poll = Poll.get_active()
            if poll:
                poll.deactivate()
            messages.success(request, 'New order added')
            return redirect('feedme:feedme_index_new', group)
    else:
        form = NewOrderForm()
        if Poll.objects.count() > 0:
            poll = Poll.get_active()
            if poll:
                form.fields['restaurant'].initial = poll.get_winner()
        form.fields["date"].initial = get_next_wednesday()
        form.fields['group'].initial = group
    r = dict()
    r['group'] = group
    r['feedme_groups'] = [g for g in get_feedme_groups() if request.user in g.user_set.all()]
    r['form'] = form
    r['is_admin'] = is_admin(request)
    return render(request, 'feedme/admin.html', r)


def admin(request, group=None):
    # Admin index - defaults to new order page. Should in the future probably implement a summary page? Paid, unpaid etc.
    r = dict()
    group = get_object_or_404(Group, name=group)

    if request.method == 'POST':
        form = NewOrderForm(request.POST)
        if form.is_valid():
            form.save()
            poll = Poll.get_active()
            if poll:
                poll.deactivate()
            messages.success(request, 'New order added')
            return redirect('feedme:feedme_index_new', group)
    else:
        form = NewOrderForm()
        if Poll.objects.count() > 0:
            poll = Poll.get_active()
            if poll:
                form.fields['restaurant'].initial = poll.get_winner()
        form.fields["date"].initial = get_next_wednesday()


    # r['form'] = form
    r['feedme_groups'] = [g for g in get_feedme_groups() if request.user in g.user_set.all()]
    r['group'] = group
    r['is_admin'] = is_admin(request)
    return render(request, 'feedme/admin.html', r)

# Manage users (deposit, withdraw, overview)
class ManageUserViewSet(DetailView):
    model = Balance
    fields = ('user', 'get_balance')
    template_name = 'feedme/manage_users.html'

    def get(self, request, group=None):
        r = {}
        group = get_object_or_404(Group, name=group)
        r['group'] = group
        r['form'] = ManageBalanceForm()
        r['form'].fields["user"].queryset = Balance.objects.filter(user__groups=group)

        return render(request, 'feedme/manage_users.html', r)

    def post(self, request, group=None):
        r = {}
        group = get_object_or_404(Group, name=group)
        form = ManageBalanceForm(request.POST)
        if form.is_valid():
            balance = form.cleaned_data['user']
            amount = form.cleaned_data['amount']
            user_balance = [balance.get_balance(),]
            balance.deposit(amount) if amount > 0 else balance.withdraw(amount * -1)
            user_balance.append(balance.get_balance())
            messages.success(request, 'Successfully deposited %s for %s (Changed from %s to %s)' % (balance.user, amount, user_balance[0], user_balance[1]))
            return redirect('feedme:manage_users', group)
        else:
            r['form'] = form
            messages.error(request, 'Invalid values supplied, check form error for details.')

        return render(request, 'feedme/manage_users.html', r)

# Manage order (payment handling)
@permission_required('feedme.change_balance', raise_exception=True)
def manage_order(request, group=None):
    r = dict()
    group = get_object_or_404(Group, name=group)
    r['feedme_groups'] = [g for g in get_feedme_groups() if request.user in g.user_set.all()]
    r['group'] = group

    if request.method == 'POST':
        form = ManageOrderForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            order = get_object_or_404(Order, pk=data['orders'].id)
            if 'active_order_submit' in request.POST:
                order.active = request.POST['active_order_submit'] == 'Activate'
                order.save()
                return redirect('feedme:manage_order', group)
            orderlines = order.orderline_set.all()
            total_price = order.extra_costs
            for orderline in orderlines:
                orderline.users.add(orderline.creator)
                orderline.each = orderline.get_price_to_pay()
                total_price += orderline.price
            r['form'] = form
            r['order'] = order
            r['orderlines'] = orderlines
            r['total_price'] = total_price
            if request.POST['act'] == 'Load':
                return render(request, 'feedme/manage_order.html', r)
            elif request.POST['act'] == 'Edit':
                for rq in request.POST:
                    if 'edit_orderline_price' in rq:
                        i = rq.split('-')[1]
                        ol = orderlines.get(id=i)
                        change = int(request.POST[rq])
                        if ol.price != change:
                            ol.price = change
                            ol.save()
                            messages.success(request, 'Changed price for %(ol)s to %(price)s' % {'ol': ol, 'price': ol.price})
                return redirect('feedme:manage_order', group=group)
            elif request.POST['act'] == 'Pay':
                handle_payment(request, order)
                return redirect('feedme:manage_order', group=group)
        else:
            form = ManageOrderForm(request.POST)
    else:
        form = ManageOrderForm()

    orders = Order.objects.all()
    orders_price = {}
    active_orders = Order.objects.filter(active=True)
    inactive_orders = Order.objects.exclude(active=True)
    #orders = [('Active', active_orders), ('Inactive', inactive_orders)]
    orders = active_orders | inactive_orders
    orders = orders.order_by('-active', '-date')

    #for order in orders:
    #    orders_price[order] = order.get_total_sum()

    form.fields["orders"].queryset = orders

    r['form'] = form
    r['is_admin'] = is_admin(request)
    r['orders'] = orders

    return render(request, 'feedme/manage_order.html', r)


# New restaurant
@permission_required('feedme.add_restaurant', raise_exception=True)
def new_restaurant(request, restaurant_id=None, group=None):
    if restaurant_id is None:
        restaurant = Restaurant()
    else:
        restaurant = get_object_or_404(Restaurant, pk=restaurant_id)

    if request.method == 'POST':
        form = NewRestaurantForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, "Restaurant added")
            return redirect('feedme:new_order', group)
        else:
            form = NewRestaurantForm(request.POST)
    else:
        form = NewRestaurantForm(instance=restaurant)

    r = dict()
    group = get_object_or_404(Group, name=group)
    r['feedme_groups'] = [g for g in get_feedme_groups() if request.user in g.user_set.all()]
    r['group'] = group
    r['form'] = form
    r['is_admin'] = is_admin(request)

    return render(request, 'feedme/admin.html', r)


# Edit restaurant
@permission_required('feedme.change_restaurant', raise_exception=True)
def edit_restaurant(request, restaurant_id=None):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    return new_restaurant(request, restaurant)


@permission_required('feedme.add_poll', raise_exception=True)
def new_poll(request, group=None):
    group = get_object_or_404(Group, name=group)
    if request.method == 'POST':
        form = NewPollForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'New poll added')
            return redirect('feedme:feedme_index_new', group)
        else:
            messages.error(request, 'Form not validated')
    else:
        form = NewPollForm()
        form.fields['question'].initial = "Hvor skal dotKom spise?"
        form.fields['due_date'].initial = get_next_tuesday()
        form.fields['group'].initial = group

    r = dict()
    r['feedme_groups'] = [g for g in get_feedme_groups() if request.user in g.user_set.all()]
    r['group'] = group
    r['form'] = form
    r['is_admin'] = is_admin(request)

    return render(request, 'feedme/admin.html', r)


# Validation of orderline
def check_orderline(request, form, orderline_id=None, buddies=None, group=None):
    orderline_exists = False
    if orderline_id is None:
        orderline = OrderLine()
        orderline.creator = User.objects.get(username=form.creator.username)
    else:
        orderline = get_object_or_404(OrderLine, pk=orderline_id)
        orderline_exists = True
    amount = form.price
    users = [orderline.creator]
    if orderline_exists:
        if len(orderline.users.all()) > 0:
            users.extend(orderline.users.all())
    else:
        users.extend(buddies)
    amount = amount / len(users)
    if get_order(group).use_validation:
        for user in users:
            if not validate_user_funds(user, amount):
                messages.error(request, 'Unsufficient funds caught for %s' % user)
                return False
    return True


# Check that the user has enough funds
def validate_user_funds(user, amount):
    get_or_create_balance(user)
    return user.balance.get_balance() >= amount


# Handle payment
def handle_payment(request, order):
    orderlines = order.orderline_set.all()

    paid = []
    already_paid = []
    negatives = []

    for orderline in orderlines:
        if not orderline.paid_for:
            if orderline.users.count() > 0:
                #amount = (orderline.get_total_price()) / (orderline.users.count() + 1)
                amount = orderline.get_price_to_pay()
                if orderline.creator not in orderline.users.all():
                    pay(orderline.creator, amount)
                for user in orderline.users.all():
                    pay(user, amount)
                    paid.append(user.get_username())
                    if user.balance.get_balance() < 0:
                        negatives.append(user.get_username())
                orderline.paid_for = True
                orderline.save()
            else:
                pay(orderline.creator, orderline.get_price_to_pay())
                orderline.paid_for = True
                orderline.save()
                paid.append(orderline.creator.get_username())
                if orderline.creator.balance.get_balance() < 0:
                    negatives.append(orderline.creator.get_username())
        else:
            already_paid.append(orderline.creator.get_username())
            if orderline.users.all().count() > 0:
                for user in orderline.users.all():
                    if user == orderline.creator:
                        print('user both in users and creator')
                    else:
                        already_paid.append(user.get_username())
    if len(paid) > 0:
        messages.success(request, 'Paid orderlines for %s.' % ', '.join(paid))
    if len(already_paid) > 0:
        messages.error(request, 'Already paid orderlines for %s.' % ', '.join(already_paid))
    if len(negatives) > 0:
        messages.error(request, 'These users now have negative balances: %s' % ', '.join(negatives))

    order.active = False
    order.save()


# The actual function for payment
def pay(user, amount):
    user.balance.withdraw(amount)  # This returns True/False whether or not the payment was possible.
    user.balance.save()


# Deposit of funds
def handle_deposit(data):
    balance = get_or_create_balance(data['user'])
    print('updating %s' % balance)
    amount = data['amount']
    if amount >= 0:
        balance.deposit(amount)
    else:
        balance.withdraw(amount)


# Get or create balance for a user
def get_or_create_balance(user):
    return Balance.objects.get_or_create(user=user)[0]


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
        diff = timedelta(days=(1 - day))
    elif day > 2:
        diff = timedelta(days=(7 - day + 1))
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
        return False


# Gets latest active poll
def get_poll(group=None):
    if Poll.objects.filter():
        if Poll.objects.filter(group=group, active=True).count() >= 1:
            return Poll.objects.filter(group=group, active=True).order_by('-id')[0]
        else:
            return None


# Checks if user is in current order line
def is_in_current_order(order_type, group, order_id):
    order = get_order(group)
    if order_type == 'orderline':
        orderline = get_object_or_404(OrderLine, pk=order_id)
        return orderline in order.orderline_set.all()
    elif order_type == 'order':
        order = get_object_or_404(Order, pk=order_id)
        return order in order.order_set.all()
    else:
        return False


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
def in_other_orderline(user):
    order = get_order(user)
    r1 = ""
    r2 = ""
    if order:
        if order.orderline_set:
            if order.orderline_set.filter(creator=user.id):
                r1 = user == order.orderline_set.filter(creator=user.id)[0].creator
            if order.orderline_set.filter(users=user.id):
                r2 = user in order.orderline_set.filter(users=user.id)[0].users.all()
    return r1 or r2
