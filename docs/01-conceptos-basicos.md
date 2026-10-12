# 1. Conceptos básicos

Esta guía explica, sin tecnicismos, las piezas que forman la aplicación. Si nunca ha programado, empiece aquí.

## La analogía del restaurante

Piense en la aplicación como un restaurante:

| En el restaurante | En la aplicación | Carpeta o servicio |
| --- | --- | --- |
| El salón, las mesas y la carta que ve el cliente | **Frontend**: las pantallas, botones y gráficos | `frontend/` |
| La cocina, donde se preparan los platos con recetas | **Backend**: las reglas y los cálculos | `backend/` |
| La ventanilla por donde el mesero pasa pedidos a la cocina | **API**: la lista de "pedidos" que el backend sabe atender | `backend/app/api/` |
| La bodega donde se guardan los ingredientes | **Base de datos**: donde quedan guardados usuarios y mediciones | Supabase |
| Un chef invitado experto en un tema | **Gemini**: la IA que responde preguntas | Google |
| El local que se arrienda para abrir al público | **Hosting**: el computador en internet donde corre la app | Render |
| El cuaderno de recetas con todas sus versiones | **Repositorio**: el código con su historial de cambios | GitHub |

El cliente (paciente) nunca entra a la cocina: solo habla con el mesero (frontend). El mesero lleva el pedido por la ventanilla (API), la cocina (backend) lo prepara usando ingredientes de la bodega (base de datos) y devuelve el plato.

## ¿Por qué separar frontend y backend?

- **Seguridad**: la llave de Gemini, la clave de la base de datos y las reglas clínicas viven en el backend, donde el paciente no puede verlas ni modificarlas.
- **Orden**: quien diseña pantallas trabaja en `frontend/` y quien programa reglas trabaja en `backend/`, sin estorbarse.
- **Crecimiento**: el día que se construya una app para celular (Flutter o React Native), esa app usará el mismo backend sin cambiarle nada.

## Recorrido de un ejemplo real

La paciente María se mide la presión y el tensiómetro marca 150/95:

1. El tensiómetro envía los datos por Bluetooth al navegador (frontend).
2. El frontend los manda a la dirección `/dispositivos/1/sincronizar-ble` de la API.
3. El backend revisa que María haya iniciado sesión, decodifica los datos, clasifica la lectura como "hipertensión" y la guarda en Supabase.
4. El backend responde: "Medición guardada, categoría hipertensión".
5. El frontend muestra el número grande, la barra de colores y el mensaje.

## Glosario

**Servidor**: un computador que está siempre encendido esperando pedidos. Render nos presta uno gratis.

**Endpoint o ruta**: una dirección específica de la API, como `/lecturas/manual`. Cada una hace una sola cosa.

**JSON**: el formato de texto en que frontend y backend se mandan datos. Ejemplo: `{"sistolica": 150, "diastolica": 95}`.

**Token**: un "pase" firmado que el backend entrega al iniciar sesión. El navegador lo muestra en cada pedido para demostrar quién es, como una manilla en un evento.

**Variable de entorno**: un valor secreto o de configuración (claves, direcciones) que se guarda fuera del código. En su computador va en el archivo `backend/.env`; en Render, en la sección *Environment*.

**CORS**: una regla de los navegadores. Como el frontend y el backend viven en direcciones distintas, el backend debe decir explícitamente "acepto pedidos de esa página".

**Despliegue (deploy)**: el proceso de publicar la aplicación en internet.

**Cifrado**: convertir un texto en algo ilegible que solo se recupera con una llave. Los antecedentes y medicamentos de los pacientes se guardan cifrados.

**Prueba automática (test)**: un pequeño programa que verifica que otra parte del programa funcione bien. Este proyecto tiene 47.
