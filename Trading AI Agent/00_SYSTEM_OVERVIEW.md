# Trading AI Agent - System Overview

## 🧠 Propósito del sistema

Este sistema es un agente cuantitativo modular diseñado para analizar activos financieros, seleccionar automáticamente la mejor estrategia de trading y ajustar dinámicamente la gestión de riesgo antes de ejecutar cualquier operación.

El objetivo principal es ejecutar decisiones estructuradas, consistentes y auditables basadas en datos de mercado.

---

## ⚙️ Filosofía del sistema

El agente opera bajo tres principios fundamentales:

### 1. Determinismo
Las decisiones deben ser reproducibles bajo las mismas condiciones de mercado.

### 2. Modularidad
Cada etapa del análisis es independiente y reemplazable sin afectar el resto del sistema.

### 3. Trazabilidad
Cada decisión debe poder ser explicada y registrada.

---

## 🧩 Pipeline obligatorio

Toda operación sigue estrictamente este flujo:

### 1. Análisis de contexto de mercado
- Volumen
- Volatilidad
- Tendencia
- Liquidez
- Spread
- Sesión de mercado
- Sentimiento (si disponible)

---

### 2. Selección de estrategia
Se evalúan múltiples estrategias y se calcula un score de compatibilidad.

Estrategias disponibles:
- Scalping
- Swing Trading
- Breakout
- Mean Reversion

---

### 3. Configuración de riesgo
Se ajustan dinámicamente los siguientes parámetros:

- Capital asignado (% del portafolio)
- Stop-loss dinámico
- Take-profit basado en ratio riesgo/beneficio
- Exposición máxima
- Número máximo de posiciones simultáneas

---

### 4. Validación previa a ejecución
Antes de ejecutar cualquier operación:

- Se realiza un mini backtest con datos recientes
- Se evalúa coherencia entre estrategia y contexto
- Se calcula un score de confianza

Si no cumple el umbral mínimo → el trade se rechaza.

---

### 5. Ejecución del trade
Si la validación es aprobada:

- Se ejecuta la orden con parámetros definidos
- No se permiten modificaciones durante ejecución

---

### 6. Registro de la operación
Se almacena toda la información del trade:

- Estrategia utilizada
- Condiciones de mercado
- Parámetros de riesgo
- Resultado final
- PnL
- Timestamp

---

### 7. Aprendizaje del sistema
Los resultados alimentan un módulo de mejora continua:

- Ajuste de pesos de estrategias
- Optimización de riesgo
- Evaluación de rendimiento por régimen de mercado

---

## 🚫 Restricciones del sistema

- No se permite ejecutar trades sin validación previa
- No se permiten decisiones sin datos de contexto
- No se permite alterar parámetros después de validación
- No se permite “intuición” sin respaldo de datos

---

## 🧠 Salida esperada del sistema

Cada ejecución debe producir un objeto estructurado:

```json
{
  "asset": "BTCUSDT",
  "context": {},
  "selected_strategy": "scalping",
  "risk_profile": {},
  "validation": {},
  "execution": {},
  "result": {}
}