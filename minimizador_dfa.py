import json
import os

def cargar_dfa(file_path):
    """Carga un DFA desde un archivo JSON"""
    with open(file_path, 'r') as file:
        dfa = json.load(file)
    return dfa

def guardar_dfa(dfa, file_path):
    """Guarda un DFA en un archivo JSON"""
    with open(file_path, 'w') as file:
        json.dump(dfa, file, indent=4)

def eliminar_estados_inalcanzables(Q, Delta, q0):
    """Elimina estados inalcanzables del DFA"""
    alcanzables = set()
    cola = [q0]
    while cola:
        estado = cola.pop(0)
        if estado not in alcanzables:
            alcanzables.add(estado)
            for transicion in Delta:
                if transicion[0] == estado:
                    cola.append(transicion[2])
    return [estado for estado in Q if estado in alcanzables]

def construir_tabla(Q, F, Delta):
    """Construye la tabla de pares de estados y marca equivalencias iniciales"""
    tabla = {}
    finales = set(F)
    for i, p in enumerate(Q):
        for j, q in enumerate(Q):
            if i < j:
                tabla[(p, q)] = (p in finales) != (q in finales)  # Marca si uno es final y el otro no
    return tabla

def actualizar_tabla(tabla, Delta, Sigma):
    """Actualiza las marcas de la tabla según las transiciones del DFA"""
    cambiando = True
    while cambiando:
        cambiando = False
        for (p, q), marcado in tabla.items():
            if not marcado:  # Si no está marcado, revisamos
                for simbolo in Sigma:
                    p_prima = next((t[2] for t in Delta if t[0] == p and t[1] == simbolo), None)
                    q_prima = next((t[2] for t in Delta if t[0] == q and t[1] == simbolo), None)
                    if p_prima and q_prima and tabla.get((min(p_prima, q_prima), max(p_prima, q_prima)), False):
                        tabla[(p, q)] = True
                        cambiando = True
                        break
    return tabla

def fusionar_estados(Q, Delta, q0, F, tabla):
    """Fusiona estados no marcados y reconstruye el DFA"""
    equivalencias = {}
    
    # Crear grupos de equivalencia a partir de la tabla
    for (p, q), marcado in tabla.items():
        if not marcado:  # No están marcados, se consideran equivalentes
            if p not in equivalencias and q not in equivalencias:
                equivalencias[p] = {p, q}
                equivalencias[q] = equivalencias[p]
            elif p in equivalencias:
                equivalencias[p].add(q)
                equivalencias[q] = equivalencias[p]
            elif q in equivalencias:
                equivalencias[q].add(p)
                equivalencias[p] = equivalencias[q]

    # Asegurarse de incluir todos los estados, incluso los no agrupados
    representativos = {}
    for estado in Q:
        if estado in equivalencias:
            # Crear un nombre representativo basado en los estados del grupo
            grupo = equivalencias[estado]
            nuevo_nombre = "_".join(sorted(grupo))  # Concatenar nombres ordenados
            representativos[estado] = nuevo_nombre
        else:
            representativos[estado] = estado  # Estado se representa a sí mismo

    # Reconstruir el DFA mínimo
    Q_min = sorted(list(set(representativos.values())))  # Lista de estados minimizados
    Delta_min = set()
    for t in Delta:
        if t[0] in representativos and t[2] in representativos:
            # Agregar la transición como una tupla inmutable al conjunto
            Delta_min.add((representativos[t[0]], t[1], representativos[t[2]]))
    # Convertir el conjunto de nuevo a una lista (si es necesario)
    Delta_min = sorted(list(Delta_min))
    q0_min = representativos[q0]
    F_min = sorted(list(set(representativos[f] for f in F if f in representativos)))

    return Q_min, Delta_min, q0_min, F_min

def minimizar_dfa(dfa):
    Q, Sigma, Delta, q0, F = dfa['Q'], dfa['Sigma'], dfa['Delta'], dfa['q0'], dfa['F']

    # Paso 1: Eliminar estados inalcanzables
    Q = eliminar_estados_inalcanzables(Q, Delta, q0)
    Delta = [t for t in Delta if t[0] in Q and t[2] in Q]
    F = [estado for estado in F if estado in Q]

    # Paso 2: Construir y actualizar la tabla
    tabla = construir_tabla(Q, F, Delta)
    tabla = actualizar_tabla(tabla, Delta, Sigma)

    # Paso 3: Fusionar estados
    Q_min, Delta_min, q0_min, F_min = fusionar_estados(Q, Delta, q0, F, tabla)

    return {
        "type": "dfa",
        "Q": Q_min,
        "Sigma": Sigma,
        "Delta": Delta_min,
        "q0": q0_min,
        "F": F_min
    }

# Ejecución principal
if __name__ == "__main__":
    nombre_archivo = "dfa01.json"
    dfa = cargar_dfa(nombre_archivo)
    dfa_minimizado = minimizar_dfa(dfa)

    # Extraer el nombre base del DFA original
    nombre_base = os.path.splitext(nombre_archivo)[0]
    nombre_minimizado = nombre_base + "_minimizado.json"

    guardar_dfa(dfa_minimizado, nombre_minimizado)
    print(f"DFA minimizado guardado en '{nombre_minimizado}'.")