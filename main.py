import requests
import json
import time

BASE_URL = "https://pokeapi.co/api/v2"

def fetch_data(url: str):
    """
    Realiza una solicitud GET a la URL proporcionada y maneja posibles errores.
    Retorna los datos JSON o None en caso de fallo.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP al acceder a {url}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error desconocido al acceder a {url}: {e}")
        return None

def get_pokemon_id_range(region_name: str):
    """
    Obtiene el rango de IDs de Pokémon para una región específica (Kanto/Johto).
    """
    if region_name.lower() == 'kanto':
        return range(1, 152)
    elif region_name.lower() == 'johto':
        return range(152, 252)
    else:
        return []

def get_all_pokemon_species_data():
    """
    Obtiene la lista completa de todos los Pokémon (species) para iteración.
    """
    print("\nObteniendo la lista completa de todos los Pokémon Species (puede tardar)")
    limit_url = f"{BASE_URL}/pokemon-species?limit=10000"
    data = fetch_data(limit_url)
    if data:
        print(f"Total de especies encontradas: {len(data['results'])}")
        return data['results']
    return []

def q_fire_kanto(region_name="kanto"):
    """
    a) ¿Cuántos Pokémon de tipo fuego existen en la región de Kanto?
    """
    print(f"\n--- Clasificación por Tipos: Fuego en {region_name.capitalize()} ---")
    type_data = fetch_data(f"{BASE_URL}/type/fire")
    if not type_data:
        return 0, "No se pudo obtener la información del tipo Fuego."

    kanto_ids = set(get_pokemon_id_range(region_name))
    fire_pokemon_in_kanto = 0

    for pokemon_entry in type_data.get('pokemon', []):
        pokemon_url = pokemon_entry['pokemon']['url']
        pokemon_id = int(pokemon_url.split('/')[-2])

        if pokemon_id in kanto_ids:
            fire_pokemon_in_kanto += 1

    return fire_pokemon_in_kanto, f"Existen **{fire_pokemon_in_kanto}** Pokémon de tipo Fuego en la región de {region_name.capitalize()}."

def q_water_tall(min_height=10):
    """
    b) ¿Cuáles son los nombres de los Pokémon tipo agua con una altura mayor a 10? (10 dm = 1 metro)
    """
    print(f"\n--- Clasificación por Tipos: Agua > {min_height} dm ---")
    type_data = fetch_data(f"{BASE_URL}/type/water")
    if not type_data:
        return None, "No se pudo obtener la información del tipo Agua."

    tall_water_pokemon = []
    pokemon_urls = [entry['pokemon']['url'] for entry in type_data.get('pokemon', [])]

    for url in pokemon_urls:
        pokemon_data = fetch_data(url)
        if pokemon_data and pokemon_data.get('height', 0) > min_height:
            tall_water_pokemon.append(pokemon_data['name'].capitalize())
    
    result = (f"Los Pokémon tipo Agua con una altura superior a {min_height} dm (1 metro) son "
              f"({len(tall_water_pokemon)} en total): \n"
              f"**{', '.join(tall_water_pokemon)}**")
    
    return tall_water_pokemon, result

def q_starter_evolution_chain(starter_name="squirtle"):
    """
    a) Selecciona un Pokémon inicial (de cualquier región) y describe su cadena evolutiva completa.
    """
    print(f"\n--- Evoluciones: Cadena de {starter_name.capitalize()} ---")
    species_data = fetch_data(f"{BASE_URL}/pokemon-species/{starter_name.lower()}")
    if not species_data:
        return None, f"No se pudo encontrar la especie de {starter_name.capitalize()}."

    evolution_chain_url = species_data.get('evolution_chain', {}).get('url')
    if not evolution_chain_url:
        return None, f"{starter_name.capitalize()} no tiene una cadena evolutiva registrada."

    chain_data = fetch_data(evolution_chain_url)
    if not chain_data:
        return None, "No se pudo obtener la información de la cadena evolutiva."

    chain_list = []
    current_chain = chain_data['chain']
    
    while current_chain:
        name = current_chain['species']['name'].capitalize()
        details = []
        
        if current_chain['evolution_details']:
            details = [
                f"{d['trigger']['name'].capitalize()}" +
                (f" (Nivel: {d['min_level']})" if d['min_level'] else "") +
                (f" (Objeto: {d['item']['name'].capitalize()})" if d.get('item') else "")
                for d in current_chain['evolution_details']
            ]
        
        chain_list.append((name, details))
        
        if current_chain['evolves_to']:
            current_chain = current_chain['evolves_to'][0]
        else:
            current_chain = None

    result = f"Cadena evolutiva de **{starter_name.capitalize()}**:\n"
    for i, (name, details) in enumerate(chain_list):
        if i == 0:
            result += f"1. **{name}** (Base)\n"
        else:
            evo_detail = " con " + " y ".join(details) if details else ""
            result += f"{' ' * (i-1) * 2} -> {i+1}. **{name}** (Evoluciona{evo_detail})\n"

    return chain_list, result

def q_electric_no_evolution():
    """
    b) ¿Qué Pokémon de tipo eléctrico no tienen evoluciones?
    """
    print("\n--- Evoluciones: Eléctricos sin Evolución ---")
    type_data = fetch_data(f"{BASE_URL}/type/electric")
    if not type_data:
        return None, "No se pudo obtener la información del tipo Eléctrico."

    electric_pokemon_names = [entry['pokemon']['name'] for entry in type_data.get('pokemon', [])]
    correct_no_evo_list = []
    
    print("Buscando especies eléctricas sin cadena evolutiva (puede tardar)...")
    
    for name in electric_pokemon_names:
        species_data = fetch_data(f"{BASE_URL}/pokemon-species/{name}")
        
        if species_data and not species_data['evolves_from_species']:
            evolution_chain_url = species_data.get('evolution_chain', {}).get('url')
            if not evolution_chain_url:
                continue

            chain_data = fetch_data(evolution_chain_url)
            if chain_data:
                # Si el Pokémon es la base de la cadena y no tiene 'evolves_to', es "sin evolución"
                if chain_data['chain']['species']['name'] == name and not chain_data['chain']['evolves_to']:
                    correct_no_evo_list.append(name.capitalize())
                    
    result = (f"Los Pokémon de tipo Eléctrico que no tienen evoluciones (ni pre-evoluciones) son "
              f"({len(correct_no_evo_list)} en total): \n"
              f"**{', '.join(correct_no_evo_list)}**")
    
    return correct_no_evo_list, result

def q_highest_attack_johto(region_name="johto"):
    """
    a) ¿Cuál es el Pokémon con el mayor ataque base en la región de Johto?
    """
    print(f"\n--- Estadísticas de Batalla: Mayor Ataque en {region_name.capitalize()} ---")
    johto_ids = get_pokemon_id_range(region_name)
    max_attack = -1
    pokemon_with_max_attack = None

    for poke_id in johto_ids:
        pokemon_data = fetch_data(f"{BASE_URL}/pokemon/{poke_id}")
        if pokemon_data:
            attack_stat = next((s['base_stat'] for s in pokemon_data['stats'] if s['stat']['name'] == 'attack'), 0)
            
            if attack_stat > max_attack:
                max_attack = attack_stat
                pokemon_with_max_attack = pokemon_data['name'].capitalize()

    result = (f"El Pokémon de la región de {region_name.capitalize()} con el mayor Ataque Base es "
              f"**{pokemon_with_max_attack}** con un ataque de **{max_attack}**.")
    
    return pokemon_with_max_attack, result

def q_highest_speed_non_legendary():
    """
    b) ¿Cuál es el Pokémon con la velocidad más alta que no sea legendario?
    """
    print("\n--- Estadísticas de Batalla: Mayor Velocidad (No Legendario) ---")
    
    max_speed = -1
    pokemon_with_max_speed = None
    
    all_species = get_all_pokemon_species_data()
    
    for species_entry in all_species:
        name = species_entry['name']
        
        species_data = fetch_data(species_entry['url'])
        if species_data:
            is_legendary = species_data.get('is_legendary', False) or species_data.get('is_mythical', False)
            
            if not is_legendary:
                pokemon_data = fetch_data(f"{BASE_URL}/pokemon/{name}")
                if pokemon_data:
                    speed_stat = next((s['base_stat'] for s in pokemon_data['stats'] if s['stat']['name'] == 'speed'), 0)
                    
                    if speed_stat > max_speed:
                        max_speed = speed_stat
                        pokemon_with_max_speed = name.capitalize()

    result = (f"El Pokémon **no legendario/mítico** con la Velocidad Base más alta es "
              f"**{pokemon_with_max_speed}** con una velocidad de **{max_speed}**.")
    
    return pokemon_with_max_speed, result

def q_most_common_habitat_plant():
    """
    a) ¿Cuál es el hábitat más común entre los Pokémon de tipo planta?
    """
    print("\n--- Extras: Hábitat más Común (Planta) ---")
    
    type_data = fetch_data(f"{BASE_URL}/type/grass")
    if not type_data:
        return None, "No se pudo obtener la información del tipo Planta."
    
    pokemon_names = [entry['pokemon']['name'] for entry in type_data.get('pokemon', [])]
    habitat_counts = {}
    
    print("Contando hábitats de Pokémon tipo Planta (puede tardar)...")
    
    for name in pokemon_names:
        species_data = fetch_data(f"{BASE_URL}/pokemon-species/{name}")
        
        if species_data and species_data.get('habitat'):
            habitat_name = species_data['habitat']['name'].capitalize()
            habitat_counts[habitat_name] = habitat_counts.get(habitat_name, 0) + 1

    if not habitat_counts:
        return None, "No se encontró información de hábitat para los Pokémon de tipo Planta."

    most_common_habitat = max(habitat_counts.items(), key=lambda item: item[1])
    
    result = (f"El **hábitat más común** entre los Pokémon de tipo Planta es **{most_common_habitat[0]}**, "
              f"con **{most_common_habitat[1]}** Pokémon registrados en ese hábitat.")
    
    return most_common_habitat[0], result

def q_lightest_pokemon():
    """
    b) ¿Qué Pokémon tiene el menor peso registrado en toda la API?
    """
    print("\n--- Extras: Menor Peso Registrado ---")
    
    min_weight = float('inf')
    pokemon_with_min_weight = None
    
    all_species = get_all_pokemon_species_data()
    
    for species_entry in all_species:
        name = species_entry['name']
        
        pokemon_data = fetch_data(f"{BASE_URL}/pokemon/{name}")
        
        if pokemon_data:
            weight = pokemon_data.get('weight', float('inf'))
            
            if weight == 1:
                pokemon_with_min_weight = name.capitalize()
                min_weight = weight
                break
                
            if weight < min_weight:
                min_weight = weight
                pokemon_with_min_weight = name.capitalize()

    min_weight_kg = min_weight / 10
    
    result = (f"El Pokémon con el **menor peso** registrado es **{pokemon_with_min_weight}**, "
              f"con un peso de **{min_weight_kg} kg** ({min_weight} hectogramos).")
    
    return pokemon_with_min_weight, result

def main():
    """
    Ejecuta todas las consultas y presenta los resultados.
    """
    results_output = []
    
    def log_result(question: str, result_text: str):
        output = f"\n{'-' * 40}\n**PREGUNTA:** {question}\n{'-' * 40}\n{result_text}\n"
        print(output)
        results_output.append(output)

    print("         POKÉMON EXPLORER - INICIANDO          ")

    _, result_text = q_fire_kanto()
    log_result("a) ¿Cuántos Pokémon de tipo fuego existen en la región de Kanto?", result_text)

    _, result_text = q_water_tall()
    log_result("b) ¿Cuáles son los nombres de los Pokémon tipo agua con una altura mayor a 10?", result_text)

    _, result_text = q_starter_evolution_chain("squirtle")
    log_result("a) Cadena evolutiva del inicial Squirtle", result_text)
    
    _, result_text = q_electric_no_evolution()
    log_result("b) ¿Qué Pokémon de tipo eléctrico no tienen evoluciones?", result_text)

    _, result_text = q_highest_attack_johto()
    log_result("a) ¿Cuál es el Pokémon con el mayor ataque base en la región de Johto?", result_text)
    
    _, result_text = q_highest_speed_non_legendary()
    log_result("b) ¿Cuál es el Pokémon con la velocidad más alta que no sea legendario?", result_text)
    
    _, result_text = q_most_common_habitat_plant()
    log_result("a) ¿Cuál es el hábitat más común entre los Pokémon de tipo planta?", result_text)
    
    _, result_text = q_lightest_pokemon()
    log_result("b) ¿Qué Pokémon tiene el menor peso registrado en toda la API?", result_text)

    with open("results.txt", "w", encoding="utf-8") as f:
        f.write("POKÉMON EXPLORER - RESULTADOS DE CONSULTA A POKEAPI\n")
        f.write("\n".join(results_output))

    print("              PROCESO COMPLETADO                ")
    print("Los resultados han sido guardados en 'results.txt'.")

if __name__ == "__main__":
    main()
