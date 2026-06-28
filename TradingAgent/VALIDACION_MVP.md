# PLAN DE VALIDACION MVP

## NIVEL 1 - Validacion Tecnica (¿El sistema funciona?)

| # | Validacion | Estado | Notas |
|---|------------|--------|-------|
| 1 | Recepcion correcta de datos de Bitget | ✅ | ExchangeClient + MarketData funcionando |
| 2 | Calculo correcto de indicadores | ✅ | EMA, ATR, RSI, Volumen calculados |
| 3 | Strategy Selector selecciona la estrategia esperada | ✅ | Breakout 15M activo |
| 4 | Risk Engine calcula correctamente SL, TP y Position Size | ✅ | DrawdownManager integrado con risk dinamico |
| 5 | Filtro No-Trade bloquea operaciones cuando corresponde | ✅ | 5 condiciones verificadas |
| 6 | Trailing Stop funciona correctamente | ✅ | 3 etapas: breakeven -> profit locked -> trailing |
| 7 | Logging guarda todos los eventos | ✅ | EventStore + LogManager (SQL) integrados |
| 8 | Dashboard refleja el estado real del sistema | ✅ | 5 pantallas, WebSocket en tiempo real |
| 9 | WebSocket/actualizacion en tiempo real funciona correctamente | ✅ | EventStore -> HTTP POST -> WebSocket -> React |
| 10 | Ejecucion en Testnet sin errores | ⏸️ | PENDIENTE FUTURA (OrderExecutor listo) |

## NIVEL 2 - Validacion Operativa (¿Opera como fue disenado?)

### Criterios de finalizacion (primero que ocurra):

| Condicion | Valor | Obligatoria |
|-----------|-------|-------------|
| Senales generadas | >= 30 | ✅ |
| Operaciones ejecutadas | >= 20 | ✅ |
| Dias de funcionamiento | >= 7 | ✅ |

### Sub-niveles:

| Nivel | Trades | Obligatoria |
|-------|--------|-------------|
| Inicial | 20 | ✅ |
| Seria | 50 | ✅ |
| Antes de dinero real | 100 | ✅ |

## NIVEL 3 - Validacion Estadistica (¿Existe una ventaja?)

### Criterios obligatorios para pasar a dinero real:

| Metrica | Criterio | Obligatoria |
|---------|----------|-------------|
| Expectancy | > 0 | ✅ |
| Profit Factor | > 1.5 | ✅ |
| Drawdown | < 8-10% | ✅ |
| Trades documentados | >= 100 | ✅ |
| Logging completo | 100% (12 campos) | ✅ |
| Kill Switch | Probado | ✅ |
| Risk Engine | Validado | ✅ |
| Dashboard | Sin inconsistencias | ✅ |

### Campos minimos por trade (12/12 IMPLEMENTADOS):

| # | Campo | Estado | Ubicacion |
|---|-------|--------|-----------|
| 1 | Contexto del mercado | ✅ | CONTEXT_SNAPSHOT con trade_id |
| 2 | Regimen | ✅ | log_regime() + CONTEXT_SNAPSHOT |
| 3 | Estrategia | ✅ | ENTRY.data.strategy |
| 4 | Hipotesis | ✅ | HYPOTHESIS_CREATED + log_hypothesis() |
| 5 | Nivel de confianza | ✅ | ENTRY.data.confidence |
| 6 | Riesgo | ✅ | RISK_CALCULATED + drawdown_status |
| 7 | Entrada | ✅ | ENTRY.data.entry_price (con spread/slippage) |
| 8 | Salida | ✅ | EXIT.data.price (con spread/slippage) |
| 9 | Motivo de salida | ✅ | EXIT.data.reason |
| 10 | Resultado | ✅ | TRADE_RESULT.data.result (WIN/LOSS) |
| 11 | Duracion | ✅ | EXIT.data.duration_minutes |
| 12 | Evidencia disponible | ✅ | HYPOTHESIS_CREATED.data.supporting_evidence |

## COMPONENTES IMPLEMENTADOS

### FASE 1: DrawdownManager Integration ✅
- `drawdown.update()` llamado despues de cada trade
- Risk dinamico: 1% -> 0.75% -> 0.25% segun rachas
- Evento DRAWDOWN_STATUS en timeline
- Fix acceso privado `_daily_pnl` -> `daily_pnl_pct`

### FASE 2: LogManager Integration ✅
- `log_regime()` en `_refresh_context()`
- `log_hypothesis()` en `_run_scanner()` (retorna DB ID)
- `log_context()` en `_execute_entry()`
- `log_trade()` en `_execute_entry()` (entry record)
- `update_trade_exit()` en `_execute_exit()` (update record)
- `log_monitoring()` en `_run_monitor()`
- `log_manager.close()` en `stop()`

### FASE 3: Paper Trading Realista ✅
- Capital: 1000 USDT
- Spread: Real del orderbook de Bitget
- Slippage: 0.05% fijo
- Commission: 0.1% (taker)
- Execution delay: 100-500ms simulado
- PnL neto despues de costos

### FASE 4: ThesisMonitor Integration ✅
- Regime change detection
- Volume drop detection (< 0.3)
- Confidence decay por hora
- Acciones: CLOSE, REDUCE, ADJUST_SL, HOLD

## PAPER TRADING CONFIGURATION

```bash
cd TradingAgent
python main_loop.py --log-level INFO --scanner-interval 30 --context-interval 60
```

### Parámetros:
- Capital: $1000 USDT
- Scanner: cada 30 segundos
- Context: cada 60 segundos
- Monitor: cada 30 segundos

## VALIDACION: Nivel 1 - Prueba Tecnica (30 min)

| # | Validacion | Comando/Verificacion | Criterio |
|---|------------|----------------------|----------|
| 1 | Datos Bitget | Log "Context:" con precio | Price > 50000 |
| 2 | Indicadores | Log "Context: ... ATR: ...%" | ATR > 0 |
| 3 | Strategy | Log "Signal:" cuando hay oportunidad | Direction = LONG/SHORT |
| 4 | Risk Engine | Log "Risk: Size=... Capital=..." | Size > 0 |
| 5 | Filtro No-Trade | Evento NO_TRADE en timeline | Aparece cuando volume bajo |
| 6 | Trailing | Log "Trail: Stage..." | Stage avanza |
| 7 | Logging SQL | `sqlite3 trading_agent.db "SELECT COUNT(*) FROM trades"` | Count > 0 |
| 8 | Dashboard | Abrir http://localhost:3000 | Datos visibles |
| 9 | WebSocket | Eventos en tiempo real | Sin refresh |
| 10 | Paper costs | Log "[PAPER] Spread:..." | Spread > 0 |

## ARCHIVOS MODIFICADOS

| # | Archivo | Fase | Estado |
|---|---------|------|--------|
| 1 | `main_loop.py` | 1,2,3,4 | ✅ Implementado |
| 2 | `logs/log_manager.py` | 2 | ✅ Implementado |
| 3 | `logs/event_store.py` | 1 | ✅ Implementado |
| 4 | `api/routers/trades.py` | - | ✅ Query desde EventStore |
| 5 | `api/routers/stats.py` | - | ✅ Query desde EventStore |
