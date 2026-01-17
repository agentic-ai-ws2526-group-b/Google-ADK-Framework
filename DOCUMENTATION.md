# Framework Advisor - Technical Documentation

## 1. Projektüberblick

### Name und Ziel

Das Projekt heißt "Framework Advisor" und ist eine intelligente Beratungsplattform zur Auswahl von Software-Frameworks für spezifische Agent-Entwicklungsszenarien. Die Plattform analysiert Anforderungen und gibt strukturierte, begründete Empfehlungen ab, welche Frameworks sich am besten für einen geplanten Agent-Use-Case eignen.

### Problem und Kontext

In der Praxis haben Entwickler, Architekten und Projektmanager häufig Schwierigkeiten, das richtige Framework für ihre spezifischen Anforderungen auszuwählen. Die Landschaft ist fragmentiert: LangChain, Google ADK, LlamaIndex, Rasa, LangGraph, AutoGPT und weitere Optionen existieren parallel, jede mit eigenen Stärken. Diese Plattform automatisiert die Evaluierungsprozess, indem sie systematisch verschiedene Dimensionen analysiert und vergleicht.

### Zielgruppe

Die Plattform richtet sich an:

- Softwareentwickler, die Agent-Systeme bauen möchten
- Projektmanager und Architekten bei Evaluierungsentscheidungen
- Teams bei Bosch, die AI-Agenten prototypisieren
- Organisationen, die ihre Framework-Strategie überprüfen möchten

Die Plattform ist bewusst generic designed, bietet aber konkrete Bosch-Use-Cases als Referenz.

### Was die Plattform bewusst nicht macht

Die Plattform:

- Führt keinen Code aus und kann nicht die tatsächliche Performance einzelner Frameworks messen
- Ersetzt keine tiefgehendes manuelles Code-Review oder POC-Evaluierung
- Lehrt nicht, wie man mit den empfohlenen Frameworks arbeitet (das ist Aufgabe separater Trainingsmaterialien)
- Empfiehlt nicht automatisch, ein bestehendes System zu migrieren
- Bietet keine Implementierungs-Unterstützung für die Frameworks selbst

---

## 2. Grundidee des Systems

### Der „Agent-for-Agents"-Ansatz

Das System ist bewusst als "Agent-for-Agents" architektiert, nicht als monolithische Anwendung. Das bedeutet:

Statt einen großen, universellen Agenten zu bauen, der alles kann, werden sechs spezialisierte Agenten orchestriert, die jeweils eine spezifische Aufgabe optimal erfüllen. Diese Agenten arbeiten sequenziell zusammen, wobei jeder vom Vorgänger Informationen erhält, diese verarbeitet und an den Nachfolger weitergibt.

### Warum mehrere spezialisierte Agenten?

Der Grund für diese Architektur ist Separation of Concerns:

- Ein Agent für Requirements-Analyse ist anders optimiert als ein Agent für Framework-Evaluierung
- Spezialisierung ermöglicht bessere Fehlerbehandlung, Timeouts und Fallback-Logik für jede Aufgabe
- Jeder Agent kann fokussiert auf eine Sache trainiert oder entwickelt werden
- Die Orchestrierung (LangGraph) verwaltet Zustand und Fehlerbehandlung zentral

Das ist methodologisch ähnlich wie in der klassischen Softwarearchitektur: Ein System mit klaren Verantwortlichkeiten ist wartbarer und erweiterbarer als ein monolithisches System.

### Rolle der Plattform

Die Plattform ist ein Entscheidungs-Helfer (Decision Support System). Sie nimmt menschliche Input-Signale auf, verarbeitet diese strukturiert und gibt eine Empfehlung ab. Die Entscheidung selbst trifft immer noch der Mensch – die Plattform bietet nur die Informationsgrundlage.

---

## 3. Benutzerinteraktion

### Eingaben des Nutzers

Die Nutzer können die Plattform über zwei Wege nutzen:

**Web-Interface (Streamlit):**
- Freie Texteingabe mit "Schnelle Empfehlung" Mode
- Strukturierte Fragen im "Geführte Beratung" Mode
- Browsen des Use-Case-Katalogs
- Einsicht in Feedback-Historie

**Kommandozeilen-Interface (CLI):**
- Einfache Menü-Navigation
- Direkter Input von Use-Case-Beschreibungen
- Text-basierte Empfehlungsanzeige

### Arten von Fragen / Eingaben

Der Nutzer kann verschiedenartige Eingaben machen:

- **Use-Case-Beschreibungen:** "Ich brauche einen RAG-Agent für technische Dokumentation"
- **Constraint-getriebene Anfragen:** "Muss Open Source sein" oder "Keine Python-Abhängigkeiten"
- **Profil-orientierte Anfragen:** "Wir sind ein kleines Team mit wenig AI-Experience"
- **Framing-Fragen:** "Soll viel Automation können oder eher Q&A?"

Die Plattform normalisiert diese unterschiedlichen Eingaben zu strukturierten Anforderungen.

### Unterschied: Schnelle Empfehlung vs. Geführte Beratung

**Schnelle Empfehlung:**
- Nutzer gibt ein oder zwei Sätze ein
- Plattform analysiert sofort
- Empfehlung wird in wenigen Sekunden angezeigt
- Geeignet für: Nutzer mit klarer Vorstellung
- Output: Framework-Name, Score, kurze Begründung

**Geführte Beratung:**
- Plattform stellt strukturierte Fragen
- Nutzer antwortet auf Fragen zu Skill-Level, Budget, Automation-Anforderungen, etc.
- Plattform sammelt schrittweise ein detailleres Profil
- Geeignet für: Nutzer mit unscharfen Anforderungen
- Output: Detaillierte Bewertungen, mehrere Frameworks, Architektur-Vorschläge

### Strukturiert erfasste Informationen

Die Plattform erfasst (teilweise direkt, teilweise durch Inferenz):

- **Use-Case-Beschreibung:** Was genau soll der Agent tun?
- **Automation-Anforderungen:** Q&A-System, Workflow-Automation, oder Hybrid?
- **Data-Integration:** Welche Datenquellen müssen angebunden werden?
- **Team-Profil:** Skill-Level der Entwickler, Org-Kontext (Prototyp vs. Enterprise)
- **Constraints:** Budget, Open-Source-Anforderung, Cloud vs. On-Premise
- **Prioritäten:** Was ist kritischer – Schnelligkeit, Zuverlässigkeit, Skalierbarkeit?
- **Risiko-Toleranz:** Wie experimentell darf die Lösung sein?

---

## 4. Die sechs Agenten im System

Alle sechs Agenten arbeiten innerhalb des LangGraph Orchestrators und kommunizieren über einen gemeinsamen State.

### Agent A: Requirements Analyzer

**Aufgabe:**
Nimmt natürlichsprachliche User-Eingaben und strukturiert sie in maschinenverarbeitbare Requirements-Objekte.

**Input erhält von:**
- Direkter Nutzer-Input aus Web-UI oder CLI

**Output gibt weiter an:**
- Agent B (Profiler) und Agent C (Use-Case Analyzer)

**Warum dieser Agent existiert:**
Freier Text ist mehrdeutig und für nachgelagerte Agenten schwer verarbeitbar. Dieser Agent normalisiert die Eingabe und extrahiert strukturierte Informationen wie Automation-Level, Constraints, Datenquellen.

**Implementierungsdetail:**
Nutzt Google Gemini 2.5 Flash mit einem speziellen Prompt für deutsche Texte. Falls API timeout, nutzt Fallback-Defaults (z.B. "intermediate" Automation-Level, leere Constraints).

---

### Agent B: Profiler

**Aufgabe:**
Erstellt ein Profil des Benutzers basierend auf seinen Anforderungen und optional auf direktem User-Feedback.

**Input erhält von:**
- Agent A (Requirements)

**Output gibt weiter an:**
- Agent E (Decision Agent)

**Warum dieser Agent existiert:**
Framework-Empfehlungen müssen zum Kontext des Teams passen. Ein Anfänger-Team sollte nicht in die Komplexität von LangGraph geworfen werden, wenn LangChain ausreicht. Dieser Agent klassifiziert:

- Skill-Level: Anfänger, Intermediate, Expert
- Org-Context: Prototyp oder Enterprise
- Risk-Toleranz: Low, Medium, High
- Compliance-Sensibilität: Wichtig bei größeren Organisationen

---

### Agent C: Use-Case Analyzer

**Aufgabe:**
Matched die User-Anforderungen gegen einen Pool von vordefinierten Bosch Use-Cases. Findet semantisch ähnliche Use-Cases und extrahiert "typische Frameworks" für diese Use-Cases.

**Input erhält von:**
- Agent A (Requirements)

**Output gibt weiter an:**
- Agent E (Decision Agent)

**Warum dieser Agent existiert:**
Der Nutzer beschreibt möglicherweise nur vage "Ich brauche einen Agenten". Der Use-Case Pool bietet konkrete Beispiele: "Technische Dokumentation Q&A", "Remote Diagnostics", etc. Durch Matching gegen diese realen Use-Cases wird die Anfrage konkretisiert und Best Practices können herangezogen werden.

**Wie es funktioniert:**
- Embedded die User-Requirements mit Google GenAI Embedding Model
- Sucht in Chroma Vector DB nach ähnlichen Use-Cases (Cosine Similarity)
- Gibt Top 3-5 gematched Use-Cases zurück, mit Confidence Scores

---

### Agent D: Framework Analyzer

**Aufgabe:**
Evaluiert verfügbare Frameworks basierend auf den Requirements und den gematched Use-Cases. Gibt eine Liste von Framework-Kandidaten mit Scores zurück.

**Input erhält von:**
- Agent A (Requirements)
- Agent C (Use-Case Match Results)

**Output gibt weiter an:**
- Agent E (Decision Agent)

**Warum dieser Agent existiert:**
Requirements allein sind nicht genug. Dieser Agent implementiert die eigentliche Evaluierungslogik:

- Welche Frameworks unterstützen RAG (Retrieval Augmented Generation)?
- Welche sind Open-Source?
- Welche haben die beste Community?
- Welche laufen lokal vs. nur in der Cloud?

Der Agent nutzt Heuristiken, bekannte Framework-Eigenschaften und die extrahierten Anforderungen, um zu scored.

**Implementierungsdetail:**
Nutzt eine interne Framework-Datenbank mit bekannten Eigenschaften. Falls Embeddings fehlschlagen (API timeout), nutzt Position-basierte Fallback-Scores (First Match bekommt 0.8, Second 0.7, etc.).

---

### Agent E: Decision Agent

**Aufgabe:**
Kombiniert alle Informationen von Agenten A-D zu einer finalen Empfehlung. Wählt Top-1 Framework aus, schlägt Top-3 Alternativen vor, generiert Begründungen und Architektur-Vorschläge.

**Input erhält von:**
- Agent A (Requirements)
- Agent B (User Profile)
- Agent C (Use-Case Matches)
- Agent D (Framework Candidates)

**Output gibt weiter an:**
- Agent F (Control Agent)

**Warum dieser Agent existiert:**
Die Synthese ist komplex. Einfaches Scoring funktioniert nicht. Beispiel:

- Framework X hat höchsten technischen Score
- Aber Team ist Anfänger und Framework X ist schwer zu lernen
- Framework Y hat niedrigeren technischen Score, aber passt besser zum Team
- Der Decision Agent balanciert diese Trade-offs

Falls keine Framework-Kandidaten gefunden werden (z.B. weil Embeddings zeiteten aus), nutzt dieser Agent intelligente Fallback-Logik: Er schlägt dann universelle Frameworks wie LangChain vor mit einer Warnung zur niedrigen Confidence.

---

### Agent F: Control Agent

**Aufgabe:**
Ist ein Quality Gate. Bewertet ob die aktuelle Empfehlung gut genug ist oder ob das System:

- Erneut analysieren sollte (mit erhöhter Suchtiefe)
- Den Nutzer um Clarification fragen sollte
- Die Analyse beenden sollte

**Input erhält von:**
- Alle anderen Agenten (via State)

**Output:**
- Decision: END (Empfehlung akzeptabel) oder RERUN_* (Neuerung mit anderen Parametern) oder ASK_USER (Rückfrage)

**Warum dieser Agent existiert:**
Verhindert fehlerhafte oder unzureichende Empfehlungen. Implementiert Quality-Gates wie:

- Ist Use-Case Confidence >= 0.60? Sonst RERUN_USECASE mit erhöhtem top_k
- Ist Framework Confidence >= 0.60? Sonst RERUN_FRAMEWORK
- Sind kritische Infos bekannt oder gibt es zu viele "Unknowns"? Dann ASK_USER
- Haben wir bereits 2 Iterationen gemacht? Dann hard END (Limit)

---

## 5. Orchestrierung und Ablauf

### Wie die Agenten zusammenarbeiten

Die Agenten kommunizieren nicht direkt miteinander. Stattdessen verwenden sie einen gemeinsamen Zustand-Objekt (State), das von der Orchestrierungs-Engine (LangGraph) verwaltet wird:

1. Nutzer gibt Input ein → State wird initialisiert
2. Agent A verarbeitet Input → schreibt Results in State
3. Agent B liest aus State → verarbeitet → schreibt Results
4. ... (Agent C, D, E)
5. Agent F liest gesamten State → entscheidet über Routing
6. Je nach Decision: Ausgabe an Nutzer ODER Routing zu vorherigem Agenten ODER Rückfrage

### Reihenfolge der Agenten

Die Standard-Abfolge ist:

```
START → A (Requirements) → B (Profiler) → C (UseCase) → D (Framework) → E (Decision) → F (Control) → END oder LOOP
```

Dies ist die "Happy Path". Der Control Agent kann jedoch Loops initiieren:

```
... → E → F [Confidence zu niedrig] → C [erneutes UseCase-Matching] → D → E → F → ...
```

Maximum 2 Iterationen (Hard Limit) sind implementiert. Danach: Zwangweise END.

### Rolle der Orchestrierung (LangGraph)

LangGraph ist die Orchestrierungs-Engine. Sie:

- Verwaltet den State (Pydantic-Objekt mit allen Zwischenergebnissen)
- Definiert die Netzwerk-Topologie (welcher Agent folgt welchem)
- Verhandelt Conditional Routing (IF Confidence < 0.6 THEN reroute to Agent C)
- Handhält Fehlerbehandlung (Timeouts, Exceptions)
- Begrenzt Iterations (max 2 Loops)

Die Engine ist "invisible" aus Nutzersicht – sie orchestriert nur im Hintergrund.

### Was der "State" bedeutet

Der State ist ein Objekt, das alle Zwischenergebnisse speichert:

```
State = {
  requirements: (Agent A Output),
  user_profile: (Agent B Output),
  usecase_match: (Agent C Output),
  framework_candidates: (Agent D Output),
  recommendation: (Agent E Output),
  control_decision: (Agent F Output),
  iteration_count: (wie viele Loops bislang),
  messages_history: (Log von allen Agenten-Ausgaben)
}
```

Jeder Agent liest aus State, verarbeitet, und schreibt sein Output zurück in State. Dies ermöglicht Transparenz und Debugging.

---

## 6. Kontroll- und Loop-Logik

### Rolle des Control Agents

Der Control Agent ist der Quality-Gate-Keeper. Er prüft nach jeder Entscheidung, ob das Ergebnis "gut genug" ist.

### Welche Qualitätsprüfungen durchgeführt werden

Der Control Agent prüft konkret:

1. **Use-Case Confidence:** Wurde der Use-Case gut verstanden? (Threshold: 0.60)
2. **Framework Confidence:** Gibt es gute Framework-Kandidaten? (Threshold: 0.60)
3. **Type Matching:** Passt der empfohlene Framework zum Use-Case-Typ?
4. **Information Completeness:** Kennen wir genug über die Anforderungen?

### Wann das System erneut analysiert, Rückfragen stellt oder endet

**RERUN_USECASE:** 
- Use-Case Confidence < 0.60
- Aktion: Erhöhe top_k bei Embedding-Suche, versuche erneut

**RERUN_FRAMEWORK:**
- Framework Confidence < 0.60
- Typ-Mismatch erkannt (z.B. RAG erforderlich, aber kein RAG-Framework empfohlen)
- Aktion: Erweiterte Framework-Suche

**ASK_USER:**
- Zu viele Unknowns in den Requirements
- Kritische Infos fehlen
- Aktion: Stellt präzise Clarification-Fragen

**END:**
- Alle Quality Gates bestanden
- Empfehlung ist solide → Ausgabe an Nutzer

### Warum Begrenzung der Iterationen

Zwei Iterationen Maximum sind implementiert, um:

- Infinite Loops zu verhindern (Safety)
- User Experience zu wahren (Antwort soll schnell kommen)
- Performance zu schützen (API Calls reduzieren)

Nach 2 Iterationen: Force-Ausgabe der besten verfügbaren Empfehlung.

---

## 7. Bosch Use Cases

### Warum Bosch Use Cases im Projekt verwendet werden

Die Plattform ist generic, nutzt aber einen Pool von 15 realen Bosch-Use-Cases als Referenz. Das dient mehreren Zwecken:

1. **Konkretisierung:** Nutzer "RAG Agent" ist vague. "Technical Documentation Q&A Agent" ist konkret.
2. **Best Practices:** Diese Use-Cases kommen aus realen Bosch-Projekten und POCs. Sie repräsentieren tatsächliche Anforderungen.
3. **Evaluierungshilfe:** Agent-Evaluation ist leichter, wenn man reale Use-Cases als Referenz hat.
4. **Domain Knowledge:** Sie codieren Wissen darüber, welche Frameworks für welche Use-Cases geeignet sind.

### Wie die Use Cases genutzt werden

Die Use-Cases sind KEINE Ziele der Implementierung. Stattdessen:

- Sie dienen als **Matching-Basis:** Nutzer-Input wird gegen sie gematched
- Sie liefern **Framework-Hinweise:** Jeder Use-Case hat eine Liste "typischer Frameworks"
- Sie bieten **Kontext:** Wenn ein Nutzer sagt "RAG-Agent", kann das System sagen "Ähnlich wie Use-Case X, typischerweise LangChain"

### Nutzen für die Entscheidungsfindung

Wenn ein Nutzer sagt "Ich brauche einen Agenten für technische Q&A", kann das System:

1. Matchen gegen "Technical Documentation Q&A Agent" aus dem Pool
2. Sehen: "Typische Frameworks: LangChain, LlamaIndex, Google ADK"
3. Diese Information in die Evaluierung einfließen lassen
4. Dem Nutzer sagen: "Ähnliche Use-Cases verwenden diese drei Frameworks"

Das gibt Empfehlungen eine empirische Grundlage.

---

## 8. Framework-Empfehlungen

### Wie Frameworks grundsätzlich bewertet werden

Die Framework-Evaluierung ist Multi-Kriterial. Es gibt kein perfektes Framework – es gibt nur "best fit für diese spezifischen Anforderungen".

Kriterien sind (beispielhaft):

- **RAG Capability:** Kann der Framework Dokumentation indexieren und Q&A darauf machen?
- **Automation Level:** Kann er Workflows automatisieren oder nur Q&A?
- **Learning Curve:** Wie schnell können Anfänger produktiv werden?
- **Community & Docs:** Gibt es Unterstützung?
- **Cloud vs. Local:** Läuft On-Premise oder nur in der Cloud?
- **Cost:** Open-Source, oder Enterprise-Lizenzgebühr?
- **Scalability:** Funktioniert für 1000e Anfragen/Tag?

Kein Framework überzeugt in allen Kriterien.

### Warum mehrere Frameworks verglichen werden

Ein single Framework-Recommendation hätte zu wenig Kontext. Stattdessen gibt die Plattform:

- **Top-1:** Beste Empfehlung basierend auf Gesamtbewertung
- **Top-3 Alternativen:** Mit unterschiedlichen Stärken (z.B. Top-1 ist bestes Scoring, Top-2 ist günstigste, Top-3 ist einfachste)

Dies gibt dem Nutzer Handlungsraum für eigene Abwägungen.

### Transparenz und Begründung

Jede Empfehlung includes eine ausführliche Begründung:

- Warum dieser Framework?
- Welche Anforderungen erfüllt er gut?
- Was sind Schwachstellen?
- Was sind Alternativen und wann nutzen?

Dies ist entscheidend: Ein Black-Box-Recommendation wäre nicht vertrauenswürdig.

---

## 9. Personalisierung und Erklärstil

### Ob und wie Nutzerprofile berücksichtigt werden

Der Profiler Agent (Agent B) erstellt ein detailliertes Profil. Dieses hat direkten Einfluss:

**Für Anfänger:**
- Empfiehlt einfachere Frameworks (LangChain vor LangGraph)
- Warnt vor zu komplexen Systemen
- Gibt mehr Erklärungen
- Betont Community-Support und Dokumentation

**Für Experten:**
- Kann komplexere Optionen empfehlen (LangGraph, AutoGPT)
- Fokus auf Performance und Customization
- Weniger Hold-Your-Hand, mehr technisches Detail

**Für Enterprise:**
- Compliance und Support wichtiger
- Open-Source vs. Commercial tritt in den Hintergrund
- Skalierbarkeit wird höher gewichtet

### Wie Erklärungen sich unterscheiden

**Anfänger sehen:**
- Vereinfachte Begründungen
- Glossar-Links
- Analogien (z.B. "LangChain ist wie LEGO – viele Bauteile, viel Flexibilität")

**Experten sehen:**
- Technische Begründungen
- Architektur-Skizzen
- Vergleiche zu Alternativen

### Ziel der Personalisierung

Die Personalisierung macht die Empfehlung **verständlich und anwendbar** für die spezifische Zielgruppe. Eine Empfehlung, die ein Anfänger nicht versteht, hilft nicht.

---

## 10. Feedback und Lernfähigkeit

### Ob Nutzer Feedback geben können

Ja. Nach jeder Empfehlung kann der Nutzer:

1. Ein Rating geben (1-5 Sterne)
2. Sagen, ob er die Empfehlung nutzen würde (Ja/Nein)
3. Optionale Freitext-Kommentare geben

### Warum Feedback gesammelt wird

Das Feedback dient mehreren Zwecken:

- **Validation:** War die Empfehlung korrekt? (Nur der Nutzer weiß das später)
- **Learning:** Wenn viele Nutzer Feedback geben, können wir die Modelle anpassen
- **Continuous Improvement:** Das System soll über Zeit besser werden

### Wie Feedback das System verbessern kann (Perspektive)

**Kurz-fristig (dieser Zyklus):**
- Feedback wird in JSON gespeichert
- Nutzer können späterhin ihre Feedback-Historie ansehen
- Pattern werden manuell analysiert

**Mittel-fristig (nächste Version):**
- Feedback-Daten werden systematisch ausgewertet
- "Wenn Nutzer Feedback sagen 'Framework X war zu komplex', dann skaliere X-Score runter für Anfänger"
- Embedding-Modelle können auf Feedback-Daten feinjustiert werden

**Langfristig:**
- Das System könnte sich vollständig selbstlernend weiterentwickeln
- Feedback in Chroma speichern und für zukünftige Matches nutzen

---

## 11. Technologie-Überblick (ohne Code)

### Haupttechnologien und ihre Rolle

**Google Gemini 2.5 Flash (LLM):**
- Generiert natürlichsprachliche Empfehlungen
- Parst User-Input und strukturiert es
- Erstellt Begründungen

**Google GenAI Embeddings Model:**
- Konvertiert Text in numerische Vektoren
- Ermöglicht semantische Ähnlichkeitssuche (Cosine Similarity)
- Nicht Code-basiert, sondern Embedding-basiert

**Chroma Vector Database:**
- Speichert Bosch Use-Cases als Vektoren
- Schnelle Similarity-Suche (findet ähnliche Use-Cases in Millisekunden)
- Persistente Speicherung auf Disk

**LangGraph:**
- Orchestrierungs-Framework
- Verwaltet Agent-Sequenzen und Conditional Routing
- State Management

**Streamlit:**
- Web-UI Framework
- Schnell, ohne Frontend-Programmierung
- Responsive für interaktive Chat-ähnliche Interfaces

**Python (3.11+):**
- Gesamtsprache für Agenten und Orchestrierung
- Ecosystem: pydantic (für type-safe data), google-genai (SDK), langgraph, chroma, etc.

### Wie die Technologien zusammenwirken

Grobes Datenfluss:

1. Nutzer gibt Text über Streamlit Web-UI ein
2. Text geht an RequirementsAgent (LLM)
3. Strukturierte Requirements gehen in State
4. UseCase Analyzer embedded Text mit GenAI, sucht in Chroma
5. Framework Analyzer evaluiert basierend auf Results
6. Decision Agent nutzt LLM für finale Synthese
7. Control Agent prüft Quality Gates
8. Empfehlung wird an Streamlit zurück gegeben und angezeigt

---

## 12. Grenzen und mögliche Weiterentwicklung

### Aktuelle Limitationen

**Embedding-Zuverlässigkeit:**
- Google GenAI Embedding API ist manchmal langsam
- Bei Timeouts wird auf Fallback-Vektoren (Dummy Vectors) zurückgegriffen
- Dies reduziert Matching-Genauigkeit

**Use-Case Pool:**
- Nur 15 vordefinierte Use-Cases
- Nicht alle möglichen Szenarien sind abgedeckt
- Manuell aktualisiert, nicht automatisch

**Framework Knowledge:**
- Framework-Eigenschaften sind in Code codiert, nicht in Vector Store
- Framework-Updates (z.B. neue Version mit neuen Features) werden nicht automatisch erfasst

**Keine echten API Integrationen:**
- Die Plattform kann nicht tatsächlich mit den Frameworks kommunizieren
- Sie basiert auf statischem Wissen, nicht Live-Daten

**Single-User nur:**
- Keine Multi-User Accounts oder Permission
- Feedback wird lokal gespeichert, nicht zentral

### Was bewusst nicht umgesetzt wurde

**Keine Auto-Codegen:**
- Plattform schreibt nicht automatisch Code für die Frameworks
- Sie empfiehlt nur, Implementierung muss der Nutzer tun

**Keine Live-Benchmarking:**
- Keine automatisierten Performance-Tests der Frameworks
- Empfehlungen basieren auf Wissen und Heuristiken, nicht gemessenen Metriken

**Keine Natursprachliche Iterative Refinement:**
- Nutzer kann nicht einfach sagen "das ist mir zu komplex, empfiehl etwas Einfacheres"
- Der Control Agent macht Loops auf Confidence-Basis, nicht auf natürlichsprachlichem Feedback

**Keine Multi-Language Support** (aktuell):
- Plattform ist auf Deutsch optimiert
- Englische oder andere Sprachen sind nicht getestet

### Mögliche Weiterentwicklungen

**Kurzfristig (nächste Monate):**
- Mehr Use-Cases hinzufügen (über 15 hinaus)
- Framework-Datenbank erweitern und strukturierter machen (Vector Store statt Code)
- Robust Embedding-Fallbacks (nicht einfach Dummy Vectors, sondern intelligentere Heuristiken)

**Mittelfristig (nächste Quartale):**
- Multi-User Support mit User Profiles
- Integration mit Framework Websites für Live-Feature Updates
- Feedback-Loop schließen (Feedback in Embeddings trainieren)
- Performance-Testing-Module hinzufügen (für Bechmarking)

**Langfristig (nächstes Jahr+):**
- Automatische Code-Skeleton-Generierung
- Integration in IDE-Plugins (VS Code Extension)
- Collaborative Framework Evaluation (Teams können gemeinsam bewerten)
- Automatische Framework-Monitoring (warnt bei Releases, Security Patches)

---

## Zusammenfassung

Die Framework Advisor Plattform ist ein intelligentes, multi-agen orchestriertes System zur Empfehlung von AI-Frameworks. Sie kombiniert spezialisierte Agenten (Requirements, Profiler, UseCase Analyzer, Framework Analyzer, Decision, Control) mit semantischer Suche über einen Bosch-Use-Case Pool und LLM-basierte Synthese zu einer nutzbaren Entscheidungshilfe.

Das System ist transparent, personalisiert und iterativ – es stellt Rückfragen, wenn Unsicherheit zu hoch ist, und endet mit begründeten, nachvollziehbaren Empfehlungen. Feedback wird gesammelt für kontinuierliches Lernen.

Die Architektur als "Agent-for-Agents" ermöglicht Separation of Concerns, bessere Fehlerbehandlung und einfachere Erweiterung. Jeder Agent hat eine klare Verantwortung, was das System wartbar und verständlich macht.
