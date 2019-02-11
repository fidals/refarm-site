"""Reusable views for eCommerce app."""

from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.urlresolvers import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.template.defaultfilters import floatformat
from django.template.loader import render_to_string
from django.views.generic import View

from pages.models import CustomPage
from pages.views import CustomPageView

from ecommerce import mailer
from ecommerce.cart import Cart
from ecommerce.forms import OrderForm
from ecommerce.models import Order


def save_order_to_session(session, order: Order):
    """Save order's id to user's session and mark session as modified."""
    session['order_id'] = order.id
    session.modified = True


def get_keys_from_post(request, *args):
    """Get a tuple of given keys from request.POST object."""
    return tuple(request.POST[arg] for arg in args)


class OrderPage(CustomPageView):
    order_form = OrderForm
    cart = Cart
    success_url = reverse_lazy(
        CustomPage.ROUTE,
        current_app='ecommerce',
        kwargs={'page': 'order-success'}
    )
    template_name = 'ecommerce/order/order.html'
    email_extra_context = {}

    def get_context_data(self, request, **kwargs):
        post = getattr(request, 'POST', None)

        form = self.order_form(post) if post else self.order_form()
        cart = self.cart(request.session)

        context = super(OrderPage, self).get_context_data(**kwargs)

        return {
            **context,
            'cart': cart,
            'form': form
        }

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()  # Define this attr, for get_context_data method
        context = self.get_context_data(request=request)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        def save_order(form_, cart_):
            """Save order to DB and to session."""
            order_ = form_.save()
            order_.set_positions(cart_)
            cart_.clear()
            save_order_to_session(request.session, order_)
            return order_

        self.object = self.get_object()  # Define this attr, for get_context_data method
        context = self.get_context_data(request=request)

        cart, form = context['cart'], context['form']

        # sometimes we have two posts in a row
        if cart.is_empty():
            return redirect('/', permanent=True)

        if not form.is_valid():
            return render(request, self.template_name, context)

        order = save_order(form, cart)
        mailer.send_order(
            subject=settings.EMAIL_SUBJECTS['order'],
            order=order,
            **self.email_extra_context
        )

        return redirect(self.success_url)


class OrderSuccess(CustomPageView):
    template_name = 'ecommerce/order/success.html'
    order = Order

    def get_order_id(self):
        return self.request.session.get('order_id', None)

    def get(self, request, *args, **kwargs):
        if not self.get_order_id():
            raise Http404()

        return super(OrderSuccess, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        order_id = self.get_order_id()
        context = super(OrderSuccess, self).get_context_data(**kwargs)

        return {
            **context,
            'order': get_object_or_404(self.order, id=order_id)
        }


class CartModifier(View):
    header_template = 'ecommerce/header_cart.html'
    table_template = 'ecommerce/order/table_form.html'
    position_key = 'product'
    order_form = OrderForm
    position_model = None  # Necessary define at client-side
    cart = Cart

    def json_response(self, request):
        cart = self.cart(request.session)
        header = render_to_string(self.header_template, request=request)

        table = render_to_string(
            self.table_template,
            {'form': self.order_form()},
            request=request
        )
        return JsonResponse({
            'header': header,
            'table': table,
            'total_price': cart.total_price,
            'total_quantity': intcomma(floatformat(cart.total_quantity, 0)),
        })


class AddToCart(CartModifier):
    def post(self, request):
        cart = self.cart(request.session)
        position = get_object_or_404(
            self.position_model,
            id=request.POST.get(self.position_key)
        )
        cart.add(position, int(request.POST.get('quantity')))

        return self.json_response(request)


class RemoveFromCart(CartModifier):
    def post(self, request):
        cart = self.cart(request.session)
        position = get_object_or_404(
            self.position_model,
            id=request.POST.get(self.position_key)
        )
        cart.remove(position)

        return self.json_response(request)


class FlushCart(CartModifier):
    def post(self, request):
        self.cart(request.session).clear()

        return self.json_response(request)


class ChangeCount(CartModifier):
    def post(self, request):
        cart = self.cart(request.session)
        position_id, quantity = get_keys_from_post(
            request, self.position_key, 'quantity'
        )
        position = get_object_or_404(self.position_model, id=position_id)
        cart.set_position_quantity(position, int(quantity))

        return self.json_response(request)
