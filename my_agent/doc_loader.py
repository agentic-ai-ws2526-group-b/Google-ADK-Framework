"""
Doc Loader Module
Utilities für das Laden und Importieren von Framework-Dokumentationen
aus URLs, Dateien und anderen Quellen.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import requests
from bs4 import BeautifulSoup

from my_agent.agent import FrameworkAdvisorAgent
from my_agent.framework_docs_config import (
    FRAMEWORK_DOCUMENTATION_URLS,
    get_documentation_urls,
    get_all_frameworks
)


# ============================================================================
# Datenklassen
# ============================================================================

@dataclass
class DocumentationSource:
    """Repräsentation einer Dokumentationsquelle."""
    framework_name: str
    source_url: str
    title: str
    content: str
    source_type: str = "web"  # "web", "file", "manual"


# ============================================================================
# Utility-Funktionen
# ============================================================================

def fetch_page_text(url: str, timeout: int = 10) -> str:
    """
    Ruft eine URL per HTTP GET ab und extrahiert lesbaren Text mit BeautifulSoup.
    
    HTML-Tags, Scripts, Styles und andere nicht-relevante Inhalte werden entfernt.
    
    Args:
        url: Die zu scrapende URL.
        timeout: Timeout für den HTTP-Request in Sekunden (Default: 10).
        
    Returns:
        Der extrahierte Textinhalt der Seite.
        
    Raises:
        requests.RequestException: Falls der HTTP-Request fehlschlägt.
    """
    try:
        # HTTP-Request mit User-Agent Header
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, timeout=timeout, headers=headers)
        response.raise_for_status()

        # HTML mit BeautifulSoup parsen
        soup = BeautifulSoup(response.content, "html.parser")

        # Script- und Style-Tags entfernen
        for script in soup(["script", "style"]):
            script.decompose()

        # Text extrahieren
        text = soup.get_text()

        # Whitespace bereinigen
        lines = (line.strip() for line in text.split("\n"))
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)

        return text

    except requests.RequestException as e:
        raise requests.RequestException(f"Fehler beim Abrufen der URL '{url}': {e}")


def load_documentation_from_file(file_path: str, encoding: str = "utf-8") -> str:
    """
    Lädt Dokumentation aus einer lokalen Textdatei.
    
    Args:
        file_path: Pfad zur Dokumentationsdatei (z.B. "docs/framework.txt").
        encoding: Datei-Encoding (Default: UTF-8).
        
    Returns:
        Der Inhalt der Datei als String.
        
    Raises:
        FileNotFoundError: Falls die Datei nicht existiert.
    """
    try:
        with open(file_path, "r", encoding=encoding) as f:
            content = f.read()
        return content
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Dokumentationsdatei nicht gefunden: {file_path}") from e


def load_documentation_from_url(
    framework_name: str,
    url: str,
    title: str = None
) -> DocumentationSource:
    """
    Lädt eine Framework-Dokumentation von einer URL.
    
    Args:
        framework_name: Name des Frameworks (z.B. "Google ADK").
        url: URL der Dokumentation.
        title: Optionaler Titel der Dokumentation.
        
    Returns:
        Ein DocumentationSource-Objekt mit dem geladenem Inhalt.
        
    Raises:
        requests.RequestException: Falls die URL nicht abrufbar ist.
    """
    content = fetch_page_text(url)
    
    if not title:
        title = f"Documentation from {url}"
    
    return DocumentationSource(
        framework_name=framework_name,
        source_url=url,
        title=title,
        content=content,
        source_type="web"
    )


def load_documentation_from_file_source(
    framework_name: str,
    file_path: str,
    title: str = None
) -> DocumentationSource:
    """
    Lädt eine Framework-Dokumentation aus einer lokalen Datei.
    
    Args:
        framework_name: Name des Frameworks.
        file_path: Pfad zur lokalen Datei.
        title: Optionaler Titel der Dokumentation.
        
    Returns:
        Ein DocumentationSource-Objekt mit dem geladenem Inhalt.
        
    Raises:
        FileNotFoundError: Falls die Datei nicht existiert.
    """
    content = load_documentation_from_file(file_path)
    
    if not title:
        title = f"Documentation from {file_path}"
    
    return DocumentationSource(
        framework_name=framework_name,
        source_url=file_path,
        title=title,
        content=content,
        source_type="file"
    )


# ============================================================================
# Doc Importer Klasse
# ============================================================================

class DocumentationImporter:
    """
    Helper-Klasse zum Importieren und Hinzufügen von Dokumentationen
    zu einem FrameworkAdvisorAgent.
    """

    def __init__(self, agent: FrameworkAdvisorAgent) -> None:
        """
        Initialisiert den DocumentationImporter.
        
        Args:
            agent: Eine FrameworkAdvisorAgent-Instanz.
        """
        self.agent = agent

    def add_documentation(
        self,
        framework_name: str,
        content: str,
        source: str = "manual"
    ) -> None:
        """
        Fügt Dokumentation zum Agent hinzu.
        
        Args:
            framework_name: Name des Frameworks.
            content: Der Dokumentationstext.
            source: Quelle der Dokumentation.
        """
        self.agent.add_framework_documentation(
            framework_name=framework_name,
            documentation=content,
            doc_source=source
        )
        print(f"✓ Dokumentation für '{framework_name}' importiert.")

    def add_from_url(
        self,
        framework_name: str,
        url: str,
        title: str = None
    ) -> None:
        """
        Importiert Dokumentation von einer URL.
        
        Args:
            framework_name: Name des Frameworks.
            url: URL der Dokumentation.
            title: Optionaler Titel.
        """
        try:
            print(f"🔗 Lade Dokumentation von {url}...")
            doc_source = load_documentation_from_url(framework_name, url, title)
            self.add_documentation(
                framework_name=doc_source.framework_name,
                content=doc_source.content,
                source=f"url_{url}"
            )
        except requests.RequestException as e:
            print(f"✗ Fehler beim Abrufen der URL: {e}")
            raise

    def add_from_file(
        self,
        framework_name: str,
        file_path: str,
        title: str = None
    ) -> None:
        """
        Importiert Dokumentation aus einer lokalen Datei.
        
        Args:
            framework_name: Name des Frameworks.
            file_path: Pfad zur Datei.
            title: Optionaler Titel.
        """
        try:
            print(f"📄 Lade Dokumentation aus {file_path}...")
            doc_source = load_documentation_from_file_source(
                framework_name,
                file_path,
                title
            )
            self.add_documentation(
                framework_name=doc_source.framework_name,
                content=doc_source.content,
                source=f"file_{file_path}"
            )
        except FileNotFoundError as e:
            print(f"✗ Fehler beim Laden der Datei: {e}")
            raise

    def add_from_urls(self, url_mappings: List[tuple]) -> None:
        """
        Importiert Dokumentationen von mehreren URLs.
        
        Args:
            url_mappings: Liste von Tupeln (framework_name, url, title).
            
        Example:
            importer.add_from_urls([
                ("Google ADK", "https://example.com/adk", "ADK Docs"),
                ("LangChain", "https://docs.langchain.com", "LangChain Docs"),
            ])
        """
        for mapping in url_mappings:
            if len(mapping) == 2:
                framework_name, url = mapping
                title = None
            elif len(mapping) == 3:
                framework_name, url, title = mapping
            else:
                print(f"⚠ Ungültiges Mapping: {mapping}. Übersprungen.")
                continue

            try:
                self.add_from_url(framework_name, url, title)
            except Exception as e:
                print(f"⚠ Fehler bei {framework_name}: {e}. Fahre fort...")
                continue

    def add_from_files(self, file_mappings: List[tuple]) -> None:
        """
        Importiert Dokumentationen aus mehreren lokalen Dateien.
        
        Args:
            file_mappings: Liste von Tupeln (framework_name, file_path, title).
            
        Example:
            importer.add_from_files([
                ("Google ADK", "docs/adk.txt", "ADK Docs"),
                ("LangChain", "docs/langchain.md", "LangChain Docs"),
            ])
        """
        for mapping in file_mappings:
            if len(mapping) == 2:
                framework_name, file_path = mapping
                title = None
            elif len(mapping) == 3:
                framework_name, file_path, title = mapping
            else:
                print(f"⚠ Ungültiges Mapping: {mapping}. Übersprungen.")
                continue

            try:
                self.add_from_file(framework_name, file_path, title)
            except Exception as e:
                print(f"⚠ Fehler bei {framework_name}: {e}. Fahre fort...")
                continue

    def add_from_config(self, framework_name: str = None, source_filter: str = None) -> None:
        """
        Lädt Dokumentationen basierend auf der zentralen Konfiguration.
        
        Args:
            framework_name: Spezifischer Framework-Name, oder None für alle.
            source_filter: Filter nach Quelle (z.B. "official", "github", "reference").
                          None = alle Quellen.
                          
        Example:
            # Alle Dokumentationen laden
            importer.add_from_config()
            
            # Nur LangChain
            importer.add_from_config(framework_name="LangChain")
            
            # Nur offizielle Docs
            importer.add_from_config(source_filter="official")
        """
        if framework_name:
            # Spezifisches Framework laden
            urls = get_documentation_urls(framework_name)
            if not urls:
                print(f"⚠ Keine Dokumentationen für '{framework_name}' konfiguriert.")
                return
            frameworks_to_load = [(framework_name, urls)]
        else:
            # Alle Frameworks laden
            frameworks_to_load = [
                (name, docs) for name, docs in FRAMEWORK_DOCUMENTATION_URLS.items()
            ]

        total_loaded = 0
        total_failed = 0

        for fw_name, docs in frameworks_to_load:
            print(f"\n📚 Lade Dokumentationen für '{fw_name}'...")
            
            for doc_info in docs:
                # Quelle filtern falls gewünscht
                if source_filter and doc_info["source"] != source_filter:
                    continue

                try:
                    url = doc_info["url"]
                    title = doc_info["title"]
                    source = doc_info["source"]
                    
                    print(f"  🔗 {title}...")
                    self.add_from_url(fw_name, url, title)
                    total_loaded += 1
                    
                except Exception as e:
                    print(f"  ✗ Fehler: {e}")
                    total_failed += 1
                    continue

        print(f"\n✓ Import abgeschlossen: {total_loaded} erfolgreich, {total_failed} fehlgeschlagen.")

    def add_all_frameworks_from_config(self) -> None:
        """
        Convenience-Methode: Lädt Dokumentationen für ALLE Frameworks aus der Config.
        
        Dies kann eine Weile dauern, da viele URLs abgerufen werden.
        """
        print("🚀 Starte Massenimport aller Framework-Dokumentationen...")
        print("   Dies kann einige Minuten dauern.\n")
        self.add_from_config()



# ============================================================================
# Beispiel-Script (optional, zum Testen)
# ============================================================================

if __name__ == "__main__":
    # Beispiel: Agent und Importer initialisieren
    print("📚 Documentation Loader - Beispiel\n")

    try:
        agent = FrameworkAdvisorAgent()
        importer = DocumentationImporter(agent)

        # Seed-Daten laden
        agent.seed_basic_framework_knowledge()

        # Beispiel 1: Nur LangChain Dokumentationen laden
        # importer.add_from_config(framework_name="LangChain")

        # Beispiel 2: Nur offizielle Dokumentationen laden
        # importer.add_from_config(source_filter="official")

        # Beispiel 3: ALLE Dokumentationen laden (Vorsicht: kann lange dauern!)
        # importer.add_all_frameworks_from_config()

        # Beispiel 4: Einzelne URL manuell laden
        # importer.add_from_url(
        #     framework_name="LangChain",
        #     url="https://docs.langchain.com/oss/python/langchain/overview"
        # )

        print("\n✓ DocumentationImporter ist bereit zur Verwendung!")
        print("\n  Verfügbare Methoden:")
        print("  • importer.add_from_config(framework_name='...')     - Ein Framework laden")
        print("  • importer.add_from_config(source_filter='official') - Nach Quelle filtern")
        print("  • importer.add_all_frameworks_from_config()         - Alles laden")
        print("  • importer.add_from_url(framework_name, url)        - Manuell eine URL laden")

    except Exception as e:
        print(f"❌ Fehler: {e}")

