# Pattern Discovery Engine

## 🧠 Propósito

Este módulo tiene como objetivo descubrir patrones recurrentes presentes en el mercado utilizando la información histórica almacenada por el sistema.

Su función NO es ejecutar operaciones.

Su responsabilidad es identificar relaciones estadísticas entre:

- Contexto del mercado.
- Estrategia utilizada.
- Gestión de riesgo aplicada.
- Resultado obtenido.

El conocimiento descubierto alimentará la mejora continua del sistema y permitirá detectar condiciones de mercado similares en el futuro.

---

# 🎯 Objetivos

El sistema debe ser capaz de responder preguntas como:

- ¿Qué tenían en común las operaciones ganadoras?
- ¿Qué factores aparecen antes de una pérdida?
- ¿Qué indicadores suelen anticipar un breakout exitoso?
- ¿Qué combinación de variables produce el mayor Expectancy?
- ¿Qué contexto favorece cada estrategia?
- ¿Qué patrones dejan de funcionar con el tiempo?

---

# 🔗 Dependencias

## Consume información desde

06_LOGGING_SCHEMA.md

---

## Alimenta

07_LEARNING_FEEDBACK_LOOP.md

09_MARKET_REGIME_ENGINE.md

02_STRATEGY_SELECTOR.md

03_RISK_ENGINE.md

---

# Principios

## Basado únicamente en evidencia

Nunca generar patrones por intuición.

Toda conclusión debe provenir de datos históricos.

---

## Correlación ≠ causalidad

Detectar una correlación NO implica asumir una relación causal.

Los patrones descubiertos deben validarse antes de incorporarse al sistema.

---

## Muestras suficientes

No aceptar patrones con una cantidad insuficiente de observaciones.

---

## Versionado

Todo patrón aprobado debe almacenarse con:

- fecha
- versión
- nivel de confianza
- tamaño de muestra

---

# 📥 Entrada del módulo

El módulo recibe toda la información almacenada por:

06_LOGGING_SCHEMA.md

Especialmente:

## Contexto del mercado

- ATR
- ATR Percentile
- RSI
- ADX
- MACD
- Bollinger Width
- VWAP Distance
- Spread
- Liquidez
- Volumen
- Volume Z-Score
- Order Book Imbalance
- Funding Rate
- Open Interest
- Fear & Greed
- Sentimiento
- Tendencia

---

## Contexto temporal

- Día de la semana
- Hora
- Sesión
- Cambio de sesión
- Mes
- Trimestre

---

## Decisiones del sistema

- Estrategia seleccionada
- Strategy Score
- Confidence Score
- Risk Profile
- Capital Allocation
- Stop Loss
- Take Profit
- RR Ratio

---

## Resultado

- WIN
- LOSS
- BREAKEVEN
- Net PnL
- Return %
- Drawdown
- MAE
- MFE
- Duración

---

# Proceso de descubrimiento

## Etapa 1

Agrupar operaciones similares.

Ejemplo:

Todas las operaciones:

- Breakout
- BTCUSDT
- NY Session

---

## Etapa 2

Construir vectores de características.

Ejemplo:

```text
[
Volatility Score,
Volume Score,
ATR,
ADX,
RSI,
Liquidity,
Funding,
Open Interest,
Sentiment,
Spread
]
```

---

## Etapa 3

Buscar patrones repetitivos.

Ejemplos:

- combinaciones frecuentes
- clusters
- asociaciones
- anomalías
- secuencias

---

## Etapa 4

Calcular estadísticas.

Para cada patrón:

- Win Rate

- Expectancy

- Profit Factor

- Drawdown

- Sharpe

- Frecuencia

---

## Etapa 5

Filtrar patrones débiles.

Descartar automáticamente:

- muestras pequeñas

- bajo Profit Factor

- Expectancy negativa

- alta inestabilidad

---

## Etapa 6

Asignar Confidence Score.

Cada patrón recibe una puntuación de confianza.

Ejemplo:

```text
Confidence =
Calidad Estadística
+
Frecuencia
+
Estabilidad
+
Recencia
```

---

# Tipos de patrones

## Contextuales

Ejemplo:

Alta volatilidad

↓

Breakout gana con mayor frecuencia.

---

## Temporales

Ejemplo:

Martes

↓

Swing Trading mejora.

---

## Indicadores

Ejemplo:

ADX > 30

ATR creciendo

↓

Mayor probabilidad de continuación.

---

## Liquidez

Ejemplo:

Alta liquidez

Spread reducido

↓

Scalping mejora significativamente.

---

## Riesgo

Ejemplo:

Capital Allocation 5%

↓

Mayor Drawdown.

---

## Secuenciales

Ejemplo:

ATR aumenta

↓

Volumen aumenta

↓

Open Interest aumenta

↓

Breakout rentable.

---

# Ejemplo de patrón descubierto

```json
{
  "pattern_id": "PATTERN-00031",

  "asset": "BTCUSDT",

  "conditions": {

    "volatility_score": ">0.75",

    "volume_score": ">0.80",

    "ADX": ">25",

    "session": "NY",

    "trend": "bullish"
  },

  "recommended_strategy": "Breakout",

  "statistics": {

    "sample_size": 642,

    "win_rate": 0.71,

    "expectancy": 0.39,

    "profit_factor": 2.18,

    "max_drawdown": 0.08
  },

  "confidence": 0.91
}
```

---

# Validación del patrón

Antes de aprobar un patrón:

Debe superar:

Sample Size mínimo

Win Rate mínimo

Expectancy positiva

Profit Factor mínimo

Estabilidad temporal

Validación Out-of-Sample

Walk Forward

---

# Registro de patrones

Todos los patrones deben almacenarse.

Ejemplo:

```json
{
  "pattern_id": "",

  "version": "",

  "creation_date": "",

  "last_validation": "",

  "sample_size": 0,

  "confidence": 0,

  "status": "ACTIVE | REVIEW | DEPRECATED"
}
```

---

# Detección de degradación

Si un patrón deja de funcionar:

Cambiar estado:

ACTIVE

↓

REVIEW

↓

DEPRECATED

Nunca eliminar.

---

# Reutilización

Cuando llega un nuevo mercado:

El sistema compara el contexto actual con:

Todos los patrones almacenados.

Calcula:

Similarity Score

---

Ejemplo

Contexto actual

↓

87% similar

↓

Pattern #31

↓

Históricamente:

Breakout

Win Rate:

71%

↓

Enviar recomendación al Strategy Selector.

---

# Salida del módulo

```json
{
  "matched_patterns": [

    {

      "pattern_id": "PATTERN-31",

      "similarity": 0.87,

      "confidence": 0.91,

      "recommended_strategy": "Breakout"
    }

  ],

  "new_patterns": [

    {

      "pattern_id": "PATTERN-58",

      "confidence": 0.82
    }

  ]
}
```

---

# Restricciones

Nunca crear patrones con menos de la muestra mínima definida.

Nunca utilizar un patrón no validado.

Nunca eliminar patrones históricos.

Nunca reemplazar reglas determinísticas sin validación.

Nunca modificar automáticamente los pesos del sistema.

---

# Resultado del módulo

Este módulo transforma miles de operaciones históricas en conocimiento reutilizable.

Su responsabilidad es responder:

> "¿Hemos visto antes un mercado similar y qué ocurrió cuando sucedió?"

El objetivo no es predecir el futuro.

El objetivo es reconocer situaciones estadísticamente similares y utilizar esa experiencia para mejorar la toma de decisiones futuras.