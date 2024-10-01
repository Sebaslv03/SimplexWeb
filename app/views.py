from django.shortcuts import render, redirect
from django.http import HttpResponse
from .simplex import SimplexAlgorithm

def menu(request):
    if request.method == 'POST':
        restricciones = request.POST.get('restricciones')
        variables = request.POST.get('variables')
        method = request.POST.get('method')
        
        if restricciones and variables and method:
            return redirect('variables', restricciones=restricciones, variables=variables, method=method)
        else:
            return HttpResponse("Por favor, complete todos los campos del formulario.")
    return render(request, 'menu.html')

def variables(request, restricciones, variables, method):
    restricciones = int(restricciones)
    variables = int(variables)
    context = {
        'restricciones': restricciones,
        'variables': variables,
        'method': method,
        'range_restricciones': range(restricciones),
        'range_variables': range(variables)
    }
    return render(request, 'variables.html', context)

def simplex(request):
    if request.method == 'POST':
        methodSimplex = request.POST.get('method')
        method = request.POST.get('objective')
        variables_count = request.POST.get('variables')
        restricciones_count = request.POST.get('restricciones')

        if variables_count is None or restricciones_count is None:
            return HttpResponse("Faltan datos necesarios", status=400)

        variables = [float(request.POST.get(f'x{i}')) for i in range(int(variables_count))]
        restricciones = []
        print(variables_count)
        print(variables)
        for j in range(int(restricciones_count)):
            aux = []
            restriccion = [float(request.POST.get(f'r{j}x{k}')) for k in range(int(variables_count))]
            operator = request.POST.get(f'r{j}_operator')
            value = float(request.POST.get(f'r{j}_value'))
            for r in restriccion:
                aux.append(r)
            aux.append(operator)
            aux.append(value)
            restricciones.append(aux)
        print(restricciones_count)
        print(restricciones)
        # Aquí puedes llamar a tu algoritmo de Simplex con los valores capturados
        simplex = SimplexAlgorithm(method, methodSimplex, variables, restricciones, variables_count, restricciones_count)
        iteraciones = simplex.createMatrix()
        print(iteraciones)
        
        return render(request, 'resultado.html', {'iteraciones': iteraciones})
    return HttpResponse("Método no permitido", status=405)

