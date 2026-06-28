# MVP Plan — Trading Agent

## Filosofía

> "No automatices complejidad que todavía no entiendes."

El MVP busca una sola cosa: **demostrar expectativa positiva con consistencia**.

---

## Arquitectura MVP

```
┌─────────────────────────────────────────────────────────┐
│                    MARKET DATA (Bitget)                 │
│                        OHLCV + OrderBook                │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│               MARKET CONTEXT (Simplificado)             │
│  • Precio actual + cambio %                             │
│  • Volumen vs promedio 20 períodos                      │
│  • ATR(5) para volatilidad                              │
│  • Sesión (Asia/London/NY)                              │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│          NO TRADE FILTER (Bloqueador Simple)            │
│  • ¿Volumen suficiente?                                 │
│  • ¿Spread aceptable?                                   │
│  • ¿Sesión activa?                                      │
│  • ¿Drawdown dentro de límites?                         │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│           STRATEGY ORCHESTRATOR (2 Estrategias)         │
│                                                         │
│  ┌─────────────────────┐  ┌─────────────────────────┐  │
│  │ BREAKOUT (Principal)│  │ PULLBACK (Secundaria)   │  │
│  │ Compresión → Ruptura│  │ Tendencia → Retroceso   │  │
│  └─────────────────────┘  └─────────────────────────┘  │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│               RISK ENGINE (Esencial)                    │
│  • Cálculo SL/TP (ATR-based)                           │
│  • Position Sizing (fijo % del capital)                 │
│  • Stop Loss basado en estructura                       │
│  • Take Profit = SL × 2 (R:R mínimo 2:1)               │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│            EXECUTION PROTOCOL (Secuencial)              │
│  1. Crear hipótesis                                     │
│  2. Calcular riesgo                                     │
│  3. Ejecutar entrada                                    │
│  4. Monitorear posición                                 │
│  5. Ejecutar salida                                     │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│            THESIS MONITOR (Simple)                      │
│  • Trailing Stop: +0.8% → BE, +1.2% → +0.3%           │
│  • Cierre si régimen cambia                             │
│  • Cierre si volumen desaparece                         │
│  • SL/TP hard stops                                     │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│               EVENT STORE (No Trade-Centric)            │
│  • Timestamp + Evento + Datos                          │
│  • Timeline completa de cada operación                  │
│  • No solo resultados, sino proceso                     │
└─────────────────────────────────────────────────────────┘
```

---

## Módulos MVP vs Módulos para Expansión

### MVP — Usar Ahora

| Módulo | Archivo | Estado | Notas |
|--------|---------|--------|-------|
| Contexto | `context/market_context.py` | ✅ Listo | Solo volumen + volatilidad + sesión |
| Estrategia Breakout | `strategies/continuation/acceptance_breakout.py` | ✅ Listo | Estrategia principal |
| Estrategia Pullback | `strategies/momentum/relative_strength_rotation.py` | ✅ Listo | Adaptar para pullback |
| Risk SL/TP | `risk/sl_tp_calculator.py` | ✅ Listo | ATR-based |
| Risk Position | `risk/position_sizer.py` | ✅ Listo | Fijo % capital |
| Risk Drawdown | `risk/drawdown.py` | ✅ Listo | 3F-R básico |
| Execution | `execution/order_executor.py` | ✅ Listo | Dry-run mode |
| Protocol | `execution/protocol_manager.py` | ✅ Listo | Lifecycle management |
| Monitor | `monitor/thesis_monitor.py` | ✅ Listo | Trailing + cierre |
| Config | `config/settings.py` | ✅ Listo | Parámetros centrales |
| DB | `db/database.py` + `db/models.py` | ✅ Listo | SQLite WAL |

### Para Expansión — No Usar en MVP

| Módulo | Archivo | Fase | Razón |
|--------|---------|------|-------|
| 8 Regímenes | `regime/` | Fase 3 | Necesita datos primero |
| 10 Estrategias | `strategies/` (8 restantes) | Fase 4 | Probar 2 primero |
| Learning Matrix | `strategies/learning_matrix.py` | Fase 2 | Necesita 500+ trades |
| Pattern Discovery | `learning/pattern_discovery.py` | Fase 3 | Necesita 1000+ trades |
| Alpha Research | *(pendiente)* | Fase 4 | Necesita miles de trades |
| Validación Completa | `validation/` | Fase 2 | Simplificar a No-Trade Filter |
| Regime Risk | `risk/regime_risk.py` | Fase 3 | Sin regímenes aún |
| Strategy Risk | `risk/strategy_risk.py` | Fase 3 | Probar primero sin ajustes |
| Capital Allocator | `risk/capital_allocator.py` | Fase 2 | Usar fijo % inicialmente |
| Historical Similarity | `regime/historical_similarity.py` | Fase 3 | Necesita historial |
| Evidence Collector | `validation/evidence_collector.py` | Fase 2 | Simplificar |
| Hypothesis Builder | `hypothesis/hypothesis_builder.py` | Fase 1 | Simplificar |

---

## Estrategia Principal: Breakout con Confirmación

### Hipótesis
> "Después de un período de compresión, el precio rompe una zona relevante con aumento de volumen y liquidez. Existe una probabilidad favorable de continuación."

### Indicadores Requeridos (mínimo)
1. **ATR(5)** — Detectar compresión (ATR < percentil 30 de últimos 20 períodos)
2. **Volumen actual vs promedio 20** — Confirmación (volumen > 1.5× promedio)
3. **Precio** — Ruptura de rango (close > high de últimas 10 velas o close < low)
4. **Sesión** — Operar solo en horarios líquidos (NY o London)

### Reglas de Entrada (LONG ejemplo)
```
SI:
  - ATR(5) < percentil_30(ATR_20)     → Compresión detectada
  - Precio cierra por encima del máximo de 10 velas  → Ruptura
  - Volumen > 1.5 × promedio_20       → Confirmación
  - Sesión = NY o London              → Liquidez
ENTonces:
  - Entrada: siguiente vela (market)
  - SL: ATR(5) × 1.5 por debajo de entrada
  - TP: SL × 2 (R:R 2:1)
  - Duración máxima: 48 horas
```

### Reglas de Salida
```
SI:
  - Precio toca SL → Cierre inmediato
  - Precio toca TP → Cierre inmediato
  - Ganancia ≥ 0.8% → Mover SL a Break Even
  - Ganancia ≥ 1.2% → SL a +0.3%
  - Ganancia ≥ 1.6% → Trailing 0.5% detrás
  - Duración > 48h → Cierre
  - Volumen cae > 50% vs entrada → Cierre parcial
```

---

## Estrategia Secundaria: Pullback en Tendencia

### Hipótesis
> "La tendencia principal sigue intacta. El retroceso ofrece una mejor relación riesgo/beneficio."

### Indicadores Requeridos
1. **EMA 20 y EMA 50** — Detectar tendencia (EMA20 > EMA50 = bullish)
2. **RSI(14)** — Detectar retroceso (RSI < 40 en tendencia alcista)
3. **Soporte/Resistencia** — Zona de retroceso (último swing low)
4. **Volumen** — Volumen en retroceso menor que en impulso

### Reglas de Entrada (LONG ejemplo)
```
SI:
  - EMA20 > EMA50                    → Tendencia alcista
  - Precio retrocede a zona EMA20    → Pullback
  - RSI(14) < 45                    → Sobrevendido temporal
  - Volumen en retroceso < volumen en impulso → Correcto
ENTonces:
  - Entrada: en zona EMA20
  - SL: bajo el último swing low
  - TP: siguiente nivel de resistencia o R:R 2:1
  - Duración máxima: 72 horas
```

---

## Gestión de Riesgo MVP

| Parámetro | Valor | Razón |
|-----------|-------|-------|
| Riesgo por operación | 1% fijo | Supervivencia ante rachas |
| Máximo drawdown | 10% | Detener sistema si se supera |
| Máximo pérdidas consecutivas | 3 | Reducir a 0.25% por operación |
| R:R mínimo | 2:1 | Expectancia positiva |
| SL | ATR-based | Basado en estructura, no fijo |
| TP | SL × 2 | Mínimo 2:1 |
| Duración max (Breakout) | 48h | No mantener trades eternos |
| Duración max (Pullback) | 72h | Swing trade |

---

## Event Store (No Trade-Centric)

### Estructura
```
timestamp       │ event_type        │ data
────────────────┼───────────────────┼──────────────────────
2026-06-27 09:00│ CONTEXT_SNAPSHOT  │ {volume: 0.7, atr: 0.5}
2026-06-27 09:03│ REGIME_CHECK      │ {trend: "sideways"}
2026-06-27 09:05│ STRATEGY_SIGNAL   │ {strategy: "breakout", dir: "LONG"}
2026-06-27 09:07│ HYPOTHESIS_CREATED│ {id: "HYP-001", conf: 0.75}
2026-06-27 09:12│ ENTRY             │ {price: 50000, sl: 49000, tp: 52000}
2026-06-27 09:30│ MONITOR_CHECK     │ {pnl: +0.8%, action: "BE"}
2026-06-27 10:15│ MONITOR_CHECK     │ {pnl: +1.2%, action: "lock"}
2026-06-27 11:00│ EXIT              │ {price: 52000, reason: "TP", pnl: +4%}
2026-06-27 11:00│ TRADE_RESULT      │ {result: "WIN", r: 2.0}
```

### Tabla `event_store`
```sql
CREATE TABLE event_store (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    trade_id VARCHAR(50),
    data JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## Roadmap de Ejecución

### Fase 1 — Paper Trading (Objetivo: expectativa positiva)

| Paso | Descripción | Estado |
|------|-------------|--------|
| 1.1 | Simplificar Market Context (solo volumen + ATR + sesión) | Pendiente |
| 1.2 | Configurar 2 estrategias (Breakout + Pullback) | Pendiente |
| 1.3 | Risk Engine esencial (SL/TP + Position Size + Drawdown) | Pendiente |
| 1.4 | Execution Protocol (dry-run) | Pendiente |
| 1.5 | Thesis Monitor (trailing básico) | Pendiente |
| 1.6 | Event Store (tabla + logger) | Pendiente |
| 1.7 | Main Loop (scanner 5 min + monitor 3 min) | Pendiente |
| 1.8 | Ejecutar 200+ trades en paper trading | Pendiente |

**Criterio de éxito:**
- Expectancy > 0
- Profit Factor > 1.3
- Max Drawdown < 10%
- 200+ trades registrados

### Fase 2 — Entender por qué ganas

| Paso | Descripción |
|------|-------------|
| 2.1 | Learning Feedback (análisis de trades) |
| 2.2 | Dashboard de métricas |
| 2.3 | Informes automáticos semanales |
| 2.4 | Validación de hipótesis |

### Fase 3 — Hacer el sistema más inteligente

| Paso | Descripción |
|------|-------------|
| 3.1 | Market Regime Engine (si se demuestra necesario) |
| 3.2 | Pattern Discovery (si hay suficientes datos) |
| 3.3 | Strategy Learning Matrix |

### Fase 4 — Evolución cuantitativa

| Paso | Descripción |
|------|-------------|
| 4.1 | Alpha Research Engine |
| 4.2 | Nuevas estrategias (basadas en datos) |
| 4.3 | Nuevos activos (si BTC demuestra consistencia) |

---

## Métricas de Validación Paper Trading

| Métrica | Objetivo | Mínimo |
|---------|----------|--------|
| Expectancy | > 0 | > 0 |
| Profit Factor | > 1.5 | > 1.3 |
| Win Rate | > 45% | > 40% |
| Max Drawdown | < 8% | < 10% |
| Trades totales | 500+ | 200+ |
| Meses positivos | 3/3 | 2/3 |
| Sharpe Ratio | > 1.5 | > 1.0 |

---

## Próximos Pasos Inmediatos

1. **Definir qué archivos del MVP existen ya** (la mayoría)
2. **Crear Event Store** (tabla nueva + logger)
3. **Simplificar Main Loop** (scanner + monitor)
4. **Configurar paper trading** (dry-run por defecto)
5. **Ejecutar primer test completo** (1 día de datos)
