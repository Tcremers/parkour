from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from pooling.models import Pool, LibraryPreparation, LibraryPreparationForm
from pooling.utils import generate
from request.models import Request
from library.models import Library, Sample, IndexI7, IndexI5

import json
import logging

logger = logging.getLogger('db')


@login_required
def get_pooling_tree(request):
    """ Get libraries, ready for pooling. """
    children = []

    requests = Request.objects.select_related()
    for req in requests:
        libraries = []
        for library in req.libraries.all():
            if library.index_i7 and library.is_pooled is False:

                index_i7 = IndexI7.objects.filter(
                    index=library.index_i7,
                    index_type=library.index_type
                )
                index_i7_id = index_i7[0].index_id if index_i7 else ''

                index_i5 = IndexI5.objects.filter(
                    index=library.index_i5,
                    index_type=library.index_type
                )
                index_i5_id = index_i5[0].index_id if index_i5 else ''

                libraries.append({
                    'text': library.name,
                    'libraryId': library.id,
                    'recordType': 'L',
                    'sequencingDepth': library.sequencing_depth,
                    'libraryProtocolName': library.library_protocol.name,
                    'indexI7': library.index_i7,
                    'indexI7Id': index_i7_id,
                    'indexI5Id': index_i5_id,
                    'indexI5': library.index_i5,
                    'indexType': library.index_type.id,
                    'indexTypeName': library.index_type.name,
                    'sequencingRunCondition':
                        library.sequencing_run_condition.id,
                    'sequencingRunConditionName':
                        library.sequencing_run_condition.name,
                    'iconCls': 'x-fa fa-flask',
                    'checked': False,
                    'leaf': True
                })

        for sample in req.samples.all():
            if sample.is_pooled is False:
                libraries.append({
                    'text': sample.name,
                    'sampleId': sample.id,
                    'recordType': 'S',
                    'sequencingDepth': sample.sequencing_depth,
                    'libraryProtocolName': sample.sample_protocol.name,
                    'indexI7': '',
                    'indexI7Id': '',
                    'indexI5Id': '',
                    'indexI5': '',
                    'indexType':
                        sample.index_type.id
                        if sample.index_type is not None
                        else '',
                    'indexTypeName':
                        sample.index_type.name
                        if sample.index_type is not None
                        else '',
                    'sequencingRunCondition':
                        sample.sequencing_run_condition.id,
                    'sequencingRunConditionName':
                        sample.sequencing_run_condition.name,
                    'iconCls': 'x-fa fa-flask',
                    'checked': False,
                    'leaf': True
                })

        if libraries:
            children.append({
                'text': req.name,
                'expanded': True,
                'iconCls': 'x-fa fa-pencil-square-o',
                'children': libraries
            })

    data = {
        'text': '.',
        'children': children
    }

    return HttpResponse(
        json.dumps(data),
        content_type='application/json',
    )


@login_required
def save_pool(request):
    """ Save pool. """
    error = ''

    try:
        libraries = [
            library_id
            for library_id in json.loads(request.POST.get('libraries'))
        ]

        samples = [
            sample['sample_id']
            for sample in json.loads(request.POST.get('samples'))
        ]

        name = '_' + request.user.name.replace(' ', '_')

        if request.user.pi:
            name = request.user.pi.name + name

        pool = Pool(name=name)
        pool.save()
        pool.libraries.add(*libraries)
        pool.samples.add(*samples)
        pool.name = str(pool.id) + '_' + name
        pool.save()

        # Make current libraries not available for repeated pooling
        for library_id in libraries:
            library = Library.objects.get(id=library_id)
            library.is_pooled = True
            library.save()

        # Make current samples not available for repeated pooling
        # and set their Index I7 and Index I5 indices
        for smpl in json.loads(request.POST.get('samples')):
            sample = Sample.objects.get(id=smpl['sample_id'])
            sample.index_i7 = smpl['index_i7']
            sample.index_i5 = smpl['index_i5']
            sample.is_pooled = True
            sample.save()

            # Create Library Preparation object
            obj = LibraryPreparation(sample=sample)
            obj.save()

    except Exception as e:
        error = str(e)
        print(error)
        logger.exception(error)

    return HttpResponse(
        json.dumps({
            'success': not error,
            'error': error
        }),
        content_type='application/json',
    )


def update_sequencing_run_condition(request):
    """ Update Sequencing Run Condition before Index generation. """
    record_type = request.POST.get('record_type')
    record_id = request.POST.get('record_id')
    sequencing_run_condition_id = \
        request.POST.get('sequencing_run_condition_id')

    if record_type == 'L':
        record = Library.objects.get(id=record_id)
    else:
        record = Sample.objects.get(id=record_id)
    record.sequencing_run_condition_id = sequencing_run_condition_id
    record.save()

    return HttpResponse(content_type='application/json')


def update_index_type(request):
    """ Update Index Type for a given sample. """
    sample_id = request.POST.get('sample_id')
    index_type_id = request.POST.get('index_type_id')
    sample = Sample.objects.get(id=sample_id)
    sample.index_type_id = index_type_id
    sample.save()
    return HttpResponse(content_type='application/json')


def generate_indices(request):
    """ Generate indices for libraries and samples. """
    error = ''
    data = []

    try:
        library_ids = json.loads(request.POST.get('libraries'))
        sample_ids = json.loads(request.POST.get('samples'))
        generated_indices = generate(library_ids, sample_ids)

        for record in sorted(generated_indices, key=lambda x: x['name']):
            index_i7 = record['predicted_index_i7']['index']
            index_i5 = record['predicted_index_i5']['index']

            rec = {
                'name': record['name'],
                'sequencingDepth': record['depth'],
                'sequencingRunCondition': record['read_length'],
                'indexI7': index_i7,
                'indexI7Id': record['predicted_index_i7']['index_id'],
                'indexI5': index_i5,
                'indexI5Id': record['predicted_index_i5']['index_id']
            }

            if 'sample_id' in record.keys():
                rec.update({
                    'recordType': 'S',
                    'sampleId': record['sample_id']
                })

            if 'library_id' in record.keys():
                rec.update({
                    'recordType': 'L',
                    'libraryId': record['library_id']
                })

            for i in range(len(index_i7)):
                rec.update({'indexI7_' + str(i + 1): rec['indexI7'][i]})

            for i in range(len(index_i5)):
                rec.update({'indexI5_' + str(i + 1): rec['indexI5'][i]})

            data.append(rec)

    except Exception as e:
        error = str(e)
        print(error)
        logger.exception(error)

    return HttpResponse(
        json.dumps({
            'success': not error,
            'error': error,
            'data': data
        }),
        content_type='application/json',
    )


def get_library_preparation(request):
    """ Get the list of samples for Library Preparation. """
    error = ''
    data = []

    for obj in LibraryPreparation.objects.all():
        index_i7 = IndexI7.objects.get(
            index=obj.sample.index_i7,
            index_type_id=obj.sample.index_type_id
        )
        index_i7_id = index_i7.index_id

        try:
            index_i5 = IndexI5.objects.get(
                index=obj.sample.index_i5,
                index_type_id=obj.sample.index_type_id
            )
            index_i5_id = index_i5.index_id
        except IndexI5.DoesNotExist:
            index_i5_id = ''

        data.append({
            'name': obj.sample.name,
            'sampleId': obj.sample.id,
            'barcode': obj.sample.barcode,
            'libraryProtocol': obj.sample.sample_protocol.id,
            'libraryProtocolName': obj.sample.sample_protocol.name,
            'concentrationSample': obj.sample.concentration,
            'startingAmount': obj.starting_amount,
            'startingVolume': obj.starting_volume,
            'spikeInDescription': obj.spike_in_description,
            'spikeInVolume': obj.spike_in_volume,
            'ulSample': obj.ul_sample,
            'ulBuffer': obj.ul_buffer,
            'indexI7Id': index_i7_id,
            'indexI5Id': index_i5_id,
            'pcrCycles': obj.pcr_cycles,
            'concentrationLibrary': obj.concentration_library,
            'meanFragmentSize': obj.mean_fragment_size,
            'nM': obj.nM
        })

    return HttpResponse(
        json.dumps({
            'success': not error,
            'error': error,
            'data': data
        }),
        content_type='application/json',
    )


def edit_library_preparation(request):
    """ Edit sample in Library Preparation step. """
    error = ''

    sample_id = request.POST.get('sample_id')
    obj = LibraryPreparation.objects.get(sample_id=sample_id)

    try:
        form = LibraryPreparationForm(request.POST, instance=obj)

        if form.is_valid():
            form.save()
        else:
            for key, value in form.errors.items():
                error += '%s: %s<br/>' % (key, value)

    except Exception as e:
        error = str(e)
        logger.exception(e)

    return HttpResponse(
        json.dumps({
            'success': not error,
            'error': error
        }),
        content_type='application/json',
    )
