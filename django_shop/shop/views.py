from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .models import Card, Order, Product


def product_list(request):
    """Display all products."""
    products = Product.objects.all()
    return render(request, 'shop/index.html', {'products': products})


@require_POST
def buy_product(request, slug):
    """
    Handle product purchase.
    Uses atomic transaction and select_for_update to prevent race conditions.
    """
    product = get_object_or_404(Product, slug=slug)
    email = request.POST.get('email')

    if not email:
        return HttpResponseBadRequest("Email is required")

    with transaction.atomic():
        # Select one unsold card with row-level locking
        card = (
            Card.objects
            .select_for_update(skip_locked=True)
            .filter(product=product, status='unsold')
            .first()
        )

        if not card:
            return render(request, 'shop/error.html', {
                'message': 'Sorry, this product is out of stock.'
            }, status=400)

        # Create order
        order = Order.objects.create(
            email=email,
            total_amount=product.price,
            status='completed'
        )

        # Mark card as sold and link to order
        card.status = 'sold'
        card.order = order
        card.save()

    return render(request, 'shop/success.html', {
        'order': order,
        'card': card,
        'product': product,
    })
