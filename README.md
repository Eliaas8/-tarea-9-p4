# PokeAPI Explorer (Python)

Este proyecto es una solución a un desafío de programación que utiliza la **PokeAPI** para responder preguntas específicas sobre Pokémon, haciendo uso de consultas HTTP con la librería `requests` de Python.

## Objetivo

Acceder y procesar datos de la PokeAPI para obtener información sobre tipos, estadísticas de batalla, evoluciones y datos curiosos de los Pokémon.

## Características

* **Cliente HTTP Robusto:** Implementación de manejo de errores (HTTP, conexión, timeout) para consultas a la API.
* **Procesamiento de Datos:** Uso de bucles, filtrado, y estructuras de control para manipular los datos JSON recibidos.
* **Manejo de Cadenas Evolutivas:** Lógica para recorrer y describir una cadena evolutiva.
* **Filtros Complejos:** Aplicación de múltiples criterios de filtrado (e.g., tipo + región, tipo + altura, velocidad + estado legendario).

## Cómo Ejecutar

### Requisitos

Necesitas tener Python 3.x instalado en tu sistema y la librería `requests`.

```bash
pip install requests
