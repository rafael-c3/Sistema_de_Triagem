from django.shortcuts import render, redirect, get_object_or_404, redirect
from .models import Paciente
from .forms import PacienteForm, CustomUserCreationForm
from collections import Counter
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .ml.predict import predict_from_dict
from django.contrib.auth.decorators import login_required # Importe o login_required
from django.contrib import messages

def index_view(request):
    return render(request, 'site/index.html')

@login_required # Mantenha a permissão de tipo de usuário
def create_view(request):
    if request.method == 'GET':
        form = PacienteForm()
        return render(request, 'site/criar.html', {'form': form})
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('hosp:listar')
        else:
            print("Erros de validação:", form.errors)
            return render(request, 'site/criar.html', {'form': form})

@login_required        
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
    
@login_required
def dashboard_view(request):
    pacientes = Paciente.objects.all()
    status_contagem = Counter(p.status for p in pacientes)

    return render(request, 'site/dashboard.html', {
        'pacientes': pacientes,
        'status_contagem': status_contagem
    })
    
def triagem_view(request):
    return render(request, 'site/triagem.html')

@csrf_exempt
def predict_view(request):
    if request.method != 'POST':
        return JsonResponse({'error':'Use POST'}, status=405)
    data = json.loads(request.body)
    pred, probs = predict_from_dict(data)
    return JsonResponse({'classificacao': pred, 'probs': probs})

def registro_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Conta criada com sucesso! Por favor, faça o login.')
            return redirect('hosp:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'site/registro.html', {'form': form})

@login_required # Garante que apenas usuários logados possam ver esta página
def perfil_view(request):
    """
    Exibe as informações do usuário logado.
    """
    # O objeto do usuário logado já vem pronto no 'request.user'
    # Não precisamos fazer nenhuma busca no banco de dados!
    return render(request, 'site/perfil.html')