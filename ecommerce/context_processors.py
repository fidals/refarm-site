from ecommerce.cart import Cart

def cart(request):
    """Injects cart object into request."""
    return {'cart': Cart(request.session)}
