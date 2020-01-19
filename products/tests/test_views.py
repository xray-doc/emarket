from django.db.models import Q
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse


from ..models import Product
from comments.models import Comment

User = get_user_model()


class CommentTestCase(TestCase):

    def setUp(self):
        user_obj = User(username='testuser', email='test@test.com')
        user_obj.set_password("somepassrandom")
        user_obj.save()

        product = Product.objects.create(
            name='zte-16gb-black',
            price=25000
        )
        product.save()

        c_type = product.get_content_type
        c_type = str(c_type).lower()
        content_type = ContentType.objects.get(model=c_type)
        obj_id = product.id

        parent_comment = Comment.objects.create(
            user = user_obj,
            content_type=content_type,
            object_id=obj_id,
            content="Parent comment content",
            parent=None
        )
        self.parent_comment = parent_comment

        child_comment = Comment.objects.create(
            user = user_obj,
            content_type=content_type,
            object_id=obj_id,
            content="Child comment content",
            parent=parent_comment
        )
        self.child_comment = child_comment

    def test_get_product_detail(self):
        product = Product.objects.first()
        url = product.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_detail.html')

    def test_post_comment_with_authenticated_user(self):
        user_obj = User(username='testuserN2', email='test@testN2.com')
        user_obj.set_password("somepassrandomN2")
        user_obj.save()
        self.client.login(username='testuserN2', password='somepassrandomN2')

        product = Product.objects.first()
        parent_comment = Comment.objects.first()

        content = 'Test comment from testuser.'
        url = product.get_absolute_url()
        resp = self.client.post(url, {
            'content': content,
            'content_type': product.get_content_type,
            'object_id': product.id,
            'parent_id': parent_comment.id
        })
        self.assertEqual(resp.status_code, 302)  # Redirecting to comment page
        self.assertTemplateNotUsed(resp, 'products/product_detail.html')

        user_comment = Comment.objects.filter(user=user_obj)
        self.assertEqual(len(user_comment), 1)
        user_comment = user_comment[0]
        self.assertEqual(user_comment.content, content)
        self.assertEqual(user_comment.content_type, product.get_content_type)
        self.assertEqual(user_comment.object_id, product.id)
        self.assertEqual(user_comment.parent_id, parent_comment.id)

    def test_post_comment_with_unauthenticated_user(self):
        product = Product.objects.first()
        parent_comment = Comment.objects.first()
        initial_number_of_comments = Comment.objects.count()

        content = 'Test comment from unauthenticated user'
        url = product.get_absolute_url()
        response = self.client.post(url, {
            'content': content,
            'content_type': product.get_content_type,
            'object_id': product.id,
            'parent_id': parent_comment.id
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_detail.html')

        number_of_comments = Comment.objects.count()
        self.assertEqual(initial_number_of_comments, number_of_comments)