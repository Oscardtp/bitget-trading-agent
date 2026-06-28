// ============================================
// DICCIONARIO DE COPY - EVENT TIMELINE
// Estandar UX: Profesional, claro, educativo
// ============================================

export const EVENT_LABELS: Record<string, string> = {
  CONTEXT_SNAPSHOT: "IA actualizó su análisis de la tendencia actual.",
  REGIME_CHECK: "Estado del mercado verificado.",
  STRATEGY_SIGNAL: "Oportunidad detectada. Evaluando si cumple los criterios.",
  HYPOTHESIS_CREATED: "Hipótesis formulada. Calculando probabilidad de éxito.",
  RISK_CALCULATED: "Riesgo evaluado. Definiendo niveles de protección.",
  ENTRY: "Operación abierta. Monitoreando en tiempo real.",
  MONITOR_CHECK: "Posición verificada. Todo bajo control.",
  TRAILING_UPDATE: "Stop loss ajustado para proteger las ganancias.",
  EXIT: "Operación cerrada. Analizando resultado.",
  TRADE_RESULT: "Resultado registrado en el historial.",
  NO_TRADE: "El mercado no presentó condiciones seguras. Esperando mejor oportunidad.",
  SYSTEM_START: "Sistema activado en modo de prueba.",
  SYSTEM_STOP: "Sistema detenido correctamente.",
  ERROR: "Se detectó una anomalía en el sistema. Requiere revisión manual.",
};

export function getEventLabel(eventType: string): string {
  return EVENT_LABELS[eventType] || eventType.replace(/_/g, " ").toLowerCase();
}

export const EVENT_ICONS: Record<string, string> = {
  CONTEXT_SNAPSHOT: "📊",
  REGIME_CHECK: "🔄",
  STRATEGY_SIGNAL: "🎯",
  HYPOTHESIS_CREATED: "💡",
  RISK_CALCULATED: "⚖️",
  ENTRY: "✅",
  MONITOR_CHECK: "👁️",
  TRAILING_UPDATE: "📈",
  EXIT: "🔴",
  TRADE_RESULT: "📋",
  NO_TRADE: "⏳",
  SYSTEM_START: "🟢",
  SYSTEM_STOP: "⚫",
  ERROR: "⚠️",
};

export function getEventIcon(eventType: string): string {
  return EVENT_ICONS[eventType] || "📌";
}

// ============================================
// DICCIONARIO DE COPY - REGIME (ESTADO MERCADO)
// ============================================

export const REGIME_LABELS: Record<string, string> = {
  sideways_low_vol: "Mercado lateral con baja actividad",
  sideways: "Mercado lateral sin dirección definida",
  trending_bull: "Tendencia alcista en desarrollo",
  TRENDING_BULL: "Tendencia alcista en desarrollo",
  trending_bear: "Tendencia bajista en desarrollo",
  TRENDING_BEAR: "Tendencia bajista en desarrollo",
  high_vol: "Mercado con alta volatilidad",
  low_vol: "Mercado tranquilo, poca variación",
  breakout: "Ruptura de rango detectada",
  reversal: "Cambio de tendencia en curso",
  contraction: "Mercado en contracción",
  expansion: "Mercado en expansión",
};

export function getRegimeLabel(regime: string): string {
  return REGIME_LABELS[regime] || regime.replace(/_/g, " ").toLowerCase();
}

// ============================================
// DICCIONARIO DE COPY - TOOLTIPS (INDICADORES)
// ============================================

export const INDICATOR_TOOLTIPS: Record<string, string> = {
  confidence: "Qué tan seguro está el sistema sobre el estado actual del mercado.",
  volume_trend: "Si el volumen de operaciones está subiendo, bajando o estable.",
  atr: "Promedio de movimiento del precio. Valores altos significan mercados con oscilaciones amplias.",
  adx: "Mide la fuerza de la tendencia. Valores altos indican tendencia fuerte.",
  rsi: "Si el precio subió o bajó demasiado rápido. Valores altos indican posible corrección a la baja.",
  regime: "El estado general del mercado: tendencia, lateral, alta o baja volatilidad.",
  trend: "Dirección principal del precio: subiendo (alcista), bajando (bajista) o sin dirección.",
  volatility: "Qué tan impredecible es el mercado. Alta volatilidad = movimientos repentinos.",
  liquidity: "Facilidad para entrar y salir de operaciones sin afectar el precio.",
  session: "La sesión de trading actual: Asia, Europa o América.",
};

export function getIndicatorTooltip(indicator: string): string {
  return INDICATOR_TOOLTIPS[indicator] || "";
}

// ============================================
// DICCIONARIO DE COPY - LABELS DE UI
// ============================================

export const UI_LABELS = {
  marketContext: "Contexto del Mercado",
  currentRegime: "Estado Actual del Mercado",
  performance: "Rendimiento",
  openPositions: "Posiciones Abiertas",
  recentTrades: "Operaciones Recientes",
  eventTimeline: "Historial de Actividad",
  latestEvent: "Última Actividad",
  trend: "Tendencia",
  volume: "Volumen",
  volatility: "Volatilidad",
  liquidity: "Liquididad",
  session: "Sesión",
  confidence: "Confianza",
  volumeTrend: "Tendencia de Volumen",
  atr: "Variación Promedio",
  regime: "Estado",
  strategies: "Estrategias",
  bullish: "Alcista",
  bearish: "Bajista",
  neutral: "Neutral",
  active: "Activa",
  pending: "Pendiente",
  closed: "Cerrada",
  noOpenPositions: "No hay posiciones abiertas en este momento.",
  noTrades: "Aún no se han registrado operaciones.",
  noEvents: "Esperando actividad del sistema...",
  loading: "Cargando...",
};

export default UI_LABELS;
