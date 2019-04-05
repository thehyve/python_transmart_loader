from typing import List

from .ontology_mapper import OntologyMapper
from transmart_loader.copy_writer import TransmartCopyWriter


def normalise_code(code: str) -> str:
    return code.replace('!', '').replace('*', '')


class OntologyWriter:

    def process_chapter_row(self, row: List[str]) -> None:
        [code, name] = row
        self.mapper.map_chapter(code, name)

    def process_group_row(self, row: List[str]) -> None:
        [range_start, range_end, chapter, name] = row
        self.mapper.map_group(range_start, range_end, chapter, name)

    def process_code_row(self, row: List[str]) -> None:
        [
            #         Feld 1 : Klassifikationsebene, 1 Zeichen
            #         3 = Dreisteller
            #         4 = Viersteller
            #         5 = Fünfsteller
            level,
            #     Feld 2 : Ort der Schlüsselnummer im Klassifikationsbaum, 1 Zeichen
            #     T = terminale Schlüsselnummer (kodierbarer Endpunkt)
            #     N = nichtterminale Schlüsselnummer (kein kodierbarer Endpunkt)
            node_type,
            #     Feld 3 : Art der Vier- und Fünfsteller
            #     X = explizit aufgeführt (präkombiniert)
            #     S = per Subklassifikation (postkombiniert)
            code_type,
            # Feld 4 : Kapitelnummer, max. 2 Zeichen
            chapter,
            # Feld 5 : erster Dreisteller der Gruppe, 3 Zeichen
            group,
            # Feld 6 : Schlüsselnummer ohne eventuelles Kreuz, bis zu 7 Zeichen
            code,
            # Feld 7 : Schlüsselnummer ohne Strich, Stern und  Ausrufezeichen, bis zu 6 Zeichen
            _,
            # Feld 8 : Schlüsselnummer ohne Punkt, Strich, Stern und Ausrufezeichen, bis zu 5 Zeichen
            _,
            # Feld 9 : Klassentitel, zusammengesetzt aus Bestandteilen der Titel der dreistelligen, vierstelligen und
            # fünfstelligen Kodes, falls vorhanden, bis zu 255 Zeichen
            name,
            # Feld 10 : Titel des dreistelligen Kodes, bis zu 255 Zeichen
            _,
            # Feld 11 : Titel des vierstelligen Kodes, falls vorhanden, bis zu 255 Zeichen
            _,
            # Feld 12 : Titel des fünfstelligen Kodes, falls vorhanden, bis zu 255 Zeichen
            _,
            # Feld 13: Verwendung der Schlüsselnummer nach Paragraph 295
            # P = zur Primärverschlüsselung zugelassene Schlüsselnummer
            # O = nur als Sternschlüsselnummer zugelassen
            # Z = nur als Ausrufezeichenschlüsselnummer zugelassen
            # V = nicht zur Verschlüsselung zugelassen
            _,
            # Feld 14: Verwendung der Schlüsselnummer nach Paragraph 301
            # P = zur Primärverschlüsselung zugelassen
            # O = nur als Sternschlüsselnummer zugelassen
            # Z = nur als Ausrufezeichenschlüsselnummer zugelassen
            # V = nicht zur Verschlüsselung zugelassen
            _,
            # Feld 15: Bezug zur Mortalitätsliste 1
            _,
            # Feld 16: Bezug zur Mortalitätsliste 2
            _,
            # Feld 17: Bezug zur Mortalitätsliste 3
            _,
            # Feld 18: Bezug zur Mortalitätsliste 4
            _,
            # Feld 19: Bezug zur Morbiditätsliste
            _,
            # Feld 20: Geschlechtsbezug der Schlüsselnummer
            # 9 = kein Geschlechtsbezug
            # M = männlich
            # W = weiblich
            _,
            # Feld 21: Art des Fehlers bei Geschlechtsbezug
            # 9 = irrelevant
            # K = Kann-Fehler
            _,
            # Feld 22: untere Altersgrenze für eine Schlüsselnummer (Eine Krankheit kann auftreten ab einem Alter von
            # mindestens n vollendeten Lebenstagen/-jahren.)
            # 9999    = irrelevant
            # t000 - t364 = ab 0 Tage einschließlich Fetalzeit - ab 364 Lebenstagen
            # also t000 = ab Geburt (ab 1. Lebenstag) einschließlich Fetalzeit
            # t001 = ab 1 vollendeten Lebenstag (ab 2. Lebenstag)
            # t002 = ab 2 vollendeten Lebenstagen (ab 3. Lebenstag)
            # usw. bis
            # t028 = ab 28 vollendeten Lebenstagen (ab dem 29. Lebenstag, ab dem 2. Lebensmonat )
            # usw. bis
            # t364 = ab 364 vollendeten Lebenstagen (ab dem 365. Lebenstag
            # j001 - j124 = ab 1 Lebensjahr - ab 124 Lebensjahren
            # also j001 = ab 1 vollendeten Lebensjahr (ab dem 2. Lebensjahr; ab 365 vollendeten Lebenstagen)
            # j002 = ab 2 vollendeten Lebensjahren (ab dem 3. Lebensjahr)
            # j003 = ab 3 vollendeten Lebensjahren (ab dem 4. Lebensjahr)
            # usw. bis
            # j124 = ab 124 vollendeten Lebensjahren (ab dem 125. Lebensjahr)
            _,
            # Feld 23: obere Altersgrenze für eine Schlüsselnummer (Eine Krankheit kann auftreten bis zu einem Alter von
            # höchstens m vollendeten Lebenstagen/-jahren.)
            # 9999    = irrelevant
            # t000 - t364 = 0 Tage - bis zu 364 Tagen
            # also t000 = fetal, vor der Geburt
            # t001 = bis zu 1 vollendeten Lebenstag (bis Ende des 1. Lebenstages)
            # t002 = bis zu 2 vollendeten Lebenstagen (bis Ende des 2. Lebenstages)
            # usw. bis
            # t364 = bis zu 364 vollendeten Lebenstagen (bis Ende des 364. Lebenstages)
            # j001 - j124 = bis zu 1 Jahr – bis zu 124  Jahre
            # also j001 = bis zu 1 vollendeten Lebensjahr (bis Ende des 1. Lebensjahres; bis zum Ende des 365.
            # Lebenstages)
            # j002 = bis zu 2 vollendeten Lebensjahren (bis Ende des 2. Lebensjahres)
            # usw. bis
            # j124 = bis zu 124 vollendeten Lebensjahren (bis Ende des 124. Lebensjahres)
            _,
            # Feld 24: Art des Fehlers bei Altersbezug
            # 9 = irrelevant
            # M = Muss-Fehler
            # K = Kann-Fehler
            _,
            # Feld 25: Krankheit in Mitteleuropa sehr selten?
            # J = Ja (--> Kann-Fehler auslösen!)
            # N = Nein
            _,
            # Feld 26: Schlüsselnummer mit Inhalt belegt?
            # J = Ja
            # N = Nein (--> Kann-Fehler auslösen!)
            _,
            # Feld 27: IfSG-Meldung, kennzeichnet, dass bei Diagnosen, die mit dieser Schlüsselnummer kodiert sind,
            # besonders auf die Arzt-Meldepflicht nach dem Infektionsschutzgesetz (IfSG) hinzuweisen ist
            # J = Ja
            # N = Nein
            _,
            # Feld 28: IfSG-Labor, kennzeichnet, dass bei Laboruntersuchungen zu diesen Diagnosen die
            # Laborausschlussziffer des EBM (32006) gewählt werden kann
            # J = Ja
            # N = Nein
            _
        ] = row
        if node_type == 'N':
            self.mapper.map_subgroup(normalise_code(group), normalise_code(code), name)
        else:
            self.mapper.map_code(normalise_code(group), normalise_code(code), name)

    def write(self, writer: TransmartCopyWriter):
        for concept in self.mapper.concepts:
            writer.visit_concept(concept)
        for node in self.mapper.chapter_nodes.values():
            writer.visit_node(node)

    def __init__(self, system: str):
        self.mapper = OntologyMapper(system)
