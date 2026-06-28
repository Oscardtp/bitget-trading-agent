# Strategy Selection Engine

> 📄 **Módulo:** `02_STRATEGY_SELECTOR.md`

## 🧠 Propósito

Este módulo determina cuál es la estrategia de trading más adecuada para el contexto actual del mercado.

El sistema no “elige por intuición”, sino mediante un **modelo de scoring determinístico por estrategia**.

---

## ⚙️ Entrada del módulo

Este módulo recibe el output de:

👉 `01_MARKET_CONTEXT.md`

### 📥 Input esperado

```json
{
  "volumen_score": 0.72,
  "volatility_score": 0.61,
  "trend": "bullish",
  "session_score": 0.80,
  "liquidity_score": 0.90,
  "spread_score": 0.85,
  "sentiment_score": 0.65
}
```

---

## 🧩 Estrategias disponibles

El sistema evalúa 4 estrategias principales:

1. Scalping
2. Swing Trading
3. Breakout
4. Mean Reversion

---

## 📊 Método de evaluación

Cada estrategia recibe un score ponderado basado en el contexto del mercado.

### ⚡ 1. Scalping

**🧠 Lógica**
Funciona mejor cuando hay:
- Alta liquidez
- Spread bajo
- Volatilidad activa
- Buena ejecución de órdenes

**📐 Fórmula**
```text
score_scalping = 
  (0.30 * volatility_score) + 
  (0.30 * liquidity_score) + 
  (0.25 * spread_score) + 
  (0.15 * session_score)
```

### 📈 2. Swing Trading

**🧠 Lógica**
Funciona mejor cuando hay:
- Tendencia clara
- Volatilidad moderada
- Estructura direccional

**📐 Fórmula**
```text
score_swing = 
  (0.40 * trend_strength) + 
  (0.25 * volatility_score) + 
  (0.20 * volume_score) + 
  (0.15 * sentiment_score)
```

> 📌 **Nota:**
> `trend_strength` se deriva internamente:
> - `bullish` = 1
> - `bearish` = 1
> - `sideways` = 0.3

### 🚀 3. Breakout

**🧠 Lógica**
Funciona cuando:
- Hay acumulación previa
- Aumento de volumen
- Volatilidad en expansión

**📐 Fórmula**
```text
score_breakout = 
  (0.45 * volume_score) + 
  (0.30 * volatility_score) + 
  (0.25 * liquidity_score)
```

### 🔄 4. Mean Reversion

**🧠 Lógica**
Funciona cuando:
- Mercado lateral
- Baja tendencia
- Excesos de precio

**📐 Fórmula**
```text
score_mean_reversion = 
  (0.40 * (1 - volatility_score)) + 
  (0.30 * (1 - trend_strength)) + 
  (0.30 * spread_score)
```

---

## 🧮 Selección final

La estrategia seleccionada es:

```text
selected_strategy = argmax([
  scalping, 
  swing, 
  breakout, 
  mean_reversion
])
```

---

## 📤 Output del módulo

```json
{
  "scores": {
    "scalping": 0.78,
    "swing": 0.64,
    "breakout": 0.71,
    "mean_reversion": 0.52
  },
  "selected_strategy": "scalping"
}
```

---

## ⚙️ Reglas del sistema

- Siempre se evalúan las 4 estrategias.
- No se permite seleccionar una estrategia sin scoring.
- En empate → se prioriza menor riesgo implícito.
- Nunca se selecciona aleatoriamente.

---

## 🚫 Restricciones

- No se permite override manual sin logging.
- No se permite estrategia fuera del set definido.
- No se permite omitir variables de contexto.

---

## 🧠 Dependencias

Este módulo depende de:

- `01_MARKET_CONTEXT.md`

Y alimenta:

- `03_RISK_ENGINE.md`
- `04_VALIDATION_ENGINE.md`