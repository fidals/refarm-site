"""Reusable views for eCommerce app."""

from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.urlresolvers import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.template.defaultfilters import floatformat
from django.template.loader import render_to_string
from django.views.generic import View

from pages.models import Page
from pages.views import CustomPageView

from ecommerce import mailer
from ecommerce.cart import Cart
from ecommerce.forms import OrderForm
from ecommerce.models import Order
from ecommerce.session import ShoppingSession
from ecommerce.trackers import Trackers


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
        Page.CUSTOM_PAGES_URL_NAME,
        current_app='ecommerce',
        args=('order-success',)
    )
    template_name = 'ecommerce/order/order.html'
    email_extra_context = {}

    def get_context_data(self, request, **kwargs):
        post = getattr(request, 'POST', None)
        form = self.order_form(post) if post else self.order_form()
        cart = self.cart(request.session)
        context = super().get_context_data(**kwargs)

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
            save_order_to_session(request.session, order_)
            return order_

        # Define this attr, for get_context_data method
        self.object = self.get_object()
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
    cart = Cart

    def get_order_id(self):
        return self.request.session.get('order_id', None)

    def get_shopping_session(self):
        return ShoppingSession(
            self.cart(self.request.session),
            Trackers([]),
        )

    def get_context_data(self, request, **kwargs):
        order = get_object_or_404(self.order, id=self.get_order_id())
        shopping_session = self.get_shopping_session()
        shopping_session.purchase(order)
        trackers_data = shopping_session.get_tracked_data()
        return {
            **super().get_context_data(**kwargs),
            **trackers_data,
            'order': order,
        }


class CartModifier(View):

    header_template = 'ecommerce/header_cart.html'
    table_template = 'ecommerce/order/table_form.html'
    product_key = 'product'
    order_form = OrderForm
    # Necessary define at client-side
    product_model = None
    cart = Cart

    def get_shopping_session(self):
        return ShoppingSession(
            self.cart(self.request.session),
            Trackers([]),
        )

    def json_response(self, request, shopping_session):
        cart = shopping_session.cart
        header = render_to_string(self.header_template, request=request)
        table = render_to_string(
            self.table_template,
            {'form': self.order_form()},
            request=request,
        )
        trackers_data = shopping_session.get_tracked_data()
        return JsonResponse({
            **trackers_data,
            'header': header,
            'table': table,
            'total_price': cart.total_price,
            'total_quantity': intcomma(floatformat(cart.total_quantity, 0)),
        })


class AddToCart(CartModifier):

    def post(self, request):
        shopping_session = self.get_shopping_session()
        product = get_object_or_404(
            self.product_model,
            id=request.POST.get(self.product_key)
        )
        shopping_session.add(product, int(request.POST.get('quantity')))
        return self.json_response(request, shopping_session)


class RemoveFromCart(CartModifier):

    def post(self, request):
        shopping_session = self.get_shopping_session()
        product = get_object_or_404(
            self.product_model,
            id=request.POST.get(self.product_key)
        )
        shopping_session.remove(product)
        return self.json_response(request, shopping_session)


class FlushCart(CartModifier):

    def post(self, request):
        shopping_session = self.get_shopping_session()
        shopping_session.clear()
        return self.json_response(request, shopping_session)


class ChangeCount(CartModifier):

    def post(self, request):
        shopping_session = self.get_shopping_session()
        product_id, quantity = get_keys_from_post(
            request, self.product_key, 'quantity'
        )
        product = get_object_or_404(self.product_model, id=product_id)
        shopping_session.set_product_quantity(product, int(quantity))
        return self.json_response(request, shopping_session)
