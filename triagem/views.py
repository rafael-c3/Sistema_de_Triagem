from django.shortcuts import render, redirect, get_object_or_404, redirect
from .models import Paciente
from .forms import PacienteForm
from collections import Counter

def index_view(request):
    return render(request, 'site/index.html')

def create_view(request):
    if request.method == 'GET':
        form = PacienteForm()
        return render(request, 'site/criar.html', {'form': form})
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('hosp:listar')
        
def list_view(request):
    pacientes = Paciente.objects.all()
    status_contagem = Counter(p.status for p in pacientes)
    return render(request, 'site/listar.html', {
        'pacientes': pacientes,
        'status_contagem': status_contagem
    })

def detail_view(request, pk):
    paciente = Paciente.objects.get(pk = pk)
    if paciente:
        return render(request, 'site/detalhes.html', {'paciente': paciente})

def update_view(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'GET':
        form = PacienteForm(instance=paciente)
        return render(request, 'site/atualizar.html', {'paciente': paciente, 'form': form})
    elif request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('hosp:mostrar', pk=paciente.pk)
        
def delete_view(request, pk):
    paciente = Paciente.objects.get(pk = pk)
    if paciente:
        paciente.delete()
        request.status_code = 204
        return redirect('hosp:listar')
    
def dashboard_view(request):
    pacientes = Paciente.objects.all()
    status_contagem = Counter(p.status for p in pacientes)

    return render(request, 'site/dashboard.html', {
        'pacientes': pacientes,
        'status_contagem': status_contagem
    })
    
def triagem_view(request):
    return render(request, 'site/triagem.html')
