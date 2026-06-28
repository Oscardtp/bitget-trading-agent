# Pre-Trade Validation Engine

> 📄 **Módulo:** `04_VALIDATION_ENGINE.md`

## 🧠 Propósito

Este módulo tiene como objetivo validar la coherencia entre:

- El contexto actual del mercado.
- La estrategia seleccionada.
- La gestión de riesgo propuesta.

Su función es evitar operaciones con baja probabilidad estadística, condiciones inadecuadas o inconsistencias operativas.

El Validation Engine es la **última línea de defensa** antes de ejecutar una operación.

---

## 🎯 Objetivos del módulo

Antes de aprobar un trade, el sistema debe verificar que:

- La estrategia sea compatible con el mercado actual.
- El riesgo asignado sea coherente.
- Exista una ventaja estadística mínima.
- Las condiciones recientes respalden la decisión.
- No existan violaciones de las reglas del sistema.

Si cualquiera de estas validaciones falla, la operación debe ser **rechazada**.

---

## ⚙️ Entradas del módulo

Este módulo recibe información proveniente de:

- `01_MARKET_CONTEXT.md`
- `02_STRATEGY_SELECTOR.md`
- `03_RISK_ENGINE.md`

---

## 📥 Input esperado

```json
{
  "asset": "BTCUSDT",
  "context": {
    "volumen_score": 0.72,
    "volatility_score": 0.61,
    "trend": "bullish",
    "session_score": 0.80,
    "liquidity_score": 0.90,
    "spread_score": 0.85,
    "sentiment_score": 0.65
  },
  "selected_strategy": "breakout",
  "strategy_scores": {
    "scalping": 0.74,
    "swing": 0.68,
    "breakout": 0.81,
    "mean_reversion": 0.41
  },
  "risk_profile": {
    "capital_allocation": 0.03,
    "stop_loss_multiplier": 1.8,
    "take_profit_ratio": 2.0,
    "max_positions": 2
  }
}
```

---

## 🧩 Proceso de validación

La validación se realiza en cinco etapas.

### 1. Validación de coherencia estratégica

**🧠 Objetivo**
Confirmar que la estrategia seleccionada tenga suficiente compatibilidad con el contexto actual.

**Regla principal**
```text
strategy_score ≥ threshold
```

**Umbral recomendado**
```text
threshold = 0.65
```

**Reglas**
- Si `strategy_score < threshold` → **Trade = Rechazado**

---

### 2. Mini-backtest reciente

**🧠 Objetivo**
Evaluar cómo habría funcionado la combinación actual durante un período reciente.

**Ventana recomendada**
Dependiendo del timeframe utilizado:
- **Scalping:** Últimas 30–50 operaciones
- **Swing:** Últimos 3–6 meses
- **Breakout:** Últimas 50 señales
- **Mean Reversion:** Últimos 50 eventos similares

**Métricas mínimas a evaluar**
- Win Rate
- Profit Factor
- Expectancy
- Drawdown

**Umbrales sugeridos**
- **Win Rate:** `≥ 45%`
- **Profit Factor:** `≥ 1.20`
- **Expectancy:** `> 0`
- **Drawdown:** `≤ drawdown máximo permitido`

**Reglas**
- Si alguna métrica crítica falla → **Trade = Rechazado**

---

### 3. Validación de gestión de riesgo

**🧠 Objetivo**
Confirmar que el riesgo propuesto respete las reglas del sistema.

**Verificar**
- **Capital asignado:** `capital_allocation ≤ límite permitido`
- **Stop-loss:** Debe existir. `stop_loss > 0`
- **Ratio Riesgo/Beneficio:** `RR ≥ 1.5` (Recomendado: `RR ≥ 2.0`)
- **Exposición máxima:** No exceder `max_positions`

**Reglas**
- Si cualquiera falla → **Trade = Rechazado**

---

### 4. Validación operativa

**🧠 Objetivo**
Detectar condiciones del mercado que puedan deteriorar la ejecución.

**Evaluar**
- **Liquidez mínima:** `liquidity_score ≥ 0.40`
- **Spread máximo permitido:** `spread_score ≥ 0.40`
- **Sesión válida:** Evitar operar durante sesiones muertas, periodos de transición extrema o eventos especiales definidos por el sistema.

**Regla**
- Si las condiciones operativas son deficientes → **Trade = Rechazado**

---

### 5. Cálculo del Confidence Score

**🧠 Objetivo**
Consolidar todas las validaciones en una puntuación única.

**Componentes sugeridos**
- 30% compatibilidad estratégica
- 25% mini-backtest
- 20% gestión de riesgo
- 15% condiciones operativas
- 10% sentimiento

**Fórmula**
```text
confidence_score = 
  (0.30 × strategy_validation) +
  (0.25 × backtest_validation) +
  (0.20 × risk_validation) +
  (0.15 × execution_validation) +
  (0.10 × sentiment_validation)
```

**Interpretación**
- **≥ 0.80:** Aprobación fuerte
- **0.65 – 0.79:** Aprobación estándar
- **0.50 – 0.64:** Zona gris (Requiere reglas adicionales o reducción de riesgo)
- **< 0.50:** Rechazo automático

---

## 📤 Output del módulo

### ✅ Trade aprobado

```json
{
  "approved": true,
  "confidence_score": 0.84,
  "validation_details": {
    "strategy_validation": true,
    "backtest_validation": true,
    "risk_validation": true,
    "operational_validation": true
  },
  "decision": "APPROVED"
}
```

### ❌ Trade rechazado

```json
{
  "approved": false,
  "confidence_score": 0.43,
  "validation_details": {
    "strategy_validation": true,
    "backtest_validation": false,
    "risk_validation": true,
    "operational_validation": false
  },
  "decision": "REJECTED",
  "reasons": [
    "Profit Factor insuficiente",
    "Liquidez por debajo del mínimo permitido"
  ]
}
```

---

## 🚫 Restricciones obligatorias

- Ningún trade puede ejecutarse sin pasar este módulo.
- No se permite omitir ninguna etapa de validación.
- Toda operación rechazada debe registrar las razones.
- No se permite aprobación manual sin logging.
- No se pueden modificar resultados del mini-backtest.

---

## 🔗 Dependencias

Depende de:

- `01_MARKET_CONTEXT.md`
- `02_STRATEGY_SELECTOR.md`
- `03_RISK_ENGINE.md`

Alimenta:

- `05_EXECUTION_PROTOCOL.md`
- `06_LOGGING_SCHEMA.md`