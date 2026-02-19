# Desglose de Presupuesto: Proyecto Mr. Car

A continuación se detalla la inversión total de **$2.500.000 CLP** para el desarrollo de la plataforma de cotización y valoración automotriz, dividida en sus etapas fundamentales.

---

<details>
<summary><strong>1. Análisis de Requerimientos y Planificación — $200.000</strong></summary>

*   **Definición del Alcance**: Reuniones para entender el flujo de negocio de compra y consignación.
*   **Arquitectura del Sistema**: Diseño de la base de datos (Supabase) y flujo de la API (Python).
*   **Estrategia de Datos**: Planificación de la lógica de precios (reglas de negocio <8M y >8M).
*   **Selección Tecnológica**: Definición del stack (Vercel, Flask, PostgreSQL) para asegurar escalabilidad.
</details>

<details>
<summary><strong>2. Diseño UI/UX (Interfaz y Experiencia) — $350.000</strong></summary>

*   **Prototipado**: Creación de wireframes para el flujo de cotización paso a paso (Wizard).
*   **Diseño Visual**: Aplicación de la identidad corporativa de Mr. Car (colores, tipografía, logo).
*   **Experiencia Móvil**: Optimización prioritaria para celulares (Mobile First), donde ocurre el 80% del tráfico.
*   **Micro-interacciones**: Diseño de estados de carga, validaciones y feedback visual para el usuario.
</details>

<details>
<summary><strong>3. Desarrollo Frontend (Web App) — $600.000</strong></summary>

*   **Formulario Inteligente**: Desarrollo de la SPA (Single Page Application) que no recarga la página.
*   **Validaciones en Tiempo Real**: Algoritmos para validar Patentes Chilenas y RUT.
*   **Integración de Servicios**: Conexión con la API para enviar datos y recibir ofertas instantáneas.
*   **Componentes Reactivos**: Tablas de resultados, selectores de región/comuna y botones de acción (WhatsApp).
</details>

<details>
<summary><strong>4. Desarrollo Backend (Lógica de Negocio) — $750.000</strong></summary>

*   **API RESTful**: Desarrollo del servidor en Python (Flask) para procesar las solicitudes.
*   **Motor de Precios (Pricing Engine)**: Programación de las fórmulas matemáticas de compra (~52%) y consignación (Comisión vs Fee Fijo).
*   **Gestión de Leads**: Sistema para capturar y guardar cada intento de cotización en la base de datos.
*   **Seguridad**: implementación de variables de entorno y protección de rutas.
</details>

<details>
<summary><strong>5. Integración de APIs y Servicios Externos — $200.000</strong></summary>

*   **Base de Datos (Supabase)**: Configuración y conexión con PostgreSQL para persistencia de datos y leads.
*   **Emails Transaccionales (Resend)**: Configuración de plantillas HTML y envío automático de correos a clientes y administración.
*   **Integración WhatsApp**: Generación de enlaces dinámicos con el resumen de la cotización para el equipo de ventas.
*   **Servicios de Valoración**: Conexión inicial para obtener datos base del vehículo (Marca, Modelo, Año) según patente.
</details>

<details>
<summary><strong>6. Pruebas (QA) y Ajustes — $250.000</strong></summary>

*   **Pruebas de Flujo**: Verificación completa del proceso desde la carga de la página hasta la recepción del email.
*   **Pruebas de Estrés**: Simulación de múltiples cotizaciones simultáneas.
*   **Corrección de Bugs**: Ajustes finales en la interfaz y lógica basados en feedback.
*   **Compatibilidad**: Verificación de funcionamiento en distintos navegadores (Chrome, Safari) y dispositivos.
</details>

<details>
<summary><strong>7. Lanzamiento e Implementación — $150.000</strong></summary>

*   **Despliegue en Producción**: Configuración del entorno final en Vercel.
*   **Configuración de Dominio**: Conexión del dominio `mrcar.cl` (o similar) y certificación SSL (HTTPS).
*   **Entrega de Credenciales**: Traspaso de accesos a base de datos, paneles de administración y código fuente.
*   **Capacitación Básica**: Guía sobre cómo acceder a los leads y entender el sistema.
</details>

---

### **TOTAL PROYECTO: $2.500.000 CLP**
*Nota: El soporte posterior al lanzamiento se acordará en un contrato de mantenimiento separado (retainer).*
