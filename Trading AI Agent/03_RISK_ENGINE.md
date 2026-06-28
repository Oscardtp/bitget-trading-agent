# Risk Management Engine

> 📄 **Módulo:** `03_RISK_ENGINE.md`

## 🧠 Propósito

Este módulo define la **gestión de riesgo dinámica** basada en el contexto del mercado y la estrategia seleccionada.

Su objetivo es garantizar que ninguna operación exponga el capital de forma inconsistente con las condiciones del mercado.

---

## ⚙️ Entradas del módulo

Este módulo recibe datos de:

- `01_MARKET_CONTEXT.md`
- `02_STRATEGY_SELECTOR.md`

### 📥 Input esperado

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
  "selected_strategy": "scalping"
}
```

---

## 🧩 Objetivo del Risk Engine

Traducir el estado del mercado en parámetros de control de exposición:

- Capital asignado
- Stop-loss dinámico
- Take-profit adaptativo
- Exposición máxima
- Número de posiciones simultáneas

---

## 📊 1. Capital asignado

El capital se define como porcentaje del portafolio.

**⚙️ Regla base**
```text
base_capital = 0.03
```

**🔥 Ajuste por volatilidad**
- Si `volatility_score > 0.7` → `0.02`
- Si `volatility_score < 0.3` → `0.05`

**📤 Resultado**
```text
"capital_allocation": 0.02 - 0.05
```

---

## 🛑 2. Stop-Loss Dinámico

**🧠 Lógica**
El stop-loss se ajusta según volatilidad:
- Alta volatilidad → stop más amplio
- Baja volatilidad → stop más ajustado

**📐 Fórmula base**
```text
stop_loss = ATR * stop_multiplier
```

**⚙️ Multiplicador dinámico**
- Si `volatility_score > 0.7` → `2.5`
- Si `volatility_score < 0.3` → `1.2`
- `else` → `1.8`

---

## 🎯 3. Take-Profit Adaptativo

**🧠 Lógica**
El take-profit depende del ratio riesgo/beneficio.

```text
take_profit = stop_loss * risk_reward_ratio
```

**⚙️ Ratio estándar**
```text
risk_reward_ratio = 2.0
```

---

## 📦 4. Exposición máxima

**🧠 Lógica**
Depende de la liquidez del mercado.

- Si `liquidity_score > 0.7` → max 3 posiciones
- Si `liquidity_score <= 0.7` → max 1–2 posiciones

---

## ⚖️ 5. Ajuste por estrategia

Cada estrategia modifica el riesgo base:

### ⚡ Scalping
- Menor capital
- Mayor frecuencia
- Stop ajustado
- *Capital:* reducido
- *Exposure:* alta frecuencia

### 📈 Swing
- Capital moderado
- Mayor tiempo en mercado

### 🚀 Breakout
- Riesgo medio-alto
- Stop más amplio

### 🔄 Mean Reversion
- Riesgo bajo
- Entradas controladas

---

## 📤 Output del módulo

```json
{
  "capital_allocation": 0.02,
  "stop_loss_multiplier": 2.5,
  "take_profit_ratio": 2.0,
  "max_positions": 2,
  "risk_profile": "conservative | moderate | aggressive"
}
```

---

## 🚫 Reglas críticas

- Nunca se permite riesgo sin ajuste por volatilidad.
- No se puede exceder el capital máximo definido.
- Stop-loss debe existir en toda operación.
- No se permiten trades sin `risk_profile`.

---

## 🔗 Dependencias

Depende de:

- `01_MARKET_CONTEXT.md`
- `02_STRATEGY_SELECTOR.md`

Alimenta:

- `04_VALIDATION_ENGINE.md`
- `05_EXECUTION_PROTOCOL.md`