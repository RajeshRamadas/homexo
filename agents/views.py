"""
agents/views.py
"""
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Agent


def agent_list(request):
    agents = Agent.objects.filter(is_active=True).select_related('user')
    paginator = Paginator(agents, 12)
    page      = request.GET.get('page')
    agents    = paginator.get_page(page)
    return render(request, 'agents/list.html', {'agents': agents})


def agent_detail(request, pk):
    agent = get_object_or_404(Agent, pk=pk, is_active=True)
    listings = agent.listings.filter(status='active').prefetch_related('images')[:6]
    return render(request, 'agents/detail.html', {'agent': agent, 'listings': listings})
