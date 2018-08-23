from django.contrib.contenttypes.models import ContentType
from mixer.backend.django import mixer

from comments.models import Comment
from products.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

comments_per_product = 3


def main():
    mixer.cycle(15).blend(
        User,
        username=mixer.FAKE,
        first_name=mixer.FAKE,
        last_name=mixer.FAKE,
        email=mixer.FAKE
    )
    products = Product.objects.all()
    product_contenttype = ContentType.objects.get_for_model(Product)

    for product in products:
        parent_comments = mixer.cycle(comments_per_product).blend(
            Comment,
            user=mixer.RANDOM(*list(User.objects.all())),
            content=mixer.FAKE,
            content_type=product_contenttype,
            object_id=product.id,
            parent=None
        )

        child_comments = mixer.cycle(2).blend(
            Comment,
            user=mixer.RANDOM(*list(User.objects.all())),
            content=mixer.FAKE,
            content_type=product_contenttype,
            object_id=product.id,
            parent=mixer.RANDOM(*parent_comments)
        )

    print('Done!', Comment.objects.count(), 'comments in the database')

if __name__ == '__main__':
    main()