import logging
import typing

from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAdminUser

from apps.macroplate.models import Customer

from ..models.customers import PlanPriority
from .serializers import CustomerSerializer

logger = logging.getLogger('django')


class CustomerUpdateView(CreateModelMixin, UpdateModelMixin, GenericAPIView):
    """View to Create/Update customer.

    This endpoint retrieves data about the user, determines whether the
    customer exists, and either updates the existing customer or adds a new one

    This endpoint allowed only for Admins, and only by tokens.

    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminUser,)
    lookup_field = 'external_id'

    def get_object(self):
        """Find object by lookup field and return it, if it found."""
        obj = self.queryset.filter(**{
            self.lookup_field: self._get_lookup_value(),
        })

        if obj.exists():
            return obj.get()

    def post(self, request):
        """Update passed customer, if customer exists or create new."""
        logger.info(f'Request data: {request.data}')
        customer: typing.Optional[Customer] = self.get_object()
        if customer:
            method = self.update
        else:
            method = self.create
        try:
            return method(request)
        except ValidationError as exc:
            logger.info(f'Validation Errors: {exc}')
            raise exc

    def _get_lookup_value(self):
        """Get external_id value for """
        external_id = self.request.data.get('external_id')
        plan_priority = self.request.data.get('plan_priority')

        if plan_priority == PlanPriority.SECONDARY:
            external_id = f'{external_id}-{plan_priority}'
        return external_id
