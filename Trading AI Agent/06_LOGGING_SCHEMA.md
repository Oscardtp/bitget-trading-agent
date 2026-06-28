# Trade Logging & Audit Schema

> 📄 **Módulo:** `06_LOGGING_SCHEMA.md`

## 🧠 Propósito

Este módulo define el estándar obligatorio para registrar todas las decisiones, ejecuciones y resultados generados por el sistema.

Su objetivo es garantizar:

- Trazabilidad completa.
- Auditoría de decisiones.
- Evaluación del desempeño.
- Análisis estadístico.
- Alimentación del módulo de aprendizaje continuo.

Toda acción relevante del agente debe quedar registrada.

---

## 🎯 Objetivos del módulo

El sistema debe poder responder preguntas como:

- ¿Qué estrategia generó esta operación?
- ¿Qué condiciones de mercado existían?
- ¿Qué parámetros de riesgo fueron utilizados?
- ¿Cuál fue el resultado?
- ¿Qué factores estuvieron presentes en las operaciones ganadoras?
- ¿Qué patrones precedieron las pérdidas?

---

## 🔗 Dependencias

Este módulo recibe información de:

- `01_MARKET_CONTEXT.md`
- `02_STRATEGY_SELECTOR.md`
- `03_RISK_ENGINE.md`
- `04_VALIDATION_ENGINE.md`
- `05_EXECUTION_PROTOCOL.md`

Y alimenta:

- `07_LEARNING_FEEDBACK_LOOP.md`

---

## 🗂️ Tipos de eventos a registrar

Todo evento relevante debe almacenarse.

**Eventos mínimos:**

- `TRADE_APPROVED`
- `TRADE_REJECTED`
- `ORDER_EXECUTED`
- `ORDER_CANCELLED`
- `ORDER_REJECTED`
- `POSITION_OPENED`
- `POSITION_CLOSED`
- `KILL_SWITCH_TRIGGERED`
- `SYSTEM_WARNING`
- `SYSTEM_ERROR`

---

## 📌 Principios de registro

### Inmutabilidad
Una vez registrado un evento:
- No debe modificarse.
- Las correcciones deben registrarse como nuevos eventos.

### Trazabilidad
Cada operación debe poseer un identificador único.
- **Ejemplo:** `TRADE-20260622-BTCUSDT-0001`

### Integridad
- No se permite registrar información parcial.
- Todos los campos obligatorios deben existir.

---

## 🧾 Esquema principal del Trade Log

### Identificación
```json
{
  "trade_id": "",
  "asset": "",
  "timestamp": "",
  "event_type": ""
}
```

### Contexto de mercado
Registrar exactamente el contexto utilizado para decidir.
```json
{
  "market_context": {
    "volumen_score": 0,
    "volatility_score": 0,
    "trend": "",
    "session_score": 0,
    "liquidity_score": 0,
    "spread_score": 0,
    "sentiment_score": 0
  }
}
```

### Evaluación estratégica
```json
{
  "strategy_selection": {
    "scores": {
      "scalping": 0,
      "swing": 0,
      "breakout": 0,
      "mean_reversion": 0
    },
    "selected_strategy": ""
  }
}
```

### Gestión de riesgo aplicada
```json
{
  "risk_profile": {
    "capital_allocation": 0,
    "stop_loss_multiplier": 0,
    "take_profit_ratio": 0,
    "max_positions": 0,
    "risk_profile": ""
  }
}
```

### Resultado de validación
```json
{
  "validation": {
    "approved": true,
    "confidence_score": 0,
    "decision": "",
    "reasons": []
  }
}
```

### Información de ejecución
```json
{
  "execution": {
    "execution_status": "",
    "order_id": "",
    "side": "",
    "quantity": 0,
    "entry_price": 0,
    "stop_loss": 0,
    "take_profit": 0,
    "fees": 0,
    "slippage": 0
  }
}
```

### Resultado financiero
Debe completarse al cierre de la operación.
```json
{
  "trade_result": {
    "exit_price": 0,
    "gross_pnl": 0,
    "net_pnl": 0,
    "return_pct": 0,
    "duration_minutes": 0,
    "result": "WIN | LOSS | BREAKEVEN"
  }
}
```

---

## 📤 Ejemplo completo

```json
{
  "trade_id": "TRADE-20260622-BTCUSDT-0001",
  "asset": "BTCUSDT",
  "timestamp": "2026-06-22T15:45:30Z",
  "event_type": "POSITION_CLOSED",
  "market_context": {
    "volumen_score": 0.72,
    "volatility_score": 0.61,
    "trend": "bullish",
    "session_score": 0.80,
    "liquidity_score": 0.90,
    "spread_score": 0.85,
    "sentiment_score": 0.65
  },
  "strategy_selection": {
    "scores": {
      "scalping": 0.74,
      "swing": 0.68,
      "breakout": 0.81,
      "mean_reversion": 0.41
    },
    "selected_strategy": "breakout"
  },
  "risk_profile": {
    "capital_allocation": 0.03,
    "stop_loss_multiplier": 1.8,
    "take_profit_ratio": 2.0,
    "max_positions": 2,
    "risk_profile": "moderate"
  },
  "validation": {
    "approved": true,
    "confidence_score": 0.84,
    "decision": "APPROVED",
    "reasons": []
  },
  "execution": {
    "execution_status": "FILLED",
    "order_id": "ORD-20260622-001",
    "side": "BUY",
    "quantity": 0.15,
    "entry_price": 105020,
    "stop_loss": 103500,
    "take_profit": 108000,
    "fees": 4.25,
    "slippage": 0.00019
  },
  "trade_result": {
    "exit_price": 108000,
    "gross_pnl": 447,
    "net_pnl": 438.50,
    "return_pct": 4.17,
    "duration_minutes": 187,
    "result": "WIN"
  }
}
```

---

## 📈 Métricas derivadas

El sistema debe ser capaz de calcular automáticamente:

### Rendimiento
- Win Rate
- Profit Factor
- Expectancy
- Sharpe Ratio
- Sortino Ratio
- Calmar Ratio

### Riesgo
- Maximum Drawdown
- Average Drawdown
- Recovery Factor
- Risk of Ruin

### Ejecución
- Slippage promedio
- Comisiones acumuladas
- Tiempo promedio de ejecución
- Tasa de rechazos

### Estrategias
- Win Rate por estrategia
- PnL por estrategia
- Profit Factor por estrategia
- Drawdown por estrategia

### Contexto de mercado
- Rendimiento por tendencia
- Rendimiento por volatilidad
- Rendimiento por sesión
- Rendimiento por nivel de liquidez

---

## 🗄️ Recomendaciones de almacenamiento

### Producción
**PostgreSQL + TimescaleDB**
- *Ventajas:* Consultas complejas, series temporales, escalabilidad.

### Desarrollo
**SQLite**

### Dashboards
- Grafana
- Metabase
- Power BI

---

## 🚨 Registro de incidentes

También deben almacenarse eventos no financieros.

**Ejemplos:**

```json
{
  "event_type": "KILL_SWITCH_TRIGGERED",
  "reason": "3 consecutive losses",
  "timestamp": ""
}
```

```json
{
  "event_type": "SYSTEM_ERROR",
  "reason": "Exchange API unavailable",
  "timestamp": ""
}
```

---

## 🚫 Restricciones obligatorias

- Ningún trade puede existir sin `trade_id`.
- Ninguna operación puede omitirse del registro.
- No se permite editar registros históricos.
- Los errores del sistema también deben registrarse.
- El resultado financiero debe actualizarse al cierre de la posición.
- Todo cambio de estado debe generar un evento.