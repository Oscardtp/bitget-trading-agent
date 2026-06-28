"use client";

import { Card } from "@/components/shared/Card";
import { GlowValue } from "@/components/shared/GlowValue";
import { SystemStatus } from "@/components/system/SystemStatus";
import { useHealth } from "@/hooks/useHealth";

export default function SettingsPage() {
  const health = useHealth();

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-bold text-terminal-text">Configuracion del Sistema</h1>

      <Card title="Estado del Sistema" accent>
        {health ? (
          <div className="grid grid-cols-3 gap-4">
            <GlowValue 
              value={health.status === "ok" ? "Operativo" : "Degradado"} 
              label="Estado General" 
              color={health.status === "ok" ? "accent" : "danger"} 
              size="sm" 
            />
            <GlowValue 
              value={`${health.summary.ok}/${health.summary.total}`} 
              label="Componentes OK" 
              color={health.summary.error === 0 ? "accent" : "warning"} 
              size="sm" 
            />
            <GlowValue 
              value={health.summary.error.toString()} 
              label="Errores" 
              color={health.summary.error === 0 ? "info" : "danger"} 
              size="sm" 
            />
          </div>
        ) : (
          <div className="text-terminal-muted text-center py-4">Cargando...</div>
        )}
      </Card>

      <SystemStatus />

      <Card title="Configuracion Actual">
        <div className="space-y-2 text-xs">
          <div className="flex justify-between py-1 border-b border-terminal-border/30">
            <span className="text-terminal-muted">URL del API</span>
            <span className="text-terminal-text">http://localhost:8000</span>
          </div>
          <div className="flex justify-between py-1 border-b border-terminal-border/30">
            <span className="text-terminal-muted">URL del Dashboard</span>
            <span className="text-terminal-text">http://localhost:3000</span>
          </div>
          <div className="flex justify-between py-1 border-b border-terminal-border/30">
            <span className="text-terminal-muted">Activo</span>
            <span className="text-terminal-text">BTC/USDT</span>
          </div>
          <div className="flex justify-between py-1 border-b border-terminal-border/30">
            <span className="text-terminal-muted">Modo</span>
            <span className="text-terminal-accent">Prueba (Paper Trading)</span>
          </div>
          <div className="flex justify-between py-1">
            <span className="text-terminal-muted">Version del Dashboard</span>
            <span className="text-terminal-text">1.0.0</span>
          </div>
        </div>
      </Card>
    </div>
  );
}
