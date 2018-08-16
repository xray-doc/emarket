from django.db.models import Q
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType


from products.models import Product 
from ..models import Comment

User = get_user_model()

class CommentTestCase(TestCase):
    def setUp(self):
        user_obj = User(username='testuser', email='test@test.com')
        user_obj.set_password("somepassrandom")
        user_obj.save()

        product = Product.objects.create(
            name='meizu',
            price=25000
            )
        product.save()
        # self.product = product

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

    def test_comment_object_all(self):
        comments_qs = Comment.objects.all()

        # Next we filter comments_qs
        # to see if it includes comments with parents
        comments_qs = comments_qs.filter(~Q(parent=None))
        count = comments_qs.count()
        self.assertEqual(count, 0, msg="all() shouldn't return child comments")

    def test_comment_str(self):
        com = Comment.objects.first()
        self.assertEqual(str(com), 'testuser')

    def test_single_user(self):
        user_count = User.objects.count()
        self.assertEqual(user_count, 1)

    def test_single_product(self):
        product_count = Product.objects.count()
        self.assertEqual(product_count, 1)

    def test_product_with_comment_has_comment(self):
    	product = Product.objects.first()
    	self.assertIs(product.comments.count() > 0, True)

    def test_product_without_comment_has_not_comment(self):
    	product = Product.objects.create(name='huawei')
    	self.assertIs(product.comments.count() == 0, True)

    def test_parent_comment_is_parent(self):
    	self.assertIs(self.parent_comment.is_parent, True)

    def test_child_comment_is_not_parent(self):
    	self.assertIs(self.child_comment.is_parent, False)

    def test_parent_comment_has_children(self):
    	self.assertIs(self.parent_comment.children().count() > 0, True)

    def test_child_comment_has_not_children(self):
    	self.assertIs(self.child_comment.children().count() > 0, False)