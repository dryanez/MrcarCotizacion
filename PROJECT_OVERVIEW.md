# Presupuesto: Plataforma de Cotización Mr. Car MVP

## 1. Resumen Ejecutivo

**Proyecto:** Plataforma de Cotización Automotriz Inteligente  
**Descripción:** Aplicación web moderna para la cotización instantánea de vehículos, cálculo automático de ofertas de compra y consignación, y gestión de leads.  
**Estado Actual:** MVP (Producto Mínimo Viable) funcional y desplegado.

---

## 2. Descripción Técnica ("Lo que construimos")

El sistema se compone de una arquitectura moderna, escalable y mantenible:

### **A. Frontend (La cara visible)**
- **Tecnología:** Single Page Application (SPA) con JavaScript Vanilla optimizado.
- **Diseño:** Interfaz profesional siguiendo la paleta de colores corporativa de **Mr. Car** (Naranja `#f86120` y Gris Oscuro `#32373c`).
- **Experiencia de Usuario (UX):** Formulario "Wizard" paso a paso, diseñado para alta conversión en móviles y escritorio.
- **Características Clave:**
  - Validación de RUT y Patentes chilenas.
  - Detección automática de región y comuna.
  - Feedback visual inmediato (spinners, barras de progreso).
  - Integración con WhatsApp para cierre de ventas.

### **B. Backend (El cerebro)**
- **Tecnología:** Python (Flask) en entorno Serverless (Vercel).
- **Lógica de Negocio (`pricing_engine.py`):**
  - Motor de precios personalizado "Mr. Car".
  - Cálculo automático de *Compra Inmediata* (52% valor mercado).
  - Cálculo de *Consignación* con lógica dual:
    - Vehículos < $8M: Fee fijo ($428.400).
    - Vehículos > $8M: Comisión variable (4.5% + IVA).
- **Integraciones:**
  - **Supabase (PostgreSQL):** Base de datos robusta para almacenar leads y precios.
  - **Resend:** Sistema de correos transaccionales para notificar al cliente y al administrador.
  - **Web Scraping:** Módulos para extracción de datos de mercado (Chileautos, Yapo) - *Actualmente simulado/en desarrollo para producción.*

### **C. Infraestructura**
- **Hosting:** Vercel (Alta disponibilidad, CDN global).
- **Base de Datos:** Supabase (Nube).
- **Seguridad:** Manejo seguro de API Keys y variables de entorno.

---

## 3. Valoración del Proyecto ("Cuánto cuesta")

Si estuvieras contratando este servicio a un desarrollador freelance senior o una agencia boutique en Chile para desarrollar este MVP desde cero hasta producción, los costos estimados serían:

### **Opción A: Desarrollo Freelance (Senior)**
*Un desarrollador full-stack experimentado.*

| Item | Descripción | Relleno | Costo Estimado (CLP) |
|------|-------------|---------|----------------------|
| **Desarrollo Backend** | API Python, Lógica de Precios, Base de Datos | | $800.000 - $1.200.000 |
| **Desarrollo Frontend** | Diseño UI/UX, React/JS, Integración Móvil | | $600.000 - $900.000 |
| **Integraciones** | Email (Resend), WhatsApp, Web Scraping | | $400.000 - $600.000 |
| **Despliegue** | Configuración de Servidores, Dominios, SSL | | $150.000 - $300.000 |
| **Total Proyecto** | | | **$1.950.000 - $3.000.000 + IVA** |

### **Opción B: Agencia de Software**
*Equipo multidisciplinario (PM, Diseñador, Devs, QA).*

| Item | Costo Estimado (CLP) |
|------|----------------------|
| **Total Proyecto** | **$4.500.000 - $8.000.000 + IVA** |
| *Incluye garantía extendida, diseño UX profesional, QA dedicado.* | |

### **Costos Recurrentes (Mensuales)**
Estos son los costos operativos para mantener la plataforma funcionando:

1.  **Vercel (Hosting):** $20 USD/mes (Gratis al inicio).
2.  **Supabase (Base de Datos):** $25 USD/mes (Gratis al inicio).
3.  **Resend (Emails):** $20 USD/mes (Gratis hasta 3000 emails/mes).
4.  **Mantenimiento Técnico:** $150.000 - $300.000 CLP/mes (Opcional, pero recomendado para mantener los scrapers y actualizaciones).

---

## 4. Conclusión

Este sistema no es una simple "página web", es una **aplicación de software a medida** que automatiza un proceso crítico de negocio (la cotización).

- **El valor real** está en la **lógica de precios automática**: Permite capturar leads 24/7 sin intervención humana inmediata, filtrando curiosos de clientes reales.
- **Escalabilidad**: Al estar en la nube, puede recibir 10 o 10.000 cotizaciones sin caerse.

*Este documento sirve como referencia técnica y comercial del activo digital desarrollado.*
