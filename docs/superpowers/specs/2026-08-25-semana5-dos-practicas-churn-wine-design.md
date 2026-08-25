# Rediseño de la semana 5: práctica Churn y práctica Wine

## Contexto

La semana 5 debe contener dos prácticas diferentes y encadenadas por los
conceptos, no por los datos:

1. La clase 1 combina 60 minutos de teoría con 60 minutos de práctica guiada
   sobre un caso sintético de churn.
2. La clase 2 dedica 120 minutos a aplicar el mismo patrón de interfaz al
   proyecto Wine Quality, utilizando obligatoriamente el bundle construido por
   cada alumno en S4.

La versión anterior hacía que la práctica 5.1 diseñara el formulario Wine sin
implementar una interfaz. Esto no permite practicar en la clase de teoría el
ciclo completo widget → botón → función → actualización visible. El nuevo
diseño sustituye esa práctica.

## Objetivos

- Enseñar el modelo mental de rerun de Streamlit mediante una aplicación corta
  y observable.
- Conseguir que cada alumno construya un frontal funcional durante la clase 1.
- Separar de forma explícita la demo Churn del proyecto Wine.
- Transferir en la clase 2 el patrón aprendido al bundle real de S4.
- Evaluar ambas prácticas mediante tests automáticos y una comprobación visual.

## Fuera de alcance

- `st.session_state`, caché, máquinas de estados y telemetría.
- Una interfaz Gradio como parte evaluable.
- Entrenamiento o modificación de modelos en S5.
- Un `DemoGateway` o predicciones simuladas en la práctica Wine.
- Reutilizar campos, reglas o código de negocio Churn en el proyecto Wine.

## Secuencia docente

```text
Clase 1
60 min teoría y demo Churn
        ↓
60 min práctica 5.1 Churn
        ↓
Puente conceptual: conservar el patrón, cambiar el caso

Clase 2
120 min práctica 5.2 Wine con el bundle real de S4
```

## Teoría y presentación

La presentación debe identificar Churn antes de utilizarlo. El bloque teórico
mostrará:

1. El caso sintético y su propósito docente.
2. El contrato de `predict(tenure_months, monthly_spend_eur,
   support_calls, has_annual_contract)`.
3. La salida: decisión, etiqueta, score orientativo y explicación.
4. El rerun de arriba abajo.
5. `st.form` y `st.form_submit_button` como mecanismo de envío agrupado.
6. El invariante observable: cero llamadas antes de enviar y una llamada por
   envío.
7. La separación entre interfaz y función de inferencia.
8. Presentación del resultado y error comprensible.
9. Instrucciones y checkpoints de la práctica 5.1.
10. Una transición explícita de Churn a Wine.

La transición debe indicar:

| Se conserva | Cambia |
| --- | --- |
| formulario y submit | cuatro campos → once campos |
| una llamada por envío | `predict()` → `InferenceGateway.predict()` |
| separación UI/inferencia | regla sintética → bundle de S4 |
| presentación y error | salida Churn → `PredictionPayload` |

Gradio puede mencionarse como alternativa o demostración opcional del docente,
pero no forma parte de ninguna entrega.

La presentación original no se modifica. Se generará una nueva copia con un
nombre inequívoco y se volverán a validar todas sus diapositivas.

## Práctica 5.1 — Del formulario a la inferencia: miniapp Churn

### Propósito y duración

Práctica guiada de 60 minutos. El alumno construye una interfaz Streamlit sobre
una función Python ya implementada.

### Material proporcionado

- `model.py` completo y probado.
- La firma y el contrato de `predict()`.
- Un `app.py` con estructura y TODO explícitos.
- Tests del modelo y tests de la interfaz.
- Instrucciones de ejecución y checklist visual.

El ejemplo Churn completo existente se migrará a la solución de esta práctica,
evitando mantener una segunda implementación activa que pueda confundirse con
el ejercicio.

### Trabajo del alumno

1. Leer la firma y predecir el resultado de dos perfiles.
2. Crear un único `st.form` con cuatro widgets:
   - antigüedad en meses;
   - gasto mensual;
   - llamadas a soporte;
   - contrato anual.
3. Añadir `st.form_submit_button`.
4. No llamar a `predict()` antes del envío.
5. Llamar exactamente una vez a `predict()` después del envío.
6. Mostrar la etiqueta, el score orientativo y la explicación.
7. Convertir un fallo de `predict()` en un mensaje humano sin traceback.
8. Ejecutar tests y completar el checklist visual.

### Flujo

```text
abrir app → editar widgets → sin inferencia
                       ↓
                 pulsar submit
                       ↓
             una llamada a predict()
                       ↓
      etiqueta + score + explicación, o error humano
```

### Secuencia de 60 minutos

- 0–10: leer el contrato y predecir dos casos.
- 10–25: construir el formulario.
- 25–35: conectar submit y `predict()`.
- 35–45: presentar resultado y error.
- 45–55: ejecutar y corregir tests.
- 55–60: QA manual y puente hacia Wine.

### Validación

Los tests deben comprobar:

- cuatro widgets con tipos, rangos y claves correctos;
- un único formulario y un único botón de envío;
- cero llamadas antes de enviar;
- una llamada por envío con los cuatro valores;
- presentación de etiqueta, score y explicación;
- error comprensible sin mostrar la excepción cruda.

La revisión manual debe cubrir: arranque, edición sin envío, envío válido y
resultado actualizado.

### Entregables y rúbrica

- `app.py` terminado.
- Tests verdes.
- Checklist manual breve.

Rúbrica sobre 10:

- formulario y widgets: 2;
- submit y semántica de llamadas: 2;
- separación UI/inferencia: 2;
- resultado y error: 2;
- tests y QA: 2.

## Práctica 5.2 — Del bundle S4 al frontal Wine

### Propósito y duración

Taller guiado de 120 minutos. El alumno aplica el patrón de la práctica 5.1 al
proyecto Wine Quality y utiliza obligatoriamente su bundle de S4.

### Material proporcionado

- Starter con `app.py`, contrato, gateway, tipos de salida y tests.
- Un `ui_schema.py` Wine completo con las once claves canónicas, etiquetas,
  rangos, valores iniciales y pasos. No procede de la práctica 5.1.
- Instrucciones para configurar `MODEL_UI_BUNDLE`.
- Checklist de pruebas manuales.

No se proporciona `DemoGateway`. Los dobles de gateway solo pueden existir en
los tests automáticos y no constituyen un modo de ejecución de la aplicación.

### Trabajo del alumno

1. Configurar y cargar el bundle real de S4.
2. Construir un único formulario con las once variables Wine.
3. Conservar exactamente las claves canónicas del contrato.
4. Añadir el botón de envío y evitar inferencias durante la edición.
5. Llamar una sola vez a `gateway.predict(values)` por envío.
6. Mostrar `quality_band`, `confidence`, `model_version` y
   `preprocessing_version`.
7. Presentar un error accionable si falta o no puede cargarse el bundle, sin
   traceback, ruta interna ni detalle crudo.
8. Ejecutar tests y validar visualmente la aplicación con el bundle real.

La UI no puede llamar directamente a `joblib.load`, al estimador ni al
preprocesador. Toda inferencia atraviesa el gateway.

### Secuencia de 120 minutos

- 0–15: localizar y validar el bundle de S4.
- 15–35: construir los once widgets.
- 35–55: formulario y semántica del submit.
- 55–75: conexión con el gateway.
- 75–90: presentación del resultado.
- 90–105: tratamiento del bundle ausente.
- 105–115: tests y QA visual.
- 115–120: documentar ejecución y límites para S6.

### Validación

Los tests deben comprobar:

- las once claves exactas, sin duplicados;
- valores iniciales y pasos válidos;
- un único formulario y un único botón;
- cero llamadas antes del envío y una después;
- uso exclusivo del gateway desde la UI;
- presentación de los cuatro campos de salida;
- mensaje seguro ante bundle ausente.

La evidencia final debe ejecutarse con el bundle real. La revisión manual debe
cubrir: arranque con bundle, edición sin envío, envío válido y bundle ausente.

### Entregables y rúbrica

- Aplicación Streamlit funcional.
- Configuración documentada del bundle de S4.
- Tests verdes.
- Evidencia de ejecución válida y de bundle ausente.
- Checklist manual.

Rúbrica sobre 10:

- integración con el bundle y contrato Wine: 2;
- formulario y semántica del submit: 2;
- frontera del gateway: 2;
- resultado y error: 2;
- reproducibilidad, tests y QA: 2.

## Assignments y documentación

Se regenerarán ambos PDF:

- Assignment 5.1: «Del formulario a la inferencia: miniapp Churn», 60 minutos.
- Assignment 5.2: «Del bundle S4 al frontal Wine», 120 minutos.

Las guías, README, sesiones y enlaces deben reflejar una única secuencia. No
deben quedar referencias activas a la antigua práctica 5.1 de diseño de
`ui_schema.py` ni a un modo demo de la práctica Wine.

## Criterios de aceptación globales

- Un alumno que solo consulte presentación y assignment distingue claramente
  Churn de Wine.
- La práctica 5.1 produce una aplicación Streamlit ejecutable.
- La práctica 5.2 no arranca en modo simulado y exige el bundle de S4.
- Ninguna práctica requiere Gradio, estado, caché, FSM o telemetría.
- Todos los tests y comprobaciones de estilo de las soluciones pasan.
- Los starters fallan únicamente en los TODO que debe completar el alumno.
- Los dos assignments tienen rutas, comandos, tiempos y rúbricas consistentes.
- La presentación y los PDF se revisan visualmente sin recortes ni solapes.
- La presentación original permanece intacta.
