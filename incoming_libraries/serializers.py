from rest_framework.serializers import (
    ModelSerializer,
    ListSerializer,
    SerializerMethodField,
    IntegerField,
    CharField,
)
from library.models import Library
from sample.models import Sample


class BaseListSerializer(ListSerializer):

    def update(self, instance, validated_data):
        # Maps for id->instance and id->data item.
        object_mapping = {obj.pk: obj for obj in instance}
        data_mapping = {item['pk']: item for item in validated_data}

        # Perform updates
        ret = []
        for obj_id, data in data_mapping.items():
            obj = object_mapping.get(obj_id, None)
            if obj is not None:
                if 'quality_check' in data.keys():
                    if data['quality_check'] == 'passed':
                        obj.status = 2
                    elif data['quality_check'] == 'failed':
                        obj.status = -1
                    elif data['quality_check'] == 'compromised':
                        obj.status = -2
                ret.append(self.child.update(obj, data))
        return ret


class BaseSerializer(ModelSerializer):
    pk = IntegerField()
    quality_check = CharField(required=False)
    record_type = SerializerMethodField()
    request = SerializerMethodField()
    request_name = SerializerMethodField()
    library_protocol_name = SerializerMethodField()
    samples_submitted = SerializerMethodField()

    class Meta:
        list_serializer_class = BaseListSerializer
        fields = ('pk', 'name', 'barcode', 'record_type', 'library_protocol',
                  'concentration', 'concentration_method', 'dilution_factor',
                  'concentration_facility', 'concentration_method_facility',
                  'sample_volume_facility', 'amount_facility', 'quality_check',
                  'size_distribution_facility', 'comments_facility',
                  'request', 'request_name', 'sequencing_depth',
                  'library_protocol_name', 'samples_submitted',)
        extra_kwargs = {
            'name': {'required': False},
            'barcode': {'required': False},
            'library_protocol': {'required': False},
            'concentration': {'required': False},
            'concentration_method': {'required': False},
            'sequencing_depth': {'required': False},
        }

    def get_request(self, obj):
        return obj.request.get().pk

    def get_request_name(self, obj):
        return obj.request.get().name

    def get_library_protocol_name(self, obj):
        return obj.library_protocol.name

    def get_samples_submitted(self, obj):
        return obj.request.get().samples_submitted


class LibrarySerializer(BaseSerializer):

    class Meta(BaseSerializer.Meta):
        model = Library
        fields = BaseSerializer.Meta.fields + \
            ('qpcr_result', 'qpcr_result_facility',
             'mean_fragment_size',)
        extra_kwargs = {**BaseSerializer.Meta.extra_kwargs, **{
            'qpcr_result': {'required': False},
            'mean_fragment_size': {'required': False},
        }}

    def get_record_type(self, obj):
        return 'Library'


class SampleSerializer(BaseSerializer):
    nucleic_acid_type_name = SerializerMethodField()

    class Meta(BaseSerializer.Meta):
        model = Sample
        fields = BaseSerializer.Meta.fields + \
            ('nucleic_acid_type', 'nucleic_acid_type_name', 'rna_quality',
             'rna_quality_facility',)
        extra_kwargs = {**BaseSerializer.Meta.extra_kwargs, **{
            'nucleic_acid_type': {'required': False},
            'rna_quality': {'required': False},
        }}

    def get_record_type(self, obj):
        return 'Sample'

    def get_nucleic_acid_type_name(self, obj):
        return obj.nucleic_acid_type.name
