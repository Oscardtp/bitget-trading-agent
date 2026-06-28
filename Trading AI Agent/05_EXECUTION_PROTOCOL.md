# Trade Execution Protocol

> 📄 **Módulo:** `05_EXECUTION_PROTOCOL.md`

## 🧠 Propósito

Este módulo es responsable de transformar una decisión aprobada en una ejecución real o simulada del mercado.

Su función es garantizar que:

- Solo se ejecuten operaciones aprobadas.
- La orden enviada coincida exactamente con la validación previa.
- Existan controles frente a errores operativos.
- Todas las acciones sean registradas y auditables.

---

## 🎯 Objetivos del módulo

Antes de enviar cualquier orden, el sistema debe garantizar que:

- ✅ La operación fue aprobada.
- ✅ Los parámetros de riesgo son válidos.
- ✅ El tamaño de posición es correcto.
- ✅ El mercado cumple condiciones mínimas de ejecución.
- ✅ No se violan límites globales del portafolio.

---

## 🔗 Dependencias

Este módulo recibe información proveniente de:

- `01_MARKET_CONTEXT.md`
- `02_STRATEGY_SELECTOR.md`
- `03_RISK_ENGINE.md`
- `04_VALIDATION_ENGINE.md`

Y alimenta:

- `06_LOGGING_SCHEMA.md`

---

## 📥 Input esperado

```json
{
  "asset": "BTCUSDT",
  "approved": true,
  "confidence_score": 0.84,
  "selected_strategy": "breakout",
  "risk_profile": {
    "capital_allocation": 0.03,
    "stop_loss_multiplier": 1.8,
    "take_profit_ratio": 2.0,
    "max_positions": 2
  },
  "execution_parameters": {
    "entry_price": 105000,
    "stop_loss": 103500,
    "take_profit": 108000
  }
}
```

---

## 🛑 Etapa 1: Verificación de aprobación

**Regla obligatoria**
```text
approved == true
```

- Si `approved = false` → NO ejecutar.
- Registrar intento rechazado.
- Finalizar proceso.

---

## 📊 Etapa 2: Verificación de exposición

**🧠 Objetivo**
Evitar sobreapalancamiento y exceso de operaciones.

**Validar**
- **Número máximo de posiciones:** `open_positions < max_positions`
- **Exposición total del portafolio:** `portfolio_exposure ≤ portfolio_limit`

**Límite recomendado**
```text
portfolio_limit = 10%–20%
```

**Regla**
- Si se excede → **Trade = Rechazado**

---

## 💰 Etapa 3: Cálculo del tamaño de posición

**🧠 Objetivo**
Determinar cuántas unidades comprar o vender.

**Fórmula**
```text
capital_risked = portfolio_value × capital_allocation
```

**Tamaño de posición**
```text
position_size = capital_risked ÷ distancia_stop_loss
```

**Restricciones**
Debe respetar:
- Tamaño mínimo del exchange.
- Precisión decimal.
- Lotes permitidos.

---

## 🎯 Etapa 4: Construcción de la orden

**Información mínima**
Toda orden debe incluir:

```json
{
  "symbol": "",
  "side": "",
  "order_type": "",
  "quantity": 0,
  "entry_price": 0,
  "stop_loss": 0,
  "take_profit": 0
}
```

### Tipos de orden soportados

#### 🟢 Market Order
- **Uso recomendado:** Cuando la velocidad es prioritaria.
- **Riesgos:** Slippage elevado.

#### 🔵 Limit Order
- **Uso recomendado:** Mercados líquidos.
- **Riesgos:** Ejecución parcial o ausencia de ejecución.

#### 🟠 Stop Order
- **Uso recomendado:** Breakouts.

#### 🟣 Stop Limit
- **Uso recomendado:** Control avanzado de entrada.

### 🧮 Selección del tipo de orden por estrategia

- **Scalping:** Preferencia `Limit` → `Market`
- **Swing:** Preferencia `Limit`
- **Breakout:** Preferencia `Stop Market`
- **Mean Reversion:** Preferencia `Limit`

---

## ⚠️ Etapa 5: Control de slippage

**🧠 Objetivo**
Evitar ejecuciones demasiado alejadas del precio esperado.

**Fórmula**
```text
slippage = |execution_price - expected_price| ÷ expected_price
```

**Umbral recomendado**
- **Criptomonedas:** `≤ 0.50%`
- **Forex:** `≤ 0.20%`
- **Acciones:** `≤ 0.30%`

**Regla**
- Si `slippage` excede el límite → Cancelar ejecución y registrar incidente.

---

## 🛡️ Etapa 6: Confirmación de órdenes de protección

**🧠 Objetivo**
Garantizar que exista protección inmediata.

**Verificar**
- **Stop-Loss:** Debe existir.
- **Take-Profit:** Debe existir.

**Regla**
- Si alguno falta → Cancelar operación.

---

## 🔄 Etapa 7: Confirmación de ejecución

Una vez enviada la orden, verificar:
- Estado
- Precio ejecutado
- Cantidad ejecutada
- Comisiones

**Estados válidos**
- `Filled`: Ejecutada completamente.
- `Partially Filled`: Ejecutada parcialmente.
- `Pending`: Esperando ejecución.
- `Cancelled`: Cancelada.
- `Rejected`: Rechazada por exchange.

---

## 📤 Output del módulo

### ✅ Ejecución exitosa

```json
{
  "execution_status": "FILLED",
  "order_id": "ORD-20260622-001",
  "symbol": "BTCUSDT",
  "side": "BUY",
  "quantity": 0.15,
  "entry_price": 105020,
  "stop_loss": 103500,
  "take_profit": 108000,
  "fees": 4.25,
  "slippage": 0.00019,
  "timestamp": "2026-06-22T15:45:30Z"
}
```

### ❌ Ejecución rechazada

```json
{
  "execution_status": "REJECTED",
  "reason": "Slippage exceeded allowed threshold",
  "timestamp": "2026-06-22T15:45:30Z"
}
```

---

## 🚨 Protocolos de seguridad (Kill Switch)

El sistema debe detener nuevas operaciones si ocurre alguno de los siguientes eventos:

- **Drawdown diario máximo:** `≥ 5%`
- **Pérdidas consecutivas:** `≥ 3 trades consecutivos`
- **Error crítico del exchange:** API unavailable, Order synchronization failure, Authentication failure.
- **Latencia extrema:** `Execution latency > límite permitido`

**Acción**
1. Suspender nuevas ejecuciones.
2. Notificar incidente.
3. Requerir revisión del sistema.

---

## 🚫 Restricciones obligatorias

- Nunca ejecutar operaciones no aprobadas.
- Nunca modificar parámetros validados.
- Nunca enviar órdenes sin Stop-Loss.
- Nunca exceder límites de exposición.
- Nunca ignorar controles de slippage.
- Nunca omitir el registro del resultado de ejecución.