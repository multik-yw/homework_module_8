from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet

from users.models import Payment
from users.serializers import PaymentSerializer


# Create your views here.
class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ('payment_date', 'paid_course', 'paid_lesson', 'payment_method')
    ordering_fields = ('payment_date',)
    ordering = ('-payment_date',)