# Market Context Analysis Module

## 🧠 Propósito

Este módulo se encarga de transformar datos crudos del mercado en un conjunto estructurado de variables normalizadas (0–1) que serán utilizadas por el sistema de selección de estrategia y gestión de riesgo.

El objetivo es convertir el mercado en un **vector de decisión cuantificable**.

---

## ⚙️ Entradas del módulo

El sistema recibe datos crudos del mercado (OHLCV + métricas externas si están disponibles).

### 📥 Input esperado

```json
{
  "asset": "BTCUSDT",
  "price": 0,
  "volume": 0,
  "volatility": 0,
  "high": 0,
  "low": 0,
  "open": 0,
  "close": 0,
  "timestamp": 0,
  "orderbook": {},
  "sentiment": null,
  "spread": 0,
  "liquidity": 0,
  "session": "NY"
}
```

---

## 📊 Variables de contexto generadas

El módulo transforma los datos en un conjunto de variables normalizadas:

1. 📦 **Volumen relativo**
   - Mide actividad del mercado.
   - Normalizado entre 0 y 1.
   - Fórmula: `volumen_score = volume_actual / volume_promedio`

2. 🌪 **Volatilidad**
   - Basada en ATR o rango (high-low).
   - Indica agresividad del mercado.
   - Fórmula: `volatility_score = ATR_normalizado`

3. 📈 **Tendencia**
   - Clasificación estructural:
     - `bullish`
     - `bearish`
     - `sideways`
   - Derivado de:
     - Medias móviles.
     - Estructura de máximos y mínimos.

4. 🕒 **Sesión de mercado**
   - Representa actividad según horario global:
     - Asia
     - Londres
     - Nueva York
     - Baja liquidez
   - Normalizado: `session_score ∈ [0,1]`

5. 💧 **Liquidez**
   - Mide facilidad de ejecución sin slippage:
     - Order book depth
     - Market participation
   - Normalizado: `liquidity_score ∈ [0,1]`

6. 📉 **Spread**
   - Coste implícito de entrada/salida.
   - Spread alto = peor condición.
   - Invertido a score: `spread_score = 1 - normalized_spread`

7. 🧠 **Sentimiento del mercado**
   - Opcional (si disponible):
     - Noticias
     - Social media
     - Fear & Greed Index
   - Normalizado: `sentiment_score ∈ [0,1]`

---

## ⚙️ Normalización estándar

Todas las variables numéricas deben ser convertidas a escala:

- **0.0** = condición débil o desfavorable
- **1.0** = condición fuerte o favorable

---

## 🧠 Reglas importantes

- Ningún valor debe salir sin normalización.
- Si un dato no está disponible → usar fallback neutro (`0.5`).
- No se deben inferir valores sin datos de entrada.
- Tendencia no se expresa como número, solo como categoría.

---

## 🚫 Restricciones

- No se permite usar “intuición” para llenar datos faltantes.
- No se deben generar valores fuera del rango `[0,1]`.
- No se deben mezclar unidades sin normalización previa.

---

## 🎯 Resultado del módulo

Este módulo convierte el mercado en:

- Un vector cuantitativo listo para scoring de estrategias.

---

## 🔗 Dependencias

Este módulo alimenta directamente a:

- `02_STRATEGY_SELECTOR.md`
- `03_RISK_ENGINE.md`