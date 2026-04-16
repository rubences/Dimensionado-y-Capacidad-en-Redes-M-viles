# Dimensionado-y-Capacidad-en-Redes-M-viles

Práctica de dimensionado de capacidad uplink en un campus en hora punta con dos entregables principales:

- Notebook de análisis en [Practica1_Saturacion_Uplink_Campus.ipynb](Practica1_Saturacion_Uplink_Campus.ipynb)
- Dashboard web en Flask a partir del mismo modelo de cálculo

## Requisitos

```bash
python -m pip install -r requirements.txt
```

## Ejecutar el notebook

Abrir [Practica1_Saturacion_Uplink_Campus.ipynb](Practica1_Saturacion_Uplink_Campus.ipynb) en Jupyter o VS Code y ejecutar las celdas en orden.

## Ejecutar el dashboard Flask

```bash
python app.py
```

Después abrir en el navegador:

```text
http://127.0.0.1:5000
```

Puedes aplicar filtros por query string, por ejemplo:

```text
http://127.0.0.1:5000/?speed=50&activity=0.65&eta=0.72&i=0.75
```

## API y exportaciones

- API JSON: [api/uplink](api/uplink)
- Exportación HTML de conclusiones: [export/conclusions.html](export/conclusions.html)
- Exportación PDF de conclusiones: [export/conclusions.pdf](export/conclusions.pdf)

Ejemplo con filtros:

```text
/api/uplink?speed=15&activity=0.55&eta=0.70&i=0.65
```

## Estructura

- [uplink_model.py](uplink_model.py): modelo de cálculo y preparación de datasets para tablas y gráficas
- [app.py](app.py): aplicación Flask
- [templates/index.html](templates/index.html): plantilla principal del dashboard
- [templates/conclusions_export.html](templates/conclusions_export.html): plantilla de exportación HTML de conclusiones
- [static/styles.css](static/styles.css): estilos del dashboard
