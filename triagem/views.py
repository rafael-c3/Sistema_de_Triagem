from django.shortcuts import render, redirect
from .models import Paciente
from .forms import PacienteForm

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

    prioridade_map = {
        'vermelho': 'critico',
        'amarelo': 'urgente',
        'laranja': 'urgente',
        'verde': 'normal',
        'azul': 'normal',
    }

    pacientes_convertidos = []
    for paciente in pacientes:
        prioridade_convertida = prioridade_map.get(paciente.prioridade.lower(), 'normal')
        pacientes_convertidos.append({
            'id': paciente.id,
            'nome': paciente.nome,
            'sexo': paciente.sexo,
            'status_atendimento': paciente.status_atendimento,
            'prioridade': prioridade_convertida,  # já em minúsculo
        })

    total_critico = sum(1 for p in pacientes_convertidos if p['prioridade'] == 'critico')
    total_urgente = sum(1 for p in pacientes_convertidos if p['prioridade'] == 'urgente')
    total_normal = sum(1 for p in pacientes_convertidos if p['prioridade'] == 'normal')

    context = {
        'pacientes': pacientes_convertidos,
        'total_critico': total_critico,
        'total_urgente': total_urgente,
        'total_normal': total_normal,
    }

    return render(request, 'site/listar.html', context)





def detail_view(request, pk):
    paciente = Paciente.objects.get(pk = pk)
    if paciente:
        return render(request, 'site/detalhes.html', {'paciente': paciente})

def update_view(request, pk):
    paciente = Paciente.objects.get(pk = pk)
    if request.method == 'GET':
        form = PacienteForm(instance=paciente)
        return render(request, 'site/atualizar.html', {'paciente': paciente, 'form': form})
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('hosp:listar')
        
def delete_view(request, pk):
    paciente = Paciente.objects.get(pk = pk)
    if paciente:
        paciente.delete()
        request.status_code = 204
        return redirect('hosp:listar')