import uuid

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from celery.result import AsyncResult
from celery.states import FAILURE

from apps.celery.api.serializers import CreateTaskSerializer
from apps.macroplate import tasks

# Available celery tasks
tasks_map = {
    'assign_meals': tasks.assign_meals,
    'meal_cards_export': tasks.meal_cards_export,
    'delivery_export': tasks.delivery_export,
    'packaging_export': tasks.packaging_export,
    'mod_sheet_export': tasks.mod_sheet_export,
    'promo_codes_export': tasks.promo_codes_export,
    'meal_quantity_export': tasks.meal_quantity_export,
    'all_meal_data_export': tasks.all_meal_data_export,
    'all_meal_data_import': tasks.all_meal_data_import,
}


class CeleryTaskViewSet(ViewSet):
    """Viewset for creating and retrieve celery tasks."""
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Create a task with provided name, and optional file and payload.

        Return its ID.
        """
        serializer = CreateTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task_name = serializer.validated_data.get('name')
        file = serializer.validated_data.get('file')
        kwargs = serializer.validated_data.get('payload', {})

        if file:
            tmp_path = f'uploaded-files/{uuid.uuid4()}-{file.name}'
            path = default_storage.save(tmp_path, ContentFile(file.read()))
            kwargs['file_path'] = path

        if task_name not in tasks_map:
            raise NotFound()

        task = tasks_map[task_name]
        async_result = task.apply_async(kwargs=kwargs)

        return Response(
            data={'task_id': async_result.id},
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, pk=None):
        """Retrieve a task by its ID."""
        res = AsyncResult(pk)
        data = {
            'id': pk,
            'state': res.state,
            'info': res.info,
        }

        if res.state == FAILURE:
            data['info'] = {'message': str(res.info)}

        return Response(data=data)
