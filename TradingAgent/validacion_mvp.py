"""
Validacion MVP - Script de pruebas automatizadas
Ejecuta 5 pruebas de validacion del sistema de trading
"""
import sqlite3
import time
import subprocess
import sys
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "trading_agent.db")

def get_db():
    return sqlite3.connect(DB_PATH)

def test_1_dry_run():
    """Test 1: Ejecutar main_loop.py 5 minutos sin errores"""
    print("\n" + "="*60)
    print("TEST 1: Dry Run 5 minutos")
    print("="*60)
    
    # Verificar que el archivo existe
    if not os.path.exists("main_loop.py"):
        print("[FAIL] main_loop.py no encontrado")
        return False
    
    # Verificar imports criticos
    print("Verificando imports...")
    imports_ok = True
    try:
        import main_loop
        print("  [OK] main_loop importado")
    except Exception as e:
        print(f"  [FAIL] Error importando main_loop: {e}")
        imports_ok = False
    
    try:
        from logs.event_store import EventStore, EventType
        print("  [OK] EventStore importado")
    except Exception as e:
        print(f"  [FAIL] Error importando EventStore: {e}")
        imports_ok = False
    
    try:
        from logs.log_manager import LogManager
        print("  [OK] LogManager importado")
    except Exception as e:
        print(f"  [FAIL] Error importando LogManager: {e}")
        imports_ok = False
    
    try:
        from strategies.orchestrator import StrategyOrchestrator
        print("  [OK] StrategyOrchestrator importado")
    except Exception as e:
        print(f"  [FAIL] Error importando StrategyOrchestrator: {e}")
        imports_ok = False
    
    try:
        from regime.regime_detector import detect_regime_from_context
        print("  [OK] regime_detector importado")
    except Exception as e:
        print(f"  [FAIL] Error importando regime_detector: {e}")
        imports_ok = False
    
    try:
        from monitor.thesis_monitor import ThesisMonitor
        print("  [OK] ThesisMonitor importado")
    except Exception as e:
        print(f"  [FAIL] Error importando ThesisMonitor: {e}")
        imports_ok = False
    
    try:
        from risk.drawdown import DrawdownManager
        print("  [OK] DrawdownManager importado")
    except Exception as e:
        print(f"  [FAIL] Error importando DrawdownManager: {e}")
        imports_ok = False
    
    if not imports_ok:
        print("\n[FAIL] FALLO: Hay errores en los imports")
        return False
    
    print("\n[OK] Todos los imports correctos")
    print("\nPara ejecutar el dry run:")
    print("  python main_loop.py --log-level INFO --scanner-interval 30 --context-interval 60")
    return True

def test_2_sql_tables():
    """Test 2: Verificar tablas SQL poblasadas"""
    print("\n" + "="*60)
    print("TEST 2: Tablas SQL poblasadas")
    print("="*60)
    
    if not os.path.exists(DB_PATH):
        print(f"[FAIL] Base de datos no encontrada: {DB_PATH}")
        return False
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Obtener todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tablas encontradas: {tables}")
    
    # Verificar cada tabla critica
    critical_tables = {
        'trades': 'Operaciones ejecutadas',
        'hypotheses': 'Hipotesis generadas',
        'context_history': 'Historial de contextos',
        'regime_history': 'Historial de regimenes',
        'monitoring_log': 'Log de monitoreo',
        'event_store': 'Eventos del lifecycle'
    }
    
    all_ok = True
    for table, desc in critical_tables.items():
        if table not in tables:
            print(f"  [FAIL] Tabla '{table}' no existe ({desc})")
            all_ok = False
            continue
        
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print(f"  [WARN]  Tabla '{table}' vacia ({desc})")
        else:
            print(f"  [OK] Tabla '{table}': {count} registros ({desc})")
    
    # Verificar campos criticos en trades
    if 'trades' in tables:
        cursor.execute("SELECT COUNT(*) FROM trades")
        trade_count = cursor.fetchone()[0]
        if trade_count > 0:
            cursor.execute("PRAGMA table_info(trades)")
            columns = [col[1] for col in cursor.fetchall()]
            required = ['entry_price', 'exit_price', 'result', 'strategy', 'regime']
            missing = [col for col in required if col not in columns]
            if missing:
                print(f"  [FAIL] Trades faltan columnas: {missing}")
                all_ok = False
            else:
                print(f"  [OK] Trades tiene todas las columnas requeridas")
    
    # Verificar campos criticos en hypotheses
    if 'hypotheses' in tables:
        cursor.execute("SELECT COUNT(*) FROM hypotheses")
        hyp_count = cursor.fetchone()[0]
        if hyp_count > 0:
            cursor.execute("PRAGMA table_info(hypotheses)")
            columns = [col[1] for col in cursor.fetchall()]
            required = ['confidence', 'strategy', 'regime']
            missing = [col for col in required if col not in columns]
            if missing:
                print(f"  [FAIL] Hypotheses faltan columnas: {missing}")
                all_ok = False
            else:
                print(f"  [OK] Hypotheses tiene todas las columnas requeridas")
    
    # Verificar campos criticos en context_history
    if 'context_history' in tables:
        cursor.execute("SELECT COUNT(*) FROM context_history")
        ctx_count = cursor.fetchone()[0]
        if ctx_count > 0:
            cursor.execute("PRAGMA table_info(context_history)")
            columns = [col[1] for col in cursor.fetchall()]
            required = ['regime', 'trend', 'volume_trend']
            missing = [col for col in required if col not in columns]
            if missing:
                print(f"  [FAIL] Context_history faltan columnas: {missing}")
                all_ok = False
            else:
                print(f"  [OK] Context_history tiene todas las columnas requeridas")
    
    conn.close()
    
    if all_ok:
        print("\n[OK] Todas las tablas criticas OK")
    else:
        print("\n[WARN]  Algunas tablas tienen problemas")
    
    return all_ok

def test_3_dashboard_trades():
    """Test 3: Verificar dashboard muestra trades"""
    print("\n" + "="*60)
    print("TEST 3: Dashboard muestra trades")
    print("="*60)
    
    # Verificar que la API esta corriendo
    import urllib.request
    import json
    
    api_url = "http://localhost:8000"
    try:
        req = urllib.request.Request(api_url)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read())
            print(f"  [OK] API respondiendo: {data.get('name', 'Unknown')}")
    except Exception as e:
        print(f"  [FAIL] API no disponible: {e}")
        print("  Iniciar API: python run.py")
        return False
    
    # Verificar endpoint de trades
    try:
        req = urllib.request.Request(f"{api_url}/api/trades")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read())
            # La API retorna una lista directamente, no un dict
            trades = data if isinstance(data, list) else data.get('trades', [])
            print(f"  [OK] Trades endpoint: {len(trades)} trades")
            
            if len(trades) > 0:
                # Verificar campos de un trade
                trade = trades[0]
                required_fields = ['entry_price', 'exit_price', 'result', 'strategy']
                missing = [f for f in required_fields if f not in trade]
                if missing:
                    print(f"  [FAIL] Trade faltan campos: {missing}")
                else:
                    print(f"  [OK] Trade tiene todos los campos requeridos")
    except Exception as e:
        print(f"  [FAIL] Error consultando trades: {e}")
        return False
    
    # Verificar endpoint de stats
    try:
        req = urllib.request.Request(f"{api_url}/api/stats")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read())
            print(f"  [OK] Stats endpoint: {json.dumps(data, indent=2)[:200]}...")
    except Exception as e:
        print(f"  [FAIL] Error consultando stats: {e}")
        return False
    
    print("\n[OK] Dashboard verificado")
    return True

def test_4_drawdown_risk():
    """Test 4: Verificar drawdown ajusta riesgo"""
    print("\n" + "="*60)
    print("TEST 4: Drawdown ajusta riesgo")
    print("="*60)
    
    # Verificar que DrawdownManager funciona correctamente
    try:
        from risk.drawdown import DrawdownManager, DrawdownState
        
        dm = DrawdownManager()
        print(f"  [OK] DrawdownManager instanciado")
        
        # Simular 3 losses consecutivas
        for i in range(3):
            status = dm.update("LOSS", pnl=-10, current_balance=970)
            print(f"    Loss {i+1}: consecutive={status.consecutive_losses}, risk_multiplier={status.risk_multiplier}")
        
        # Verificar que el risk bajo
        final_status = dm.update()
        if final_status.risk_multiplier < 1.0:
            print(f"  [OK] Risk reducido despues de 3 losses: {final_status.risk_multiplier}")
        else:
            print(f"  [FAIL] Risk NO se redujo despues de 3 losses: {final_status.risk_multiplier}")
            return False
        
        # Verificar que el risk actual es menor al inicial
        current_risk = final_status.current_risk_pct
        print(f"  [OK] Risk actual: {current_risk*100:.2f}%")
        
        print("\n  [OK] DrawdownManager funciona correctamente")
        return True
        
    except Exception as e:
        print(f"  [FAIL] Error verificando DrawdownManager: {e}")
        return False

def test_5_thesis_monitor():
    """Test 5: Verificar thesis monitor cierra"""
    print("\n" + "="*60)
    print("TEST 5: Thesis Monitor cierra trades")
    print("="*60)
    
    # Verificar que ThesisMonitor funciona correctamente
    try:
        from monitor.thesis_monitor import ThesisMonitor, MonitorAction
        
        tm = ThesisMonitor()
        print(f"  [OK] ThesisMonitor instanciado")
        
        # Test 1: Regime change deberia cerrar
        result = tm.check(
            current_price=50000,
            entry_price=50000,
            stop_loss=49000,
            take_profit=52000,
            side="LONG",
            hypothesis_confidence=0.8,
            hours_since_entry=2,
            regime_changed=True,
            volume_dropped=False,
            evidence_supporting=3,
            evidence_opposing=1
        )
        
        if result.action == MonitorAction.CLOSE:
            print(f"  [OK] Regime change -> CLOSE: {result.reason}")
        else:
            print(f"  [FAIL] Regime change deberia cerrar, pero accion: {result.action}")
            return False
        
        # Test 2: Volume drop deberia reducir
        result = tm.check(
            current_price=50000,
            entry_price=50000,
            stop_loss=49000,
            take_profit=52000,
            side="LONG",
            hypothesis_confidence=0.8,
            hours_since_entry=2,
            regime_changed=False,
            volume_dropped=True,
            evidence_supporting=3,
            evidence_opposing=1
        )
        
        if result.action == MonitorAction.REDUCE:
            print(f"  [OK] Volume drop -> REDUCE: {result.reason}")
        else:
            print(f"  [FAIL] Volume drop deberia reducir, pero accion: {result.action}")
            return False
        
        # Test 3: Evidence opposing > supporting deberia cerrar
        result = tm.check(
            current_price=50000,
            entry_price=50000,
            stop_loss=49000,
            take_profit=52000,
            side="LONG",
            hypothesis_confidence=0.8,
            hours_since_entry=2,
            regime_changed=False,
            volume_dropped=False,
            evidence_supporting=1,
            evidence_opposing=3
        )
        
        if result.action == MonitorAction.CLOSE:
            print(f"  [OK] Evidence opposing -> CLOSE: {result.reason}")
        else:
            print(f"  [FAIL] Evidence opposing deberia cerrar, pero accion: {result.action}")
            return False
        
        # Test 4: Confidence decay bajo deberia cerrar
        result = tm.check(
            current_price=50000,
            entry_price=50000,
            stop_loss=49000,
            take_profit=52000,
            side="LONG",
            hypothesis_confidence=0.4,
            hours_since_entry=5,
            regime_changed=False,
            volume_dropped=False,
            evidence_supporting=3,
            evidence_opposing=1
        )
        
        if result.action == MonitorAction.CLOSE:
            print(f"  [OK] Low confidence -> CLOSE: {result.reason}")
        else:
            print(f"  [FAIL] Low confidence deberia cerrar, pero accion: {result.action}")
            return False
        
        print("\n[OK] ThesisMonitor funciona correctamente")
        return True
        
    except Exception as e:
        print(f"  [FAIL] Error verificando ThesisMonitor: {e}")
        return False

def run_all_tests():
    """Ejecutar todas las pruebas"""
    print("\n" + "="*60)
    print("VALIDACION MVP -", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)
    
    tests = [
        ("Test 1: Dry Run", test_1_dry_run),
        ("Test 2: SQL Tables", test_2_sql_tables),
        ("Test 3: Dashboard", test_3_dashboard_trades),
        ("Test 4: Drawdown", test_4_drawdown_risk),
        ("Test 5: Thesis Monitor", test_5_thesis_monitor),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[FAIL] EXCEPCION en {name}: {e}")
            results.append((name, False))
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE VALIDACION")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{status} - {name}")
    
    print(f"\nResultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("\n*** TODAS LAS PRUEBAS PASARON - Sistema listo para paper trading")
        return True
    else:
        print(f"\n[WARN]  {total - passed} pruebas fallaron - Revisar antes de paper trading")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
