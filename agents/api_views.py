"""
agents/api_views.py
"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Agent
from .serializers import AgentSerializer


class AgentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset           = Agent.objects.filter(is_active=True).select_related('user')
    serializer_class   = AgentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['user__first_name', 'user__last_name', 'specialization', 'languages']
    ordering_fields    = ['rating', 'experience_years']
