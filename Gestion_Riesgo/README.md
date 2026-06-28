# Índice de Gestión de Riesgo

## Archivos

| Archivo | Descripción |
|---|---|
| [01-atr-orderbook.md](01-atr-orderbook.md) | Gestión dinámica basada en ATR + Order Book |
| [02-3f-r.md](02-3f-r.md) | Sistema 3F-R (Fracción-Filtro-Recompensa) |
| [checklist-operativa.md](checklist-operativa.md) | Checklist pre-operativa unificada |

---

## Resumen de Reglas Universales

| Regla | Valor |
|---|---|
| Riesgo máximo por trade | 1-2% del capital |
| R:R mínimo | 2:1 |
| SL basado en | Estructura real o ATR, nunca porcentual fijo |
| 3 pérdidas seguidas | Reducir riesgo a 0.25% |
| Retiro de ganancias | 10-15% cada +25% de cuenta |

---

## Para la IA

1. **Antes de cada trade:** cargar checklist de `checklist-operativa.md`
2. **Seleccionar gestión:** según volatilidad → `01-atr-orderbook.md` o `02-3f-r.md`
3. **Nunca operar** sin SL definido y R:R ≥ 2:1
4. **Registrar** cada trade en diario de rendimiento
