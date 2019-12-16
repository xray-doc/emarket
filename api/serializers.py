from rest_framework import serializers

from products.models import Product


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ProductSerializer(DynamicFieldsModelSerializer):
    #url         = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Product
        fields = [
            'name',
            'price',
            'discount',
            'short_description',
            'diagonal',
            'built_in_memory',
            'ram',
            'os',
            'screen_resolution',
            'processor',
            'main_camera',
            'other_specifications'
        ]

    # def get_url(self, obj):
    #     # request
    #     request = self.context.get("request")
    #     return obj.get_api_url(request=request)

    # def validate_title(self, value):
    #     qs = BlogPost.objects.filter(title__iexact=value) # including instance
    #     if self.instance:
    #         qs = qs.exclude(pk=self.instance.pk)
    #     if qs.exists():
    #         raise serializers.ValidationError("This title has already been used")
    #     return value