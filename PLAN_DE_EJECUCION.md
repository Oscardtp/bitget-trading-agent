# Trading Agent - Plan de Ejecución Final v3.0

**Fecha:** 2026-06-27
**Filosofía:** El mercado cambia constantemente. Las estrategias son herramientas. El verdadero trabajo del agente es identificar el contexto, formular una hipótesis, arriesgar poco, validar continuamente esa hipótesis y retirarse rápidamente cuando la evidencia deja de apoyarla.

---

## Arquitectura General

```
IDENTIFICAR → FORMULAR → ARRIESGAR → VALIDAR → RETIRAR → APRENDER
  (contexto)  (hipótesis)  (poco)   (continuo)  (rápido)  (mejorar)
```

### Pipeline de 11 Módulos

| # | Módulo | Fase | Archivo Principal | Estado |
|---|--------|------|-------------------|--------|
| 01 | Market Context | Identificar | `context/market_context.py` | Fase 1 |
| 02 | Strategy Orchestrator | Formular + Activar/Apagar | `strategies/orchestrator.py` | Fase 3 |
| 03 | Risk Engine | Arriesgar Poco | `risk/risk_engine.py` | Fase 4 |
| 04 | Validation Engine | Antes de Ejecutar | `validation/validation_engine.py` | Fase 5 |
| 05 | Execution Protocol | Ejecutar | `execution/order_executor.py` | Fase 7 |
| 06 | Logging Schema | Registrar | `logging/trade_logger.py` | Fase 9 |
| 07 | Learning Feedback Loop | Aprender | `learning/adaptive_engine.py` | Fase 10 |
| 08 | Pattern Discovery | Descubrir | `patterns/pattern_discovery.py` | Fase 10 |
| 09 | Market Regime Engine | Clasificar | `regime/regime_detector.py` | Fase 2 |
| 10 | Thesis Monitor | Validar Continuo | `monitor/evidence_checker.py` | Fase 8 |
| 11 | Hypothesis Builder | Formular Hipótesis | `hypothesis/hypothesis_builder.py` | Fase 6 |
| -- | Alpha Research Engine | Investigar (I+D) | `alpha_research/` | **FUTURA (500+ trades)** |

---

## Filosofía del Sistema

```
BOT RETAIL:                          AGENTE HIPÓTESIS:
"Compré porque RSI dice X"          "Creo que X porque [razón]"
↓                                   ↓
Espera SL/TP                        Cada 3 min: ¿La razón sigue válida?
↓                                   ↓
Si pierde: "mala señal"             Si razón desaparece: SALE
                                    ↓
                                    Si pierde: "mi hipótesis estaba mal, ¿por qué?"
```

### El Edge Real

```
Nivel 1 (bot básico):    "Ejecuto señales de RSI"
Nivel 2 (estrategia):    "Ejecuto la estrategia que mejor se adapta"
Nivel 3 (orchestrator):  "APAGO las estrategias que fallan en este contexto"
Nivel 4 (aprendizaje):   "APAGO basado en MI historial de trades"
Nivel 5 (patterns):      "Este régimen se parece al que vimos en X fecha"
```

---

## Estructura del Proyecto

```
TradingAgent/
├── main.py
├── config/settings.py
│
├── context/                          # FASE 1: IDENTIFICAR
│   ├── __init__.py
│   ├── market_context.py
│   ├── volume_analyzer.py
│   ├── volatility_analyzer.py
│   ├── trend_analyzer.py
│   ├── session_analyzer.py
│   └── liquidity_analyzer.py
│
├── hypothesis/                       # FASE 6: FORMULAR HIPÓTESIS
│   ├── __init__.py
│   ├── hypothesis_builder.py
│   ├── hypothesis_scorer.py
│   └── hypothesis_templates.py
│
├── regime/                           # FASE 2: CLASIFICAR
│   ├── __init__.py
│   ├── regime_detector.py
│   ├── regime_rules.py
│   └── historical_similarity.py
│
├── strategies/                       # FASE 3: ORQUESTAR
│   ├── __init__.py
│   ├── orchestrator.py               # NÚCLEO: decide qué activar/apagar
│   ├── strategy_base.py
│   ├── registry.py
│   ├── scoring.py
│   ├── learning_matrix.py
│   │
│   ├── momentum/
│   │   └── relative_strength_rotation.py
│   ├── continuation/
│   │   └── acceptance_breakout.py
│   ├── reversion/
│   │   ├── liquidity_sweep.py
│   │   └── failed_auction.py
│   ├── volatility/
│   │   └── expansion_after_compression.py
│   ├── sentiment/
│   │   └── funding_extremes.py
│   ├── positioning/
│   │   └── oi_divergence.py
│   ├── contrarian/
│   │   └── exhaustion_move.py
│   └── filters/
│       ├── btc_leadership.py
│       └── no_trade.py
│
├── risk/                             # FASE 4: ARRIESGAR POCO
│   ├── __init__.py
│   ├── risk_engine.py
│   ├── capital_allocator.py
│   ├── sl_tp_calculator.py
│   ├── trailing.py
│   ├── drawdown.py
│   ├── position_sizer.py
│   ├── regime_risk.py
│   └── strategy_risk.py
│
├── validation/                       # FASE 5: VALIDAR ANTES DE EJECUTAR
│   ├── __init__.py
│   ├── validation_engine.py
│   ├── coherence_check.py
│   ├── mini_backtest.py
│   ├── risk_validation.py
│   ├── operational_check.py
│   └── confidence_scorer.py
│
├── execution/                        # FASE 7: EJECUTAR
│   ├── __init__.py
│   ├── order_executor.py
│   ├── bitget_client.py
│   ├── slippage_checker.py
│   └── kill_switch.py
│
├── monitor/                          # FASE 8: VALIDAR CONTINUO ← EL CORAZÓN
│   ├── __init__.py
│   ├── thesis_lifecycle.py
│   ├── evidence_checker.py
│   ├── position_exiter.py
│   ├── time_decay.py
│   ├── regime_delta.py
│   └── score_delta.py
│
├── logging/                          # FASE 9: REGISTRAR
│   ├── __init__.py
│   ├── trade_logger.py
│   └── metrics_calculator.py
│
├── learning/                         # FASE 10: APRENDER
│   ├── __init__.py
│   ├── adaptive_engine.py
│   ├── degradation_detector.py
│   ├── weight_updater.py
│   ├── version_manager.py
│   └── hypothesis_review.py
│
├── patterns/                         # FASE 10: DESCUBRIR PATRONES
│   ├── __init__.py
│   ├── pattern_discovery.py
│   ├── pattern_validator.py
│   └── pattern_matcher.py
│
├── fundamental/                      # FASE 11: ANÁLISIS FUNDAMENTAL
│   ├── __init__.py
│   ├── news_collector.py
│   ├── sentiment.py
│   └── fundamental_scorer.py
│
├── db/
│   ├── database.py
│   └── models.py
│
└── requirements.txt
```

---

## Las 10 Estrategias del Baúl

| # | Estrategia | Tipo | Contexto Ideal | Cuándo APAGAR |
|---|-----------|------|----------------|---------------|
| 1 | Relative Strength Rotation | Momentum | Tendencias claras | Laterales, baja liquidez |
| 2 | Acceptance Breakout | Continuación | Compresión | After news, alta vol no estructurada |
| 3 | Liquidity Sweep | Reversión | Laterales | Tendencia fuerte |
| 4 | Failed Auction | Reversión | Extremos de precio | Tendencia intacta |
| 5 | Expansion After Compression | Volatilidad | Pre-expansión (squeeze) | After expansion ya empezó |
| 6 | BTC Leadership | Filtro | Siempre | BTC dominancia cayendo fuerte |
| 7 | Funding Extremes | Sentimiento | Sobreapalancamiento | Mercado calmado |
| 8 | OI Divergence | Posicionamiento | Confirmación | Mercado sin dirección |
| 9 | Exhaustion Move | Contrarian | Clímax de movimiento | Tendencia temprana |
| 10 | No Trade | Protección | Contexto desfavorable | (siempre disponible) |

---

## Fase 0: Infraestructura Base (2 días)

### 0.1 - Crear estructura de directorios
Crear todos los directorios del proyecto con sus `__init__.py`.

### 0.2 - requirements.txt
```
ccxt>=4.0
pandas>=2.0
numpy>=1.24
requests>=2.31
sqlalchemy>=2.0
pydantic>=2.0
python-dotenv>=1.0
```

### 0.3 - config/settings.py
```python
RISK_BASE = 0.01
RISK_MIN = 0.005
RISK_MAX = 0.05
RR_MIN = 2.0
MAX_POSITIONS = 3
MAX_TRADES_DAY = 5
SESSIONS = ["london", "new_york"]
STRATEGY_THRESHOLD = 0.65
CONFIDENCE_THRESHOLD = 0.65

DURATION_LIMITS = {
    "scalping": 6,
    "swing": 360,
    "breakout": 72,
    "mean_reversion": 12
}

MAX_DRAWDOWN_DAILY = 0.05
MAX_CONSECUTIVE_LOSSES = 3
MAX_SLIPPAGE = 0.005

SCANNER_INTERVAL = 300
MONITOR_INTERVAL = 120
```

### 0.4 - db/database.py
Conexión SQLite con SQLAlchemy.

### 0.5 - db/models.py
Tablas:
- `trades`
- `context_history`
- `regime_history`
- `hypotheses`
- `monitoring_log`
- `patterns`
- `strategy_performance_matrix` (régimen × estrategia × métricas)
- `system_versions`

---

## Fase 1: Market Context (01_MARKET_CONTEXT) - 3 días

### Archivos

| Archivo | Responsabilidad |
|---------|-----------------|
| `context/volume_analyzer.py` | `volumen_score = volume_actual / volume_promedio_20d` normalizado 0-1 |
| `context/volatility_analyzer.py` | `volatility_score = ATR_normalizado` (ATR(5) o rango) |
| `context/trend_analyzer.py` | Clasifica: `bullish`/`bearish`/`sideways` + `trend_strength` |
| `context/session_analyzer.py` | `session_score ∈ [0,1]` según actividad global |
| `context/liquidity_analyzer.py` | `liquidity_score` + `spread_score = 1 - normalized_spread` |
| `context/market_context.py` | Agrega todo → output JSON normalizado 0-1 |

### Input
```json
{
  "asset": "BTCUSDT",
  "price": 0, "volume": 0, "high": 0, "low": 0, "open": 0, "close": 0,
  "timestamp": 0, "orderbook": {}, "spread": 0
}
```

### Output
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

### Reglas
- Todas las variables normalizadas 0-1
- Si dato no disponible → fallback 0.5
- No inferir valores sin datos
- Tendencia solo como categoría, no número

---

## Fase 2: Market Regime Engine (09) - 3 días

### Archivos

| Archivo | Responsabilidad |
|---------|-----------------|
| `regime/regime_rules.py` | Define 8 regímenes con condiciones |
| `regime/regime_detector.py` | Analiza variables → score por régimen |
| `regime/historical_similarity.py` | Consulta Pattern Discovery para comparar |

### 8 Regímenes

| # | Régimen | Características | Estrategias Recomendadas |
|---|---------|-----------------|--------------------------|
| 1 | TRENDING_BULL | ADX alto, ATR creciente, HH/HL | Relative Strength Rotation, Acceptance Breakout |
| 2 | TRENDING_BEAR | Momentum negativo, ATR creciente | Relative Strength Rotation, Liquidity Sweep |
| 3 | SIDEWAYS_LOW_VOL | ADX bajo, ATR bajo, Bollinger reducido | Liquidity Sweep, Failed Auction, No Trade |
| 4 | SIDEWAYS_HIGH_VOL | Lateral, oscillaciones amplias | Liquidity Sweep, Exhaustion Move |
| 5 | EXPANSION | ATR aumentando, volumen creciente | Acceptance Breakout, Expansion After Compression |
| 6 | CONTRACTION | ATR disminuyendo, volumen decreciente | Expansion After Compression, No Trade |
| 7 | OVERLEVERAGED | Funding alto, OI creciendo | Funding Extremes, OI Divergence |
| 8 | CLIMAX | Movimiento extremo, volumen pico | Exhaustion Move, Failed Auction |

### Output
```json
{
  "regime": "TRENDING_BULL",
  "confidence": 0.91,
  "historical_match": 0.87,
  "recommended_strategies": ["relative_strength_rotation", "acceptance_breakout"],
  "recommended_risk_profile": "Moderate"
}
```

### Reglas
- Nunca asumir régimen sin datos suficientes
- Nunca usar régimen con baja confianza
- Nunca cambiar de régimen por una única vela
- Confirmar con múltiples observaciones

---

## Fase 3: Strategy Orchestrator (02) - 3 días

### Archivos

| Archivo | Responsabilidad |
|---------|-----------------|
| `strategies/orchestrator.py` | NÚCLEO: decide qué activar/apagar |
| `strategies/strategy_base.py` | Interfaz común para todas las estrategias |
| `strategies/registry.py` | Registro de estrategias disponibles |
| `strategies/scoring.py` | Score por estrategia |
| `strategies/learning_matrix.py` | Matriz de desempeño régimen × estrategia |
| `strategies/momentum/relative_strength_rotation.py` | Implementación |
| `strategies/continuation/acceptance_breakout.py` | Implementación |
| `strategies/reversion/liquidity_sweep.py` | Implementación |
| `strategies/reversion/failed_auction.py` | Implementación |
| `strategies/volatility/expansion_after_compression.py` | Implementación |
| `strategies/sentiment/funding_extremes.py` | Implementación |
| `strategies/positioning/oi_divergence.py` | Implementación |
| `strategies/contrarian/exhaustion_move.py` | Implementación |
| `strategies/filters/btc_leadership.py` | Implementación |
| `strategies/filters/no_trade.py` | Implementación |

### Lógica del Orchestrator

```python
def get_active_strategies(regime, context):
    all_strategies = registry.get_all()
    active = []

    for strategy in all_strategies:
        # 1. ¿Compatible con el régimen?
        if not is_compatible(strategy, regime):
            continue

        # 2. ¿Historial positivo en este régimen?
        performance = performance_matrix.get(strategy.name, regime)
        if performance and performance["win_rate"] < 0.40:
            continue  # APAGADA

        # 3. ¿Condiciones específicas se cumplen?
        if not strategy.check_conditions(context):
            continue

        active.append(strategy)

    return active
```

### Matriz de Desempeño (lo que la IA aprende)

```python
# Cada 50 trades se actualiza
# La IA aprende: "En este régimen, esta estrategia falla el 70% de las veces"

# Ejemplo de decisión:
# Regime: OVERLEVERAGED
# Estrategias activas: funding_extremes (0.92), oi_divergence (0.78), btc_leadership (0.85)
# APAGADAS: relative_strength_rotation, liquidity_sweep, acceptance_breakout, etc.
```

### Output
```json
{
  "scores": {
    "relative_strength_rotation": 0.88,
    "acceptance_breakout": 0.74,
    "liquidity_sweep": 0.0,
    "funding_extremes": 0.92
  },
  "active_strategies": ["relative_strength_rotation", "acceptance_breakout", "btc_leadership"],
  "disabled_strategies": ["liquidity_sweep", "failed_auction", "no_trade"]
}
```

---

## Fase 4: Risk Engine (03) - 3 días

### Archivos

| Archivo | Responsabilidad |
|---------|-----------------|
| `risk/risk_engine.py` | Motor principal |
| `risk/capital_allocator.py` | Base 0.03, si volatility>0.7 → 0.02, si <0.3 → 0.05 |
| `risk/sl_tp_calculator.py` | SL = ATR × multiplier (1.2/1.8/2.5), TP = SL × 2.0 |
| `risk/trailing.py` | +0.8% → BE, +1.2% → +0.3%, +1.6% → +0.6% |
| `risk/drawdown.py` | 2 pérdidas → -25%, 3 → 0.25%, 4 → parar |
| `risk/position_sizer.py` | `position_size = capital_risked / distancia_stop` |
| `risk/regime_risk.py` | Ajuste por régimen |
| `risk/strategy_risk.py` | Ajuste por tipo de estrategia |

### Integración con Gestion_Riesgo
- `risk/sl_tp_calculator.py` → usa lógica ATR + Order Book (`Gestion_Riesgo/01-atr-orderbook.md`)
- `risk/drawdown.py` → usa sistema 3F-R (`Gestion_Riesgo/02-3f-r.md`)
- `risk/position_sizer.py` → usa fórmula de position sizing

### Output
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

## Fase 5: Validation Engine (04) - 3 días

### 5 Etapas de Validación

| # | Etapa | Archivo | Umbral |
|---|-------|---------|--------|
| 1 | Coherencia estratégica | `validation/coherence_check.py` | `strategy_score ≥ 0.65` |
| 2 | Mini-backtest reciente | `validation/mini_backtest.py` | WR ≥45%, PF ≥1.20, Expectancy >0 |
| 3 | Gestión de riesgo | `validation/risk_validation.py` | Capital ≤ límite, SL existe, RR ≥1.5 |
| 4 | Condiciones operativas | `validation/operational_check.py` | Liquidez ≥0.40, Spread ≥0.40 |
| 5 | Confidence Score | `validation/confidence_scorer.py` | `0.30*strategy + 0.25*backtest + 0.20*risk + 0.15*operational + 0.10*sentiment` |

### Interpretación
- ≥0.80: Aprobación fuerte
- 0.65-0.79: Aprobación estándar
- 0.50-0.64: Zona gris (reducir riesgo)
- <0.50: Rechazo automático

### Checklist Pre-Operativa (del proyecto)

**General (6/8 mínimo):**
1. Estructura del mercado clara
2. Zona de liquidez/OB/FVG identificada
3. Señal de entrada confirmada
4. Volumen acompaña la señal
5. SL basado en estructura real
6. TP definido con R:R ≥ 2:1
7. No hay noticias importantes en próximas 2h
8. Position sizing calculado correctamente

**Gestión de Riesgo (5/6 mínimo):**
1. Riesgo por trade: 0.5% – 2%
2. SL colocado
3. TP1/TP2 definidos
4. Trailing stop planificado
5. No estoy en racha de 3 pérdidas seguidas
6. No excedí mi riesgo diario/mensual

**Psicológico (4/4 obligatorio):**
1. Estoy tranquilo y enfocado
2. No estoy "recuperando" pérdidas
3. No es un trade por aburrimiento/FOMO
4. Sigo mi sistema, no mi intuición

---

## Fase 6: Hypothesis Builder (NUEVO) - 2 días

### Archivos

| Archivo | Responsabilidad |
|---------|-----------------|
| `hypothesis/hypothesis_builder.py` | Construye hipótesis desde contexto + estrategia |
| `hypothesis/hypothesis_scorer.py` | Evalúa fuerza de la hipótesis (0-1) |
| `hypothesis/hypothesis_templates.py` | Templates: continuación, reversión, ruptura |

### Estructura de una Hipótesis

```python
class Hypothesis:
    statement: str              # "BTC continuará subiendo porque..."
    context_snapshot: dict      # Qué vi cuando la formulé
    probability: float          # Qué tan probable creo que es (0-1)
    evidence_for: list          # Qué la apoya
    evidence_against: list      # Qué la contradice
    time_limit_hours: int       # Cuánto tiempo le doy
    invalidation_triggers: list # Qué la destruye
    risk_budget: float          # Cuánto estoy dispuesto a perder
```

### Generación Automática

```python
def build_hypothesis(context, strategy, risk):
    return Hypothesis(
        statement=f"{strategy} en {context['trend']} porque volumen={context['volumen_score']}, régimen=favorable",
        context_snapshot=context,
        probability=calculate_probability(context, strategy),
        evidence_for=extract_evidence_for(context),
        evidence_against=extract_evidence_against(context),
        time_limit_hours=DURATION_LIMITS[strategy],
        invalidation_triggers=define_triggers(context, strategy),
        risk_budget=risk["capital_allocation"]
    )
```

---

## Fase 7: Execution Protocol (05) - 2 días

### Archivos

| Archivo | Responsabilidad |
|---------|-----------------|
| `execution/bitget_client.py` | Wrapper ccxt: auth, balance, ticker, order |
| `execution/order_executor.py` | Verifica aprobación → construye orden → envía → confirma |
| `execution/slippage_checker.py` | `slippage = |exec - expected| / expected ≤ 0.50%` |
| `execution/kill_switch.py` | DD ≥5%, 3 pérdidas, API error, latencia extrema |

### Kill Switch
- Drawdown diario ≥5%
- Pérdidas consecutivas ≥3
- Error crítico del exchange
- Latencia extrema

---

## Fase 8: Thesis Monitor (CRÍTICO) - 3 días

### Archivos

| Archivo | Responsabilidad |
|---------|-----------------|
| `monitor/thesis_lifecycle.py` | Gestiona la vida de cada hipótesis |
| `monitor/evidence_checker.py` | Verifica evidencia cada 1-3 minutos |
| `monitor/position_exiter.py` | Salida rápida (parcial o total) |
| `monitor/time_decay.py` | Control de duración vs límite |
| `monitor/regime_delta.py` | Compara régimen apertura vs actual |
| `monitor/score_delta.py` | Compara scores apertura vs actual |

### Las 5 Preguntas de Validación

| # | Pregunta | Qué verifica | Si falla |
|---|----------|--------------|----------|
| 1 | ¿El contexto original sigue presente? | Régimen, tendencia, volumen | INVALIDAR |
| 2 | ¿Ha aparecido contrasevidencia? | Algo nuevo que contradice | Si fuerte → INVALIDAR |
| 3 | ¿El mercado me está dando la razón? | Precio se mueve como esperaba | Si no → DEBILITAR |
| 4 | ¿Pasó demasiado tiempo? | Duración vs límite | Si expiró → INVALIDAR |
| 5 | ¿El riesgo creció sin recompensa? | Slippage, spread, volatilidad | Si creció → DEBILITAR |

### Veredictos

```python
class EvidenceVerdict(Enum):
    VALID = "valid"           # Mantener posición
    WEAKENED = "weakened"     # Reducir 30-50%
    INVALIDATED = "invalidated" # Cerrar completamente
```

### Límites de Tiempo

| Estrategia | Duración típica | Máximo |
|------------|-----------------|--------|
| Scalping | 1-4 horas | 6 horas |
| Swing | 2-10 días | 15 días |
| Breakout | 4-48 horas | 72 horas |
| Mean Reversion | 1-8 horas | 12 horas |

### Datos por Posición (snapshot de apertura)

```json
{
  "position_id": "POS-001",
  "entry_timestamp": "2026-06-22T15:45:30Z",
  "entry_context": {
    "regime": "TRENDING_BULL",
    "regime_confidence": 0.91,
    "strategy_score": 0.81,
    "fundamental_score": 0.72,
    "volatility_score": 0.61,
    "volume_score": 0.72
  },
  "entry_strategy": "breakout",
  "max_duration_hours": 48,
  "thesis_summary": "Breakout en BTC con régimen Trending Bull"
}
```

---

## Fase 9: Logging (06) - 2 días

### Schema por Trade

```json
{
  "trade_id": "TRADE-001",
  "asset": "BTCUSDT",
  "timestamp": "2026-06-22T15:45:30Z",
  "event_type": "POSITION_CLOSED",
  "hypothesis": {
    "statement": "...",
    "probability": 0.72,
    "evidence_for": [...],
    "evidence_against": [...],
    "time_limit_hours": 8,
    "invalidation_triggers": [...]
  },
  "market_context": {...},
  "strategy_selection": {...},
  "risk_profile": {...},
  "validation": {...},
  "execution": {...},
  "monitoring_log": [
    {"time": "T+1h", "verdict": "VALID"},
    {"time": "T+3h", "verdict": "WEAKENED", "reason": "volumen cayó"},
    {"time": "T+4h", "verdict": "INVALIDATED", "reason": "régimen cambió"}
  ],
  "trade_result": {
    "exit_price": 0,
    "gross_pnl": 0,
    "net_pnl": 0,
    "return_pct": 0,
    "duration_minutes": 0,
    "result": "WIN | LOSS | BREAKEVEN",
    "exit_reason": "THESIS_INVALIDATED"
  }
}
```

### Métricas Derivadas

| Categoría | Métricas |
|-----------|----------|
| Rendimiento | Win Rate, Profit Factor, Expectancy, Sharpe, Sortino, Calmar |
| Riesgo | Max Drawdown, Avg Drawdown, Recovery Factor, Risk of Ruin |
| Ejecución | Slippage promedio, Comisiones, Latencia, Tasa de rechazos |
| Estrategias | WR por estrategia, PnL por estrategia, PF por estrategia |
| Contexto | Rendimiento por tendencia, por volatilidad, por sesión, por liquidez |
| Hipótesis | Tasa de invalidación, Tiempo promedio de vida, Razones más comunes |

---

## Fase 10: Learning + Pattern Discovery (07+08) - 3 días

### 10.1 - Detección de Degradación

| Métrica | Señal de Alerta |
|---------|-----------------|
| Profit Factor | PF actual < PF histórico × 0.80 |
| Drawdown | DD actual > DD histórico × 1.50 |
| Win Rate | WR actual < WR histórico − 10% |

### 10.2 - Ajuste de Pesos
- Variables: volumen, volatilidad, liquidez, spread, sentimiento, tendencia
- Restricción: ±5% por ciclo de revisión

### 10.3 - Pattern Discovery

**Proceso:**
1. Agrupar operaciones similares
2. Construir vectores de características
3. Buscar patrones repetitivos
4. Calcular estadísticas (WR, PF, expectancy, Sharpe, frecuencia)
5. Filtrar patrones débiles
6. Asignar Confidence Score

**Tipos de patrones:**
- Contextuales, Temporales, Indicadores, Liquidez, Secuenciales

### 10.4 - Hypothesis Review
- ¿Qué razones fallaron más?
- ¿Qué tipo de hipótesis tiene mayor éxito?
- ¿Cuánto tiempo viven ganadoras vs perdedoras?
- ¿Qué invalidation triggers son más efectivos?

---

## Fase 11: Fundamental (tu adición) - 2 días

### APIs

| Fuente | Uso | Costo |
|--------|-----|-------|
| CryptoPanic | Noticias crypto | Free tier |
| Alternative.me | Fear & Greed | Gratis |
| Bitget API | OHLCV, precio, orderbook | Gratis |

### Archivos

| Archivo | Responsabilidad |
|---------|-----------------|
| `fundamental/news_collector.py` | CryptoPanic API |
| `fundamental/sentiment.py` | Fear & Greed, social |
| `fundamental/fundamental_scorer.py` | Score fundamental 0-1 |

---

## Fase 12: Loop Principal (main.py) - 2 días

### Los 2 Modos del Loop

```python
class TradingAgent:
    def run(self):
        while True:
            # MODO 1: Scanner cada 5-15 min
            if time_to_scan():
                opportunities = self.scan_opportunities()
                for opp in opportunities:
                    if opp.approved:
                        self.execute(opp)

            # MODO 2: Monitor cada 1-3 min (SIEMPRE)
            open_positions = self.get_open_positions()
            for position in open_positions:
                verdict = self.thesis_monitor.check(position)

                if verdict == EvidenceVerdict.VALID:
                    continue
                elif verdict == EvidenceVerdict.WEAKENED:
                    self.reduce_position(position, percentage=0.40)
                elif verdict == EvidenceVerdict.INVALIDATED:
                    self.close_position(position)

                self.log_trade_event(position, verdict)

            time.sleep(self.poll_interval)
```

### Flujo Completo

```
┌─────────────────────────────────────────────────────────┐
│                    main.py (LOOP)                        │
│                                                          │
│  ┌──────────────┐    ┌──────────────────┐               │
│  │   SCANNER     │    │   MONITOR         │               │
│  │  (5-15 min)  │    │  (1-3 min)        │               │
│  │              │    │                    │               │
│  │ Contexto     │    │ Para cada posición: │               │
│  │ Regime       │    │ ¿La tesis vive?    │               │
│  │ Orchestrator │    │                    │               │
│  │ Hypothesis   │    │ SÍ → mantener      │               │
│  │ Risk         │    │ DÉBIL → reducir    │               │
│  │ Validation   │    │ NO → cerrar        │               │
│  │ Execution    │    │                    │               │
│  └──────────────┘    └──────────────────┘               │
│                                                          │
│         SIEMPRE en paralelo                              │
└─────────────────────────────────────────────────────────┘
```

---

## Fase 13: Alpha Research Engine (FUTURA) - Solo después de 500+ trades

### ⚠️ RECUERDA: Agregar esta fase después de acumular 500+ trades

### Condición de Activación
- Mínimo 500 trades cerrados
- Mínimo 6 meses de operación
- Datos suficientes para validación estadística

### Archivos (cuando se active)

```
alpha_research/
├── __init__.py
├── hypothesis_generator.py        # Genera nuevas hipótesis
├── backtester.py                  # Backtesting de hipótesis
├── walk_forward.py                # Validación walk-forward
├── out_of_sample.py               # Validación out-of-sample
├── stress_tester.py               # Stress testing
├── alpha_scorer.py                # Alpha Score formal
├── hypothesis_lifecycle.py        # Research → Candidate → Validated → Production
├── integration_pipeline.py        # Backtest → Paper → Producción
└── research_dashboard.py          # Visualización
```

### Proceso

```
Etapa 1: Generación de hipótesis
  "ADX > 30 mejora Breakout"
  "ATR Percentile > 80 mejora continuaciones"

Etapa 2: Extracción de datos históricos (desde 06_LOGGING_SCHEMA)

Etapa 3: Construcción del dataset
  Variables independientes → Resultado

Etapa 4: Backtesting
  WR, PF, Expectancy, DD, Sharpe, Sortino, Calmar, Recovery Factor

Etapa 5: Walk-forward validation
  Confirmar estabilidad temporal

Etapa 6: Out-of-sample validation
  Nunca validar con mismos datos de entrenamiento

Etapa 7: Stress testing
  Alta volatilidad, lateral, alcista, bajista, eventos extremos

Etapa 8: Alpha Score
  30% Expectancy + 20% PF + 15% Sharpe + 15% DD + 10% Estabilidad + 10% Robustez

Etapa 9: Clasificación
  Research → Candidate → Validated → Production Ready → Deprecated

Etapa 10: Integración
  Backtest Final → Walk-forward → Paper Trading → Capital Reducido → Producción
```

### Alpha Score

```python
alpha_score = (
    0.30 * normalize(expectancy) +
    0.20 * normalize(profit_factor) +
    0.15 * normalize(sharpe) +
    0.15 * normalize(1 - drawdown) +
    0.10 * normalize(stability) +
    0.10 * normalize(robustness)
)
```

### Rechazo Automático
- Sample insuficiente
- Overfitting
- Profit Factor bajo
- Expectancy negativa
- Drawdown excesivo
- Alta inestabilidad

### Restricciones
- Nunca desplegar automáticamente
- Nunca modificar estrategias existentes sin validación
- Nunca eliminar investigaciones
- Nunca investigar con muestras pequeñas
- Nunca validar con mismos datos de entrenamiento
- Nunca aceptar sin evidencia estadística

---

## Resumen de Tiempo

| Fase | Días | Módulo |
|------|------|--------|
| 0 - Setup | 2 | Infraestructura |
| 1 - Context | 3 | 01_MARKET_CONTEXT |
| 2 - Regime | 3 | 09_MARKET_REGIME_ENGINE |
| 3 - Orchestrator | 3 | 02_STRATEGY_ORCHESTRATOR |
| 4 - Risk | 3 | 03_RISK_ENGINE |
| 5 - Validation | 3 | 04_VALIDATION_ENGINE |
| 6 - Hypothesis | 2 | Hypothesis Builder |
| 7 - Execution | 2 | 05_EXECUTION_PROTOCOL |
| 8 - Monitor | 3 | Thesis Monitor (CRÍTICO) |
| 9 - Logging | 2 | 06_LOGGING_SCHEMA |
| 10 - Learning | 3 | 07+08 |
| 11 - Fundamental | 2 | Análisis fundamental |
| 12 - Orchestrator | 2 | main.py |
| **13 - Alpha Research** | **FUTURA** | **Solo después de 500+ trades** |
| **Total** | **~32 días** | **+ Alpha Research (futuro)** |

---

## Flujo de Decisión

```
¿Hay Setup Válido?
├─ NO → Esperar / No Trade
└─ SI → ¿Cumple Checklist General (6/8)?
         ├─ NO → Esperar
         └─ SI → ¿Cumple Gestión de Riesgo (5/6)?
                  ├─ NO → Ajustar o esperar
                  └─ SI → ¿Estoy bien psicológicamente?
                           ├─ NO → Descansar
                           └─ SI → ¿El Orchestrator activa esta estrategia?
                                    ├─ NO → Esperar (estrategia apagada)
                                    └─ SI → EJECUTAR
                                              ↓
                                        MONITOREAR CONTINUO (cada 1-3 min)
                                              ↓
                                     ¿La tesis sigue viva?
                                     ├─ SÍ → Mantener
                                     ├─ DÉBIL → Reducir 40%
                                     └─ NO → Cerrar
                                              ↓
                                        REGISTRAR
                                              ↓
                                        APRENDER
```

---

## Checklist de Verificación Antes de Implementar

- [ ] Estructura de directorios creada
- [ ] requirements.txt instalado
- [ ] config/settings.py configurado
- [ ] db/database.py funcional
- [ ] db/models.py con todas las tablas
- [ ] context/ completo y testeado
- [ ] regime/ completo y testeado
- [ ] strategies/ con orchestrator y 10 estrategias
- [ ] risk/ completo con ATR+OrderBook y 3F-R
- [ ] validation/ con 5 etapas
- [ ] hypothesis/ construyendo hipótesis
- [ ] execution/ con Bitget
- [ ] monitor/ validando tesis continuamente
- [ ] logging/ registrando todo
- [ ] learning/ ajustando pesos
- [ ] patterns/ descubriendo patrones
- [ ] fundamental/ con APIs básicas
- [ ] main.py con 2 modos (Scanner + Monitor)
- [ ] 500+ trades acumulados → **ACTIVAR Alpha Research Engine**

---

## Recordatorio Importante

**DESPUÉS DE 500+ TRADES:**
1. Activar Alpha Research Engine (Fase 13)
2. Crear directorio `alpha_research/`
3. Implementar: hypothesis_generator, backtester, walk_forward, out_of_sample, stress_tester, alpha_scorer, hypothesis_lifecycle, integration_pipeline, research_dashboard
4. Empezar a investigar nuevas fuentes de alpha basado en datos reales
