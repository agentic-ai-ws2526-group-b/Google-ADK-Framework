# Agent Routing System - Developer Documentation

## Projektkontext

Dieses Repository ist Teil des Hochschulprojekts "Agentic AI for Customer Lifecycle Management" mit Bosch. Es implementiert ein intelligentes Routing-System, das eingehende Aufgaben analysiert und den am besten geeigneten KI-Agenten empfiehlt. Ziel ist es, Mitarbeiter:innen schnell zum richtigen KI-Agenten zu leiten, der ihre spezifische Aufgabe optimal lösen kann.

## Architektur (Prototyp 1)

Das System ist in drei Schichten aufgebaut:

### 1. User Interface (main.py)
- Einfache CLI-Demo für Proof of Concept
- Nimmt Nutzer-Input entgegen
- Formatiert und zeigt Empfehlungen an
- Später: Wird durch Dashboard UI ersetzt

### 2. Advisor/Router Logik (advisor_agent.py)
- Kernlogik des Systems
- Matched Tasks gegen Agent-Profile
- Berechnet Confidence Scores
- Generiert verständliche Begründungen
- Gibt strukturierte Empfehlungen

### 3. Agenten-Datenbank (agents_catalog.py)
- "Datenbank" der verfügbaren Agenten
- Profile mit Skills und typischen Aufgaben
- Später: Migration zu Vector DB (z.B. Chroma)

**Hinweis**: In späteren Iterationen wird die gleiche Architektur in LangChain/LangGraph und Google ADK nachgebaut, um verschiedene Framework-Ansätze zu evaluieren.

## Wie teste ich das lokal?

### Schritt 1: Start des Systems
```bash
python main.py
```

### Schritt 2: Beispiel-Tasks eingeben

Testen Sie verschiedene Szenarien:

**Content Agent testen:**
```
Schreibe mir eine Produktbeschreibung für unseren neuen Staubsaugerroboter für Amazon
```

**Summary Agent testen:**
```
Fasse diese Kundenbeschwerden zusammen und gib mir die 3 wichtigsten Pain Points
```

**Analytics Agent testen:**
```
Welche Support-Kategorie ist gerade kritisch und was müssen wir priorisieren?
```

### Schritt 3: Analyse
- Prüfen Sie die Confidence Scores
- Validieren Sie die Begründungen
- Machen Sie Screenshots für die Dokumentation
- Testen Sie Edge Cases

## Bekannte Limitierungen

1. **Einfache Routing-Logik**: 
   - Basiert nur auf Keyword-Matching
   - Keine semantische Analyse
   - Kann bei komplexen Aufgaben ungenau sein

2. **Keine echten Daten**:
   - Kein Zugriff auf tatsächliche Kundendaten
   - Analytics Agent arbeitet mit simulierten Szenarien

3. **Fehlende Features**:
   - Kein Feedback-Learning nach Sessions
   - Kein automatischer Agent-Builder
   - Keine Persistenz von Entscheidungen

4. **Lokale Ausführung**:
   - Keine Cloud-Integration
   - Keine Skalierung
   - Keine Authentifizierung

## Next Steps (für Prototyp 2 und 3)

1. **Intelligentes Routing**:
   - Integration von LLM-basiertem Routing (Google ADK / LangChain)
   - Semantische Analyse statt Keyword-Matching
   - Kontextverständnis verbessern

2. **Verbesserte Datenhaltung**:
   - Agentenbeschreibungen in Vector Store (Chroma) migrieren
   - Versionierung von Agent-Profilen
   - Zentrale Verwaltung von Skills und Capabilities

3. **Feedback & Learning**:
   - Feedback nach jeder Session erfassen
   - Router-Logik kontinuierlich verbessern
   - Performance-Metriken tracken

4. **UI & Integration**:
   - Dashboard statt CLI entwickeln
   - Integration in Bosch-Systeme
   - Multi-User Support

5. **Agent Building**:
   - Automatische Agent-Generierung bei Bedarf
   - Skill-basierte Bauanleitungen
   - Template-System für neue Agenten