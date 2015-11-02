from django.contrib import admin

from feedme.models import Answer, Balance, Order, OrderLine, Poll, Restaurant, Transaction


class DepositWithdrawalFilter(admin.SimpleListFilter):
    """
    A simple filter to select deposits, withdrawals or empty transactions
    """
    title = 'transaction type'

    parameter_name = 'amount'

    def lookups(self, request, model_admin):
        """
        Tuples with values for url and display term
        """
        return (
            ('positive', 'Deposit'),
            ('negative', 'Withdrawal'),
            ('empty', 'Empty')
        )

    def queryset(self, request, queryset):
        if self.value() == 'positive':
            return queryset.filter(amount__gt=0)

        if self.value() == 'negative':
            return queryset.filter(amount__lt=0)

        if self.value() == 'empty':
            return queryset.filter(amount=0)


class OrderLineAdmin(admin.ModelAdmin):
    model = OrderLine
    fieldsets = (
        ('Order Line', {
            'fields': ('order', 'creator', 'users', 'menu_item', 'soda', 'extras', 'price',)
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('paid_for',)
        })
    )
    list_display = (
        'order', 'creator', 'menu_item', 'soda', 'extras',
        'price', 'price_to_pay', 'total_price', 'paid_for', 'num_users'
    )
    list_filter = (
        'paid_for', 'users', 'order',
    )

    def num_users(self, instance):
        return instance.get_num_users()
    num_users.short_description = "Num users"

    def price_to_pay(self, instance):
        return instance.get_price_to_pay()
    price_to_pay.short_description = "Price per user"

    def total_price(self, instance):
        return instance.get_total_price()
    total_price.short_description = "Total price"


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    fields = (
        'creator', 'users', 'menu_item', 'soda', 'extras', 'price', 'paid_for',
    )
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    model = Order
    fieldsets = (
        ('Order', {
            'fields': ('group', 'restaurant', 'date', 'extra_costs')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('active', 'use_validation')
        })
    )
    list_display = (
        'restaurant', 'date', 'group', 'extra_costs', 'active', 'use_validation',
        'total_cost',
    )
    list_filter = (
        'restaurant', 'date', 'group', 'active', 'use_validation',
    )
    search_fields = (
        'restaurant', 'date', 'group',
    )
    inlines = [
        OrderLineInline
    ]

    def total_cost(self, instance):
        return instance.get_total_sum
    total_cost.short_description = "Total cost"


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0


class PollAdmin(admin.ModelAdmin):
    model = Poll
    inlines = [
        AnswerInline
    ]


class TransactionAdmin(admin.ModelAdmin):
    model = Transaction
    fieldsets = (
        ('Transaction', {
            'fields': ('user', 'amount')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('date',)
        })
    )
    list_display = (
        'user', 'date', 'amount',
    )
    list_filter = (
        'user', 'date', DepositWithdrawalFilter,
    )
    search_fields = (
        'user', 'date', 'amount',
    )

    def get_queryset(self, request):  # Only allow to see own if not superuser
        qs = super(TransactionAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


class BalanceAdmin(admin.ModelAdmin):
    model = Balance
    readonly_fields = ('user',)
    list_display = (
        'user', 'balance'
    )

    def balance(self, instance):
        return instance.get_balance()

    def get_queryset(self, request):  # Only allow to see own if not superuser
        qs = super(BalanceAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

admin.site.register(Balance, BalanceAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderLine, OrderLineAdmin)
admin.site.register(Poll, PollAdmin)
admin.site.register(Restaurant)
admin.site.register(Transaction, TransactionAdmin)
