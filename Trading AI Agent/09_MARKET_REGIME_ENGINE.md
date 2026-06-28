# Market Regime Engine

## 🧠 Propósito

Este módulo identifica el régimen actual del mercado mediante el análisis de múltiples variables cuantitativas.

Su objetivo es clasificar el estado del mercado antes de seleccionar una estrategia.

No predice el mercado.

Lo clasifica.

El régimen detectado será utilizado por:

- Strategy Selector
- Risk Engine
- Pattern Discovery Engine
- Learning Feedback Loop

---

# 🎯 Objetivos

El sistema debe responder:

- ¿El mercado está en tendencia?
- ¿Existe expansión o contracción de volatilidad?
- ¿La liquidez favorece operar?
- ¿Qué régimen histórico es más parecido?
- ¿Qué estrategias funcionan mejor bajo este régimen?

---

# Dependencias

## Consume información desde

01_MARKET_CONTEXT.md

06_LOGGING_SCHEMA.md

08_PATTERN_DISCOVERY_ENGINE.md

---

## Alimenta

02_STRATEGY_SELECTOR.md

03_RISK_ENGINE.md

07_LEARNING_FEEDBACK_LOOP.md

---

# Filosofía

El mercado cambia constantemente.

Una estrategia no debe evaluarse únicamente por indicadores individuales.

Debe evaluarse considerando el régimen completo del mercado.

---

# Variables analizadas

## Tendencia

- EMA Slope
- SMA Slope
- Higher Highs
- Higher Lows
- Lower Highs
- Lower Lows

---

## Volatilidad

- ATR

- ATR Percentile

- Historical Volatility

- Bollinger Width

---

## Momentum

- RSI

- MACD

- ADX

---

## Liquidez

- Spread

- Bid Ask Imbalance

- Order Book Depth

- Average Volume

---

## Participación

- Open Interest

- Funding Rate

- Liquidaciones

---

## Contexto temporal

- Sesión

- Día

- Hora

- Eventos macroeconómicos

---

# Regímenes soportados

## 1 Trending Bull

Características

- Tendencia alcista

- ADX elevado

- ATR creciente

- Higher Highs

- Higher Lows

---

## Estrategias recomendadas

- Swing

- Trend Following

- Breakout

---

## 2 Trending Bear

Características

- Tendencia bajista

- Momentum negativo

- ATR creciente

---

## Estrategias recomendadas

- Swing Short

- Breakout Short

---

## 3 Sideways Low Volatility

Características

- ADX bajo

- ATR bajo

- Bollinger Width reducido

---

## Estrategias recomendadas

- Mean Reversion

- Range Trading

---

## 4 Sideways High Volatility

Características

- Mercado lateral

- Oscilaciones amplias

- ATR elevado

---

## Estrategias recomendadas

- Mean Reversion

- Scalping

---

## 5 Expansion Phase

Características

- ATR aumentando

- Volumen creciente

- Open Interest creciendo

- Bollinger Width expandiéndose

---

## Estrategias recomendadas

- Breakout

---

## 6 Contraction Phase

Características

- ATR disminuyendo

- Volumen decreciente

- Compresión de rango

---

## Estrategias recomendadas

Esperar.

Prepararse para futuros Breakouts.

---

## 7 Liquidity Crisis

Características

- Spread elevado

- Baja liquidez

- Order Book débil

---

## Estrategias

Reducir exposición.

O no operar.

---

## 8 High Impact News

Características

- Eventos económicos

- Noticias relevantes

- Volatilidad extrema

---

## Estrategias

Reducir riesgo.

Esperar estabilización.

---

# Clasificación

Cada régimen recibe un score.

Ejemplo

```text
Trending Bull

Score = 0.82

Trending Bear

Score = 0.11

Sideways

Score = 0.28

Expansion

Score = 0.77
```

El régimen con mayor puntuación será el activo.

---

# Confidence Score

Cada clasificación tendrá un nivel de confianza.

Ejemplo

```text
Regime

Trending Bull

Confidence

91%
```

---

# Similaridad histórica

El sistema consulta el Pattern Discovery Engine.

Pregunta:

¿Ya vimos este régimen?

Si existe:

Recuperar:

Win Rate

Expectancy

Profit Factor

Estrategias exitosas

---

# Ejemplo

```json
{

"current_regime":"TRENDING_BULL",

"confidence":0.91,

"historical_similarity":0.88,

"recommended_strategies":[

"Swing",

"Breakout"

]
}
```

---

# Cambios de régimen

El sistema debe detectar transiciones.

Ejemplo

Sideways

↓

Expansion

↓

Trending Bull

Cada transición debe registrarse.

---

# Persistencia

Registrar:

- inicio del régimen

- fin del régimen

- duración

- activo

- variables

---

# Output

```json
{

"regime":"TRENDING_BULL",

"confidence":0.91,

"historical_match":0.87,

"recommended_strategies":[

"Swing",

"Breakout"

],

"recommended_risk_profile":"Moderate"

}
```

---

# Restricciones

Nunca asumir un régimen sin datos suficientes.

Nunca utilizar un régimen con baja confianza.

Nunca cambiar de régimen por una única vela.

Confirmar mediante múltiples observaciones.

Registrar todos los cambios de régimen.

---

# Resultado

Este módulo transforma cientos de indicadores individuales en una única interpretación estructurada del mercado.

Su responsabilidad es responder:

> "¿Qué tipo de mercado estamos observando en este momento y qué comportamiento histórico suele presentar?"

La salida de este módulo permitirá que el resto del sistema adapte automáticamente la estrategia, la gestión del riesgo y el nivel de exposición al contexto real del mercado.