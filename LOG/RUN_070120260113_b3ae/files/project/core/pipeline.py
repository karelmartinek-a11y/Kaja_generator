# Plní úkoly A/B pipeline
# Vytvořeno pro Kajovo
def run():
    from datetime import datetime
    print('Projekt: # ZADÁNÍ PRO GENEROVÁNÍ PROGRAMU: „KÁJA“ (WINDOWS) – KONSOLIDOVANÁ VERZE

Datum konsolidace: 2026-01-06

Zdrojové dokumenty:
- `00_zadani_MASTER_FULL.md` (původní MASTER zadání programu)
- `Skill_Design.md` (DESIGN MANIFEST UI)

## 0) Závaznost a pořadí přednosti

Tento dokument je určen jako jediný prompt/zadání pro generování programu.

Závazné části:
- Kapitola 1) DESIGN MANIFEST UI (závazná pravidla vzhledu a chování UI).
- Kapitola 3) Konsolidované MASTER zadání programu (funkční a technické požadavky; upravené do souladu s DESIGN MANIFESTEM).

Nezávazné části:
- PŘÍLOHA A) Původní MASTER zadání (verbatim) je přiložena pouze pro audit a pro splnění požadavku „neztratit ani byte“ původního zadání. V případě jakéhokoliv rozdílu mezi PŘÍLOHOU A a Kapitolami 1) + 3) platí Kapitoly 1) + 3).

## 1) DESIGN MANIFEST UI (ZÁVAZNÝ TEXT)

# DESIGN MANUÁL – KÁJOVO
VERZE: v1.0  
STAV: DRAFT

---

## 1.00.000 ÚČEL A ZÁVAZNOST DOKUMENTU

Tento dokument definuje oficiální, závazná a jednotná pravidla designu uživatelského rozhraní.

Platí pro:
- všechny desktopové programy,
- všechny jejich části (pracovní plocha, záhlaví, sekce, komponenty, dialogy, tabulky, seznamy),
- všechny nové i existující projekty.

Nedodržení tohoto dokumentu je chyba návrhu.

Ve vlastním textu manuálu se nepoužívá název „Kájovo“. Název se používá pouze v názvu dokumentu.

---

## 2.00.000 OBECNÁ PRAVIDLA

### 2.01.000 Vizuální charakter

- Design je technický, funkční, art-deco.
- Neexistují dekorativní prvky bez funkce.
- Každý prvek musí být okamžitě čitelný, pochopitelný a jednoznačný.
- Všechny prvky jsou klasifikovány jako:
  - monolit,
  - biolit,
  - triolit.
Žádná jiná strukturální forma není přípustná.

---

### 2.02.000 Barevný systém (globální pravidla)

- Uživatelské rozhraní je striktně černobílé.
- Červená barva je vyhrazena výhradně pro:
  - ukončovací prvky (EXIT / QUIT / CLOSE),
  - kritické akce,
  - nebezpečné stavy,
  - zákaz,
  - nedostupnost.
- Šedá barva je povolena pouze pro:
  - neaktivní text,
  - neaktivní grafiku / symboly.
- Použití jiných barev není dovoleno.
- Barevný systém není rozšiřitelný bez revize tohoto dokumentu.

---

### 2.03.000 Povinný formát zadávání barev (pro každý prvek)

Barva každého UI prvku se skládá z vizuálních složek. Každý prvek musí mít barvy definované explicitně tímto formátem.

Povinný formát:

Standardní barvy prvku XY jsou:
a) lem – [barva], 1 pixel  
b) okraj – [barva], 1 pixel  
c) písmo nebo grafika – [barva]  
d) pozadí – [barva]  

- Pokud některá složka neexistuje, musí to být explicitně uvedeno (např. „prvek nemá lem“).
- Pokud se liší tloušťka, musí být explicitně uvedena.
- Není dovoleno používat zjednodušené popisy typu „černobílý prvek“ bez rozkladu na složky.

---

### 2.04.000 Typografie

- Jediný povolený font: Montserrat.
- Povolené řezy: Regular, Bold.
- Nadpisy, názvy sekcí, názvy sloupců tabulek, názvy skupin:
  - Montserrat Bold,
  - VŠE VELKÝMI PÍSMENY.
- Běžný obsah a hodnoty:
  - Montserrat Regular,
  - standardní velikost písma (identická v celém UI).
- Fonty musí být:
  - součástí aplikace nebo projektu,
  - lokálně dostupné,
  - nikdy načítané z externích zdrojů,
  - nikdy závislé na systémových fontech.

---

### 2.05.000 Tvarosloví a geometrie

- Ostré rohy jsou v celém systému zakázány.
- Každý prvek musí mít:
  - zaoblené rohy,
  - jednotný poloměr zaoblení.
- Pravidlo platí pro:
  - komponenty,
  - kontejnery,
  - viewporty,
  - sekce,
  - dialogy,
  - tabulky,
  - veškeré vrstvy UI.
- Výjimky nejsou povoleny.

---

## 3.00.000 PRACOVNÍ PLOCHA PROGRAMU

### 3.01.000 Spuštění a základní režim

Program se vždy spouští:
- na hlavním monitoru,
- v maximalizovaném okně,
- s černým pozadím,
- bez vizuálního problikávání nebo změn režimu.

UI je plně dynamické.

---

### 3.02.000 Dynamika, responzivita a poměrové chování

- Poměrové chování platí hierarchicky:
  - okno → sekce,
  - sekce → komponenty,
  - komponenty → typografie a grafika.
- Pevné rozměry jsou zakázány, pokud nejsou technologicky nutné.
- Komponenty se mohou škálovat:
  - do mikroskopických (i nečitelných) rozměrů,
  - do extrémně velkých rozměrů,
  - bez umělých limitů.
- Sekce musí být uživatelsky měnitelné:
  - na šířku,
  - na výšku.
- Obsah se nikdy:
  - automaticky nepřeskupuje,
  - nedeformuje,
  - nemění pořadí.

---

## 4.00.000 SEKCE (LOGICKÉ SKUPINY KOMPONENTŮ A PRVKŮ)

### 4.01.000 Definice

Sekce je logická skupina komponentů a jiných prvků, která tvoří funkční celek.

---

### 4.02.000 Standardní barvy sekce

Standardní barvy sekce jsou:
a) lem – bílý, 1 pixel  
b) okraj – černý, 1 pixel  
c) písmo nebo grafika – bílé  
d) pozadí – černé  

- Sekce má vždy viditelný lem.
- Sekce je vizuálně oddělená od ostatních sekcí.

---

### 4.03.000 Název sekce jako součást horního lemu

Název sekce:
- je součástí horního bílého lemu sekce,
- píše se VŠE VELKÝMI PÍSMENY,
- je zarovnán vlevo.

Konstrukce horního lemu sekce je povinná a přesná:
1) Horní lem zleva pokračuje.  
2) Horní lem je zleva přerušen.  
3) Následuje mezera odpovídající šířce písmene „A“.  
4) Následuje vlastní název sekce.  
5) Následuje mezera odpovídající šířce písmene „A“.  
6) Horní lem pokračuje dále až do pravého okraje sekce.  

Výškové umístění:
- Horní lem je na stejné úrovni jako střed výšky textového pole, ve kterém je umístěn název sekce.

---

## 5.00.000 ZÁHLAVÍ PROGRAMU

### 5.01.000 Povinné části záhlaví

Záhlaví každého programu se skládá z:
a) Název programu + verze  
b) Konfigurační ovládací prvky vlevo + EXIT/QUIT/CLOSE vpravo  
c) Stavový řádek  

Celé záhlaví má pevná pole, která:
- se nepřeskupují,
- jsou poměrově pevná vůči ploše celého programu,
- při změně velikosti okna se dynamicky mění velikost obsahu stejně jako u sekcí (obsah škáluje, pole se nepřeskupují).

---

### 5.02.000 Název programu + verze

Název programu:
- je vždy napsán VŠEMI VELKÝMI PÍSMENY,
- je následovaný verzí ve formátu v0.00,
- je vycentrovaný blok,
- je na samostatném řádku.

---

### 5.03.000 Konfigurační ovládací prvky + ukončení programu

Konfigurační ovládací prvky a volby (např. ULOŽIT/SAVE, LOAD, SETTINGS, NOVÝ/NEW, LOG a podobné):
- jsou zarovnané vlevo,
- jsou na stejném řádku jako ukončovací prvky.

Ukončovací prvky:
- EXIT / QUIT / CLOSE
- jsou vždy vpravo,
- jsou vždy na stejném řádku jako konfigurační ovládací prvky.

Konfigurační ovládací prvky jsou interaktivní prvky a musí mít povinné stavy dle kapitoly 6 a kontraktu v kapitole 8.

Standardní barvy konfiguračního ovládacího prvku ve stavu NORMÁLNÍ (redundantně):
a) lem – bílý, 1 pixel  
b) okraj – černý, 1 pixel  
c) písmo nebo grafika – bílé  
d) pozadí – černé  

Ukončovací prvek je červený prvek a řídí se speciálním režimem červených prvků (kapitola 6 a kapitola 8).

Standardní barvy ukončovacího prvku ve stavu NORMAL (redundantně):
a) lem – červený, 1 pixel  
b) okraj – černý, 1 pixel  
c) písmo nebo grafika – černé  
d) pozadí – červené  

Standardní barvy ukončovacího prvku ve stavu ACTIVE (redundantně):
a) lem – červený, 1 pixel  
b) okraj – černý, 1 pixel  
c) písmo nebo grafika – červené  
d) pozadí – černé  

---

### 5.04.000 Stavový řádek

Stavový řádek vždy zobrazuje:
- aktuální čas,
- aktuální datum.

Stavový řádek musí být na první pohled jednoznačný v tom, zda:
- program nic nedělá,
- program vykonává funkci / proces v běhu.

Pokud je proces aktivní, stavový řádek vždy zobrazuje současně:
- progress „teploměr“,
- odpočet zbývajícího času (pokud je odhadnutelný),
- procentuální stav procesu (pokud je odhadnutelný),
- aktuální krok / činnost, která se děje:
  - deterministicky,
  - na úrovni největšího možného detailu.

Pokud nelze čas ani procenta odhadnout:
- použije se varianta, kdy v progress teploměru „rtuť“ běhá stále sem a tam.

---

## 6.00.000 INTERAKČNÍ PRVKY (TLAČÍTKA, PŘEPÍNAČE, VOLBY, POLOŽKY)

### 6.01.000 Povinnost stavů (globální pravidlo)

Každý interaktivní prvek, kromě červeného prvku, musí podporovat tři povinné stavy:
a) Normální / připravený / vypnutý  
b) Aktivní / vybraný / zapnutý  
c) Neaktivní / nedostupný / nepoužitelný  

Červený prvek má pouze dva stavy:
a) Normal  
b) Active  

---

### 6.02.000 Povinné stavy interaktivních prvků (nečervené prvky)

Každý interaktivní prvek (nečervený) musí mít následující barvy.

a) Normální / připravený / vypnutý

Standardní barvy interaktivního prvku ve stavu NORMÁLNÍ jsou:
a) lem – bílý, 1 pixel  
b) okraj – černý, 1 pixel  
c) pozadí – černé  
d) písmo nebo symbol – bílé  

b) Aktivní / vybraný / zapnutý

Standardní barvy interaktivního prvku ve stavu AKTIVNÍ jsou:
a) lem – bílý, 1 pixel  
b) okraj – černý, 1 pixel  
c) pozadí – bílé  
d) písmo nebo symbol – černé  

c) Neaktivní / nedostupný / nepoužitelný

Standardní barvy interaktivního prvku ve stavu NEAKTIVNÍ jsou:
a) lem – červený, 1 pixel  
b) okraj – červený, 1 pixel  
c) pozadí – černé  
d) písmo nebo symbol – šedivé  

Změna stavu:
- nesmí měnit rozměry prvku,
- nesmí měnit jeho pozici,
- nesmí měnit layout,
- mění pouze barvy.

---

### 6.03.000 Červený (kritický) prvek – povinné stavy (NORMAL/ACTIVE)

Červený prvek reprezentuje kritickou funkci.

Červený prvek – stav NORMAL:
a) lem – červený, 1 pixel  
b) okraj – černý, 1 pixel  
c) pozadí – červené  
d) písmo nebo symbol – černé  

Červený prvek – stav ACTIVE:
a) lem – červený, 1 pixel  
b) okraj – černý, 1 pixel  
c) pozadí – černé  
d) písmo nebo symbol – červené  

Červený prvek:
- nemá stav NEAKTIVNÍ (disabled),
- je vždy dostupný nebo aktivní dle implementace,
- nikdy nepoužívá schéma „červený lem + červený okraj + šedivý text“ jako svůj vlastní disabled stav.

---

### 6.04.000 Tlačítko (nečervené) – redundantní výpis stavů

Tlačítko (nečervené) musí mít tři povinné stavy dle 6.02.

Tlačítko – stav NORMÁLNÍ:
a) lem – bílý, 1 pixel  
b) okraj – černý, 1 pixel  
c) pozadí – černé  
d) písmo nebo symbol – bílé  

Tlačítko – stav AKTIVNÍ:
a) lem – bílý, 1 pixel  
b) okraj – černý, 1 pixel  
c) pozadí – bílé  
d) písmo nebo symbol – černé  

Tlačítko – stav NEAKTIVNÍ:
a) lem – červený, 1 pixel  
b) okraj – červený, 1 pixel  
c) pozadí – černé  
d) písmo nebo symbol – šedivé  

---

### 6.05.000 Tlačítko (červené, např. EXIT/QUIT/CLOSE) – redundantní výpis stavů

Červené tlačítko má pouze NORMAL a ACTIVE dle 6.03.

Červené tlačítko – stav NORMAL:
a) lem – červený, 1 pixel  
b) okraj – černý, 1 pixel  
c) pozadí – červené  
d) písmo nebo symbol – černé  

Červené tlačítko – stav ACTIVE:
a) lem – červený, 1 pixel  
b) okraj – černý, 1 pixel  
c) pozadí – černé  
d) písmo nebo symbol – červené  

---

### 6.06.000 Přepínač (toggle) – redundantní výpis stavů

Přepínač (toggle) je nečervený interaktivní prvek, musí mít tři povinné stavy dle 6.02.

Přepínač – stav VYPNUTÝ (NORMÁLNÍ):
a) lem – bílý, 1 pixel  
b) okraj – černý, 1 pixel  
c) pozadí – černé  
d) písmo nebo symbol – bílé  

Přepínač – stav ZAPNUTÝ (AKTIVNÍ):
a) lem – bílý, 1 pixel  
b) okraj – černý, 1 pixel  
c) pozadí – bílé  
d) písmo nebo symbol – černé  

Přepínač – stav NEPOUŽITELNÝ (NEAKTIVNÍ):
a) lem – červený, 1 pixel  
b) okraj – červený, 1 pixel  
c) pozadí – černé  
d) písmo nebo symbol – šedivé  

Logika výběru:
- Pokud je povolen pouze jeden výběr: vždy musí být aktivní právě jeden.
- Pokud je vícenásobný výběr: každý přepínač je nezávislý.
- Pokud není explicitně uvedeno jinak: platí výše uvedené.

---

### 6.07.000 Radio volba – redundantní výpis stavů

Radio volba je nečervený interaktivní prvek, musí mít tři povinné stavy dle 6.02.

Radio volba – stav NORMÁLNÍ:
a) lem – bílý, 1 pixel  
b) okraj – černý, 1 pixel  
c) pozadí – černé  
d) písmo nebo symbol – bílé  

Radio volba – stav AKTIVNÍ (VYBRANÁ):
a) lem – bílý, 1 pixel  
b) okraj – černý, 1 pixel  
c) pozadí – bílé  
d) písmo nebo symbol – černé  

Radio volba – stav NEAKTIVNÍ:
a) lem – červený, 1 pixel  
b) okraj – červený, 1 pixel  
c) pozadí – černé  
d) písmo nebo symbol – šedivé  

---

### 6.08.000 Checkbox – redundantní výpis stavů

Checkbox je nečervený interaktivní prvek, musí mít tři povinné stavy dle 6.02.

Checkbox – stav NORMÁLNÍ (NEZAŠKRTNUTÝ):
a) lem – bílý, 1 pixel  
b) okraj – černý, 1 pixel  
c) pozadí – černé  
d) písmo nebo symbol – bílé  

Checkbox – stav AKTIVNÍ (ZAŠKRTNUTÝ):
a) lem – bílý, 1 pixel  
b) okraj – černý, 1 pixel  
c) pozadí – bílé  
d) písmo nebo symbol – černé  

Checkbox – stav NEAKTIVNÍ:
a) lem – červený, 1 pixel  
b) okraj – červený, 1 pixel  
c) pozadí – černé  
d) písmo nebo symbol – šedivé  

---

### 6.09.000 Klikatelná ikona – redundantní výpis stavů

Klikatelná ikona je nečervený interaktivní prvek, musí mít tři povinné stavy dle 6.02.

Klikatelná ikona – stav NORMÁLNÍ:
a) lem – bílý, 1 pixel  
b) okraj – černý, 1 pixel  
c) pozadí – černé  
d) písmo nebo grafika – bílé  

Klikatelná ikona – stav AKTIVNÍ:
a) lem – bílý, 1 pixel  
b) okraj – černý, 1 pixel  
c) pozadí – bílé  
d) písmo nebo grafika – černé  
Klikatelná ikona – stav NEAKTIVNÍ:
a) lem – červený, 1 pixel  
b) okraj – červený, 1 pixel  
c) pozadí – černé  
d) písmo nebo grafika – šedivé  

---

## 7.00.000 TABULKY, TABULKY SOUBORŮ A SEZNAMY

Pro tabulky jsou platná pouze níže uvedená pravidla (tato kapitola je uzavřená a nepřebírá jiné tabulkové varianty).

### 7.01.000 Základní vlastnosti

Standardní barvy tabulky jsou:
- a) lem – bílý, 1 pixel  
- b) okraj – černý, 1 pixel  
- c) písmo – bílé  
- d) pozadí – černé  

Tabulka je plně dynamická.

---

### 7.02.000 Zaoblení buněk

- horní levá buňka – zaoblený horní levý roh  
- horní pravá buňka – zaoblený horní pravý roh  
- dolní levá buňka – zaoblený dolní levý roh  
- dolní pravá buňka – zaoblený dolní pravý roh  

Ostatní buňky zaoblení nemají.

---

### 7.03.000 Sloupce a řádky

- Šířku sloupců lze měnit tažením.
- Výšku řádků nelze měnit.
- Levá i pravá hrana tabulky je pevně spojena s lemem sekce.

---

### 7.04.000 Text a výběr

- Hlavičky sloupců:
  - Bold,
  - VŠE VELKÝMI PÍSMENY.
- Text v buňkách:
  - Regular,
  - standardní velikost.
- Vybraná řádka:
  - bílé pozadí,
  - černý text.
- Pokud není řečeno jinak, je povolen vícenásobný výběr.

---

### 7.05.000 Tooltipy a kopírování

- Po 2 sekundách nehybného kurzoru:
  - tooltip s plným obsahem buňky,
  - černý text na bílém pozadí.
- Obsah tabulky lze vždy kopírovat pomocí CTRL+C.

---

## 8.00.000 BAREVNÉ STAVY – TABULKOVÝ KONTRAKT (GLOBÁLNÍ)

Tato kapitola je globální kontrakt a je nadřazená lokálním popisům.

### 8.01.000 Kontrakt stavů pro nečervené interaktivní prvky (3 stavy)

| STAV (NEČERVENÉ) | LEM              | OKRAJ            | PÍSMO / SYMBOL | POZADÍ |
|------------------|------------------|------------------|----------------|--------|
| NORMAL           | bílý, 1 pixel    | černý, 1 pixel   | bílé           | černé  |
| ACTIVE           | bílý, 1 pixel    | černý, 1 pixel   | černé          | bílé   |
| DISABLED         | červený, 1 pixel | červený, 1 pixel | šedivé         | černé  |

Výklad:
- NORMAL = normální / připravený / vypnutý
- ACTIVE = aktivní / vybraný / zapnutý
- DISABLED = neaktivní / nedostupný / nepoužitelný

---

### 8.02.000 Kontrakt stavů pro červené (kritické) prvky (2 stavy)

| STAV (ČERVENÉ) | LEM              | OKRAJ          | PÍSMO / SYMBOL | POZADÍ  |
|----------------|------------------|----------------|----------------|---------|
| NORMAL         | červený, 1 pixel | černý, 1 pixel | černé          | červené |
| ACTIVE         | červený, 1 pixel | černý, 1 pixel | červené        | černé   |

Výklad:
- Červený prvek nemá DISABLED stav.
- Červený prvek používá pouze NORMAL a ACTIVE.

---

### 8.03.000 Závazná pravidla přechodů stavů

Pro všechny prvky:
- přechod mezi stavy nesmí měnit rozměry prvku,
- přechod mezi stavy nesmí měnit pozici prvku,
- přechod mezi stavy nesmí měnit layout,
- přechod mezi stavy mění pouze barvy dle kontraktu.

---

KONEC DOKUMENTU

## 2) Implementační aplikace DESIGN MANIFESTU na „KÁJU“

1) Základní princip: vše, co je v dalších kapitolách popsané jako „UI“, „tlačítko“, „sekce“, „dialog“, „tabulka“, „seznam“, „status“, „progress“ apod., se musí realizovat v souladu s DESIGN MANIFESTEM.

2) Klasifikace prvků (monolit/biolit/triolit) – praktická aplikace:
- Monolit: celé okno aplikace; záhlaví; hlavní pracovní plocha (workspace); samostatná okna (SETTINGS, CENY).
- Biolit: jednotlivé sekce/karty na hlavní pracovní ploše; skupiny v rámci SETTINGS/CENY; progress dialog.
- Triolit: konkrétní komponenty uvnitř sekcí (tlačítka, checkboxy, dropdowny, tabulky, textová pole, ikonky koše, progress bar).

3) Textová pole (vstup i výstup):
- Textová pole jsou interaktivní prvky. Musí respektovat stavy dle kontraktu (NORMAL/ACTIVE/DISABLED).
- Pro čitelnost je povoleno, aby multiline pole určené pro „ZADÁNÍ“ a „ANSWARE“ bylo ve výchozím stavu stylované jako ACTIVE (bílé pozadí + černý text), protože jde o přípustnou kombinaci v rámci černobílého systému. DISABLED stav se použije pouze tehdy, když je pole skutečně nedostupné.

4) Záhlaví programu:
- Musí obsahovat přesně tři povinné části dle DESIGN MANIFESTU: název+verze, řádek s ovládacími prvky (vlevo) + EXIT (vpravo), a stavový řádek (čas/datum + progress při běhu).
- Popisy tlačítek v kapitole 3) určují „jaká tlačítka existují“; DESIGN MANIFEST určuje „jak vypadají a jaké mají stavy“.

5) Sekce/karty:
- Názvy sekcí se nesmí centrovat; musí být realizované jako součást horního lemu sekce, zarovnané vlevo, dle přesné konstrukce v DESIGN MANIFESTU.
- Zaoblení: žádné ostré rohy v žádné vrstvě UI.

6) Responzivita / změna velikosti okna:
- UI se škáluje poměrově.
- Obsah se nesmí automaticky přeskupovat (žádný průběžný auto-reflow). Požadavek 1–3 sloupců z kapitoly 3.4 je řešen layout presetem; při resize se prvky škálují.

7) Stavový řádek vs. progress dialog:
- Stavový řádek je „always-on“ indikace stavu (idle vs. running).
- Progress dialog (teploměr) je detailní průběhový dialog pro dlouhé operace dle kapitoly 1.1 a zároveň musí vizuálně odpovídat DESIGN MANIFESTU.

## 3) KONSOLIDOVANÉ MASTER ZADÁNÍ PROGRAMU (NORMATIVNÍ)

# MASTER ZADÁNÍ: Desktopový program „Kája" (Windows) pro automatizaci requestů na OpenAI (Responses API) + automatické zpracování odpovědí {#master-zadání-desktopový-program-kája-windows-pro-automatizaci-requestů-na-openai-responses-api-automatické-zpracování-odpovědí}

Jsi senior programátor. Všechny programy, které píšeš jsou funkční a
plně provozuschopné. Programy, které píšeš jsou robustní natolik, že
jsou ošetřeny pro většině situací, kdy by mohli spadnout nebo zamrznout.
Všechny tvoje programy musí tvořit detailní logování a to natolik
detailní, že při eventuální chybě, nebo problému je ihned v kombinaci s
projevem chyby identifikovat co je za problém. Program musí být stavěn
tak, že pokud nejsou nutné vstupy k dispozici musí na to být jejich
uživatel upozorněn. Všechny možnosti a komponenty v programu jsou
realizovány tak, aby nemohl uživatel ani takové kombinace zadat. Pokud
nějaká operace v programu trvá více než 3-5 sekund zavedeš v programu
Pop Up okno ve kterém informuješ uživatele o tom co se děje a předcházíš
tomu, aby program vytuhnul, nebo se tak tvářil.

Vygeneruj desktopový program s názvem **„Kája"**, který bude
**automatizovat requesty na OpenAI** (Responses API) a **zpracovávat
odpovědi** podle tohoto zadání. Program bude fungovat jako **detailní
ovládací panel**, kde uživatel nastaví očekávání, vstupy, režim, model a
zpracování odpovědí. Po spuštění requestu se provede **automatická sada
kroků** definovaná volbami v UI.

**Důležité:** V tomto zadání je záměrně redundance. Nesmíš vynechat
žádný detail ani když je redundantní.


- **Fonty (TTF):**
  - resources/montserrat_bold.ttf (Montserrat Bold)
  - resources/montserrat_regular.ttf (Montserrat Regular)

Chování: - Pokud některý z povinných souborů chybí, uživatel musí dostat
jasné hlášení + program musí pokračovat v degradovaném režimu.

## 1) Nezbytné vlastnosti a zásady {#nezbytné-vlastnosti-a-zásady}

### 1.1 Robustnost {#robustnost}

- Program musí být **robustní** a **nikdy nesmí spadnout**.
- Veškeré procesy musí být **detailně zobrazovány** ve vyskakovacím
  dialogu:
  - průběžné logování kroků
  - odhad zbývajícího času (ETA)
  - procentuální průběh (0--100 %) pro celý krok i sub-kroky
- UI se nesmí blokovat: síťové operace, uploady, pollingy, kopírování
  stromu adresářů, zipování bundle apod. poběží na pozadí.

### 1.2 Logování {#logování}

- V adresáři spuštění programu vytvoř složku **LOG/** (pokud
  neexistuje).
- Každý běh ("run") má vlastní **Run ID** (např.
  `RUN_<DDMMRRRRHHMM>_<random4>`).
- Každý request a response se uloží jako **samostatný soubor** do LOG/.
- Název log souboru musí obsahovat:
  - **Název projektu** (pokud je vyplněn)
  - **ResponseID** (nebo BatchID / C_RUN_ID / RUN_ID)
  - časový kód **DDMMRRRHHMM** (čas) -- přesně v názvu souboru

Povinné artefakty v LOG (per run): - kompletní request JSON (odeslaný)
-- *samostatný soubor* - kompletní response JSON (přijatý) --
*samostatný soubor* - kompletní "UI state" (co bylo vyplněno a zvoleno)
-- *samostatný soubor* (a zároveň embed do request logu, aby šel použít
pro LOAD REQUEST) - manifesty: - mirror manifest (IN mirror) -
diagnostické manifesty (Windows/SSH snapshot) - výstupní mapa uložených
souborů (co se uložilo kam) - stavové logy kroků: uploady, pollingy,
validace, retry, backoff, cancel

Logovat se musí navíc detailně: - seznam všech souborů, které program: -
přidal (nově vytvořil) - přepsal - smazal (lokálně nebo na File API) -
přesunul / zkopíroval - vytvořil adresář - u každé této změny: - časové
razítko - původní cesta + cílová cesta - velikost před/po (pokud
existuje) - hash (např. SHA256) před/po, pokud je to rozumné (u velkých
souborů volitelně) - u uploadů na File API: - lokální path - file_id -
purpose - velikost - timestamp uploadu - u mazání na File API: -
file_id - původní jméno (pokud dostupné) - timestamp

Batch logování: - vstupní JSONL - výstupní JSONL - error JSONL -
mapování `custom_id → path` (pokud je použito) - stavový průběh jobu
(polling snapshots)

Skripty (pouze pokud jsou vyžádány diagnostikou OUT a přijdou v
response): - `readmerepair.txt` - skripty - log spuštění skriptu
(stdout/stderr) - návratové kódy - záznam o potvrzení uživatele před
spuštěním

### 1.3 Kontrola logiky kombinací {#kontrola-logiky-kombinací}

Program musí kontrolovat, že zvolené kombinace nastavení jsou přípustné.
Nesmí odeslat request v neplatné kombinaci. Chyba se musí zobrazit
uživateli jasně a s návrhem opravy.

### 1.4 Cenová evidence a nacenění (důraz na přesnost) {#cenová-evidence-a-nacenění-důraz-na-přesnost}

Program musí implementovat: - přesné sledování cen za jednotlivé
requesty i batch joby - přesná evidence nákladů na: - input tokens -
output tokens - Batch (výsledná cena musí reflektovat Batch pricing) -
file_search a Vector store náklady (tool + storage) - důraz na přesnost
a aktuálnost ceníku

V UI musí existovat samostatná obrazovka pro ceny pod tlačítkem **„\$"**
(v záhlaví vedle tlačítka API-KEY). Na hlavní ploše programu se ceny
nezobrazují a neovlivňují workflow; ceny se řeší pouze v této samostatné
obrazovce.

**Elektronická účtenka**: - pro každý běh vzniká "účtenka" (detailní
rozpad položek) a ukládá se do lokální databáze (SQLite) +
exportovatelný JSON v LOG. - účtenky musí být filtrovatelné podle data,
projektu, modelu, režimu, typu (A/B/QA/C), obsahu zadání (fulltext),
ResponseID/BatchID. - musí být možné mazat, exportovat, sumarizovat za
období.

Aktualizace ceníku: - program musí podporovat lokální cache "price
table" + ruční refresh z oficiálních podkladů (konfigurovatelné v
SETTINGS). - program musí podporovat i automatický refresh při startu
(pokud je v SETTINGS zapnuto). - pokud program nemá aktuální ceny,
musí: - jasně upozornit (banner/popup) - umožnit pokračovat, ale
"účtenka" musí být označena jako "odhad / neověřeno" (explicitně).

## 2) Technologie a runtime požadavky (implementuj stabilně) {#technologie-a-runtime-požadavky-implementuj-stabilně}

- Program musí být připaven pro provoz na Windows 10 a Windows 11.
- Program jako takový vždy poběží jen na Windows a lokálním PC.
- UI musí být stabilní, s podporou dlouhých běhů a background operací
  (neblokovat UI).
- Použij „standardní OpenAI SDK knihovnu" (Python nebo JS). Implementace
  musí být plně funkční.

Komunikace s OpenAI: - Responses API pro generování (s
previous_response_id pro řetězení) -- pro A/B/QA. - Files API pro
upload/list/delete. - Models endpoint pro list modelů. - Vector store +
file_search (pokud je zvolen IN režim a model to podporuje). - Batch API
-- pro režim C a pro sledování batch jobů.

Důležité: - Program musí umět detekovat capabilities modelu a podle
toho: - **nepoužít** nepodporované tooly (zejména file_search) -
přepnout se do fallback režimu dle pravidel (A3.1) pouze tam, kde je
fallback definovaný a bezpečný.

## 3) Start aplikace, okno a automatická inicializace {#start-aplikace-okno-a-automatická-inicializace}

### 3.3 Hlavní okno {#hlavní-okno}

- Program se musí spustit **v maximalizovaném okně** na **hlavním
  monitoru**.
- přes celý program:
  - nesmí bránit ovládání. Zakázané jsou trvalé blokující overlaye; modální dialogy jsou povolené pouze tam, kde jsou v zadání explicitně vyžádané (např. potvrzení, progress), a UI se při nich nesmí „zaseknout“.

### 3.4 Jedna pracovní plocha, responsivní rozvržení do 1--3 sloupců {#jedna-pracovní-plocha-responsivní-rozvržení-do-13-sloupců}
- hlavní plocha je jedna scrollovatelná pracovní plocha ("workspace").
- všechny sekce existují jako "karty/sekce" na této ploše.

**Dynamika a rozvržení (musí být v souladu s DESIGN MANIFESTEM):**
- UI je plně dynamické a škáluje se poměrově.
- Při změně velikosti okna se **nesmí** automaticky měnit pořadí ani pozice sekcí (žádné automatické přeskupování obsahu).
- Požadavek rozvržení do 1–3 sloupců se realizuje jako **layout preset** (1/2/3 sloupce) se **stabilním pořadím sekcí**, který:
  - je možné zvolit uživatelem (např. volba v SETTINGS nebo v UI),
  - a/nebo je jednorázově zvolen při startu podle šířky okna (bez průběžného auto-reflow při resize).
- Sekce musí být uživatelsky měnitelné na šířku i na výšku (splittery/dock layout), bez pevných rozměrů, pokud to není technologicky nutné.

**Scrollování:**
- horizontální scroll na úrovni celé plochy se nepoužívá;
- horizontální scroll pouze v konkrétních multiline polích, kde je explicitně požadován.


### 3.5 Automatická inicializace po startu {#automatická-inicializace-po-startu}

Po startu aplikace program:

1) Rychle zkontroluje, zda existuje nedokončený run v LOG/ (viz 17.A2). Pokud existuje, nabídne uživateli „RESUME LAST RUN“ co nejdřív (ještě před dokončením inicializace). Tato volba nesmí být blokována probíhající inicializací.

2) Automatickou inicializaci provede na pozadí (s progress dialogem) a bez blokování UI. Iniciační kroky:
- načtení aktuálního seznamu **OpenAI modelů** (pro uložený API key)
- načtení aktuálního seznamu souborů na **Files API**
- načtení aktuálního seznamu existujících **Vector Stores**
- načtení stavu všech rozpracovaných **Batch jobů** a jejich zobrazení v Batch monitoru

Pokud API key chybí, místo toho zobrazí jasnou informaci, že automatická inicializace není možná, a nabídne uživateli otevřít dialog API-KEY.

## 4) Záhlaví (toolbar) -- tlačítka a chování {#záhlaví-toolbar-tlačítka-a-chování}

Záhlaví musí být realizováno v souladu s DESIGN MANIFESTEM (kapitola 1 tohoto dokumentu), tj. povinně obsahuje:

a) **Název programu + verze** (samostatný řádek, vycentrovaný blok, VŠE VELKÝMI PÍSMENY, verze ve formátu `v0.00`).  
b) **Konfigurační ovládací prvky vlevo + EXIT vpravo** (na jednom řádku).  
c) **Stavový řádek** (čas, datum, a při běhu procesu i progress „teploměr“, ETA, %, aktuální krok).

Níže jsou vyjmenované povinné ovládací prvky v části (b).

V záhlaví obrazovky budou tlačítka:

### Vlevo:

1.  **API-KEY**
2.  **\$** (CENY / ÚČTENKY / CENÍK)
3.  **SETTINGS**
4.  **SAVE**
5.  **LOAD**
6.  **LOAD REQUEST**

### Vpravo:

7.  **EXIT**

## 5) Dialog „API-KEY" {#dialog-api-key}

Po stisknutí **API-KEY** se otevře vyskakovací dialog s: - **dlouhá
řádka** (jednořádkové pole), kam lze napsat API key pro OpenAI

Pod řádkou budou volby (tlačítka):

### 5.1 Uložit {#uložit}

- Uloží API key do **systémových proměnných dat** (system environment
  variables).
- Po uložení musí být program schopen key používat bez restartu
  (aktuální běh).

### 5.2 Zobraz {#zobraz}

- Ukáže viditelně v řádku API key, pokud je uloženo v systémových
  proměnných.

### 5.3 Smazat {#smazat}

- Smaže uložené API key ze systémových proměnných.

### 5.4 STORNO {#storno}

- Zavře okno beze změn.

## 6) SETTINGS {#settings}

Tlačítko SETTINGS otevře samostatné okno (mimo hlavní pracovní plochu).
SETTINGS je určeno pouze pro nastavení chodu programu, nikoliv pro
plnění funkce requestu a jejich automatického zpracování.

SETTINGS musí obsahovat minimálně: - lokace lokální databáze (default v
adresáři programu) - limity logování (rotace / max velikost / max počet
runů) - politika retry/backoff (limity, jitter, max pokusů, circuit
breaker) - ceník: zdroj (URL / lokální), refresh, cache TTL,
auto-refresh při startu - bezpečnost: - volitelné maskování tajemství v
logu (default: OFF, ale varování musí existovat) - volitelné šifrování
logů (default OFF) - panic wipe lokální cache (tlačítko) - Batch polling
interval a timeouty - výchozí model a defaultní teploty dle politiky -
povolení/konfigurace post-run hooks (lokálně/SSH)

## 7) \$ (CENY) -- samostatná obrazovka {#ceny-samostatná-obrazovka}

Tlačítko **\$** otevře samostatnou obrazovku s:

### 7.1 Přehled ceníku {#přehled-ceníku}

- tabulka cen per model:
  - input token
  - output token
  - batch pricing (pokud relevantní)
  - tool náklady (file_search)
  - storage náklady (vector store)
- datum poslední aktualizace
- tlačítko "REFRESH CENÍK"
- možnost nastavit zdroj ceníku a TTL (odkaz do SETTINGS)

### 7.2 Účtenky (evidence) {#účtenky-evidence}

- filtrování:
  - datum od-do
  - projekt
  - model
  - režim (GENERATE/MODIFY/QA/C)
  - ResponseID / BatchID
  - textový fulltext (v zadání / notes)
- detail účtenky:
  - rozpad tokenů a ceny
  - rozpad tool/storage nákladů
  - čas běhu, počty requestů, počty souborů
  - příznak „odhad / neověřeno" pokud nebyl ceník aktuální
- akce:
  - export (JSON / CSV)
  - smazat vybrané
  - sumarizace za období

### 7.3 Vazba na LOG {#vazba-na-log}

- každá účtenka musí obsahovat přímý odkaz na příslušné LOG soubory (na
  disk, lokální path).

## 8) EXIT -- potvrzení ukončení {#exit-potvrzení-ukončení}

Po stisknutí **EXIT**: - Zobrazí se potvrzovací dialog s upozorněním, že
uživatel přijde o neuloženou práci, pokud nedal **SAVE**. - Pokud
uživatel potvrdí, program se ukončí. - Pokud nepotvrdí, vrátí se do
programu.

## 9) SAVE / LOAD / LOAD REQUEST (persistování stavu) {#save-load-load-request-persistování-stavu}

### 9.1 SAVE {#save}

- Uloží rozpracovanou mapu nastavení tak, jak je v danou chvíli zvolena.
- Po stisknutí se zobrazí výběr adresáře a jména souboru.
- Formát musí být **JSON**.
- Strukturu JSON určí program.
- Musí být uloženy všechny volby a stav UI.

### 9.2 LOAD {#load}

- Umožní vybrat uložený JSON soubor a nahrát nastavení obrazovky.
- Po načtení se UI přepne do stavu odpovídajícího uloženému souboru.

### 9.3 LOAD REQUEST {#load-request}

- Umožní vybrat request uložený v **LOG/**.
- Po načtení se v programu nastaví všechna zadání a dialogová okna
  explicitně identicky, jak byla nastavena a vyplněná při odeslání
  requestu.
- Uživatel může provést drobné úpravy a odeslat znovu.

Pravidla: - Funkčně je LOAD REQUEST stejné jako LOAD, rozdíl je pouze v
tom, odkud se stav bere: - LOAD = soubor uložený tlačítkem SAVE - LOAD
REQUEST = request log z LOG, který obsahuje embednutý UI state a
technické vazby - LOAD REQUEST musí obnovit i technické vazby (model,
režim, IN/OUT, attached file-id listy, vector_store_id, batch_id,
response_id chain), ale pro nový běh se musí správně oddělit "historické
ID" od "nových volání".

## 10) Sekce na hlavní ploše (karty/sekce) {#sekce-na-hlavní-ploše-kartysekce}

Všechny níže uvedené sekce musí existovat. Jejich vizuální rozmístění je
dynamické (responsivní) podle šířky okna.

### 10.1 Sekce „Zadání" {#sekce-zadání}

Obsah: - Textový řádek (jednořádkové pole) s názvem: **„Název
projektu:"** - není povinné - je-li zadán, použije se ve všech
requestech jako identifikátor - Dialogové okno pro zadání (multiline): -
zobrazení cca **6 řádků** - při více řádcích posuvníky **horizontálně i
vertikálně**

### 10.2 Sekce „Připojené soubory" {#sekce-připojené-soubory}

- Tabulka souborů / id-files souborů.
- Tabulka by měla být vysoká tak, aby byla standardně vidět zhruba **2
  soubory**. Pokud je souborů víc, použije se **vertikální posuvný
  válec**.
- Do tabulky lze přesunout soubory ze sekce FILE API.
- Tyto soubory:
  - lze odkazovat v promptu přes file-id
  - objeví se v instructions jako jednotlivé soubory (každý zvlášť)
  - zároveň se objeví automaticky v promptu jako input
  - budou označeny jako **„pro informaci"**
- U každého souboru v tabulce bude ikonka **koše**, kterou lze z této
  tabulky soubor odstranit.

### 10.3 Sekce „IN" {#sekce-in}

Obsah: - Tlačítko **„VSTUP"** - Vedle něj textové pole (zobrazí
kompletní PATH zvoleného adresáře)
Chování: - Po stisku „VSTUP" uživatel vybere libovolný adresář. - Do
textového pole se uloží kompletní PATH.

Funkce při spuštění requestu (až při GO): - Pokud je vybrán IN
adresář: - rekurzivně načti všechny soubory včetně podadresářů - vyjmi
adresáře: **venv**, **.venv**, **LOG** - navíc vyjmi versing snapshot
adresáře: - adresář, jehož název odpovídá patternu (tj. končí 12
číslicemi a začíná shodně názvem root adresáře) - všechny **kompatibilní
soubory pro File API** uploaduj na File API - vytvoř mirror manifest
(soubor) se všemi soubory + memo o neuploadovaných

#### 10.3.1 Model capability check + fallback {#model-capability-check-fallback}

Před použitím **file_search + vector store** musí program ověřit, zda
zvolený model podporuje: - file_search tool - práci s vector store
(vector_store_ids)

Kontrola musí být robustní a může být provedena kombinací: - metadata z
Models endpointu (pokud dostupná) - bezpečný „probe" request a detekce
chyb typu „tool not supported / invalid tool".

**Pokud model podporuje file_search + vector store:** - vytvoř vector
store - připoj všechny uploadované soubory do vector store s atributem
jejich plné původní PATH - připoj mirror manifest do vector store (aby
ve store byla i existence neuploadovaných)

**Pokud model NEpodporuje file_search + vector store (fallback):** -
**nepoužívej** vector store ani file_search tool - použij jen Files
API: - uploadni kompatibilní soubory na Files API - uploadni manifest na
Files API - v requestech se pak mirror řeší takto: - v instructions
uveď: - seznam všech input souborů včetně jejich původních PATH -
file_id pro každý uploadovaný soubor - explicitně uveď manifest jako
soubor (s file_id) - v input přilož všechny tyto soubory jako input_file
(včetně manifestu) - bez tools a bez vector_store_ids

**Důležitá redundance (platí VŽDY):** - I když je zapnuté file_search +
vector store, program musí redundantně poslat: - manifest i jako upload
na Files API (aby měl file_id) - file_id manifestu (a všech input
souborů) vypsat v instructions - a současně tyto soubory přiložit jako
input_file v input

Označení (název) vector store: - použij **název projektu** + čas ve
formátu **DDMMRRRRHHMM**

### 10.4 Sekce „OUT" {#sekce-out}

Obsah: - Tlačítko **„IN=OUT"** - Tlačítko **„Výstup"** - Tlačítko
**„VERSING"** - Textové pole (výstupní PATH)

Chování: - „Výstup": vybere se adresář pro ukládání souborů přijatých v
Response. - „IN=OUT": - nastaví výstupní adresář na stejný jako
vstupní - aktivuje možnost stisknutí tlačítka **VERSING** - Ukládání
souborů: - do zvoleného OUT adresáře se uloží soubory přijaté v
Response - pokud ve stejném PATH existuje soubor stejného jména, **bez
upozornění se přepíše**

VERSING -- funkce: - Pokud je aktivní VERSING a přijde response alespoň
s jedním souborem, který se má uložit do OUT: - před prvním zápisem
program vytvoří ve zvoleném pracovním adresáři snapshot kopii aktuálního
stavu - snapshot adresář se vytvoří **uvnitř pracovního adresáře** -
název snapshot adresáře je

Příklad: - Projekt ABC je v adresáři `D:\PROJEKTY\ABC\`. - V adresáři
`D:\PROJEKTY\ABC\` jsou např. `.venv`, `LOG`, `app`, `data`, ... - Při
vytvoření nové verze se snapshot uloží do
`D:\PROJEKTY\ABC\ABC171220251634\`.

Pravidla kopírování při VERSING: - kopíruje se kompletní struktura
pracovního adresáře, **kromě**: - `venv`, `.venv`, `LOG` - a kromě všech
adresářů, které odpovídají versing konvenci - a samozřejmě kromě právě
vytvářeného snapshot adresáře - snapshot adresáře se považují za versing
a proto se **nikdy** nezahrnují do IN mirroru ani do manifestu.

### 10.5 Sekce „DIAGNOSTICS (WINDOWS / SSH)" {#sekce-diagnostics-windows-ssh}

V této sekci jsou volby: - **WINDOWS IN** (checkbox) - **WINDOWS OUT**
(checkbox) - **SSH IN** (checkbox) - **SSH OUT** (checkbox)

Zakázané kombinace: - Jakákoliv kombinace **WINDOWS** s **SSH** je
zakázána (tj. nelze mít současně žádný WINDOWS checkbox a žádný SSH
checkbox).

Povolené kombinace v rámci jedné skupiny: - WINDOWS IN může být společně
zvolena s WINDOWS OUT - SSH IN může být společně zvolena s SSH OUT

Vynucení závislostí (tiše):
- pokud je zvolen **WINDOWS OUT**, musí být zvolen **WINDOWS IN** (program automaticky zaškrtne WINDOWS IN)
- pokud je zvolen **SSH OUT**, musí být zvolen **SSH IN** (program automaticky zaškrtne SSH IN)

**Výjimka pro tok C (SEND AS C (BATCH)):**
- protože tok C nemá IN, volby **WINDOWS IN** a **SSH IN** jsou v toku C zakázané (DISABLED)
- v toku C je povoleno zvolit **WINDOWS OUT** nebo **SSH OUT** i bez příslušné IN volby (nevynucuje se OUT→IN), při zachování ostatních pravidel (nelze kombinovat WINDOWS a SSH, a OUT volby vyžadují vybraný OUT adresář)

Závislosti na výběru adresářů: - WINDOWS IN nebo SSH IN lze použít
jedině pokud je zvolen **IN adresář** - WINDOWS OUT nebo SSH OUT lze
použít jedině pokud je zvolen **OUT adresář**

Pokud uživatel zaškrtne volbu, která je v rozporu s výběrem adresářů,
program: - jasně zobrazí, co chybí (např. „Pro WINDOWS IN vyber IN
adresář") - a zablokuje GO, dokud nebude stav validní

Funkce: - **WINDOWS IN / SSH IN** - při spuštění „KÁJO GO'": - WINDOWS
IN: provede snímek kompletního nastavení Windows (Přesná specifikace "diagnostický balík" dle specifikace v příloze: "PŘÍLOHA FULL Windows Diagnostics.md")
SSH IN: po zadání IP adresy a autentizace, popřípadě jsou-li uloženy v sekci "NASTAVENÍ", automaticky stáhne
diagnostický snímek vzdáleného systému - (Přesná specifikace "diagnostický balík" dle specifikace v příloze: "PŘÍLOHA FULL Ubuntu (Web Server) Diagnostics.md")
(diagnostický balík), která se: - nahraje na Files API - zaznamená do
manifestu (včetně popisu obsahu a timestampů) - file_id se zapíše do
instructions - a zároveň se přiloží do input jako input_file části -
pokud je aktivní vector store, diagnostické soubory se navíc připojí do
vector store s atributy (např. `source=diagnostics`,
`scope=windows|ssh`, `captured_at=...`).

- **WINDOWS OUT / SSH OUT**
  - při spuštění „KÁJO GO'" program do instructions i do input
    redundantně zapíše očekávání, že výstup musí obsahovat:
    - vlastní skript
    - soubor **readmerepair.txt** s popisem změny systému a návodem k
      ručnímu použití
  - pro SSH OUT je skript **spustitelný na Windows PC** (tj. skript je
    připraven tak, aby z Windows provedl změny na vzdáleném SSH pomocí
    stejného typu přístupu, který byl použit při SSH IN).

Bezpečnostní upozornění: - diagnostické snapshoty mohou obsahovat
citlivá data; program musí před prvním použitím WINDOWS/SSH diagnostiky
zobrazit varování a vyžádat potvrzení. - pokud je v SETTINGS maskování
tajemství OFF, program upozorní, že citlivé údaje mohou skončit v LOG.

SSH UI (pokud je zvoleno SSH IN nebo SSH OUT): - program se zeptá na: -
uživatelské jméno (výchozí root) - IP adresu - autentizace: SSH key
(povinně podporovat; heslo volitelně jako fallback) - sudo se nepoužívá,
jen root.

### 10.6 Sekce „MODE" {#sekce-mode}

Obsah: - Tlačítko **„GENERATE"** - Tlačítko **„MODIFY"** - Tlačítko
**„QA"** - Pole **RESPONSE ID** (textové pole)

Pravidla: - Může být zvoleno vždy jen jedno z tlačítek
(GENERATE/MODIFY/QA). - Alespoň jedno musí být zvoleno vždy.

Režimy: - **GENERATE** - nesmí být zvolen IN adresář - musí být zvolen
OUT adresář

- **MODIFY**
  - musí být zvolen IN i OUT adresář
- **QA**
  - nesmí být zvolen ani IN ani OUT adresář
  - do instructions i do input se dá instrukce, že se čeká **textová
    odpověď**, žádný soubor

RESPONSE ID: - Umožňuje zadat Response-ID ručně. - Je-li vyplněno: -
použije se v requestu jako řetězení (previous_response_id). - Není-li
vyplněno: - request začne jako nový (bez previous_response_id).

### 10.7 Sekce „Model OpenAI" {#sekce-model-openai}

Obsah: - Tlačítko **„GET MODELS"** - Roletka (dropdown) pro výběr OpenAI
modelu

Chování: - Po stisknutí „GET MODELS" se načtou aktuálně dostupné OpenAI
modely pro uložený API key. - Aktualizuje se seznam modelů ve
dropdown. - Vybraný model zůstává viditelný v roletce.

### 10.8 Sekce „BATCH MONITOR" {#sekce-batch-monitor}

Funkce: - seznam batch jobů (minimálně: "otevřené" = vše kromě
completed/failed/cancelled/expired) - tlačítko "REFRESH" - zobrazení
stavu a času vytvoření - tlačítko "DOWNLOAD RESULT" (pokud je hotovo) -
tlačítko "OPEN LOG" (link do LOG) - "CANCEL" (pokud API dovolí a
uživatel chce)

### 10.9 Sekce „GO" {#sekce-go}

Obsah: - Tlačítko **„KÁJO GO'"** - Přepínač **„SEND AS C (BATCH)"**

Chování: - Spustí kroky v pořadí podle nastavení a provede plně
automatické zpracování všeho, co je definováno na panelu. - Během běhu
se zobrazuje progress dialog (detailní kroky, %, ETA). - Vše se loguje
do LOG/.

### 10.10 Sekce „ANSWARE" {#sekce-answare}

Obsah: - Dialogové okno cca **6 řádků** - Nadpis dialogového okna bude
zobrazeno **Response ID** - V dialogovém okně se zobrazí odpověď z
response

Pod oknem tlačítka: - **CTRL+C** - **RESPONSE** - **SCRIPT**

CTRL+C: - zkopíruje obsah dialogového okna včetně Response ID do
schránky - vložení musí být jako neformátovaný text

RESPONSE: - zkopíruje přijaté Response ID do pole MODE/RESPONSE ID

SCRIPT: - je aktivní pouze pokud poslední response obsahovala skript +
`readmerepair.txt` - po stisknutí: - program zobrazí potvrzení s
varováním o nevratnosti - po potvrzení spustí skript bez dry runu - u
SSH skriptu použije stejné IP/uživatelské jméno/klíč nebo heslo, které
byly zadány při odesílání requestu (a program je drží jako součást run
state) - uživatel je informován o výsledku ve vyskakovacím okně - do LOG
se uloží stdout/stderr, návratový kód a audit provedených změn (pokud je
ze skriptu dostupný)

### 10.11 Sekce „LOCAL FILES" {#sekce-local-files}

Obsah: - tabulka souborů (cca 3--5 souborů, jinak scroll) - tlačítka pod
tabulkou: - **VLOŽ** - **UPLOAD**

Chování: - „VLOŽ": - uživatel vybere soubor - soubor se vloží do
tabulky - lze vybrat více souborů - každý řádek má ikonu pro smazání z
tabulky - „UPLOAD": - všechny soubory z tabulky uploaduj na File API s
purpose **"user data"** - po uploadu: - automaticky aktualizuj přehled
souborů v sekci FILE API - tabulka LOCAL FILES se vyprázdní

### 10.12 Sekce „FILE API" {#sekce-file-api}

Obsah: - tabulka souborů (cca 4 souborů, jinak scroll) - tlačítka pod
tabulkou: - **PŘIPOJ** - **SMAŽ** - **DEL ALL**

Chování: - Tabulka: - kliknutím lze vybrat více souborů (multi-select) -
„PŘIPOJ": - vybrané soubory se přesunou do sekce „Připojené soubory" -
„SMAŽ": - vybrané soubory smaž na File API - „DEL ALL": - smaž na File
API všechny soubory

### 10.13 Sekce „VECTOR STORES" {#sekce-vector-stores}

Funkce: - možnost se podívat, jaké aktuální vector store jsou založeny -
co v nich je - prohlížet si jejich obsah - nastavovat souborům ručně
atributy - jednotlivé soubory z vector store vyřazovat nebo zařazovat -
nastavovat expiraci

Povinné: - list vector store - detail vybraného store: - expirace
(view + update) - list souborů + jejich attributes - odstranit soubor ze
store - přidat soubor do store (z Files API) - zobrazení "usage /
velikost" (pokud API poskytuje) - vše logovat (co bylo změněno a kdy)

## 11) OpenAI request pipeline -- logika A/B variant + tok C (Batch-only) {#openai-request-pipeline-logika-ab-variant-tok-c-batch-only}

### 11.1 Základní pravidla request builderu (platí pro A/B/QA) {#základní-pravidla-request-builderu-platí-pro-abqa}

**Temperature policy:** - Jakmile je cílem vracet **obsah výstupního
souboru** (tj. kroky **A3_FILE** a **B3_FILE**), nastav temperature na
**0.0**. - Pro všechny ostatní requesty používej temperature v rozsahu
**0.0--0.2** (defaultně **0.2**, pokud není důvod snížit).

Redundance výstupu: - Vždy implementuj redundantní zadání očekávaného
výstupu: - (a) v instructions je kontrakt - (b) v input je redundantně
zopakovaný kontrakt

Projekt: - Pokud je vyplněn „Název projektu", použij ho jako
identifikátor v každém requestu (např. v instructions a v log
souborech).

Připojené soubory: - Všechny soubory v sekci „Připojené soubory": - musí
být v requestu: 1) vyjmenované v instructions jako „pro informaci"
(každý zvlášť) 2) a zároveň přiložené v input jako input_file části

Řetězení: - Pokud je vyplněn RESPONSE ID: - první request v daném běhu
použije previous_response_id = - pokud není vyplněn, nezačínej řetězení

Diagnostika (WINDOWS/SSH) -- redundance: - Pokud je aktivní WINDOWS IN /
SSH IN: - diagnostické soubory se posílají redundantně: - existence +
popis + file_id v instructions - a zároveň jako input_file v inputu - a
případně i ve vector store, pokud je aktivní - Pokud je aktivní WINDOWS
OUT / SSH OUT: - očekávání skriptu + `readmerepair.txt` se píše
redundantně: - do instructions - i do input

### 11.2 Volba varianty podle MODE {#volba-varianty-podle-mode}

- **GENERATE** → použij sérii **A1 → A2 → A3-X**
- **MODIFY** → použij sérii **B1 → B2 → B3-X** (protože IN vytváří
  mirror; primárně vector store + file_search, fallback dle 10.3.1)
- **QA** → pošli **1 request**, který v instructions i v input říká, že
  se čeká jen **textová odpověď, žádný soubor**, a nepoužije IN/OUT

### 11.3 Chunking pro soubory delší než 500 řádků (A/B) {#chunking-pro-soubory-delší-než-500-řádků-ab}

Pro A3/B3: - Pokud má výstup souboru více než 500 řádků: - musí se
vracet po chuncech - program musí iterovat requesty pro stejný path,
dokud soubor nebude kompletní - V requestu pro file content se bude
měnit jen path (a případně chunk_index).

## 12) Tok C (Batch-only, bez pipeline návazností, bez vstupních souborů, vše v jedné odpovědi) {#tok-c-batch-only-bez-pipeline-návazností-bez-vstupních-souborů-vše-v-jedné-odpovědi}

Požadavek: - C je vlastní nadefinovaný request, kde budou instructions
stejné obsahově, jako, když se posílá prompt pro generování programu,
ale bude naprosto separátně v programu sestavován a validován. - C je
jen přes BATCH (nikdy synchronně). - C nevyužívá A1/A2/A3 ani B1/B2/B3,
nemá řetězení, nemá previous_response_id. - C nepoužívá žádný vstupní
soubor: - žádný IN - žádné attached files - žádné file_search - žádné
vector_store_ids - C vrací v jedné odpovědi najednou všechny soubory. -
Jediné, co se využije ze stávající logiky, je zpracování přijatých
souborů (uložení do OUT, VERSING, logování, evidence cen).

### 12.1 UI a validace pro C {#ui-a-validace-pro-c}

Pokud uživatel zvolí "SEND AS C (BATCH)" - je to samostatný tok -
validace: - OUT musí být vybrán - IN nesmí být vybrán - připojené
soubory musí být prázdné - RESPONSE ID se nepoužívá - model musí být
zvolen

Poznámka k diagnostice:
- V toku C jsou volby diagnostiky IN zakázané (WINDOWS IN a SSH IN jsou DISABLED), protože C nemá IN.
- V toku C je povoleno použít diagnostiku OUT samostatně (WINDOWS OUT nebo SSH OUT) bez vynucení IN (výjimka z pravidla 10.5).
- Stále platí: nelze kombinovat WINDOWS a SSH; diagnostika OUT vyžaduje vybraný OUT adresář.
- Pokud je aktivní diagnostika OUT, C musí vrátit i skript + readmerepair.

### 12.2 C request kontrakt {#c-request-kontrakt}

C musí vyžadovat jediný výstupní JSON dokument: - žádné markdown
code-fences - žádné komentáře - žádné dodatečné vysvětlování mimo JSON

**KONTRAKT C_FILES_ALL:**

    {
      "contract": "C_FILES_ALL",
      "project": {
        "name": "string",
        "target_os": "Windows 10/11",
        "runtime": "string",
        "language": "string"
      },
      "root": "string",
      "files": [
        {
          "path": "relative/path/file.ext",
          "purpose": "string",
          "content": "string"
        }
      ],
      "build_run": {
        "prerequisites": ["string"],
        "commands": ["string"],
        "verification": ["string"]
      },
      "notes": ["string"]
    }

C request instructions musí obsahově odpovídat tomu, co jinak posíláš
jako prompt pro generování programu (včetně požadavků na robustnost,
logování, UI styl, atd.), ale C request builder je sestavuje samostatně.

Pokud je aktivní diagnostika OUT (WINDOWS OUT nebo SSH OUT): - C request
navíc explicitně vyžaduje, aby `files[]` obsahoval: -
`readmerepair.txt` - skript(y)

### 12.3 Batch implementace pro C {#batch-implementace-pro-c}

- vytvoř JSONL, který obsahuje právě 1 request (jedna řádka = jeden
  request na /responses)
- upload JSONL
- vytvoř batch job
- sleduj stav přes BATCH MONITOR
- po dokončení stáhni výsledek

Validace výsledku: - `json.loads()` - validace schématu C_FILES_ALL -
validace path pravidel: - relativní - nesmí začínat `/` - nesmí
obsahovat `..` - nesmí obsahovat `\\` - žádné duplicity

Pokud validace selže: - výstup se uloží do karantény `OUT/_invalid/` a
jasně se označí (v UI popup + log), a soubory se nezapíší do cílových
path.

### 12.4 Uložení souborů z C {#uložení-souborů-z-c}

- uložit všechny `files[]` do OUT
- pokud existuje stejný soubor, bez upozornění přepsat
- pokud je zapnutý VERSING, provést VERSING copy před prvním zápisem

## 13) Explicitní kontrakty (A/B) -- zachovat přesně (instructions + redundantní input) {#explicitní-kontrakty-ab-zachovat-přesně-instructions-redundantní-input}

Níže jsou přesné kontrakty pro 6 variant request JSON, které má „Kája"
generovat a posílat dle nastavení.

> Důležité: Kontrakty jsou postavené na instructions (bez text.format).
> Program musí odpovědi parsovat přes json.loads() a validovat.

### 13.0 Politika výstupů souborů (kritické) {#politika-výstupů-souborů-kritické}

- Pokud model generuje nebo modifikuje soubory, nikdy nesmí vracet
  DIFF/patch/změny.
- Očekává se kompletní výsledné znění souboru:
  - buď celé v jednom content, nebo (u chunkingu) po částech, které se
    po spojení stanou kompletním souborem.
- Žádné markdown code-fences, žádné komentáře, žádné dodatečné
  vysvětlování mimo JSON.

# 13A) A-varianta: neposílám jako vstup žádný soubor {#a-a-varianta-neposílám-jako-vstup-žádný-soubor}

## A1) Request JSON -- „PLAN (manifest / návrh projektu)" {#a1-request-json-plan-manifest-návrh-projektu}

- Bez file_search
- Bez vector store

<!-- -->

    {
      "model": "<MODEL_FROM_UI>",
      "temperature": 0.2,
      "instructions": "Jsi senior software architekt a implementátor. MASTER: žádné externí soubory. OUTPUT: VRAŤ POUZE validní JSON. ŽÁDNÝ markdown, žádné komentáře, žádný další text. KONTRAKT A1_PLAN: {\"contract\":\"A1_PLAN\",\"project\":{\"name\":string,\"one_liner\":string,\"target_os\":string,\"language\":string,\"runtime\":string},\"assumptions\":[string],\"requirements\":{\"functional\":[string],\"non_functional\":[string],\"constraints\":[string]},\"architecture\":{\"modules\":[{\"name\":string,\"responsibility\":string}],\"data_flow\":[string],\"error_handling\":[string],\"security_notes\":[string]},\"build_run\":{\"prerequisites\":[string],\"commands\":[string],\"verification\":[string]},\"deliverable_policy\":{\"file_generation_strategy\":\"PLAN->STRUCTURE->FILE_CONTENT\",\"max_lines_per_chunk\":500}}",
      "input": "ZADÁNÍ PROGRAMU: <USER_SPEC>. REDUNDANTNÍ KONTRAKT: vrať pouze JSON dle A1_PLAN (bez md, bez textu navíc)."
    }

## A2) Request JSON -- „STRUCTURE (výstup vlastní souborové struktury)" {#a2-request-json-structure-výstup-vlastní-souborové-struktury}

- Navazuje přes previous_response_id

<!-- -->

    {
      "model": "<MODEL_FROM_UI>",
      "previous_response_id": "<RESP_ID_FROM_A1_OR_USER_FIELD>",
      "temperature": 0.2,
      "instructions": "Jsi generátor projektové struktury podle schváleného plánu. OUTPUT: VRAŤ POUZE validní JSON. ŽÁDNÝ markdown ani další text. RULES: path musí být relativní, nesmí začínat '/', nesmí obsahovat '..' ani '\\\\', žádné duplicity. KONTRAKT A2_STRUCTURE: {\"contract\":\"A2_STRUCTURE\",\"root\":string,\"files\":[{\"path\":string,\"purpose\":string,\"language\":string,\"generated_in_phase\":\"A3\"}]}",
      "input": "VYGENERUJ FILE STRUCTURE pro projekt dle předchozího plánu. REDUNDANTNÍ KONTRAKT: vrať pouze JSON dle A2_STRUCTURE."
    }

## A3) Request JSON -- „FILE CONTENT (obsah 1 konkrétního souboru)" {#a3-request-json-file-content-obsah-1-konkrétního-souboru}

- Opakované volání pro každý path
- Chunking \> 500 řádků

<!-- -->

    {
      "model": "<MODEL_FROM_UI>",
      "previous_response_id": "<RESP_ID_FROM_A2_OR_USER_FIELD>",
      "temperature": 0.0,
      "instructions": "Jsi generátor obsahu jednoho konkrétního souboru podle A2_STRUCTURE. OUTPUT: VRAŤ POUZE validní JSON. ŽÁDNÝ markdown ani další text. KRITICKÉ: content je vždy čistý obsah souboru (ne DIFF, ne patch). U chunkingu posílej po částech, které se spojí do kompletního souboru. CHUNK: max 500 řádků v jednom chunku, dlouhé soubory vrať po částech. KONTRAKT A3_FILE: {\"contract\":\"A3_FILE\",\"path\":string,\"chunking\":{\"max_lines\":500,\"chunk_index\":integer,\"chunk_count\":integer,\"has_more\":boolean,\"next_chunk_index\":integer|null},\"content\":string}",
      "input": "Vrať obsah souboru PATH=<PATH_FROM_A2>. Pokud je dlouhý, použij chunking. Volitelně: CHUNK_INDEX=<N>. REDUNDANTNÍ KONTRAKT: vrať pouze JSON dle A3_FILE. KRITICKÉ: žádné DIFF/patch, jen čistý obsah souboru (nebo jeho chunk)."
    }

# 13B) B-varianta: posílám zrcadlo souborů / referenční soubory do vector store a zapnu file_search {#b-b-varianta-posílám-zrcadlo-souborů-referenční-soubory-do-vector-store-a-zapnu-file_search}

Pokud model nepodporuje file_search / vector store, v B-variantě se
vynechá tools a místo toho se použijí soubory přes Files API + manifest
dle 10.3.1.

## B1) Request JSON -- „PLAN (na základě mirroru)" {#b1-request-json-plan-na-základě-mirroru}

- file_search ON (pokud podporováno)
- vector_store_ids použij z IN kroku

<!-- -->

    {
      "model": "<MODEL_FROM_UI>",
      "temperature": 0.2,
      "tools": [
        { "type": "file_search", "vector_store_ids": ["<VS_ID_FROM_IN_STEP>"] }
      ],
      "instructions": "Jsi senior debug/maintenance inženýr. MASTER SOURCE OF TRUTH: existující soubory/config jsou pouze ve vector store přes file_search. Nic si nevymýšlej. KRITICKÉ: i když máš file_search, ber v úvahu i přiložený manifest + input file-id jako redundantní zdroj. OUTPUT: VRAŤ POUZE validní JSON. ŽÁDNÝ markdown ani další text. WORKFLOW: vždy nejdřív použij file_search, pokud něco chybí uveď missing_inputs. KONTRAKT B1_PLAN: {\"contract\":\"B1_PLAN\",\"context\":{\"vector_store_ids\":[string],\"assumed_root\":string},\"diagnosis\":{\"summary\":string,\"evidence\":[{\"path\":string,\"reason\":string}],\"likely_root_causes\":[string]},\"change_plan\":{\"goals\":[string],\"files_to_modify\":[{\"path\":string,\"intent\":string}],\"files_to_add\":[{\"path\":string,\"intent\":string}],\"verification_steps\":[string]},\"missing_inputs\":[string]}",
      "input": "MÁŠ PŘÍSTUP K MIRRORU V VECTOR STORE (file_search je zapnutý, pokud model podporuje). ÚKOL: <USER_TASK>. REDUNDANTNÍ KONTRAKT: vrať pouze JSON dle B1_PLAN."
    }

## B2) Request JSON -- „STRUCTURE (touched files)" {#b2-request-json-structure-touched-files}

- Navazuje přes previous_response_id

<!-- -->

    {
      "model": "<MODEL_FROM_UI>",
      "previous_response_id": "<RESP_ID_FROM_B1_OR_USER_FIELD>",
      "temperature": 0.2,
      "tools": [
        { "type": "file_search", "vector_store_ids": ["<VS_ID_FROM_IN_STEP>"] }
      ],
      "instructions": "Jsi implementátor změn nad existujícím systémem. MASTER: existující soubory a jejich aktuální obsah jsou pouze z vector store (file_search). KRITICKÉ: i když máš file_search, ber v úvahu i přiložený manifest + input file-id jako redundantní zdroj. OUTPUT: VRAŤ POUZE validní JSON. ŽÁDNÝ markdown ani další text. RULES: do touched_files nedávej nic, co neexistuje ve store (pokud to není nové). KONTRAKT B2_STRUCTURE: {\"contract\":\"B2_STRUCTURE\",\"touched_files\":[{\"path\":string,\"action\":\"modify\"|\"add\",\"intent\":string}],\"invariants\":[string]}",
      "input": "Na základě předchozího plánu a mirroru ve vector store vrať seznam souborů, které se budou měnit/přidávat. REDUNDANTNÍ KONTRAKT: vrať pouze JSON dle B2_STRUCTURE."
    }

## B3) Request JSON -- „FILE CONTENT (1 soubor)" {#b3-request-json-file-content-1-soubor}

- Opakované volání pro každý path
- Chunking \> 500 řádků
- Pro modify musí vycházet z aktuální verze ve store (file_search)

<!-- -->

    {
      "model": "<MODEL_FROM_UI>",
      "previous_response_id": "<RESP_ID_FROM_B2_OR_USER_FIELD>",
      "temperature": 0.0,
      "tools": [
        { "type": "file_search", "vector_store_ids": ["<VS_ID_FROM_IN_STEP>"] }
      ],
      "instructions": "Jsi implementátor obsahu jednoho konkrétního souboru. MASTER: pro modify vždy načti aktuální obsah souboru přes file_search a aplikuj změny. KRITICKÉ: content je vždy kompletní výsledné znění souboru (ne DIFF, ne patch). U chunkingu posílej po částech, které se spojí do kompletního souboru. OUTPUT: VRAŤ POUZE validní JSON. ŽÁDNÝ markdown ani další text. CHUNK: max 500 řádků v chunku. KONTRAKT B3_FILE: {\"contract\":\"B3_FILE\",\"path\":string,\"action\":\"modify\"|\"add\",\"chunking\":{\"max_lines\":500,\"chunk_index\":integer,\"chunk_count\":integer,\"has_more\":boolean,\"next_chunk_index\":integer|null},\"content\":string,\"notes\":[string]}",
      "input": "Vrať výsledný obsah souboru PATH=<PATH_FROM_B2> (ACTION=<modify|add>). Použij mirror ve vector store jako jediný zdroj pravdy pro existující verzi (pokud je dostupné). Pokud je dlouhý, vrať po chuncech. Volitelně: CHUNK_INDEX=<N>. REDUNDANTNÍ KONTRAKT: vrať pouze JSON dle B3_FILE. KRITICKÉ: žádné DIFF/patch, jen čistý obsah souboru (nebo jeho chunk)."
    }

## 14) GO -- exekuce kroků podle UI {#go-exekuce-kroků-podle-ui}

Po stisku „KÁJO GO'" proveď:

### 14.1 Validace nastavení {#validace-nastavení}

- MODE vybrán přesně jeden
- GENERATE: IN nesmí být vybrán, OUT musí být vybrán
- MODIFY: IN i OUT musí být vybrán
- QA: IN ani OUT nesmí být vybrán- C: OUT musí být vybrán, IN nesmí být vybrán, attached files musí být
  prázdné, běží jen přes Batch
- API key musí být dostupný (z uložených systémových proměnných nebo z
  dialogu)
- Diagnostics:
  - nelze kombinovat WINDOWS a SSH
  - Pro A/B/QA:
    - IN volby vyžadují vybraný IN adresář
    - OUT volby vyžadují vybraný OUT adresář
    - OUT volby si automaticky vynutí příslušnou IN volbu
  - Pro tok C (SEND AS C (BATCH)):
    - IN volby diagnostiky jsou zakázané (DISABLED)
    - OUT volby vyžadují vybraný OUT adresář
    - OUT volby nevynucují IN (výjimka z 10.5)

### 14.2 Připojené soubory (informational) -- pouze A/B/QA {#připojené-soubory-informational-pouze-abqa}

- Sestav seznam „Připojených souborů" pro instructions + input
- Tyto soubory přidej do každého requestu jako:
  - textový blok v instructions (pro informaci)
  - content parts input_file v inputu

### 14.3 Diagnostika IN (WINDOWS IN / SSH IN) -- pokud je zvoleno {#diagnostika-in-windows-in-ssh-in-pokud-je-zvoleno}

- Vygeneruj diagnostický balík:
  - WINDOWS IN: snapshot Windows - Viz příloha # PŘÍLOHA FULL Windows Diagnostics
  - SSH IN: snapshot vzdáleného systému # PŘÍLOHA FULL Ubuntu (Web Server) Diagnostics

- Uploadni diagnostické soubory na Files API
- Zapiš je do diagnostického manifestu + do mirror manifestu (jako
  externí artefakty s popisem)
- Přilož je redundatně:
  - v instructions vypiš file_id + popis
  - v input je přilož jako input_file
  - pokud existuje vector store, připoj je i do store

### 14.4 IN krok (pouze když je IN zvolen) -- pouze MODIFY {#in-krok-pouze-když-je-in-zvolen-pouze-modify}

- Rekurzivně projdi vstupní adresář (mimo venv, .venv, LOG a mimo
  versing snapshot adresáře dle 10.3)
- Uploadni kompatibilní soubory na Files API
- Vytvoř mirror manifest se všemi soubory + memo o neuploadovaných
- Ověř podporu file_search + vector store pro zvolený model
- pokud podporuje:
  - Vytvoř vector store pojmenovaný dle 10.3.1: **<NÁZEV_PROJEKTU> + DDMMRRRRHHMM** (pokud „Název projektu“ není vyplněn, použij fallback `PROJECT`).
  - Připoj všechny uploadované soubory do vector store s atributem
    jejich plné původní PATH
  - Připoj mirror manifest do vector store
  - pokud jsou k dispozici diagnostické soubory, připoj i je
- pokud nepodporuje:
  - nepoužívej vector store, nepoužívej file_search
  - používej jen Files API a manifest (viz 10.3.1)

### 14.5 Očekávání skriptu (WINDOWS OUT / SSH OUT) -- pokud je zvoleno {#očekávání-skriptu-windows-out-ssh-out-pokud-je-zvoleno}

- Do instructions i do input přidej povinné očekávání:
  - response musí obsahovat skript(y)
  - response musí obsahovat `readmerepair.txt`
- Po zpracování response:
  - `readmerepair.txt` se zobrazí v ANSWARE okně
  - aktivuje se tlačítko SCRIPT

### 14.6 Request pipeline podle režimu {#request-pipeline-podle-režimu}

- Pokud je zvoleno "SEND AS C (BATCH)": tok dle kapitoly 12.
- Jinak:
  - GENERATE: A1 → A2 → pro každý file v A2: A3 (chunk loop) → ukládat
    do OUT
  - MODIFY: B1 → B2 → pro každý touched file v B2: B3 (chunk loop) →
    ukládat do OUT
  - QA: 1 request: text-only (v instructions i input explicitně), bez
    ukládání souborů

### 14.7 OUT ukládání {#out-ukládání}

- Pokud je aktivní VERSING a přijde alespoň jeden soubor k uložení:
  - udělej snapshot kopii dle pravidel v 10.4
- Ukládej soubory:
  - bez upozornění přepisuj existující stejné soubory

### 14.8 ANSWARE panel {#answare-panel}

- Zobraz Response ID v titulku
- Zobraz odpověď (raw nebo extrahovaný text/JSON) v okně
- CTRL+C kopíruje Response ID + text
- RESPONSE přenese Response ID do pole MODE/RESPONSE ID
- Pokud je přítomen `readmerepair.txt`, zobraz jeho obsah a zpřístupni
  SCRIPT

## 15) File API panel -- synchronizace {#file-api-panel-synchronizace}

- Po každém uploadu a delete:
  - refresh seznamu FILE API
- Po uploadu z LOCAL FILES:
  - vyprázdni LOCAL FILES tabulku

## 16) Doplňující definice „kompatibilní soubory pro File API" {#doplňující-definice-kompatibilní-soubory-pro-file-api}

Implementuj výběr souborů pro upload tak, aby: - běžné textové konfigy a
zdrojáky byly uploadovány - binární soubory a extrémně velké soubory
byly detekovány jako nekompatibilní a zaznamenány do manifestu - `.env`
a jiné citlivé soubory: preferuj neuploadovat a zaznamenat do manifestu
(a případně generovat bezpečný seznam klíčů bez hodnot)

Tohle je součást robustní implementace, ale nesmí to porušit zásadu:
existence souborů musí být v mirroru zachycena.

## 17) Další povinné rozšíření (detailně) {#další-povinné-rozšíření-detailně}

### 17.A Spolehlivost a řízení běhu {#a-spolehlivost-a-řízení-běhu}

#### A1) Cancel/Stop běhu

- V UI musí být vždy dostupné tlačítko "STOP" (součást progress
  dialogu).
- STOP provede korektní ukončení:
  - zrušení čekání na batch (polling)
  - zrušení uploadů (pokud SDK umožní přerušení) nebo jejich bezpečné
    dokončení s jasným stavem
  - zrušení dalších requestů v pipeline (nezahajovat nové)
- STOP nikdy nesmí nechat aplikaci ve stavu "zamrzlo"; progress dialog
  se přepne do režimu "Stopping..." a po dokončení se zavře.
- Po STOP musí existovat možnost:
  - buď bezpečně "Resume"
  - nebo "Close run" (ukončit run)

#### A2) Resume běhu po pádu / restartu {#a2-resume-běhu-po-pádu-restartu}

- Program musí umět z LOG rekonstruovat poslední stav runu:
  - jaké kroky proběhly
  - jaké file_id byly uploadnuté
  - jaké response_id/batch_id už existují
  - jaké soubory už byly uloženy
- Při startu program nabídne "RESUME LAST RUN" co nejdřív, pokud najde nedokončený run (ještě před dokončením automatické inicializace z 3.5). Automatická inicializace může běžet paralelně na pozadí; volba RESUME nesmí čekat na její dokončení.
- Resume musí být idempotentní:
  - pokud se krok už provedl, přeskočí se
  - pokud není jistota, krok se provede znovu bezpečným způsobem (např.
    znovu stáhnout batch result, znovu validovat, znovu zapsat do
    karantény místo přepsání)

#### A3) Rate-limit & retry politika {#a3-rate-limit-retry-politika}

- Implementuj retry s exponenciálním backoff + jitter.
- Circuit breaker:
  - pokud se opakovaně vrací rate-limit nebo 5xx, na čas se zastaví nové
    requesty a UI ukáže "Cooling down".
- Retry pravidla:
  - retryovat transient chyby (429, 5xx, timeouts)
  - nikdy nere-tryovat chyby validace kontraktů (to je logická chyba
    výstupu)
- Veškeré retry pokusy se logují.

### 17.B Bezpečnost práce se soubory a snapshoty {#b-bezpečnost-práce-se-soubory-a-snapshoty}

#### B1) Secret scanner + redakce {#b1-secret-scanner-redakce}

- Před uploadem do Files API (mirror i diagnostika) program projede
  soubory a detekuje:
  - `.env`
  - klíče/tokeny (heuristiky a regexy)
  - privátní klíče/certy
- Default chování:
  - citlivé soubory preferuj neuploadovat
  - místo toho zapiš do manifestu, že existují, a uveď bezpečný popis
    (např. seznam klíčů bez hodnot)
- Pokud uživatel v SETTINGS vypne bezpečnostní omezení, program umožní
  upload i citlivých souborů, ale vždy zobrazí varování.

#### B2) Allow/Deny list přípon i cest

- V SETTINGS existuje konfigurace:
  - allow/deny list přípon
  - allow/deny list cest (glob patterns)
- Odděleně pro:
  - IN mirror
  - diagnostické snapshoty
- V manifestu musí být vždy vidět, co bylo vynecháno a proč.

#### B3) Šifrování logů + panic wipe {#b3-šifrování-logů-panic-wipe}

- Volitelné šifrování lokálních logů (minimálně: symetrické šifrování
  celé LOG složky nebo per-file, klíč uložen dle Windows bezpečného
  úložiště, pokud dostupné).
- "Panic wipe":
  - smaže lokální cache (dočasné soubory, stažené batch výsledky, price
    cache)
  - volitelně smaže i nešifrované logy
  - vždy vyžádá potvrzení

### 17.C Vývojářské workflow {#c-vývojářské-workflow}

#### C1) Dry-run režim pro MODIFY

- Volitelně v SETTINGS.
- V dry-run režimu pro MODIFY:
  - AI nejdřív vrátí seznam změn + rizika + touched files (bez
    generování obsahu)
  - uživatel musí potvrdit pokračování, teprve pak se spustí B3
    generování obsahů
- Dry-run výstup se loguje a je součástí run bundle.

#### C2) Post-run hooks

- Po uložení souborů program může spustit:
  - testy
  - lint
  - format
- Hooky lze spustit:
  - lokálně
  - nebo přes SSH (pokud je k dispozici SSH konfigurace pro hooky)
- Výstup hooků (stdout/stderr, návratové kódy) se loguje.

#### C3) Diff viewer

- V UI existuje diff viewer pouze pro přehled uživatele.
- Do AI se vždy posílá full content dle kontraktů.

### 17.D Observabilita (kromě LOG souborů) {#d-observabilita-kromě-log-souborů}

#### D1) Run timeline

- Program vede interní timeline:
  - krok
  - start/end timestamp
  - výsledek
  - související IDs (file_id, response_id, batch_id, vector_store_id)
- Timeline je viditelná v UI a exportovatelná do LOG.

#### D2) Export "Run bundle" (zip)

- Program umí vytvořit zip balík:
  - requesty
  - response
  - manifesty
  - snapshoty (pokud uživatel povolí; jinak jen odkazy)
  - skripty
  - `readmerepair.txt`
  - timeline
- Export je dostupný z UI (např. z progress dialogu po dokončení).

### 17.E Pricing (povoleno, implementovat) {#e-pricing-povoleno-implementovat}

- Program podporuje automatickou aktualizaci ceníku z oficiálních zdrojů
  (konfigurovatelný endpoint/URL v SETTINGS).
- Pro každý běh se ukládá účtenka:
  - usage (input/output tokens)
  - batch discount/pricing
  - tool calls (file_search)
  - storage-days odhad (z usage_bytes a času držení)
- Pokud ceny nelze ověřit (offline, endpoint nedostupný):
  - běh může pokračovat
  - účtenka je označena „odhad / neověřeno"

## 18) Co musí výstupní program „Kája" dodat {#co-musí-výstupní-program-kája-dodat}

- Plně funkční aplikaci dle UI a logiky výše
- Kompletní zdrojové soubory projektu
- Jasné instrukce pro spuštění (např. pip install -r requirements.txt +
  python ui_main.py nebo ekvivalent)
- Program musí implementovat přesně uvedené kroky, kontrakty A1/A2/A3 a
  B1/B2/B3, logování, progress dialogy, SAVE/LOAD/LOAD REQUEST, API-KEY
  správu, FILE API management.
- Program musí implementovat:
  - Windows/SSH diagnostics (IN snapshot + OUT očekávání skriptu)
  - Vector store management
  - Batch monitor a tok C (Batch-only)
  - Pricing screen `$` a účtenky
  - VERSING dle pravidel v 10.4

## 19) Pokyny k designu {#pokyny-k-designu}

Pokyny k designu jsou závazně definovány v samostatné kapitole **DESIGN MANIFEST UI** (kapitola 1 tohoto dokumentu).  
Tato kapitola v původním MASTER zadání byla nahrazena DESIGN MANIFESTEM a je zde ponechána pouze jako odkaz, aby nedošlo k nejasnostem při čtení/odkazování.


# PŘÍLOHA FULL Ubuntu (Web Server) Diagnostics
Tento manuál definuje **FULL diagnostický balík pro Ubuntu server**, typicky hostující webový stack (např. **nginx**, databáze, Python aplikace, webhooky, certifikáty). Cílem je poskytnout **konzistentní adresář se soubory** (bez ZIP) tak, aby bylo možné rychle určit příčinu chyb (konfigurace, procesy, síť, certifikáty, permissions, venv, systémové limity).

> Výstup je **adresář se soubory** na Ubuntu (a volitelně stažený na Windows). Neprovádí se kopie databází ani tajných klíčů – jen konfigurace, metadatové přehledy a logy.

---

## Zásady bezpečnosti (doporučeno)
- **Neexportovat** privátní klíče (TLS, SSH), tokeny a hesla.
- Konfigurační soubory, které mohou obsahovat tajemství, exportovat buď:
  - se **základním maskováním** (např. `password=***`), nebo
  - jako **metadata** (cesta, vlastník, práva, hash) + ruční poskytnutí redigované verze.
- Logy mohou obsahovat osobní údaje; sdílet selektivně.

---

## Struktura kořenového adresáře
```
Diag_YYYYMMDD-HHMMSS/
│
├─ MANIFEST.md
├─ README_problem.md
├─ CHANGELOG_last_actions.txt
│
├─ system/
├─ hardware/
├─ storage/
├─ network/
├─ firewall/
├─ users_permissions/
├─ processes_services/
├─ packages/
├─ web/
├─ nginx/
├─ app/
├─ python/
├─ database/
├─ certs/
├─ cron_webhooks/
├─ logs/
└─ virtualization_containers/
```

---

# README_problem.md (ručně doplnit)
Minimální šablona:
- **Symptom** (co nefunguje)
- **Repro kroky**
- **Očekávání vs realita**
- **Kdy to začalo** (konkrétní datum/čas)
- **Poslední změny** (deploy, update, cert renewal, firewall)
- **Výpis chyby** (kopie výstupu)

---

# system/
- `os_release.txt` – `/etc/os-release`, kernel
- `uname_a.txt` – `uname -a`
- `uptime.txt` – `uptime`, `who -b`
- `locale_timezone.txt` – `locale`, `timedatectl`
- `hostname_hosts.txt` – `hostnamectl`, `/etc/hosts`, `/etc/hostname`
- `sysctl_all.txt` – `sysctl -a`
- `limits_summary.txt` – `ulimit -a`, `/etc/security/limits.conf` + `limits.d` listing
- `systemd_failed_units.txt` – `systemctl --failed`
- `systemd_running_units.txt` – `systemctl list-units --type=service --state=running`
- `journal_boot_errors.txt` – `journalctl -b -p err..alert --no-pager`
- `env_root_sanitized.txt` – environment relevantní pro služby (bez tajemství)

---

# hardware/
- `cpuinfo.txt` – `/proc/cpuinfo` (souhrn)
- `meminfo.txt` – `/proc/meminfo` + `free -h`
- `load_ps_top.txt` – `ps aux --sort=-%cpu`, `ps aux --sort=-%mem` + `top -b -n 1`
- `dmesg_tail.txt` – `dmesg -T | tail -n 400`

---

# storage/
- `df_h.txt` – `df -hT`
- `lsblk.txt` – `lsblk -f`
- `mounts.txt` – `mount`, `/etc/fstab`
- `inode_usage.txt` – `df -ih`
- `disk_health_hint.txt` – (pokud dostupné) `smartctl -H` pro hlavní disk (jen status)
- `largest_dirs_root.csv` – top složky v `/` (1–2 úrovně) podle velikosti
- `largest_dirs_var.csv` – top složky v `/var` podle velikosti

---

# network/
- `ip_addr.txt` – `ip a`
- `ip_route.txt` – `ip r`
- `resolv_conf.txt` – `/etc/resolv.conf` + `systemd-resolve --status` (pokud je)
- `ss_listen.txt` – `ss -lntup`
- `ss_all.txt` – `ss -antup`
- `netstat_fallback.txt` – pokud `net-tools` existuje
- `dns_check.txt` – `getent hosts` pro klíčové domény (pokud definováno)
- `proxy_env.txt` – HTTP(S)_PROXY env (pokud existuje)

---

# firewall/
- `ufw_status.txt` – `ufw status verbose` (pokud je ufw)
- `iptables_rules.txt` – `iptables -S` + `iptables -L -n -v`
- `nft_ruleset.txt` – `nft list ruleset` (pokud nft)

---

# users_permissions/
- `users_groups.txt` – `getent passwd`, `getent group` (bez hashů)
- `sudoers_listing.txt` – listing `/etc/sudoers*` (bez obsahu, nebo redigovaně)
- `umask.txt` – `umask`
- `important_paths_permissions.txt` – vlastníci/práva u `/etc/nginx`, `/var/www`, `/srv`, `/opt`, app dirs

---

# processes_services/
- `ps_full.txt` – `ps auxfww`
- `systemctl_status_nginx.txt` – `systemctl status nginx --no-pager`
- `systemctl_status_app.txt` – status aplikace (gunicorn/uvicorn/systemd unit) pokud existuje
- `systemctl_status_db.txt` – status DB služby pokud existuje
- `open_files_limits.txt` – `cat /proc/sys/fs/file-max` + `lsof` souhrn (pokud dostupné)

---

# packages/
- `dpkg_list.txt` – `dpkg -l`
- `apt_policy_key_pkgs.txt` – verze balíků: nginx, openssl, python3, certbot, postgres/mysql, redis
- `snap_list.txt` – `snap list` (pokud)
- `pip_global_list.txt` – `python3 -m pip list` (pokud pip)

---

# web/
- `web_root_overview.txt` – přehled dokument rootů (např. `/var/www`, `/srv/www`) – strom do hloubky 3
- `static_assets_sizes.csv` – top složky podle velikosti v dokument rootech
- `web_server_headers_hint.txt` – (volitelně) lokální `curl -I` na `http://127.0.0.1` a vybrané vhosty

---

# nginx/
- `nginx_version.txt` – `nginx -V` (včetně configure arguments)
- `nginx_test.txt` – `nginx -t` output
- `nginx_conf_tree.txt` – strom `/etc/nginx` (hloubka 4)
- `nginx_conf_files_list.txt` – seznam `.conf` souborů
- `nginx_sites_enabled.txt` – listing sites-enabled/sites-available
- `nginx_effective_config.txt` – `nginx -T` (pozor na tajemství; případně redigovat)
- `nginx_logs_tail_access.txt` – `tail` relevantních access logů
- `nginx_logs_tail_error.txt` – `tail` relevantních error logů

---

# app/
- `app_dirs_overview.txt` – přehled typických umístění aplikace: `/srv`, `/opt`, `/var/www`, `~/apps`
- `systemd_units_related.txt` – grep na služby (gunicorn/uvicorn/celery/worker)
- `app_env_files_found.txt` – nalezené `.env`, `config*.yml`, `settings.py` (jen cesty + práva + hash)
- `app_permissions_summary.txt` – vlastník/práva pro app dir + data dir
- `webhook_configs_found.txt` – konfigurace webhooků (jen cesty + metadata)

---

# python/
Cíl: odhalit konflikty mezi více instalacemi, venv, pyenv, poetry, pipx.

- `python_versions.txt` – `which -a python python3 pip pip3` + `python3 --version`
- `python_alternatives.txt` – `update-alternatives --display python3` (pokud existuje)
- `python_sys_path.json` – `python3 -c "import sys, json; print(json.dumps(sys.path, indent=2))"`
- `python_site.json` – `python3 -c "import site, json; print(json.dumps({'sitepackages': site.getsitepackages(), 'usersite': site.getusersitepackages()}, indent=2))"`
- `pip_debug.txt` – `python3 -m pip debug -v` (pozor na index/token; redigovat)
- `pip_config_list.txt` – `pip config list -v` (cesty na configy)

## Venv/Poetry/Pipenv/Pyenv discovery
- `venv_candidates_found.txt` – hledání `pyvenv.cfg` a `bin/python` v `/srv`, `/opt`, `/var/www`, `/home`, `/root`
- `venv_tree_summaries/venv_<name>.txt` – strom venv (bin/, lib/, site-packages) + velikost
- `venv_reports/venv_<name>__report.json` – pro každou venv:
  - `sys.executable`, `sys.prefix`, `sys.base_prefix`, `sys.path`
  - `pip --version`, `pip list`, `pip freeze`

---

# database/
Bez exportu dat; jen konfigurace, verze, stav, připojení, logy.

## PostgreSQL (pokud existuje)
- `postgres_version.txt` – `psql --version`
- `postgres_service_status.txt` – `systemctl status postgresql --no-pager`
- `postgres_conf_locations.txt` – cesty na `postgresql.conf`, `pg_hba.conf` (jen metadata + hash)
- `postgres_listen_ports.txt` – `ss -lntup | grep postgres`
- `postgres_logs_tail.txt` – tail relevantních logů

## MySQL/MariaDB (pokud existuje)
- `mysql_version.txt`
- `mysql_service_status.txt`
- `mysql_conf_locations.txt` – my.cnf locations (metadata)
- `mysql_logs_tail.txt`

## Redis (pokud existuje)
- `redis_version.txt`
- `redis_service_status.txt`
- `redis_conf_metadata.txt`
- `redis_logs_tail.txt`

---

# certs/
- `cert_locations.txt` – přehled `/etc/letsencrypt`, `/etc/ssl`, custom cert dirs
- `certbot_status.txt` – `certbot certificates` (pokud)
- `cert_expiry_report.txt` – expirace certů (např. `openssl x509 -enddate` pro vybrané)
- `tls_private_keys_presence.txt` – jen detekce přítomnosti klíčů (bez exportu obsahu)

---

# cron_webhooks/
- `crontab_root.txt` – `crontab -l` (root)
- `crontab_users_listing.txt` – které user crontaby existují
- `system_cron_dirs_tree.txt` – `/etc/cron.*` listing
- `webhook_endpoints_inventory.txt` – soupis endpointů (z nginx/app config; bez tajemství)

---

# logs/
- `journal_nginx_last500.txt` – `journalctl -u nginx -n 500 --no-pager`
- `journal_app_last500.txt` – `journalctl -u <app> -n 500 --no-pager` (pokud)
- `journal_db_last500.txt` – pro DB (pokud)- `syslog_tail.txt` – `/var/log/syslog` tail (Ubuntu) nebo `journalctl` fallback
- `auth_log_tail.txt` – `/var/log/auth.log` tail (opatrně)
- `kernel_log_tail.txt` – `journalctl -k -n 400 --no-pager`

---

# virtualization_containers/
- `docker_info.txt` – `docker info` (pokud)
- `docker_ps.txt` – `docker ps -a` (pokud)
- `docker_compose_files_found.txt` – nalezené `docker-compose*.yml` (cesty + metadata)
- `k8s_hint.txt` – pokud je microk8s/k3s (stav)

---

# Automatizovaný sběr – doporučený běh
1. Na Ubuntu spustit sběr (bash skript), který vytvoří `Diag_YYYYMMDD-HHMMSS/` a naplní podsložky.
2. Volitelně stáhnout celý adresář na Windows přes SCP.

---

# Jednořádkový příkaz z Windows PowerShellu (remote sběr + stažení)
Níže je one-liner s placeholdery. Vyžaduje:
- Windows 10/11: `ssh` a `scp` (OpenSSH Client)
- Pokud chceš zadat heslo v příkazu: `sshpass` (nedoporučeno). Bezpečnější je SSH klíč.

## Varianta A (doporučeno): SSH klíč, bez hesla v příkazu
```powershell
$ip="<IP_ADDRESS>"; $user="root"; $script=@'
#!/usr/bin/env bash
set -o pipefail
set +e
timestamp=$(date +%Y%m%d-%H%M%S)
remote_root="/root/Diag_${timestamp}"
mkdir -p "$remote_root"
mkdir -p "$remote_root/system"
(cat /etc/os-release) > "$remote_root/system/os_release.txt" 2>&1
mkdir -p "$remote_root/system"
(uname -a) > "$remote_root/system/uname.txt" 2>&1
mkdir -p "$remote_root/system"
(uptime && who -b) > "$remote_root/system/uptime.txt" 2>&1
mkdir -p "$remote_root/system"
(locale && timedatectl) > "$remote_root/system/locale_timezone.txt" 2>&1
mkdir -p "$remote_root/system"
(hostnamectl && cat /etc/hosts && cat /etc/hostname) > "$remote_root/system/hostname_hosts.txt" 2>&1
mkdir -p "$remote_root/system"
(sysctl -a) > "$remote_root/system/sysctl_all.txt" 2>&1
mkdir -p "$remote_root/system"
(ulimit -a && ls /etc/security/limits.conf /etc/security/limits.d 2>/dev/null) > "$remote_root/system/limits_summary.txt" 2>&1
mkdir -p "$remote_root/system"
(systemctl --failed) > "$remote_root/system/systemd_failed_units.txt" 2>&1
mkdir -p "$remote_root/system"
(systemctl list-units --type=service --state=running) > "$remote_root/system/systemd_running_units.txt" 2>&1
mkdir -p "$remote_root/system"
(journalctl -b -p err..alert --no-pager) > "$remote_root/system/journal_boot_errors.txt" 2>&1
mkdir -p "$remote_root/system"
(env | grep -v -E '(PASS|KEY|SECRET|TOKEN|PASSWORD)') > "$remote_root/system/env_root_sanitized.txt" 2>&1
mkdir -p "$remote_root/hardware"
(lscpu) > "$remote_root/hardware/cpu.txt" 2>&1
mkdir -p "$remote_root/hardware"
(dmidecode -t memory) > "$remote_root/hardware/memory_modules.txt" 2>&1
mkdir -p "$remote_root/hardware"
(free -h) > "$remote_root/hardware/memory_summary.txt" 2>&1
mkdir -p "$remote_root/storage"
(lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE) > "$remote_root/storage/volumes.txt" 2>&1
mkdir -p "$remote_root/storage"
(mount | column -t) > "$remote_root/storage/mount_points.txt" 2>&1
mkdir -p "$remote_root/storage"
(if command -v smartctl >/dev/null 2>&1; then for dev in /dev/sd?; do smartctl -H "$dev"; done; else echo 'smartctl missing'; fi) > "$remote_root/storage/smart_status.txt" 2>&1
mkdir -p "$remote_root/network"
(ip addr) > "$remote_root/network/ipconfig_all.txt" 2>&1
mkdir -p "$remote_root/network"
(ip link) > "$remote_root/network/adapters_details.txt" 2>&1
mkdir -p "$remote_root/network"
(resolvectl status || systemd-resolve --status || cat /etc/resolv.conf) > "$remote_root/network/dns_client_config.txt" 2>&1
mkdir -p "$remote_root/network"
(cat /etc/hosts) > "$remote_root/network/hosts_file.txt" 2>&1
mkdir -p "$remote_root/network"
(ip route) > "$remote_root/network/routes.txt" 2>&1
mkdir -p "$remote_root/network"
(ss -tunlp) > "$remote_root/network/listening_sockets.txt" 2>&1
mkdir -p "$remote_root/firewall"
(ufw status verbose) > "$remote_root/firewall/ufw_status.txt" 2>&1
mkdir -p "$remote_root/firewall"
(iptables -S && iptables -L -n -v) > "$remote_root/firewall/iptables_rules.txt" 2>&1
mkdir -p "$remote_root/firewall"
(nft list ruleset) > "$remote_root/firewall/nft_ruleset.txt" 2>&1
mkdir -p "$remote_root/users_permissions"
(getent passwd && getent group) > "$remote_root/users_permissions/users_groups.txt" 2>&1
mkdir -p "$remote_root/users_permissions"
(cat /etc/sudoers && ls /etc/sudoers.d 2>/dev/null) > "$remote_root/users_permissions/sudoers_listing.txt" 2>&1
mkdir -p "$remote_root/users_permissions"
(umask) > "$remote_root/users_permissions/umask.txt" 2>&1
mkdir -p "$remote_root/processes_services"
(ps -ef) > "$remote_root/processes_services/process_list.txt" 2>&1
mkdir -p "$remote_root/processes_services"
(systemctl list-units --type=service --all) > "$remote_root/processes_services/services_state.txt" 2>&1
mkdir -p "$remote_root/processes_services"
(systemctl list-unit-files --state=enabled) > "$remote_root/processes_services/startup_items.txt" 2>&1
mkdir -p "$remote_root/packages"
(dpkg -l) > "$remote_root/packages/dpkg_list.txt" 2>&1
mkdir -p "$remote_root/packages"
(apt-cache policy nginx openssl python3 certbot postgresql redis) > "$remote_root/packages/apt_policy_key_pkgs.txt" 2>&1
mkdir -p "$remote_root/packages"
(snap list) > "$remote_root/packages/snap_list.txt" 2>&1
mkdir -p "$remote_root/web"
(find /var/www /srv/www -maxdepth 3 -type d -print 2>/dev/null) > "$remote_root/web/web_root_overview.txt" 2>&1
mkdir -p "$remote_root/web"
(du -h --max-depth=2 /var/www /srv/www 2>/dev/null | sort -hr) > "$remote_root/web/static_assets_sizes.csv" 2>&1
mkdir -p "$remote_root/web"
(curl -I http://127.0.0.1 2>&1 || true) > "$remote_root/web/web_server_headers_hint.txt" 2>&1
mkdir -p "$remote_root/nginx"
(nginx -V) > "$remote_root/nginx/nginx_version.txt" 2>&1
mkdir -p "$remote_root/nginx"
(nginx -t) > "$remote_root/nginx/nginx_test.txt" 2>&1
mkdir -p "$remote_root/nginx"
(find /etc/nginx -maxdepth 4 -print 2>/dev/null) > "$remote_root/nginx/nginx_conf_tree.txt" 2>&1
mkdir -p "$remote_root/app"
(find /srv /opt /var/www ~/apps -maxdepth 2 -type d -print 2>/dev/null) > "$remote_root/app/app_dirs_overview.txt" 2>&1
mkdir -p "$remote_root/app"
(systemctl list-unit-files | grep -E 'gunicorn|uvicorn|celery|worker' || true) > "$remote_root/app/systemd_units_related.txt" 2>&1
mkdir -p "$remote_root/app"
(find /srv /opt /var/www ~/apps -type f \( -name '*.env' -o -name 'config*.yml' -o -name 'settings.py' \) -print -exec ls -l {} \; 2>/dev/null) > "$remote_root/app/app_env_files_found.txt" 2>&1
mkdir -p "$remote_root/python"
(which python && which python3) > "$remote_root/python/where_python.txt" 2>&1
mkdir -p "$remote_root/python"
(python3 -m pip --version && pip3 --version) > "$remote_root/python/py_launcher_list.txt" 2>&1
mkdir -p "$remote_root/python"
(python3 -c \"import json,sys; print(json.dumps({'python': sys.executable, 'paths': sys.path}))\") > "$remote_root/python/interpreters_inventory.csv" 2>&1
mkdir -p "$remote_root/database"
(psql --version) > "$remote_root/database/postgres_version.txt" 2>&1
mkdir -p "$remote_root/database"
(systemctl status postgresql --no-pager) > "$remote_root/database/postgres_service_status.txt" 2>&1
mkdir -p "$remote_root/database"
(find /etc/postgresql -name 'postgresql.conf' -o -name 'pg_hba.conf' -print 2>/dev/null) > "$remote_root/database/postgres_conf_locations.txt" 2>&1
mkdir -p "$remote_root/certs"
(find /etc/letsencrypt /etc/ssl /etc/pki -maxdepth 3 -type f \( -name '*.pem' -o -name '*.crt' \) -print 2>/dev/null) > "$remote_root/certs/cert_locations.txt" 2>&1
mkdir -p "$remote_root/certs"
(certbot certificates || echo 'certbot missing') > "$remote_root/certs/certbot_status.txt" 2>&1
mkdir -p "$remote_root/certs"
(for cert in /etc/letsencrypt/live/*/cert.pem; do echo CERT: $cert; openssl x509 -enddate -noout -in \"$cert\"; done 2>/dev/null) > "$remote_root/certs/cert_expiry_report.txt" 2>&1
mkdir -p "$remote_root/cron_webhooks"
(crontab -l) > "$remote_root/cron_webhooks/crontab_root.txt" 2>&1
mkdir -p "$remote_root/cron_webhooks"
(ls /var/spool/cron/crontabs 2>/dev/null) > "$remote_root/cron_webhooks/crontab_users_listing.txt" 2>&1
mkdir -p "$remote_root/cron_webhooks"
(ls /etc/cron.* 2>/dev/null) > "$remote_root/cron_webhooks/system_cron_dirs_tree.txt" 2>&1
mkdir -p "$remote_root/logs"
(journalctl -u nginx -n 500 --no-pager) > "$remote_root/logs/journal_nginx_last500.txt" 2>&1
mkdir -p "$remote_root/logs"
(journalctl -n 500 --no-pager) > "$remote_root/logs/journal_app_last500.txt" 2>&1
mkdir -p "$remote_root/logs"
(journalctl -u postgresql -n 500 --no-pager) > "$remote_root/logs/journal_db_last500.txt" 2>&1
mkdir -p "$remote_root/logs"
(tail -n 200 /var/log/syslog) > "$remote_root/logs/syslog_tail.txt" 2>&1
mkdir -p "$remote_root/logs"
(tail -n 200 /var/log/auth.log) > "$remote_root/logs/auth_log_tail.txt" 2>&1
mkdir -p "$remote_root/logs"
(journalctl -k -n 400 --no-pager) > "$remote_root/logs/kernel_log_tail.txt" 2>&1
mkdir -p "$remote_root/virtualization_containers"
(docker info) > "$remote_root/virtualization_containers/docker_info.txt" 2>&1
mkdir -p "$remote_root/virtualization_containers"
(docker ps -a) > "$remote_root/virtualization_containers/docker_ps.txt" 2>&1
mkdir -p "$remote_root/virtualization_containers"
(find /srv /opt /etc -name 'docker-compose*.yml' -print 2>/dev/null) > "$remote_root/virtualization_containers/docker_compose_files_found.txt" 2>&1
echo "REMOTE_ROOT=$remote_root"
'@; $remoteRoot = $script | ssh "$user@$ip" "bash -s" | Select-String -Pattern '^REMOTE_ROOT=' | Select-Object -First 1 | ForEach-Object { $_.Line -replace '^REMOTE_ROOT=' }; scp -r "$user@$ip:$remoteRoot" .
```

## Varianta B (heslo v příkazu – méně bezpečné; vyžaduje sshpass)
```powershell
$ip="<IP_ADDRESS>"; $user="root"; $pw="<ROOT_PASSWORD>"; $script=@'
#!/usr/bin/env bash
set -o pipefail
set +e
timestamp=$(date +%Y%m%d-%H%M%S)
remote_root="/root/Diag_${timestamp}"
mkdir -p "$remote_root"
mkdir -p "$remote_root/system"
(cat /etc/os-release) > "$remote_root/system/os_release.txt" 2>&1
mkdir -p "$remote_root/system"
(uname -a) > "$remote_root/system/uname.txt" 2>&1
mkdir -p "$remote_root/system"
(uptime && who -b) > "$remote_root/system/uptime.txt" 2>&1
mkdir -p "$remote_root/system"
(locale && timedatectl) > "$remote_root/system/locale_timezone.txt" 2>&1
mkdir -p "$remote_root/system"
(hostnamectl && cat /etc/hosts && cat /etc/hostname) > "$remote_root/system/hostname_hosts.txt" 2>&1
mkdir -p "$remote_root/system"
(sysctl -a) > "$remote_root/system/sysctl_all.txt" 2>&1
mkdir -p "$remote_root/system"
(ulimit -a && ls /etc/security/limits.conf /etc/security/limits.d 2>/dev/null) > "$remote_root/system/limits_summary.txt" 2>&1
mkdir -p "$remote_root/system"
(systemctl --failed) > "$remote_root/system/systemd_failed_units.txt" 2>&1
mkdir -p "$remote_root/system"
(systemctl list-units --type=service --state=running) > "$remote_root/system/systemd_running_units.txt" 2>&1
mkdir -p "$remote_root/system"
(journalctl -b -p err..alert --no-pager) > "$remote_root/system/journal_boot_errors.txt" 2>&1
mkdir -p "$remote_root/system"
(env | grep -v -E '(PASS|KEY|SECRET|TOKEN|PASSWORD)') > "$remote_root/system/env_root_sanitized.txt" 2>&1
mkdir -p "$remote_root/hardware"
(lscpu) > "$remote_root/hardware/cpu.txt" 2>&1
mkdir -p "$remote_root/hardware"
(dmidecode -t memory) > "$remote_root/hardware/memory_modules.txt" 2>&1
mkdir -p "$remote_root/hardware"
(free -h) > "$remote_root/hardware/memory_summary.txt" 2>&1
mkdir -p "$remote_root/storage"
(lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE) > "$remote_root/storage/volumes.txt" 2>&1
mkdir -p "$remote_root/storage"
(mount | column -t) > "$remote_root/storage/mount_points.txt" 2>&1
mkdir -p "$remote_root/storage"
(if command -v smartctl >/dev/null 2>&1; then for dev in /dev/sd?; do smartctl -H "$dev"; done; else echo 'smartctl missing'; fi) > "$remote_root/storage/smart_status.txt" 2>&1
mkdir -p "$remote_root/network"
(ip addr) > "$remote_root/network/ipconfig_all.txt" 2>&1
mkdir -p "$remote_root/network"
(ip link) > "$remote_root/network/adapters_details.txt" 2>&1
mkdir -p "$remote_root/network"
(resolvectl status || systemd-resolve --status || cat /etc/resolv.conf) > "$remote_root/network/dns_client_config.txt" 2>&1
mkdir -p "$remote_root/network"
(cat /etc/hosts) > "$remote_root/network/hosts_file.txt" 2>&1
mkdir -p "$remote_root/network"
(ip route) > "$remote_root/network/routes.txt" 2>&1
mkdir -p "$remote_root/network"
(ss -tunlp) > "$remote_root/network/listening_sockets.txt" 2>&1
mkdir -p "$remote_root/firewall"
(ufw status verbose) > "$remote_root/firewall/ufw_status.txt" 2>&1
mkdir -p "$remote_root/firewall"
(iptables -S && iptables -L -n -v) > "$remote_root/firewall/iptables_rules.txt" 2>&1
mkdir -p "$remote_root/firewall"
(nft list ruleset) > "$remote_root/firewall/nft_ruleset.txt" 2>&1
mkdir -p "$remote_root/users_permissions"
(getent passwd && getent group) > "$remote_root/users_permissions/users_groups.txt" 2>&1
mkdir -p "$remote_root/users_permissions"
(cat /etc/sudoers && ls /etc/sudoers.d 2>/dev/null) > "$remote_root/users_permissions/sudoers_listing.txt" 2>&1
mkdir -p "$remote_root/users_permissions"
(umask) > "$remote_root/users_permissions/umask.txt" 2>&1
mkdir -p "$remote_root/processes_services"
(ps -ef) > "$remote_root/processes_services/process_list.txt" 2>&1
mkdir -p "$remote_root/processes_services"
(systemctl list-units --type=service --all) > "$remote_root/processes_services/services_state.txt" 2>&1
mkdir -p "$remote_root/processes_services"
(systemctl list-unit-files --state=enabled) > "$remote_root/processes_services/startup_items.txt" 2>&1
mkdir -p "$remote_root/packages"
(dpkg -l) > "$remote_root/packages/dpkg_list.txt" 2>&1
mkdir -p "$remote_root/packages"
(apt-cache policy nginx openssl python3 certbot postgresql redis) > "$remote_root/packages/apt_policy_key_pkgs.txt" 2>&1
mkdir -p "$remote_root/packages"
(snap list) > "$remote_root/packages/snap_list.txt" 2>&1
mkdir -p "$remote_root/web"
(find /var/www /srv/www -maxdepth 3 -type d -print 2>/dev/null) > "$remote_root/web/web_root_overview.txt" 2>&1
mkdir -p "$remote_root/web"
(du -h --max-depth=2 /var/www /srv/www 2>/dev/null | sort -hr) > "$remote_root/web/static_assets_sizes.csv" 2>&1
mkdir -p "$remote_root/web"
(curl -I http://127.0.0.1 2>&1 || true) > "$remote_root/web/web_server_headers_hint.txt" 2>&1
mkdir -p "$remote_root/nginx"
(nginx -V) > "$remote_root/nginx/nginx_version.txt" 2>&1
mkdir -p "$remote_root/nginx"
(nginx -t) > "$remote_root/nginx/nginx_test.txt" 2>&1
mkdir -p "$remote_root/nginx"
(find /etc/nginx -maxdepth 4 -print 2>/dev/null) > "$remote_root/nginx/nginx_conf_tree.txt" 2>&1
mkdir -p "$remote_root/app"
(find /srv /opt /var/www ~/apps -maxdepth 2 -type d -print 2>/dev/null) > "$remote_root/app/app_dirs_overview.txt" 2>&1
mkdir -p "$remote_root/app"
(systemctl list-unit-files | grep -E 'gunicorn|uvicorn|celery|worker' || true) > "$remote_root/app/systemd_units_related.txt" 2>&1
mkdir -p "$remote_root/app"
(find /srv /opt /var/www ~/apps -type f \( -name '*.env' -o -name 'config*.yml' -o -name 'settings.py' \) -print -exec ls -l {} \; 2>/dev/null) > "$remote_root/app/app_env_files_found.txt" 2>&1
mkdir -p "$remote_root/python"
(which python && which python3) > "$remote_root/python/where_python.txt" 2>&1
mkdir -p "$remote_root/python"
(python3 -m pip --version && pip3 --version) > "$remote_root/python/py_launcher_list.txt" 2>&1
mkdir -p "$remote_root/python"
(python3 -c \"import json,sys; print(json.dumps({'python': sys.executable, 'paths': sys.path}))\") > "$remote_root/python/interpreters_inventory.csv" 2>&1
mkdir -p "$remote_root/database"
(psql --version) > "$remote_root/database/postgres_version.txt" 2>&1
mkdir -p "$remote_root/database"
(systemctl status postgresql --no-pager) > "$remote_root/database/postgres_service_status.txt" 2>&1
mkdir -p "$remote_root/database"
(find /etc/postgresql -name 'postgresql.conf' -o -name 'pg_hba.conf' -print 2>/dev/null) > "$remote_root/database/postgres_conf_locations.txt" 2>&1
mkdir -p "$remote_root/certs"
(find /etc/letsencrypt /etc/ssl /etc/pki -maxdepth 3 -type f \( -name '*.pem' -o -name '*.crt' \) -print 2>/dev/null) > "$remote_root/certs/cert_locations.txt" 2>&1
mkdir -p "$remote_root/certs"
(certbot certificates || echo 'certbot missing') > "$remote_root/certs/certbot_status.txt" 2>&1
mkdir -p "$remote_root/certs"
(for cert in /etc/letsencrypt/live/*/cert.pem; do echo CERT: $cert; openssl x509 -enddate -noout -in \"$cert\"; done 2>/dev/null) > "$remote_root/certs/cert_expiry_report.txt" 2>&1
mkdir -p "$remote_root/cron_webhooks"
(crontab -l) > "$remote_root/cron_webhooks/crontab_root.txt" 2>&1
mkdir -p "$remote_root/cron_webhooks"
(ls /var/spool/cron/crontabs 2>/dev/null) > "$remote_root/cron_webhooks/crontab_users_listing.txt" 2>&1
mkdir -p "$remote_root/cron_webhooks"
(ls /etc/cron.* 2>/dev/null) > "$remote_root/cron_webhooks/system_cron_dirs_tree.txt" 2>&1
mkdir -p "$remote_root/logs"
(journalctl -u nginx -n 500 --no-pager) > "$remote_root/logs/journal_nginx_last500.txt" 2>&1
mkdir -p "$remote_root/logs"
(journalctl -n 500 --no-pager) > "$remote_root/logs/journal_app_last500.txt" 2>&1
mkdir -p "$remote_root/logs"
(journalctl -u postgresql -n 500 --no-pager) > "$remote_root/logs/journal_db_last500.txt" 2>&1
mkdir -p "$remote_root/logs"
(tail -n 200 /var/log/syslog) > "$remote_root/logs/syslog_tail.txt" 2>&1
mkdir -p "$remote_root/logs"
(tail -n 200 /var/log/auth.log) > "$remote_root/logs/auth_log_tail.txt" 2>&1
mkdir -p "$remote_root/logs"
(journalctl -k -n 400 --no-pager) > "$remote_root/logs/kernel_log_tail.txt" 2>&1
mkdir -p "$remote_root/virtualization_containers"
(docker info) > "$remote_root/virtualization_containers/docker_info.txt" 2>&1
mkdir -p "$remote_root/virtualization_containers"
(docker ps -a) > "$remote_root/virtualization_containers/docker_ps.txt" 2>&1
mkdir -p "$remote_root/virtualization_containers"
(find /srv /opt /etc -name 'docker-compose*.yml' -print 2>/dev/null) > "$remote_root/virtualization_containers/docker_compose_files_found.txt" 2>&1
echo "REMOTE_ROOT=$remote_root"
'@; $remoteRoot = $script | sshpass -p $pw ssh -o StrictHostKeyChecking=no "$user@$ip" "bash -s" | Select-String -Pattern '^REMOTE_ROOT=' | Select-Object -First 1 | ForEach-Object { $_.Line -replace '^REMOTE_ROOT=' }; sshpass -p $pw scp -o StrictHostKeyChecking=no -r "$user@$ip:$remoteRoot" .
```

> Pozn?mka: Snippet pos?l? inline bash skript identick? s t?m, kter? generuje aplikace; stdout obsahuje jen `REMOTE_ROOT=...`, kter? se pou?ije pro n?sledn? `scp`.

---

# MANIFEST.md (poslední kapitola; šablona)

```markdown
# Diagnostic Manifest

Generated at: {{timestamp_local}}
Host: {{hostname}}
User: {{collector_user}}
Run as root: {{is_root}}
OS: {{os_pretty_name}}
Kernel: {{kernel}}
Uptime: {{uptime}}
Output root: {{output_root}}

## Purpose
This folder contains a full Ubuntu web server diagnostic snapshot for troubleshooting issues in nginx/app/database/certs/network.

## Folder Overview
- system/ – OS/kernel/timezone/sysctl/limits/systemd health
- hardware/ – CPU/RAM/load/dmesg hints
- storage/ – mounts/df/inodes/top sizes
- network/ – IP/routes/DNS/ports
- firewall/ – ufw/iptables/nft rules
- users_permissions/ – users/groups/sudoers listing/permissions summary
- processes_services/ – ps/systemctl statuses/open ports correlation
- packages/ – dpkg/apt versions of key packages
- web/ – web roots overview + size triage
- nginx/ – nginx -V/-t/-T, config tree, log tails
- app/ – app dirs, systemd units, env/config discovery (metadata)
- python/ – interpreter inventory, pip config, venv discovery + per-venv reports
- database/ – postgres/mysql/redis status + config metadata + log tails
- certs/ – certbot inventory + expiry report (no private keys)
- cron_webhooks/ – crons + webhook inventory (metadata)
- logs/ – journal/syslog/auth/kernel tails
- virtualization_containers/ – docker inventory + compose metadata

## File Index
| Path | Description |
|------|-------------|
| README_problem.md | repro steps + timeline |
| system/journal_boot_errors.txt | boot errors from journal |
| network/ss_listen.txt | listening sockets |
| nginx/nginx_test.txt | nginx -t output |
| python/venv_candidates_found.txt | detected venv roots |
| python/venv_reports/venv_*__report.json | per-venv sys/pip snapshot |
| certs/cert_expiry_report.txt | certificate expiry |
| logs/journal_nginx_last500.txt | nginx journal tail |
| logs/journal_app_last500.txt | app journal tail |

## Notes
- Secrets must be redacted before sharing.
- Missing subsystems are recorded as NOT PRESENT.

## Integrity
Total files: {{file_count}}
Total size: {{total_size_human}}
Optional checksums: checksums/sha256.txt
```


# PŘÍLOHA FULL Windows Diagnostics

Tento dokument definuje **konečný návrh FULL diagnostiky pro Windows**, zaměřený na:
- úplnou rekonstrukci systému bez ZIP archivace
- jednoznačné určení výchozích vs. runtime hodnot
- detailní rozbor **více instalací Pythonu a všech venv**
- transparentní analýzu PATH, registry, aliasů a asociací

Výstupem je **adresář se soubory**, nikoli archiv.

---

## Struktura kořenového adresáře
```
Diag_YYYYMMDD-HHMMSS/
│
├─ MANIFEST.md
├─ README_problem.md
├─ CHANGELOG_last_actions.txt
│
├─ system/
├─ registry/
├─ filesystem/
├─ hardware/
├─ storage/
├─ drivers/
├─ processes_services/
├─ network/
├─ security/
├─ python/
├─ devtools/
├─ virtualization/
├─ wsl/
└─ logs/
```

---

# MANIFEST.md (automaticky generovaný)

Slouží jako **index a kontrola úplnosti**.

```markdown
# Diagnostic Manifest

Generated at: YYYY-MM-DD HH:MM:SS
Machine: <COMPUTERNAME>
User: <USERNAME>
PowerShell: 5.1 / 7.x
Run as Administrator: YES / NO

## Folder Overview
system/      – OS, build, PATH, environment
registry/    – authoritative Windows configuration
filesystem/  – actual files, Python installs, venvs
python/      – runtime Python diagnostics
network/     – adapters, DNS, proxy, firewall
logs/        – crashes and event logs
...

## Files
| File | Description | Size |
|------|-------------|------|
| system/systeminfo.txt | OS + HW summary | 45 KB |
| registry/env_machine.reg | System PATH and env | 3 KB |
| python/venv_reports/venv_projA.json | Full venv report | 18 KB |

## Notes
- ACCESS DENIED = requires Administrator
- Missing subsystems are explicitly noted
```

---

# system/
**Jak Windows má fungovat po přihlášení**

- systeminfo.txt – OS, build, hotfixy, HW
- os_build.txt – edice, build, UBR
- windows_updates_hotfixes.txt
- timezone_locale.txt
- uptime_boot.txt
- power_settings.txt
- group_policy_summary.html
- run_context.txt

### Environment & PATH
- env_machine.txt – HKLM environment (rozparsované)
- env_user.txt – HKCU environment
- path_effective_process.txt – PATH skutečně viděný během běhu
- path_diff_analysis.txt – diff: Machine vs User vs Runtime

---

# registry/
**Zdroj pravdy – proč se spouští právě toto**

### Environment / PATH
- env_machine.reg – HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment
- env_user.reg – HKCU\\Environment

### Python – instalace & launcher
- python_core_hklm.reg
- python_core_hklm_wow6432.reg
- python_core_hkcu.reg
- pylauncher_hklm.reg
- pylauncher_hkcu.reg

### App Execution
- app_paths_python_hklm.reg
- app_paths_python_hkcu.reg
- windowsapps_execution_aliases.txt

### Asociace
- file_associations_python.reg

### Instalovaný software
- uninstall_inventory.txt – Python, Conda, VC++ runtimes

---

# filesystem/
**Co na disku reálně existuje (včetně přehledu uživatelských dat)**

> Cíl: poskytnout *přehled* souborové struktury mimo systémové složky Windows, zejména uživatelská data a AppData. Nejde o kopii obsahu – pouze strom a souhrny.
## Python & interpreters
- python_executables_found.txt
- python_install_dirs_tree.txt

## Virtual environments
- venv_candidates_found.txt
- venv_tree_summaries/
  - venv_<name>.txt

## Projekty
- project_requirements_found.txt

## User data & AppData overview (přehled)
- userprofile_tree_depth3.txt – strom `%USERPROFILE%` do hloubky 3 (bez binárního obsahu)
- userprofile_top_sizes.csv – top složky v `%USERPROFILE%` podle velikosti (rychlá orientace)
- appdata_roaming_tree_depth4.txt – strom `%APPDATA%` do hloubky 4
- appdata_local_tree_depth4.txt – strom `%LOCALAPPDATA%` do hloubky 4
- appdata_locallow_tree_depth4.txt – strom `%USERPROFILE%\AppData\LocalLow` do hloubky 4 (pokud existuje)
- appdata_top_sizes.csv – top složky v `AppData` podle velikosti
- known_folders_locations.txt – skutečné cesty na Documents/Downloads/Desktop atd. (redirects/OneDrive)
- onedrive_status_hint.txt – indikace OneDrive přesměrování (pokud existuje)

---

# python/
**Jak Python skutečně běží**

### Interpreters
- where_python.txt
- py_launcher_list.txt
- interpreters_inventory.csv

### Default runtime
- python_version_default.txt
- pip_version_default.txt
- pip_list_default.txt
- pip_freeze_default.txt
- pip_debug_default.txt
- pip_config_all.txt

### Runtime internals
- python_sys_path.json
- python_site_packages.txt
- python_platform.json

### Virtual env reports
python/venv_reports/
- venv_<name>__report.json

---

# processes_services/
- process_list.txt
- services_state.txt
- startup_items.txt
- scheduled_tasks_summary.txt

---

# network/
- ipconfig_all.txt
- adapters_details.txt
- dns_client_config.txt
- hosts_file.txt
- routes.txt
- netstat_ano.txt
- firewall_profiles.txt
- firewall_rules_export.wfw
- winhttp_proxy.txt
- internet_proxy_user.txt
- wifi_profiles.txt

---

# security/
- defender_status.txt
- applocker_effective.txt
- uac_settings.txt
- certificates_machine_summary.txt

---

# hardware/
- cpu.txt
- memory_modules.txt
- memory_summary.txt
- motherboard_bios.txt
- gpu_adapters.txt
- monitors_displays.txt

---

# storage/
- volumes.txt
- mount_points.txt
- smart_status.txt
- disk_performance_counters.txt

---

# drivers/
- driverquery_verbose.txt
- pnp_devices.txt
- problem_devices.txt
- signed_drivers.txt

---

# devtools/
- git_version.txt
- node_version.txt
- dotnet_info.txt
- vcpp_runtimes.txt

---

# virtualization/
- hyperv_state.txt
- virtual_machine_platform.txt
- windows_features.txt

---

# wsl/
- wsl_status.txt
- wsl_list_verbose.txt
- wsl_versions.txt

---

# logs/
- eventlog_system_last200.txt
- eventlog_application_last200.txt
- eventlog_security_last50.txt
- wer_crash_list.txt
- reliability_monitor_summary.txt
- windows_setup_logs_hint.txt

---

## Shrnutí
Tento balík umožňuje:
- kompletní rekonstrukci PATH (registry × runtime)
- rozlišení více Python instalací
- přesné určení aktivního interpreteru, pipu a venv
- vysvětlení chování Windows při spouštění python.exe
- analýzu pádů, blokací, politik, firewallu a proxy

# PŘÍLOHA A: PŮVODNÍ MASTER ZADÁNÍ (VERBATIM, NEZÁVAZNÉ)

Poznámka: Tato příloha je vložena beze změn pro audit a pro splnění požadavku „neztratit ani byte“ původního zadání. V případě rozdílů platí konsolidované zadání v kapitolách 1) a 3).

# MASTER ZADÁNÍ: Desktopový program „Kája" (Windows) pro automatizaci requestů na OpenAI (Responses API) + automatické zpracování odpovědí {#master-zadání-desktopový-program-kája-windows-pro-automatizaci-requestů-na-openai-responses-api-automatické-zpracování-odpovědí}

Jsi senior programátor. Všechny programy, které píšeš jsou funkční a
plně provozuschopné. Programy, které píšeš jsou robustní natolik, že
jsou ošetřeny pro většině situací, kdy by mohli spadnout nebo zamrznout.
Všechny tvoje programy musí tvořit detailní logování a to natolik
detailní, že při eventuální chybě, nebo problému je ihned v kombinaci s
projevem chyby identifikovat co je za problém. Program musí být stavěn
tak, že pokud nejsou nutné vstupy k dispozici musí na to být jejich
uživatel upozorněn. Všechny možnosti a komponenty v programu jsou
realizovány tak, aby nemohl uživatel ani takové kombinace zadat. Pokud
nějaká operace v programu trvá více než 3-5 sekund zavedeš v programu
Pop Up okno ve kterém informuješ uživatele o tom co se děje a předcházíš
tomu, aby program vytuhnul, nebo se tak tvářil.

Vygeneruj desktopový program s názvem **„Kája"**, který bude
**automatizovat requesty na OpenAI** (Responses API) a **zpracovávat
odpovědi** podle tohoto zadání. Program bude fungovat jako **detailní
ovládací panel**, kde uživatel nastaví očekávání, vstupy, režim, model a
zpracování odpovědí. Po spuštění requestu se provede **automatická sada
kroků** definovaná volbami v UI.

**Důležité:** V tomto zadání je záměrně redundance. Nesmíš vynechat
žádný detail ani když je redundantní.


- **Fonty (TTF):**
  - resources/montserrat_bold.ttf (Montserrat Bold)
  - resources/montserrat_regular.ttf (Montserrat Regular)

Chování: - Pokud některý z povinných souborů chybí, uživatel musí dostat
jasné hlášení + program musí pokračovat v degradovaném režimu.

## 1) Nezbytné vlastnosti a zásady {#nezbytné-vlastnosti-a-zásady}

### 1.1 Robustnost {#robustnost}

- Program musí být **robustní** a **nikdy nesmí spadnout**.
- Veškeré procesy musí být **detailně zobrazovány** ve vyskakovacím
  dialogu:
  - průběžné logování kroků
  - odhad zbývajícího času (ETA)
  - procentuální průběh (0--100 %) pro celý krok i sub-kroky
- UI se nesmí blokovat: síťové operace, uploady, pollingy, kopírování
  stromu adresářů, zipování bundle apod. poběží na pozadí.

### 1.2 Logování {#logování}

- V adresáři spuštění programu vytvoř složku **LOG/** (pokud
  neexistuje).
- Každý běh ("run") má vlastní **Run ID** (např.
  `RUN_<DDMMRRRRHHMM>_<random4>`).
- Každý request a response se uloží jako **samostatný soubor** do LOG/.
- Název log souboru musí obsahovat:
  - **Název projektu** (pokud je vyplněn)
  - **ResponseID** (nebo BatchID / C_RUN_ID / RUN_ID)
  - časový kód **DDMMRRRHHMM** (čas) -- přesně v názvu souboru

Povinné artefakty v LOG (per run): - kompletní request JSON (odeslaný)
-- *samostatný soubor* - kompletní response JSON (přijatý) --
*samostatný soubor* - kompletní "UI state" (co bylo vyplněno a zvoleno)
-- *samostatný soubor* (a zároveň embed do request logu, aby šel použít
pro LOAD REQUEST) - manifesty: - mirror manifest (IN mirror) -
diagnostické manifesty (Windows/SSH snapshot) - výstupní mapa uložených
souborů (co se uložilo kam) - stavové logy kroků: uploady, pollingy,
validace, retry, backoff, cancel

Logovat se musí navíc detailně: - seznam všech souborů, které program: -
přidal (nově vytvořil) - přepsal - smazal (lokálně nebo na File API) -
přesunul / zkopíroval - vytvořil adresář - u každé této změny: - časové
razítko - původní cesta + cílová cesta - velikost před/po (pokud
existuje) - hash (např. SHA256) před/po, pokud je to rozumné (u velkých
souborů volitelně) - u uploadů na File API: - lokální path - file_id -
purpose - velikost - timestamp uploadu - u mazání na File API: -
file_id - původní jméno (pokud dostupné) - timestamp

Batch logování: - vstupní JSONL - výstupní JSONL - error JSONL -
mapování `custom_id → path` (pokud je použito) - stavový průběh jobu
(polling snapshots)

Skripty (pouze pokud jsou vyžádány diagnostikou OUT a přijdou v
response): - `readmerepair.txt` - skripty - log spuštění skriptu
(stdout/stderr) - návratové kódy - záznam o potvrzení uživatele před
spuštěním

### 1.3 Kontrola logiky kombinací {#kontrola-logiky-kombinací}

Program musí kontrolovat, že zvolené kombinace nastavení jsou přípustné.
Nesmí odeslat request v neplatné kombinaci. Chyba se musí zobrazit
uživateli jasně a s návrhem opravy.

### 1.4 Cenová evidence a nacenění (důraz na přesnost) {#cenová-evidence-a-nacenění-důraz-na-přesnost}

Program musí implementovat: - přesné sledování cen za jednotlivé
requesty i batch joby - přesná evidence nákladů na: - input tokens -
output tokens - Batch (výsledná cena musí reflektovat Batch pricing) -
file_search a Vector store náklady (tool + storage) - důraz na přesnost
a aktuálnost ceníku

V UI musí existovat samostatná obrazovka pro ceny pod tlačítkem **„\$"**
(v záhlaví vedle tlačítka API-KEY). Na hlavní ploše programu se ceny
nezobrazují a neovlivňují workflow; ceny se řeší pouze v této samostatné
obrazovce.

**Elektronická účtenka**: - pro každý běh vzniká "účtenka" (detailní
rozpad položek) a ukládá se do lokální databáze (SQLite) +
exportovatelný JSON v LOG. - účtenky musí být filtrovatelné podle data,
projektu, modelu, režimu, typu (A/B/QA/C), obsahu zadání (fulltext),
ResponseID/BatchID. - musí být možné mazat, exportovat, sumarizovat za
období.

Aktualizace ceníku: - program musí podporovat lokální cache "price
table" + ruční refresh z oficiálních podkladů (konfigurovatelné v
SETTINGS). - program musí podporovat i automatický refresh při startu
(pokud je v SETTINGS zapnuto). - pokud program nemá aktuální ceny,
musí: - jasně upozornit (banner/popup) - umožnit pokračovat, ale
"účtenka" musí být označena jako "odhad / neověřeno" (explicitně).

## 2) Technologie a runtime požadavky (implementuj stabilně) {#technologie-a-runtime-požadavky-implementuj-stabilně}

- Program musí být připaven pro provoz na Windows 10 a Windows 11.
- Program jako takový vždy poběží jen na Windows a lokálním PC.
- UI musí být stabilní, s podporou dlouhých běhů a background operací
  (neblokovat UI).
- Použij „standardní OpenAI SDK knihovnu" (Python nebo JS). Implementace
  musí být plně funkční.

Komunikace s OpenAI: - Responses API pro generování (s
previous_response_id pro řetězení) -- pro A/B/QA. - Files API pro
upload/list/delete. - Models endpoint pro list modelů. - Vector store +
file_search (pokud je zvolen IN režim a model to podporuje). - Batch API
-- pro režim C a pro sledování batch jobů.

Důležité: - Program musí umět detekovat capabilities modelu a podle
toho: - **nepoužít** nepodporované tooly (zejména file_search) -
přepnout se do fallback režimu dle pravidel (A3.1) pouze tam, kde je
fallback definovaný a bezpečný.

## 3) Start aplikace, okno a automatická inicializace {#start-aplikace-okno-a-automatická-inicializace}

### 3.3 Hlavní okno {#hlavní-okno}

- Program se musí spustit **v maximalizovaném okně** na **hlavním
  monitoru**.
- přes celý program:
  - nesmí bránit ovládání (click-through)

### 3.4 Jedna pracovní plocha, responsivní rozvržení do 1--3 sloupců {#jedna-pracovní-plocha-responsivní-rozvržení-do-13-sloupců}

- hlavní plocha je jedna scrollovatelná pracovní plocha ("workspace").
- všechny sekce existují jako "karty/sekce" na této ploše.
- layout je responsivní:
  - při velké šířce okna se sekce automaticky skládají do **tří**
    sloupců
  - při menší šířce do **dvou** sloupců
  - při malé šířce do **jednoho** sloupce
- nesmí existovat tvrdé fixní rozdělení na konkrétní sloupce.
- horizontální scroll na úrovni celé plochy se nepoužívá; horizontální
  scroll pouze v konkrétních multiline polích, kde je explicitně
  požadován.

### 3.5 Automatická inicializace po startu {#automatická-inicializace-po-startu}

Před sputěním UI program automaticky (na pozadí, s progress dialogem)
provede: - načtení aktuálního seznamu **OpenAI modelů** (pro uložený API
key) - načtení aktuálního seznamu souborů na **Files API** - načtení
aktuálního seznamu existujících **Vector Stores** - načtení stavu všech
rozpracovaných **Batch jobů** a jejich zobrazení v Batch monitoru

Pokud API key chybí, místo toho zobrazí jasnou informaci, že automatická
inicializace není možná, a nabídne uživateli otevřít dialog API-KEY.

## 4) Záhlaví (toolbar) -- tlačítka a chování {#záhlaví-toolbar-tlačítka-a-chování}

V záhlaví obrazovky budou tlačítka:

### Vlevo:

1.  **API-KEY**
2.  **\$** (CENY / ÚČTENKY / CENÍK)
3.  **SETTINGS**
4.  **SAVE**
5.  **LOAD**
6.  **LOAD REQUEST**

### Vpravo:

7.  **EXIT**

## 5) Dialog „API-KEY" {#dialog-api-key}

Po stisknutí **API-KEY** se otevře vyskakovací dialog s: - **dlouhá
řádka** (jednořádkové pole), kam lze napsat API key pro OpenAI

Pod řádkou budou volby (tlačítka):

### 5.1 Uložit {#uložit}

- Uloží API key do **systémových proměnných dat** (system environment
  variables).
- Po uložení musí být program schopen key používat bez restartu
  (aktuální běh).

### 5.2 Zobraz {#zobraz}

- Ukáže viditelně v řádku API key, pokud je uloženo v systémových
  proměnných.

### 5.3 Smazat {#smazat}

- Smaže uložené API key ze systémových proměnných.

### 5.4 STORNO {#storno}

- Zavře okno beze změn.

## 6) SETTINGS {#settings}

Tlačítko SETTINGS otevře samostatné okno (mimo hlavní pracovní plochu).
SETTINGS je určeno pouze pro nastavení chodu programu, nikoliv pro
plnění funkce requestu a jejich automatického zpracování.

SETTINGS musí obsahovat minimálně: - lokace lokální databáze (default v
adresáři programu) - limity logování (rotace / max velikost / max počet
runů) - politika retry/backoff (limity, jitter, max pokusů, circuit
breaker) - ceník: zdroj (URL / lokální), refresh, cache TTL,
auto-refresh při startu - bezpečnost: - volitelné maskování tajemství v
logu (default: OFF, ale varování musí existovat) - volitelné šifrování
logů (default OFF) - panic wipe lokální cache (tlačítko) - Batch polling
interval a timeouty - výchozí model a defaultní teploty dle politiky -
povolení/konfigurace post-run hooks (lokálně/SSH)

## 7) \$ (CENY) -- samostatná obrazovka {#ceny-samostatná-obrazovka}

Tlačítko **\$** otevře samostatnou obrazovku s:

### 7.1 Přehled ceníku {#přehled-ceníku}

- tabulka cen per model:
  - input token
  - output token
  - batch pricing (pokud relevantní)
  - tool náklady (file_search)
  - storage náklady (vector store)
- datum poslední aktualizace
- tlačítko "REFRESH CENÍK"
- možnost nastavit zdroj ceníku a TTL (odkaz do SETTINGS)

### 7.2 Účtenky (evidence) {#účtenky-evidence}

- filtrování:
  - datum od-do
  - projekt
  - model
  - režim (GENERATE/MODIFY/QA/C)
  - ResponseID / BatchID
  - textový fulltext (v zadání / notes)
- detail účtenky:
  - rozpad tokenů a ceny
  - rozpad tool/storage nákladů
  - čas běhu, počty requestů, počty souborů
  - příznak „odhad / neověřeno" pokud nebyl ceník aktuální
- akce:
  - export (JSON / CSV)
  - smazat vybrané
  - sumarizace za období

### 7.3 Vazba na LOG {#vazba-na-log}

- každá účtenka musí obsahovat přímý odkaz na příslušné LOG soubory (na
  disk, lokální path).

## 8) EXIT -- potvrzení ukončení {#exit-potvrzení-ukončení}

Po stisknutí **EXIT**: - Zobrazí se potvrzovací dialog s upozorněním, že
uživatel přijde o neuloženou práci, pokud nedal **SAVE**. - Pokud
uživatel potvrdí, program se ukončí. - Pokud nepotvrdí, vrátí se do
programu.

## 9) SAVE / LOAD / LOAD REQUEST (persistování stavu) {#save-load-load-request-persistování-stavu}

### 9.1 SAVE {#save}

- Uloží rozpracovanou mapu nastavení tak, jak je v danou chvíli zvolena.
- Po stisknutí se zobrazí výběr adresáře a jména souboru.
- Formát musí být **JSON**.
- Strukturu JSON určí program.
- Musí být uloženy všechny volby a stav UI.

### 9.2 LOAD {#load}

- Umožní vybrat uložený JSON soubor a nahrát nastavení obrazovky.
- Po načtení se UI přepne do stavu odpovídajícího uloženému souboru.

### 9.3 LOAD REQUEST {#load-request}

- Umožní vybrat request uložený v **LOG/**.
- Po načtení se v programu nastaví všechna zadání a dialogová okna
  explicitně identicky, jak byla nastavena a vyplněná při odeslání
  requestu.
- Uživatel může provést drobné úpravy a odeslat znovu.

Pravidla: - Funkčně je LOAD REQUEST stejné jako LOAD, rozdíl je pouze v
tom, odkud se stav bere: - LOAD = soubor uložený tlačítkem SAVE - LOAD
REQUEST = request log z LOG, který obsahuje embednutý UI state a
technické vazby - LOAD REQUEST musí obnovit i technické vazby (model,
režim, IN/OUT, attached file-id listy, vector_store_id, batch_id,
response_id chain), ale pro nový běh se musí správně oddělit "historické
ID" od "nových volání".

## 10) Sekce na hlavní ploše (karty/sekce) {#sekce-na-hlavní-ploše-kartysekce}

Všechny níže uvedené sekce musí existovat. Jejich vizuální rozmístění je
dynamické (responsivní) podle šířky okna.

### 10.1 Sekce „Zadání" {#sekce-zadání}

Obsah: - Textový řádek (jednořádkové pole) s názvem: **„Název
projektu:"** - není povinné - je-li zadán, použije se ve všech
requestech jako identifikátor - Dialogové okno pro zadání (multiline): -
zobrazení cca **6 řádků** - při více řádcích posuvníky **horizontálně i
vertikálně**

### 10.2 Sekce „Připojené soubory" {#sekce-připojené-soubory}

- Tabulka souborů / id-files souborů.
- Tabulka by měla být vysoká tak, aby byla standardně vidět zhruba **2
  soubory**. Pokud je souborů víc, použije se **vertikální posuvný
  válec**.
- Do tabulky lze přesunout soubory ze sekce FILE API.
- Tyto soubory:
  - lze odkazovat v promptu přes file-id
  - objeví se v instructions jako jednotlivé soubory (každý zvlášť)
  - zároveň se objeví automaticky v promptu jako input
  - budou označeny jako **„pro informaci"**
- U každého souboru v tabulce bude ikonka **koše**, kterou lze z této
  tabulky soubor odstranit.

### 10.3 Sekce „IN" {#sekce-in}

Obsah: - Tlačítko **„VSTUP"** - Vedle něj textové pole (zobrazí
kompletní PATH zvoleného adresáře)

Chování: - Po stisku „VSTUP" uživatel vybere libovolný adresář. - Do
textového pole se uloží kompletní PATH.

Funkce při spuštění requestu (až při GO): - Pokud je vybrán INadresář: - rekurzivně načti všechny soubory včetně podadresářů - vyjmi
adresáře: **venv**, **.venv**, **LOG** - navíc vyjmi versing snapshot
adresáře: - adresář, jehož název odpovídá patternu (tj. končí 12
číslicemi a začíná shodně názvem root adresáře) - všechny **kompatibilní
soubory pro File API** uploaduj na File API - vytvoř mirror manifest
(soubor) se všemi soubory + memo o neuploadovaných

#### 10.3.1 Model capability check + fallback {#model-capability-check-fallback}

Před použitím **file_search + vector store** musí program ověřit, zda
zvolený model podporuje: - file_search tool - práci s vector store
(vector_store_ids)

Kontrola musí být robustní a může být provedena kombinací: - metadata z
Models endpointu (pokud dostupná) - bezpečný „probe" request a detekce
chyb typu „tool not supported / invalid tool".

**Pokud model podporuje file_search + vector store:** - vytvoř vector
store - připoj všechny uploadované soubory do vector store s atributem
jejich plné původní PATH - připoj mirror manifest do vector store (aby
ve store byla i existence neuploadovaných)

**Pokud model NEpodporuje file_search + vector store (fallback):** -
**nepoužívej** vector store ani file_search tool - použij jen Files
API: - uploadni kompatibilní soubory na Files API - uploadni manifest na
Files API - v requestech se pak mirror řeší takto: - v instructions
uveď: - seznam všech input souborů včetně jejich původních PATH -
file_id pro každý uploadovaný soubor - explicitně uveď manifest jako
soubor (s file_id) - v input přilož všechny tyto soubory jako input_file
(včetně manifestu) - bez tools a bez vector_store_ids

**Důležitá redundance (platí VŽDY):** - I když je zapnuté file_search +
vector store, program musí redundantně poslat: - manifest i jako upload
na Files API (aby měl file_id) - file_id manifestu (a všech input
souborů) vypsat v instructions - a současně tyto soubory přiložit jako
input_file v input

Označení (název) vector store: - použij **název projektu** + čas ve
formátu **DDMMRRRRHHMM**

### 10.4 Sekce „OUT" {#sekce-out}

Obsah: - Tlačítko **„IN=OUT"** - Tlačítko **„Výstup"** - Tlačítko
**„VERSING"** - Textové pole (výstupní PATH)

Chování: - „Výstup": vybere se adresář pro ukládání souborů přijatých v
Response. - „IN=OUT": - nastaví výstupní adresář na stejný jako
vstupní - aktivuje možnost stisknutí tlačítka **VERSING** - Ukládání
souborů: - do zvoleného OUT adresáře se uloží soubory přijaté v
Response - pokud ve stejném PATH existuje soubor stejného jména, **bez
upozornění se přepíše**

VERSING -- funkce: - Pokud je aktivní VERSING a přijde response alespoň
s jedním souborem, který se má uložit do OUT: - před prvním zápisem
program vytvoří ve zvoleném pracovním adresáři snapshot kopii aktuálního
stavu - snapshot adresář se vytvoří **uvnitř pracovního adresáře** -
název snapshot adresáře je

Příklad: - Projekt ABC je v adresáři `D:\PROJEKTY\ABC\`. - V adresáři
`D:\PROJEKTY\ABC\` jsou např. `.venv`, `LOG`, `app`, `data`, ... - Při
vytvoření nové verze se snapshot uloží do
`D:\PROJEKTY\ABC\ABC171220251634\`.

Pravidla kopírování při VERSING: - kopíruje se kompletní struktura
pracovního adresáře, **kromě**: - `venv`, `.venv`, `LOG` - a kromě všech
adresářů, které odpovídají versing konvenci - a samozřejmě kromě právě
vytvářeného snapshot adresáře - snapshot adresáře se považují za versing
a proto se **nikdy** nezahrnují do IN mirroru ani do manifestu.

### 10.5 Sekce „DIAGNOSTICS (WINDOWS / SSH)" {#sekce-diagnostics-windows-ssh}

V této sekci jsou volby: - **WINDOWS IN** (checkbox) - **WINDOWS OUT**
(checkbox) - **SSH IN** (checkbox) - **SSH OUT** (checkbox)

Zakázané kombinace: - Jakákoliv kombinace **WINDOWS** s **SSH** je
zakázána (tj. nelze mít současně žádný WINDOWS checkbox a žádný SSH
checkbox).

Povolené kombinace v rámci jedné skupiny: - WINDOWS IN může být společně
zvolena s WINDOWS OUT - SSH IN může být společně zvolena s SSH OUT

Vynucení závislostí (tiše): - pokud je zvolen **WINDOWS OUT**, musí být
zvolen **WINDOWS IN** (program automaticky zaškrtne WINDOWS IN) - pokud
je zvolen **SSH OUT**, musí být zvolen **SSH IN** (program automaticky
zaškrtne SSH IN)

Závislosti na výběru adresářů: - WINDOWS IN nebo SSH IN lze použít
jedině pokud je zvolen **IN adresář** - WINDOWS OUT nebo SSH OUT lze
použít jedině pokud je zvolen **OUT adresář**

Pokud uživatel zaškrtne volbu, která je v rozporu s výběrem adresářů,
program: - jasně zobrazí, co chybí (např. „Pro WINDOWS IN vyber IN
adresář") - a zablokuje GO, dokud nebude stav validní

Funkce: - **WINDOWS IN / SSH IN** - při spuštění „KÁJO GO'": - WINDOWS
IN: provede snímek kompletního nastavení Windows (Přesná specifikace "diagnostický balík" dle specifikace v příloze: "PŘÍLOHA FULL Windows Diagnostics.md")
SSH IN: po zadání IP adresy a autentizace, popřípadě jsou-li uloženy v sekci "NASTAVENÍ", automaticky stáhne
diagnostický snímek vzdáleného systému - (Přesná specifikace "diagnostický balík" dle specifikace v příloze: "PŘÍLOHA FULL Ubuntu (Web Server) Diagnostics.md")
(diagnostický balík), která se: - nahraje na Files API - zaznamená do
manifestu (včetně popisu obsahu a timestampů) - file_id se zapíše do
instructions - a zároveň se přiloží do input jako input_file části -
pokud je aktivní vector store, diagnostické soubory se navíc připojí do
vector store s atributy (např. `source=diagnostics`,
`scope=windows|ssh`, `captured_at=...`).

- **WINDOWS OUT / SSH OUT**
  - při spuštění „KÁJO GO'" program do instructions i do input
    redundantně zapíše očekávání, že výstup musí obsahovat:
    - vlastní skript
    - soubor **readmerepair.txt** s popisem změny systému a návodem k
      ručnímu použití
  - pro SSH OUT je skript **spustitelný na Windows PC** (tj. skript je
    připraven tak, aby z Windows provedl změny na vzdáleném SSH pomocí
    stejného typu přístupu, který byl použit při SSH IN).

Bezpečnostní upozornění: - diagnostické snapshoty mohou obsahovat
citlivá data; program musí před prvním použitím WINDOWS/SSH diagnostiky
zobrazit varování a vyžádat potvrzení. - pokud je v SETTINGS maskování
tajemství OFF, program upozorní, že citlivé údaje mohou skončit v LOG.

SSH UI (pokud je zvoleno SSH IN nebo SSH OUT): - program se zeptá na: -
uživatelské jméno (výchozí root) - IP adresu - autentizace: SSH key
(povinně podporovat; heslo volitelně jako fallback) - sudo se nepoužívá,
jen root.

### 10.6 Sekce „MODE" {#sekce-mode}

Obsah: - Tlačítko **„GENERATE"** - Tlačítko **„MODIFY"** - Tlačítko
**„QA"** - Pole **RESPONSE ID** (textové pole)

Pravidla: - Může být zvoleno vždy jen jedno z tlačítek
(GENERATE/MODIFY/QA). - Alespoň jedno musí být zvoleno vždy.

Režimy: - **GENERATE** - nesmí být zvolen IN adresář - musí být zvolen
OUT adresář

- **MODIFY**
  - musí být zvolen IN i OUT adresář
- **QA**
  - nesmí být zvolen ani IN ani OUT adresář
  - do instructions i do input se dá instrukce, že se čeká **textová
    odpověď**, žádný soubor

RESPONSE ID: - Umožňuje zadat Response-ID ručně. - Je-li vyplněno: -
použije se v requestu jako řetězení (previous_response_id). - Není-li
vyplněno: - request začne jako nový (bez previous_response_id).

### 10.7 Sekce „Model OpenAI" {#sekce-model-openai}

Obsah: - Tlačítko **„GET MODELS"** - Roletka (dropdown) pro výběr OpenAI
modelu

Chování: - Po stisknutí „GET MODELS" se načtou aktuálně dostupné OpenAI
modely pro uložený API key. - Aktualizuje se seznam modelů ve
dropdown. - Vybraný model zůstává viditelný v roletce.

### 10.8 Sekce „BATCH MONITOR" {#sekce-batch-monitor}

Funkce: - seznam batch jobů (minimálně: "otevřené" = vše kromě
completed/failed/cancelled/expired) - tlačítko "REFRESH" - zobrazení
stavu a času vytvoření - tlačítko "DOWNLOAD RESULT" (pokud je hotovo) -
tlačítko "OPEN LOG" (link do LOG) - "CANCEL" (pokud API dovolí a
uživatel chce)

### 10.9 Sekce „GO" {#sekce-go}

Obsah: - Tlačítko **„KÁJO GO'"** - Přepínač **„SEND AS C (BATCH)"**

Chování: - Spustí kroky v pořadí podle nastavení a provede plně
automatické zpracování všeho, co je definováno na panelu. - Během běhu
se zobrazuje progress dialog (detailní kroky, %, ETA). - Vše se loguje
do LOG/.

### 10.10 Sekce „ANSWARE" {#sekce-answare}

Obsah: - Dialogové okno cca **6 řádků** - Nadpis dialogového okna bude
zobrazeno **Response ID** - V dialogovém okně se zobrazí odpověď z
response

Pod oknem tlačítka: - **CTRL+C** - **RESPONSE** - **SCRIPT**

CTRL+C: - zkopíruje obsah dialogového okna včetně Response ID do
schránky - vložení musí být jako neformátovaný text

RESPONSE: - zkopíruje přijaté Response ID do pole MODE/RESPONSE ID

SCRIPT: - je aktivní pouze pokud poslední response obsahovala skript +
`readmerepair.txt` - po stisknutí: - program zobrazí potvrzení s
varováním o nevratnosti - po potvrzení spustí skript bez dry runu - u
SSH skriptu použije stejné IP/uživatelské jméno/klíč nebo heslo, které
byly zadány při odesílání requestu (a program je drží jako součást run
state) - uživatel je informován o výsledku ve vyskakovacím okně - do LOG
se uloží stdout/stderr, návratový kód a audit provedených změn (pokud je
ze skriptu dostupný)

### 10.11 Sekce „LOCAL FILES" {#sekce-local-files}

Obsah: - tabulka souborů (cca 3--5 souborů, jinak scroll) - tlačítka pod
tabulkou: - **VLOŽ** - **UPLOAD**

Chování: - „VLOŽ": - uživatel vybere soubor - soubor se vloží do
tabulky - lze vybrat více souborů - každý řádek má ikonu pro smazání z
tabulky - „UPLOAD": - všechny soubory z tabulky uploaduj na File API s
purpose **"user data"** - po uploadu: - automaticky aktualizuj přehled
souborů v sekci FILE API - tabulka LOCAL FILES se vyprázdní

### 10.12 Sekce „FILE API" {#sekce-file-api}

Obsah: - tabulka souborů (cca 4 souborů, jinak scroll) - tlačítka pod
tabulkou: - **PŘIPOJ** - **SMAŽ** - **DEL ALL**

Chování: - Tabulka: - kliknutím lze vybrat více souborů (multi-select) -
„PŘIPOJ": - vybrané soubory se přesunou do sekce „Připojené soubory" -
„SMAŽ": - vybrané soubory smaž na File API - „DEL ALL": - smaž na File
API všechny soubory

### 10.13 Sekce „VECTOR STORES" {#sekce-vector-stores}

Funkce: - možnost se podívat, jaké aktuální vector store jsou založeny -
co v nich je - prohlížet si jejich obsah - nastavovat souborům ručně
atributy - jednotlivé soubory z vector store vyřazovat nebo zařazovat -
nastavovat expiraci

Povinné: - list vector store - detail vybraného store: - expirace
(view + update) - list souborů + jejich attributes - odstranit soubor ze
store - přidat soubor do store (z Files API) - zobrazení "usage /
velikost" (pokud API poskytuje) - vše logovat (co bylo změněno a kdy)

## 11) OpenAI request pipeline -- logika A/B variant + tok C (Batch-only) {#openai-request-pipeline-logika-ab-variant-tok-c-batch-only}

### 11.1 Základní pravidla request builderu (platí pro A/B/QA) {#základní-pravidla-request-builderu-platí-pro-abqa}

**Temperature policy:** - Jakmile je cílem vracet **obsah výstupního
souboru** (tj. kroky **A3_FILE** a **B3_FILE**), nastav temperature na
**0.0**. - Pro všechny ostatní requesty používej temperature v rozsahu
**0.0--0.2** (defaultně **0.2**, pokud není důvod snížit).

Redundance výstupu: - Vždy implementuj redundantní zadání očekávaného
výstupu: - (a) v instructions je kontrakt - (b) v input je redundantně
zopakovaný kontrakt

Projekt: - Pokud je vyplněn „Název projektu", použij ho jako
identifikátor v každém requestu (např. v instructions a v log
souborech).

Připojené soubory: - Všechny soubory v sekci „Připojené soubory": - musí
být v requestu: 1) vyjmenované v instructions jako „pro informaci"
(každý zvlášť) 2) a zároveň přiložené v input jako input_file části

Řetězení: - Pokud je vyplněn RESPONSE ID: - první request v daném běhu
použije previous_response_id = - pokud není vyplněn, nezačínej řetězení

Diagnostika (WINDOWS/SSH) -- redundance: - Pokud je aktivní WINDOWS IN /
SSH IN: - diagnostické soubory se posílají redundantně: - existence +
popis + file_id v instructions - a zároveň jako input_file v inputu - a
případně i ve vector store, pokud je aktivní - Pokud je aktivní WINDOWS
OUT / SSH OUT: - očekávání skriptu + `readmerepair.txt` se píše
redundantně: - do instructions - i do input

### 11.2 Volba varianty podle MODE {#volba-varianty-podle-mode}

- **GENERATE** → použij sérii **A1 → A2 → A3-X**
- **MODIFY** → použij sérii **B1 → B2 → B3-X** (protože IN vytváří
  mirror; primárně vector store + file_search, fallback dle 10.3.1)
- **QA** → pošli **1 request**, který v instructions i v input říká, že
  se čeká jen **textová odpověď, žádný soubor**, a nepoužije IN/OUT

### 11.3 Chunking pro soubory delší než 500 řádků (A/B) {#chunking-pro-soubory-delší-než-500-řádků-ab}

Pro A3/B3: - Pokud má výstup souboru více než 500 řádků: - musí se
vracet po chuncech - program musí iterovat requesty pro stejný path,
dokud soubor nebude kompletní - V requestu pro file content se bude
měnit jen path (a případně chunk_index).

## 12) Tok C (Batch-only, bez pipeline návazností, bez vstupních souborů, vše v jedné odpovědi) {#tok-c-batch-only-bez-pipeline-návazností-bez-vstupních-souborů-vše-v-jedné-odpovědi}

Požadavek: - C je vlastní nadefinovaný request, kde budou instructions
stejné obsahově, jako, když se posílá prompt pro generování programu,
ale bude naprosto separátně v programu sestavován a validován. - C je
jen přes BATCH (nikdy synchronně). - C nevyužívá A1/A2/A3 ani B1/B2/B3,
nemá řetězení, nemá previous_response_id. - C nepoužívá žádný vstupní
soubor: - žádný IN - žádné attached files - žádné file_search - žádné
vector_store_ids - C vrací v jedné odpovědi najednou všechny soubory. -
Jediné, co se využije ze stávající logiky, je zpracování přijatých
souborů (uložení do OUT, VERSING, logování, evidence cen).

### 12.1 UI a validace pro C {#ui-a-validace-pro-c}

Pokud uživatel zvolí "SEND AS C (BATCH)" - je to samostatný tok -
validace: - OUT musí být vybrán - IN nesmí být vybrán - připojené
soubory musí být prázdné - RESPONSE ID se nepoužívá - model musí být
zvolen

Poznámka k diagnostice: - WINDOWS/SSH volby lze použít jen pokud jejich
závislosti na IN/OUT dávají smysl. - protože C nemá IN, diagnostika IN
je v C zakázaná. - diagnostika OUT může být v C použita pouze tehdy,
pokud je zvolena a validace je splněna (a pak C musí vrátit i skript +
readmerepair).

### 12.2 C request kontrakt {#c-request-kontrakt}

C musí vyžadovat jediný výstupní JSON dokument: - žádné markdown
code-fences - žádné komentáře - žádné dodatečné vysvětlování mimo JSON

**KONTRAKT C_FILES_ALL:**

    {
      "contract": "C_FILES_ALL",
      "project": {
        "name": "string",
        "target_os": "Windows 10/11",
        "runtime": "string",
        "language": "string"
      },
      "root": "string",
      "files": [
        {
          "path": "relative/path/file.ext",
          "purpose": "string",
          "content": "string"
        }
      ],
      "build_run": {
        "prerequisites": ["string"],
        "commands": ["string"],
        "verification": ["string"]
      },
      "notes": ["string"]
    }

C request instructions musí obsahově odpovídat tomu, co jinak posíláš
jako prompt pro generování programu (včetně požadavků na robustnost,
logování, UI styl, atd.), ale C request builder je sestavuje samostatně.

Pokud je aktivní diagnostika OUT (WINDOWS OUT nebo SSH OUT): - C request
navíc explicitně vyžaduje, aby `files[]` obsahoval: -
`readmerepair.txt` - skript(y)

### 12.3 Batch implementace pro C {#batch-implementace-pro-c}

- vytvoř JSONL, který obsahuje právě 1 request (jedna řádka = jeden
  request na /responses)
- upload JSONL
- vytvoř batch job
- sleduj stav přes BATCH MONITOR
- po dokončení stáhni výsledek

Validace výsledku: - `json.loads()` - validace schématu C_FILES_ALL -
validace path pravidel: - relativní - nesmí začínat `/` - nesmí
obsahovat `..` - nesmí obsahovat `\\` - žádné duplicity

Pokud validace selže: - výstup se uloží do karantény `OUT/_invalid/` a
jasně se označí (v UI popup + log), a soubory se nezapíší do cílových
path.

### 12.4 Uložení souborů z C {#uložení-souborů-z-c}

- uložit všechny `files[]` do OUT
- pokud existuje stejný soubor, bez upozornění přepsat
- pokud je zapnutý VERSING, provést VERSING copy před prvním zápisem

## 13) Explicitní kontrakty (A/B) -- zachovat přesně (instructions + redundantní input) {#explicitní-kontrakty-ab-zachovat-přesně-instructions-redundantní-input}

Níže jsou přesné kontrakty pro 6 variant request JSON, které má „Kája"
generovat a posílat dle nastavení.

> Důležité: Kontrakty jsou postavené na instructions (bez text.format).
> Program musí odpovědi parsovat přes json.loads() a validovat.

### 13.0 Politika výstupů souborů (kritické) {#politika-výstupů-souborů-kritické}

- Pokud model generuje nebo modifikuje soubory, nikdy nesmí vracet
  DIFF/patch/změny.
- Očekává se kompletní výsledné znění souboru:
  - buď celé v jednom content, nebo (u chunkingu) po částech, které se
    po spojení stanou kompletním souborem.
- Žádné markdown code-fences, žádné komentáře, žádné dodatečné
  vysvětlování mimo JSON.

# 13A) A-varianta: neposílám jako vstup žádný soubor {#a-a-varianta-neposílám-jako-vstup-žádný-soubor}

## A1) Request JSON -- „PLAN (manifest / návrh projektu)" {#a1-request-json-plan-manifest-návrh-projektu}

- Bez file_search
- Bez vector store

<!-- -->

    {
      "model": "<MODEL_FROM_UI>",
      "temperature": 0.2,
      "instructions": "Jsi senior software architekt a implementátor. MASTER: žádné externí soubory. OUTPUT: VRAŤ POUZE validní JSON. ŽÁDNÝ markdown, žádné komentáře, žádný další text. KONTRAKT A1_PLAN: {\"contract\":\"A1_PLAN\",\"project\":{\"name\":string,\"one_liner\":string,\"target_os\":string,\"language\":string,\"runtime\":string},\"assumptions\":[string],\"requirements\":{\"functional\":[string],\"non_functional\":[string],\"constraints\":[string]},\"architecture\":{\"modules\":[{\"name\":string,\"responsibility\":string}],\"data_flow\":[string],\"error_handling\":[string],\"security_notes\":[string]},\"build_run\":{\"prerequisites\":[string],\"commands\":[string],\"verification\":[string]},\"deliverable_policy\":{\"file_generation_strategy\":\"PLAN->STRUCTURE->FILE_CONTENT\",\"max_lines_per_chunk\":500}}",
      "input": "ZADÁNÍ PROGRAMU: <USER_SPEC>. REDUNDANTNÍ KONTRAKT: vrať pouze JSON dle A1_PLAN (bez md, bez textu navíc)."
    }

## A2) Request JSON -- „STRUCTURE (výstup vlastní souborové struktury)" {#a2-request-json-structure-výstup-vlastní-souborové-struktury}

- Navazuje přes previous_response_id

<!-- -->

    {
      "model": "<MODEL_FROM_UI>",
      "previous_response_id": "<RESP_ID_FROM_A1_OR_USER_FIELD>",
      "temperature": 0.2,
      "instructions": "Jsi generátor projektové struktury podle schváleného plánu. OUTPUT: VRAŤ POUZE validní JSON. ŽÁDNÝ markdown ani další text. RULES: path musí být relativní, nesmí začínat '/', nesmí obsahovat '..' ani '\\\\', žádné duplicity. KONTRAKT A2_STRUCTURE: {\"contract\":\"A2_STRUCTURE\",\"root\":string,\"files\":[{\"path\":string,\"purpose\":string,\"language\":string,\"generated_in_phase\":\"A3\"}]}",
      "input": "VYGENERUJ FILE STRUCTURE pro projekt dle předchozího plánu. REDUNDANTNÍ KONTRAKT: vrať pouze JSON dle A2_STRUCTURE."
    }

## A3) Request JSON -- „FILE CONTENT (obsah 1 konkrétního souboru)" {#a3-request-json-file-content-obsah-1-konkrétního-souboru}

- Opakované volání pro každý path
- Chunking \> 500 řádků

<!-- -->

    {
      "model": "<MODEL_FROM_UI>",
      "previous_response_id": "<RESP_ID_FROM_A2_OR_USER_FIELD>",
      "temperature": 0.0,
      "instructions": "Jsi generátor obsahu jednoho konkrétního souboru podle A2_STRUCTURE. OUTPUT: VRAŤ POUZE validní JSON. ŽÁDNÝ markdown ani další text. KRITICKÉ: content je vždy čistý obsah souboru (ne DIFF, ne patch). U chunkingu posílej po částech, které se spojí do kompletního souboru. CHUNK: max 500 řádků v jednom chunku, dlouhé soubory vrať po částech. KONTRAKT A3_FILE: {\"contract\":\"A3_FILE\",\"path\":string,\"chunking\":{\"max_lines\":500,\"chunk_index\":integer,\"chunk_count\":integer,\"has_more\":boolean,\"next_chunk_index\":integer|null},\"content\":string}",
      "input": "Vrať obsah souboru PATH=<PATH_FROM_A2>. Pokud je dlouhý, použij chunking. Volitelně: CHUNK_INDEX=<N>. REDUNDANTNÍ KONTRAKT: vrať pouze JSON dle A3_FILE. KRITICKÉ: žádné DIFF/patch, jen čistý obsah souboru (nebo jeho chunk)."
    }

# 13B) B-varianta: posílám zrcadlo souborů / referenční soubory do vector store a zapnu file_search {#b-b-varianta-posílám-zrcadlo-souborů-referenční-soubory-do-vector-store-a-zapnu-file_search}

Pokud model nepodporuje file_search / vector store, v B-variantě se
vynechá tools a místo toho se použijí soubory přes Files API + manifest
dle 10.3.1.

## B1) Request JSON -- „PLAN (na základě mirroru)" {#b1-request-json-plan-na-základě-mirroru}

- file_search ON (pokud podporováno)
- vector_store_ids použij z IN kroku

<!-- -->

    {
      "model": "<MODEL_FROM_UI>",
      "temperature": 0.2,
      "tools": [
        { "type": "file_search", "vector_store_ids": ["<VS_ID_FROM_IN_STEP>"] }
      ],
      "instructions": "Jsi senior debug/maintenance inženýr. MASTER SOURCE OF TRUTH: existující soubory/config jsou pouze ve vector store přes file_search. Nic si nevymýšlej. KRITICKÉ: i když máš file_search, ber v úvahu i přiložený manifest + input file-id jako redundantní zdroj. OUTPUT: VRAŤ POUZE validní JSON. ŽÁDNÝ markdown ani další text. WORKFLOW: vždy nejdřív použij file_search, pokud něco chybí uveď missing_inputs. KONTRAKT B1_PLAN: {\"contract\":\"B1_PLAN\",\"context\":{\"vector_store_ids\":[string],\"assumed_root\":string},\"diagnosis\":{\"summary\":string,\"evidence\":[{\"path\":string,\"reason\":string}],\"likely_root_causes\":[string]},\"change_plan\":{\"goals\":[string],\"files_to_modify\":[{\"path\":string,\"intent\":string}],\"files_to_add\":[{\"path\":string,\"intent\":string}],\"verification_steps\":[string]},\"missing_inputs\":[string]}",
      "input": "MÁŠ PŘÍSTUP K MIRRORU V VECTOR STORE (file_search je zapnutý, pokud model podporuje). ÚKOL: <USER_TASK>. REDUNDANTNÍ KONTRAKT: vrať pouze JSON dle B1_PLAN."
    }

## B2) Request JSON -- „STRUCTURE (touched files)" {#b2-request-json-structure-touched-files}

- Navazuje přes previous_response_id

<!-- -->

    {
      "model": "<MODEL_FROM_UI>",
      "previous_response_id": "<RESP_ID_FROM_B1_OR_USER_FIELD>",
      "temperature": 0.2,
      "tools": [
        { "type": "file_search", "vector_store_ids": ["<VS_ID_FROM_IN_STEP>"] }
      ],
      "instructions": "Jsi implementátor změn nad existujícím systémem. MASTER: existující soubory a jejich aktuální obsah jsou pouze z vector store (file_search). KRITICKÉ: i když máš file_search, ber v úvahu i přiložený manifest + input file-id jako redundantní zdroj. OUTPUT: VRAŤ POUZE validní JSON. ŽÁDNÝ markdown ani další text. RULES: do touched_files nedávej nic, co neexistuje ve store (pokud to není nové). KONTRAKT B2_STRUCTURE: {\"contract\":\"B2_STRUCTURE\",\"touched_files\":[{\"path\":string,\"action\":\"modify\"|\"add\",\"intent\":string}],\"invariants\":[string]}",
      "input": "Na základě předchozího plánu a mirroru ve vector store vrať seznam souborů, které se budou měnit/přidávat. REDUNDANTNÍ KONTRAKT: vrať pouze JSON dle B2_STRUCTURE."
    }

## B3) Request JSON -- „FILE CONTENT (1 soubor)" {#b3-request-json-file-content-1-soubor}

- Opakované volání pro každý path
- Chunking \> 500 řádků
- Pro modify musí vycházet z aktuální verze ve store (file_search)

<!-- -->

    {
      "model": "<MODEL_FROM_UI>",
      "previous_response_id": "<RESP_ID_FROM_B2_OR_USER_FIELD>",
      "temperature": 0.0,
      "tools": [
        { "type": "file_search", "vector_store_ids": ["<VS_ID_FROM_IN_STEP>"] }
      ],
      "instructions": "Jsi implementátor obsahu jednoho konkrétního souboru. MASTER: pro modify vždy načti aktuální obsah souboru přes file_search a aplikuj změny. KRITICKÉ: content je vždy kompletní výsledné znění souboru (ne DIFF, ne patch). U chunkingu posílej po částech, které se spojí do kompletního souboru. OUTPUT: VRAŤ POUZE validní JSON. ŽÁDNÝ markdown ani další text. CHUNK: max 500 řádků v chunku. KONTRAKT B3_FILE: {\"contract\":\"B3_FILE\",\"path\":string,\"action\":\"modify\"|\"add\",\"chunking\":{\"max_lines\":500,\"chunk_index\":integer,\"chunk_count\":integer,\"has_more\":boolean,\"next_chunk_index\":integer|null},\"content\":string,\"notes\":[string]}",
      "input": "Vrať výsledný obsah souboru PATH=<PATH_FROM_B2> (ACTION=<modify|add>). Použij mirror ve vector store jako jediný zdroj pravdy pro existující verzi (pokud je dostupné). Pokud je dlouhý, vrať po chuncech. Volitelně: CHUNK_INDEX=<N>. REDUNDANTNÍ KONTRAKT: vrať pouze JSON dle B3_FILE. KRITICKÉ: žádné DIFF/patch, jen čistý obsah souboru (nebo jeho chunk)."
    }

## 14) GO -- exekuce kroků podle UI {#go-exekuce-kroků-podle-ui}

Po stisku „KÁJO GO'" proveď:

### 14.1 Validace nastavení {#validace-nastavení}

- MODE vybrán přesně jeden
- GENERATE: IN nesmí být vybrán, OUT musí být vybrán
- MODIFY: IN i OUT musí být vybrán
- QA: IN ani OUT nesmí být vybrán
- C: OUT musí být vybrán, IN nesmí být vybrán, attached files musí být
  prázdné, běží jen přes Batch
- API key musí být dostupný (z uložených systémových proměnných nebo z
  dialogu)
- Diagnostics:
  - nelze kombinovat WINDOWS a SSH
  - IN volby vyžadují vybraný IN adresář  - OUT volby vyžadují vybraný OUT adresář
  - OUT volby si automaticky vynutí příslušnou IN volbu

### 14.2 Připojené soubory (informational) -- pouze A/B/QA {#připojené-soubory-informational-pouze-abqa}

- Sestav seznam „Připojených souborů" pro instructions + input
- Tyto soubory přidej do každého requestu jako:
  - textový blok v instructions (pro informaci)
  - content parts input_file v inputu

### 14.3 Diagnostika IN (WINDOWS IN / SSH IN) -- pokud je zvoleno {#diagnostika-in-windows-in-ssh-in-pokud-je-zvoleno}

- Vygeneruj diagnostický balík:
  - WINDOWS IN: snapshot Windows - Viz příloha # PŘÍLOHA FULL Windows Diagnostics
  - SSH IN: snapshot vzdáleného systému # PŘÍLOHA FULL Ubuntu (Web Server) Diagnostics

- Uploadni diagnostické soubory na Files API
- Zapiš je do diagnostického manifestu + do mirror manifestu (jako
  externí artefakty s popisem)
- Přilož je redundatně:
  - v instructions vypiš file_id + popis
  - v input je přilož jako input_file
  - pokud existuje vector store, připoj je i do store

### 14.4 IN krok (pouze když je IN zvolen) -- pouze MODIFY {#in-krok-pouze-když-je-in-zvolen-pouze-modify}

- Rekurzivně projdi vstupní adresář (mimo venv, .venv, LOG a mimo
  versing snapshot adresáře dle 10.3)
- Uploadni kompatibilní soubory na Files API
- Vytvoř mirror manifest se všemi soubory + memo o neuploadovaných
- Ověř podporu file_search + vector store pro zvolený model
- pokud podporuje:
  - Vytvoř vector store pojmenovaný „\_"
  - Připoj všechny uploadované soubory do vector store s atributem
    jejich plné původní PATH
  - Připoj mirror manifest do vector store
  - pokud jsou k dispozici diagnostické soubory, připoj i je
- pokud nepodporuje:
  - nepoužívej vector store, nepoužívej file_search
  - používej jen Files API a manifest (viz 10.3.1)

### 14.5 Očekávání skriptu (WINDOWS OUT / SSH OUT) -- pokud je zvoleno {#očekávání-skriptu-windows-out-ssh-out-pokud-je-zvoleno}

- Do instructions i do input přidej povinné očekávání:
  - response musí obsahovat skript(y)
  - response musí obsahovat `readmerepair.txt`
- Po zpracování response:
  - `readmerepair.txt` se zobrazí v ANSWARE okně
  - aktivuje se tlačítko SCRIPT

### 14.6 Request pipeline podle režimu {#request-pipeline-podle-režimu}

- Pokud je zvoleno "SEND AS C (BATCH)": tok dle kapitoly 12.
- Jinak:
  - GENERATE: A1 → A2 → pro každý file v A2: A3 (chunk loop) → ukládat
    do OUT
  - MODIFY: B1 → B2 → pro každý touched file v B2: B3 (chunk loop) →
    ukládat do OUT
  - QA: 1 request: text-only (v instructions i input explicitně), bez
    ukládání souborů

### 14.7 OUT ukládání {#out-ukládání}

- Pokud je aktivní VERSING a přijde alespoň jeden soubor k uložení:
  - udělej snapshot kopii dle pravidel v 10.4
- Ukládej soubory:
  - bez upozornění přepisuj existující stejné soubory

### 14.8 ANSWARE panel {#answare-panel}

- Zobraz Response ID v titulku
- Zobraz odpověď (raw nebo extrahovaný text/JSON) v okně
- CTRL+C kopíruje Response ID + text
- RESPONSE přenese Response ID do pole MODE/RESPONSE ID
- Pokud je přítomen `readmerepair.txt`, zobraz jeho obsah a zpřístupni
  SCRIPT

## 15) File API panel -- synchronizace {#file-api-panel-synchronizace}

- Po každém uploadu a delete:
  - refresh seznamu FILE API
- Po uploadu z LOCAL FILES:
  - vyprázdni LOCAL FILES tabulku

## 16) Doplňující definice „kompatibilní soubory pro File API" {#doplňující-definice-kompatibilní-soubory-pro-file-api}

Implementuj výběr souborů pro upload tak, aby: - běžné textové konfigy a
zdrojáky byly uploadovány - binární soubory a extrémně velké soubory
byly detekovány jako nekompatibilní a zaznamenány do manifestu - `.env`
a jiné citlivé soubory: preferuj neuploadovat a zaznamenat do manifestu
(a případně generovat bezpečný seznam klíčů bez hodnot)

Tohle je součást robustní implementace, ale nesmí to porušit zásadu:
existence souborů musí být v mirroru zachycena.

## 17) Další povinné rozšíření (detailně) {#další-povinné-rozšíření-detailně}

### 17.A Spolehlivost a řízení běhu {#a-spolehlivost-a-řízení-běhu}

#### A1) Cancel/Stop běhu

- V UI musí být vždy dostupné tlačítko "STOP" (součást progress
  dialogu).
- STOP provede korektní ukončení:
  - zrušení čekání na batch (polling)
  - zrušení uploadů (pokud SDK umožní přerušení) nebo jejich bezpečné
    dokončení s jasným stavem
  - zrušení dalších requestů v pipeline (nezahajovat nové)
- STOP nikdy nesmí nechat aplikaci ve stavu "zamrzlo"; progress dialog
  se přepne do režimu "Stopping..." a po dokončení se zavře.
- Po STOP musí existovat možnost:
  - buď bezpečně "Resume"
  - nebo "Close run" (ukončit run)

#### A2) Resume běhu po pádu / restartu {#a2-resume-běhu-po-pádu-restartu}

- Program musí umět z LOG rekonstruovat poslední stav runu:
  - jaké kroky proběhly
  - jaké file_id byly uploadnuté
  - jaké response_id/batch_id už existují
  - jaké soubory už byly uloženy
- Při startu program nabídne "RESUME LAST RUN", pokud najde nedokončený
  run.
- Resume musí být idempotentní:
  - pokud se krok už provedl, přeskočí se
  - pokud není jistota, krok se provede znovu bezpečným způsobem (např.
    znovu stáhnout batch result, znovu validovat, znovu zapsat do
    karantény místo přepsání)

#### A3) Rate-limit & retry politika {#a3-rate-limit-retry-politika}

- Implementuj retry s exponenciálním backoff + jitter.
- Circuit breaker:
  - pokud se opakovaně vrací rate-limit nebo 5xx, na čas se zastaví nové
    requesty a UI ukáže "Cooling down".
- Retry pravidla:
  - retryovat transient chyby (429, 5xx, timeouts)
  - nikdy nere-tryovat chyby validace kontraktů (to je logická chyba
    výstupu)
- Veškeré retry pokusy se logují.

### 17.B Bezpečnost práce se soubory a snapshoty {#b-bezpečnost-práce-se-soubory-a-snapshoty}

#### B1) Secret scanner + redakce {#b1-secret-scanner-redakce}

- Před uploadem do Files API (mirror i diagnostika) program projede
  soubory a detekuje:
  - `.env`
  - klíče/tokeny (heuristiky a regexy)
  - privátní klíče/certy
- Default chování:
  - citlivé soubory preferuj neuploadovat
  - místo toho zapiš do manifestu, že existují, a uveď bezpečný popis
    (např. seznam klíčů bez hodnot)
- Pokud uživatel v SETTINGS vypne bezpečnostní omezení, program umožní
  upload i citlivých souborů, ale vždy zobrazí varování.

#### B2) Allow/Deny list přípon i cest

- V SETTINGS existuje konfigurace:
  - allow/deny list přípon
  - allow/deny list cest (glob patterns)
- Odděleně pro:
  - IN mirror
  - diagnostické snapshoty
- V manifestu musí být vždy vidět, co bylo vynecháno a proč.

#### B3) Šifrování logů + panic wipe {#b3-šifrování-logů-panic-wipe}

- Volitelné šifrování lokálních logů (minimálně: symetrické šifrování
  celé LOG složky nebo per-file, klíč uložen dle Windows bezpečného
  úložiště, pokud dostupné).
- "Panic wipe":
  - smaže lokální cache (dočasné soubory, stažené batch výsledky, price
    cache)
  - volitelně smaže i nešifrované logy
  - vždy vyžádá potvrzení

### 17.C Vývojářské workflow {#c-vývojářské-workflow}

#### C1) Dry-run režim pro MODIFY

- Volitelně v SETTINGS.
- V dry-run režimu pro MODIFY:
  - AI nejdřív vrátí seznam změn + rizika + touched files (bez
    generování obsahu)
  - uživatel musí potvrdit pokračování, teprve pak se spustí B3
    generování obsahů
- Dry-run výstup se loguje a je součástí run bundle.

#### C2) Post-run hooks

- Po uložení souborů program může spustit:
  - testy
  - lint
  - format
- Hooky lze spustit:
  - lokálně
  - nebo přes SSH (pokud je k dispozici SSH konfigurace pro hooky)
- Výstup hooků (stdout/stderr, návratové kódy) se loguje.

#### C3) Diff viewer

- V UI existuje diff viewer pouze pro přehled uživatele.
- Do AI se vždy posílá full content dle kontraktů.

### 17.D Observabilita (kromě LOG souborů) {#d-observabilita-kromě-log-souborů}

#### D1) Run timeline

- Program vede interní timeline:
  - krok
  - start/end timestamp
  - výsledek
  - související IDs (file_id, response_id, batch_id, vector_store_id)
- Timeline je viditelná v UI a exportovatelná do LOG.

#### D2) Export "Run bundle" (zip)

- Program umí vytvořit zip balík:
  - requesty
  - response
  - manifesty
  - snapshoty (pokud uživatel povolí; jinak jen odkazy)
  - skripty
  - `readmerepair.txt`
  - timeline
- Export je dostupný z UI (např. z progress dialogu po dokončení).

### 17.E Pricing (povoleno, implementovat) {#e-pricing-povoleno-implementovat}

- Program podporuje automatickou aktualizaci ceníku z oficiálních zdrojů
  (konfigurovatelný endpoint/URL v SETTINGS).
- Pro každý běh se ukládá účtenka:
  - usage (input/output tokens)
  - batch discount/pricing
  - tool calls (file_search)
  - storage-days odhad (z usage_bytes a času držení)
- Pokud ceny nelze ověřit (offline, endpoint nedostupný):
  - běh může pokračovat
  - účtenka je označena „odhad / neověřeno"

## 18) Co musí výstupní program „Kája" dodat {#co-musí-výstupní-program-kája-dodat}

- Plně funkční aplikaci dle UI a logiky výše
- Kompletní zdrojové soubory projektu
- Jasné instrukce pro spuštění (např. pip install -r requirements.txt +
  python ui_main.py nebo ekvivalent)
- Program musí implementovat přesně uvedené kroky, kontrakty A1/A2/A3 a
  B1/B2/B3, logování, progress dialogy, SAVE/LOAD/LOAD REQUEST, API-KEY
  správu, FILE API management.
- Program musí implementovat:
  - Windows/SSH diagnostics (IN snapshot + OUT očekávání skriptu)
  - Vector store management
  - Batch monitor a tok C (Batch-only)
  - Pricing screen `$` a účtenky
  - VERSING dle pravidel v 10.4

## 19) Pokyny k designu {#pokyny-k-designu}

1)  UI musí být černobílé (minimalisticky), s následujícími pravidly:

- globální pozadí černé (background-color: black)
- text bílý (color: white)
- rámečky bílé (border: 1--2px solid white)
- výjimkou je pouze tlačítko EXIT (a případně varovné tlačítko stejného
  typu):
  - pozadí červené, text černý tučný, zaoblené rohy; při stisku inverze
    (pozadí černé, text červený, červený rámeček).

2)  Font:

- v celém UI používej font "Montserrat" (bezpatkový)
- nadpisy sekcí a panelů: Montserrat bold, VELKÁ PÍSMENA
- text v tlačítkách: Montserrat, bílé písmo na černém pozadí (kromě
  EXIT)
- fonty se načítají z resources/montserrat_bold.ttf a
  resources/montserrat_regular.ttf

3)  Tlačítka (standard):

- pozadí černé, text bílý
- rámeček: 2px solid white, zaoblené rohy (border-radius cca 10--15 px)
- padding 4--8 px
- při stisku/aktivaci vždy inverze barev (pozadí bílé, text černý)

4)  Panely a sekce:

- bílý rámeček, zaoblené rohy, černé pozadí
- nadpis sekce vycentrovaný, Montserrat bold, bílé písmo
- pokud bude použita jiná UI technologie než Qt Widgets, musí být
  vizuální styl ekvivalentní

5)  Textová pole:

- pro zadání dotazu a zobrazení odpovědi použij více-řádková pole s
  bílým pozadím a černým textem
- zaoblené rohy, vnitřní odsazení (padding)

6)  Tabulky a seznamy:

- QTableWidget: černé pozadí, bílé písmo, bílé mřížky, hlavička s černým
  pozadím a bílým textem
- vybraný řádek je plně invertovaný (pozadí bílé, text černý)
- QListWidget: černé pozadí, bílé písmo, bílý rámeček, zaoblené rohy

7)  Status dialogy ("teploměr"):

- QDialog: černé pozadí, bílý rámeček, zaoblené rohy
- uvnitř: název (bold), více-řádkové textové pole s černým pozadím,
  bílým textem a bílým rámečkem
- QProgressBar: černé pozadí, bílý rámeček, text bílý, chunk bílý,
  zaoblené rohy

8)  Všechny nové komponenty musí tento styl plně respektovat.

9)  Každý roh musí být zaoblený. Zákaz ostrých rohů.


# PŘÍLOHA FULL Ubuntu (Web Server) Diagnostics
Tento manuál definuje **FULL diagnostický balík pro Ubuntu server**, typicky hostující webový stack (např. **nginx**, databáze, Python aplikace, webhooky, certifikáty). Cílem je poskytnout **konzistentní adresář se soubory** (bez ZIP) tak, aby bylo možné rychle určit příčinu chyb (konfigurace, procesy, síť, certifikáty, permissions, venv, systémové limity).

> Výstup je **adresář se soubory** na Ubuntu (a volitelně stažený na Windows). Neprovádí se kopie databází ani tajných klíčů – jen konfigurace, metadatové přehledy a logy.

---

## Zásady bezpečnosti (doporučeno)
- **Neexportovat** privátní klíče (TLS, SSH), tokeny a hesla.
- Konfigurační soubory, které mohou obsahovat tajemství, exportovat buď:
  - se **základním maskováním** (např. `password=***`), nebo
  - jako **metadata** (cesta, vlastník, práva, hash) + ruční poskytnutí redigované verze.
- Logy mohou obsahovat osobní údaje; sdílet selektivně.

---

## Struktura kořenového adresáře
```
Diag_YYYYMMDD-HHMMSS/
│
├─ MANIFEST.md
├─ README_problem.md
├─ CHANGELOG_last_actions.txt
│
├─ system/
├─ hardware/
├─ storage/
├─ network/
├─ firewall/
├─ users_permissions/
├─ processes_services/
├─ packages/
├─ web/
├─ nginx/
├─ app/
├─ python/
├─ database/
├─ certs/
├─ cron_webhooks/
├─ logs/
└─ virtualization_containers/
```

---

# README_problem.md (ručně doplnit)
Minimální šablona:
- **Symptom** (co nefunguje)
- **Repro kroky**
- **Očekávání vs realita**
- **Kdy to začalo** (konkrétní datum/čas)
- **Poslední změny** (deploy, update, cert renewal, firewall)
- **Výpis chyby** (kopie výstupu)

---

# system/
- `os_release.txt` – `/etc/os-release`, kernel
- `uname_a.txt` – `uname -a`
- `uptime.txt` – `uptime`, `who -b`
- `locale_timezone.txt` – `locale`, `timedatectl`
- `hostname_hosts.txt` – `hostnamectl`, `/etc/hosts`, `/etc/hostname`
- `sysctl_all.txt` – `sysctl -a`
- `limits_summary.txt` – `ulimit -a`, `/etc/security/limits.conf` + `limits.d` listing
- `systemd_failed_units.txt` – `systemctl --failed`
- `systemd_running_units.txt` – `systemctl list-units --type=service --state=running`
- `journal_boot_errors.txt` – `journalctl -b -p err..alert --no-pager`
- `env_root_sanitized.txt` – environment relevantní pro služby (bez tajemství)

---

# hardware/
- `cpuinfo.txt` – `/proc/cpuinfo` (souhrn)
- `meminfo.txt` – `/proc/meminfo` + `free -h`
- `load_ps_top.txt` – `ps aux --sort=-%cpu`, `ps aux --sort=-%mem` + `top -b -n 1`
- `dmesg_tail.txt` – `dmesg -T | tail -n 400`

---

# storage/
- `df_h.txt` – `df -hT`
- `lsblk.txt` – `lsblk -f`
- `mounts.txt` – `mount`, `/etc/fstab`
- `inode_usage.txt` – `df -ih`
- `disk_health_hint.txt` – (pokud dostupné) `smartctl -H` pro hlavní disk (jen status)
- `largest_dirs_root.csv` – top složky v `/` (1–2 úrovně) podle velikosti
- `largest_dirs_var.csv` – top složky v `/var` podle velikosti

---

# network/
- `ip_addr.txt` – `ip a`
- `ip_route.txt` – `ip r`
- `resolv_conf.txt` – `/etc/resolv.conf` + `systemd-resolve --status` (pokud je)
- `ss_listen.txt` – `ss -lntup`
- `ss_all.txt` – `ss -antup`
- `netstat_fallback.txt` – pokud `net-tools` existuje
- `dns_check.txt` – `getent hosts` pro klíčové domény (pokud definováno)
- `proxy_env.txt` – HTTP(S)_PROXY env (pokud existuje)

---

# firewall/
- `ufw_status.txt` – `ufw status verbose` (pokud je ufw)
- `iptables_rules.txt` – `iptables -S` + `iptables -L -n -v`
- `nft_ruleset.txt` – `nft list ruleset` (pokud nft)

---

# users_permissions/
- `users_groups.txt` – `getent passwd`, `getent group` (bez hashů)
- `sudoers_listing.txt` – listing `/etc/sudoers*` (bez obsahu, nebo redigovaně)
- `umask.txt` – `umask`
- `important_paths_permissions.txt` – vlastníci/práva u `/etc/nginx`, `/var/www`, `/srv`, `/opt`, app dirs

---

# processes_services/
- `ps_full.txt` – `ps auxfww`
- `systemctl_status_nginx.txt` – `systemctl status nginx --no-pager`
- `systemctl_status_app.txt` – status aplikace (gunicorn/uvicorn/systemd unit) pokud existuje
- `systemctl_status_db.txt` – status DB služby pokud existuje
- `open_files_limits.txt` – `cat /proc/sys/fs/file-max` + `lsof` souhrn (pokud dostupné)

---

# packages/
- `dpkg_list.txt` – `dpkg -l`
- `apt_policy_key_pkgs.txt` – verze balíků: nginx, openssl, python3, certbot, postgres/mysql, redis
- `snap_list.txt` – `snap list` (pokud)
- `pip_global_list.txt` – `python3 -m pip list` (pokud pip)

---

# web/
- `web_root_overview.txt` – přehled dokument rootů (např. `/var/www`, `/srv/www`) – strom do hloubky 3
- `static_assets_sizes.csv` – top složky podle velikosti v dokument rootech
- `web_server_headers_hint.txt` – (volitelně) lokální `curl -I` na `http://127.0.0.1` a vybrané vhosty

---

# nginx/
- `nginx_version.txt` – `nginx -V` (včetně configure arguments)
- `nginx_test.txt` – `nginx -t` output
- `nginx_conf_tree.txt` – strom `/etc/nginx` (hloubka 4)
- `nginx_conf_files_list.txt` – seznam `.conf` souborů
- `nginx_sites_enabled.txt` – listing sites-enabled/sites-available
- `nginx_effective_config.txt` – `nginx -T` (pozor na tajemství; případně redigovat)
- `nginx_logs_tail_access.txt` – `tail` relevantních access logů
- `nginx_logs_tail_error.txt` – `tail` relevantních error logů

---

# app/
- `app_dirs_overview.txt` – přehled typických umístění aplikace: `/srv`, `/opt`, `/var/www`, `~/apps`
- `systemd_units_related.txt` – grep na služby (gunicorn/uvicorn/celery/worker)
- `app_env_files_found.txt` – nalezené `.env`, `config*.yml`, `settings.py` (jen cesty + práva + hash)
- `app_permissions_summary.txt` – vlastník/práva pro app dir + data dir
- `webhook_configs_found.txt` – konfigurace webhooků (jen cesty + metadata)

---

# python/
Cíl: odhalit konflikty mezi více instalacemi, venv, pyenv, poetry, pipx.

- `python_versions.txt` – `which -a python python3 pip pip3` + `python3 --version`
- `python_alternatives.txt` – `update-alternatives --display python3` (pokud existuje)
- `python_sys_path.json` – `python3 -c "import sys, json; print(json.dumps(sys.path, indent=2))"`
- `python_site.json` – `python3 -c "import site, json; print(json.dumps({'sitepackages': site.getsitepackages(), 'usersite': site.getusersitepackages()}, indent=2))"`
- `pip_debug.txt` – `python3 -m pip debug -v` (pozor na index/token; redigovat)
- `pip_config_list.txt` – `pip config list -v` (cesty na configy)

## Venv/Poetry/Pipenv/Pyenv discovery
- `venv_candidates_found.txt` – hledání `pyvenv.cfg` a `bin/python` v `/srv`, `/opt`, `/var/www`, `/home`, `/root`
- `venv_tree_summaries/venv_<name>.txt` – strom venv (bin/, lib/, site-packages) + velikost
- `venv_reports/venv_<name>__report.json` – pro každou venv:
  - `sys.executable`, `sys.prefix`, `sys.base_prefix`, `sys.path`
  - `pip --version`, `pip list`, `pip freeze`

---
# database/
Bez exportu dat; jen konfigurace, verze, stav, připojení, logy.

## PostgreSQL (pokud existuje)
- `postgres_version.txt` – `psql --version`
- `postgres_service_status.txt` – `systemctl status postgresql --no-pager`
- `postgres_conf_locations.txt` – cesty na `postgresql.conf`, `pg_hba.conf` (jen metadata + hash)
- `postgres_listen_ports.txt` – `ss -lntup | grep postgres`
- `postgres_logs_tail.txt` – tail relevantních logů

## MySQL/MariaDB (pokud existuje)
- `mysql_version.txt`
- `mysql_service_status.txt`
- `mysql_conf_locations.txt` – my.cnf locations (metadata)
- `mysql_logs_tail.txt`

## Redis (pokud existuje)
- `redis_version.txt`
- `redis_service_status.txt`
- `redis_conf_metadata.txt`
- `redis_logs_tail.txt`

---

# certs/
- `cert_locations.txt` – přehled `/etc/letsencrypt`, `/etc/ssl`, custom cert dirs
- `certbot_status.txt` – `certbot certificates` (pokud)
- `cert_expiry_report.txt` – expirace certů (např. `openssl x509 -enddate` pro vybrané)
- `tls_private_keys_presence.txt` – jen detekce přítomnosti klíčů (bez exportu obsahu)

---

# cron_webhooks/
- `crontab_root.txt` – `crontab -l` (root)
- `crontab_users_listing.txt` – které user crontaby existují
- `system_cron_dirs_tree.txt` – `/etc/cron.*` listing
- `webhook_endpoints_inventory.txt` – soupis endpointů (z nginx/app config; bez tajemství)

---

# logs/
- `journal_nginx_last500.txt` – `journalctl -u nginx -n 500 --no-pager`
- `journal_app_last500.txt` – `journalctl -u <app> -n 500 --no-pager` (pokud)
- `journal_db_last500.txt` – pro DB (pokud)
- `syslog_tail.txt` – `/var/log/syslog` tail (Ubuntu) nebo `journalctl` fallback
- `auth_log_tail.txt` – `/var/log/auth.log` tail (opatrně)
- `kernel_log_tail.txt` – `journalctl -k -n 400 --no-pager`

---

# virtualization_containers/
- `docker_info.txt` – `docker info` (pokud)
- `docker_ps.txt` – `docker ps -a` (pokud)
- `docker_compose_files_found.txt` – nalezené `docker-compose*.yml` (cesty + metadata)
- `k8s_hint.txt` – pokud je microk8s/k3s (stav)

---

# Automatizovaný sběr – doporučený běh
1. Na Ubuntu spustit sběr (bash skript), který vytvoří `Diag_YYYYMMDD-HHMMSS/` a naplní podsložky.
2. Volitelně stáhnout celý adresář na Windows přes SCP.

---

# Jednořádkový příkaz z Windows PowerShellu (remote sběr + stažení)
Níže je one-liner s placeholdery. Vyžaduje:
- Windows 10/11: `ssh` a `scp` (OpenSSH Client)
- Pokud chceš zadat heslo v příkazu: `sshpass` (nedoporučeno). Bezpečnější je SSH klíč.

## Varianta A (doporučeno): SSH klíč, bez hesla v příkazu
```powershell
$ip="<IP_ADDRESS>"; $user="root"; $script=@'
#!/usr/bin/env bash
set -o pipefail
set +e
timestamp=$(date +%Y%m%d-%H%M%S)
remote_root="/root/Diag_${timestamp}"
mkdir -p "$remote_root"
mkdir -p "$remote_root/system"
(cat /etc/os-release) > "$remote_root/system/os_release.txt" 2>&1
mkdir -p "$remote_root/system"
(uname -a) > "$remote_root/system/uname.txt" 2>&1
mkdir -p "$remote_root/system"
(uptime && who -b) > "$remote_root/system/uptime.txt" 2>&1
mkdir -p "$remote_root/system"
(locale && timedatectl) > "$remote_root/system/locale_timezone.txt" 2>&1
mkdir -p "$remote_root/system"
(hostnamectl && cat /etc/hosts && cat /etc/hostname) > "$remote_root/system/hostname_hosts.txt" 2>&1
mkdir -p "$remote_root/system"
(sysctl -a) > "$remote_root/system/sysctl_all.txt" 2>&1
mkdir -p "$remote_root/system"
(ulimit -a && ls /etc/security/limits.conf /etc/security/limits.d 2>/dev/null) > "$remote_root/system/limits_summary.txt" 2>&1
mkdir -p "$remote_root/system"
(systemctl --failed) > "$remote_root/system/systemd_failed_units.txt" 2>&1
mkdir -p "$remote_root/system"
(systemctl list-units --type=service --state=running) > "$remote_root/system/systemd_running_units.txt" 2>&1
mkdir -p "$remote_root/system"
(journalctl -b -p err..alert --no-pager) > "$remote_root/system/journal_boot_errors.txt" 2>&1
mkdir -p "$remote_root/system"
(env | grep -v -E '(PASS|KEY|SECRET|TOKEN|PASSWORD)') > "$remote_root/system/env_root_sanitized.txt" 2>&1
mkdir -p "$remote_root/hardware"
(lscpu) > "$remote_root/hardware/cpu.txt" 2>&1
mkdir -p "$remote_root/hardware"
(dmidecode -t memory) > "$remote_root/hardware/memory_modules.txt" 2>&1
mkdir -p "$remote_root/hardware"
(free -h) > "$remote_root/hardware/memory_summary.txt" 2>&1
mkdir -p "$remote_root/storage"
(lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE) > "$remote_root/storage/volumes.txt" 2>&1
mkdir -p "$remote_root/storage"
(mount | column -t) > "$remote_root/storage/mount_points.txt" 2>&1
mkdir -p "$remote_root/storage"
(if command -v smartctl >/dev/null 2>&1; then for dev in /dev/sd?; do smartctl -H "$dev"; done; else echo 'smartctl missing'; fi) > "$remote_root/storage/smart_status.txt" 2>&1
mkdir -p "$remote_root/network"
(ip addr) > "$remote_root/network/ipconfig_all.txt" 2>&1
mkdir -p "$remote_root/network"
(ip link) > "$remote_root/network/adapters_details.txt" 2>&1
mkdir -p "$remote_root/network"
(resolvectl status || systemd-resolve --status || cat /etc/resolv.conf) > "$remote_root/network/dns_client_config.txt" 2>&1
mkdir -p "$remote_root/network"
(cat /etc/hosts) > "$remote_root/network/hosts_file.txt" 2>&1
mkdir -p "$remote_root/network"
(ip route) > "$remote_root/network/routes.txt" 2>&1
mkdir -p "$remote_root/network"
(ss -tunlp) > "$remote_root/network/listening_sockets.txt" 2>&1
mkdir -p "$remote_root/firewall"
(ufw status verbose) > "$remote_root/firewall/ufw_status.txt" 2>&1
mkdir -p "$remote_root/firewall"
(iptables -S && iptables -L -n -v) > "$remote_root/firewall/iptables_rules.txt" 2>&1
mkdir -p "$remote_root/firewall"
(nft list ruleset) > "$remote_root/firewall/nft_ruleset.txt" 2>&1
mkdir -p "$remote_root/users_permissions"
(getent passwd && getent group) > "$remote_root/users_permissions/users_groups.txt" 2>&1
mkdir -p "$remote_root/users_permissions"
(cat /etc/sudoers && ls /etc/sudoers.d 2>/dev/null) > "$remote_root/users_permissions/sudoers_listing.txt" 2>&1
mkdir -p "$remote_root/users_permissions"
(umask) > "$remote_root/users_permissions/umask.txt" 2>&1
mkdir -p "$remote_root/processes_services"
(ps -ef) > "$remote_root/processes_services/process_list.txt" 2>&1
mkdir -p "$remote_root/processes_services"
(systemctl list-units --type=service --all) > "$remote_root/processes_services/services_state.txt" 2>&1
mkdir -p "$remote_root/processes_services"
(systemctl list-unit-files --state=enabled) > "$remote_root/processes_services/startup_items.txt" 2>&1
mkdir -p "$remote_root/packages"
(dpkg -l) > "$remote_root/packages/dpkg_list.txt" 2>&1
mkdir -p "$remote_root/packages"
(apt-cache policy nginx openssl python3 certbot postgresql redis) > "$remote_root/packages/apt_policy_key_pkgs.txt" 2>&1
mkdir -p "$remote_root/packages"
(snap list) > "$remote_root/packages/snap_list.txt" 2>&1
mkdir -p "$remote_root/web"
(find /var/www /srv/www -maxdepth 3 -type d -print 2>/dev/null) > "$remote_root/web/web_root_overview.txt" 2>&1
mkdir -p "$remote_root/web"
(du -h --max-depth=2 /var/www /srv/www 2>/dev/null | sort -hr) > "$remote_root/web/static_assets_sizes.csv" 2>&1
mkdir -p "$remote_root/web"
(curl -I http://127.0.0.1 2>&1 || true) > "$remote_root/web/web_server_headers_hint.txt" 2>&1
mkdir -p "$remote_root/nginx"
(nginx -V) > "$remote_root/nginx/nginx_version.txt" 2>&1
mkdir -p "$remote_root/nginx"
(nginx -t) > "$remote_root/nginx/nginx_test.txt" 2>&1
mkdir -p "$remote_root/nginx"
(find /etc/nginx -maxdepth 4 -print 2>/dev/null) > "$remote_root/nginx/nginx_conf_tree.txt" 2>&1
mkdir -p "$remote_root/app"
(find /srv /opt /var/www ~/apps -maxdepth 2 -type d -print 2>/dev/null) > "$remote_root/app/app_dirs_overview.txt" 2>&1
mkdir -p "$remote_root/app"
(systemctl list-unit-files | grep -E 'gunicorn|uvicorn|celery|worker' || true) > "$remote_root/app/systemd_units_related.txt" 2>&1
mkdir -p "$remote_root/app"
(find /srv /opt /var/www ~/apps -type f \( -name '*.env' -o -name 'config*.yml' -o -name 'settings.py' \) -print -exec ls -l {} \; 2>/dev/null) > "$remote_root/app/app_env_files_found.txt" 2>&1
mkdir -p "$remote_root/python"
(which python && which python3) > "$remote_root/python/where_python.txt" 2>&1
mkdir -p "$remote_root/python"
(python3 -m pip --version && pip3 --version) > "$remote_root/python/py_launcher_list.txt" 2>&1
mkdir -p "$remote_root/python"
(python3 -c \"import json,sys; print(json.dumps({'python': sys.executable, 'paths': sys.path}))\") > "$remote_root/python/interpreters_inventory.csv" 2>&1
mkdir -p "$remote_root/database"
(psql --version) > "$remote_root/database/postgres_version.txt" 2>&1
mkdir -p "$remote_root/database"
(systemctl status postgresql --no-pager) > "$remote_root/database/postgres_service_status.txt" 2>&1
mkdir -p "$remote_root/database"
(find /etc/postgresql -name 'postgresql.conf' -o -name 'pg_hba.conf' -print 2>/dev/null) > "$remote_root/database/postgres_conf_locations.txt" 2>&1
mkdir -p "$remote_root/certs"
(find /etc/letsencrypt /etc/ssl /etc/pki -maxdepth 3 -type f \( -name '*.pem' -o -name '*.crt' \) -print 2>/dev/null) > "$remote_root/certs/cert_locations.txt" 2>&1
mkdir -p "$remote_root/certs"
(certbot certificates || echo 'certbot missing') > "$remote_root/certs/certbot_status.txt" 2>&1
mkdir -p "$remote_root/certs"
(for cert in /etc/letsencrypt/live/*/cert.pem; do echo CERT: $cert; openssl x509 -enddate -noout -in \"$cert\"; done 2>/dev/null) > "$remote_root/certs/cert_expiry_report.txt" 2>&1
mkdir -p "$remote_root/cron_webhooks"
(crontab -l) > "$remote_root/cron_webhooks/crontab_root.txt" 2>&1
mkdir -p "$remote_root/cron_webhooks"
(ls /var/spool/cron/crontabs 2>/dev/null) > "$remote_root/cron_webhooks/crontab_users_listing.txt" 2>&1
mkdir -p "$remote_root/cron_webhooks"
(ls /etc/cron.* 2>/dev/null) > "$remote_root/cron_webhooks/system_cron_dirs_tree.txt" 2>&1
mkdir -p "$remote_root/logs"
(journalctl -u nginx -n 500 --no-pager) > "$remote_root/logs/journal_nginx_last500.txt" 2>&1
mkdir -p "$remote_root/logs"
(journalctl -n 500 --no-pager) > "$remote_root/logs/journal_app_last500.txt" 2>&1
mkdir -p "$remote_root/logs"
(journalctl -u postgresql -n 500 --no-pager) > "$remote_root/logs/journal_db_last500.txt" 2>&1
mkdir -p "$remote_root/logs"
(tail -n 200 /var/log/syslog) > "$remote_root/logs/syslog_tail.txt" 2>&1
mkdir -p "$remote_root/logs"
(tail -n 200 /var/log/auth.log) > "$remote_root/logs/auth_log_tail.txt" 2>&1
mkdir -p "$remote_root/logs"
(journalctl -k -n 400 --no-pager) > "$remote_root/logs/kernel_log_tail.txt" 2>&1
mkdir -p "$remote_root/virtualization_containers"
(docker info) > "$remote_root/virtualization_containers/docker_info.txt" 2>&1
mkdir -p "$remote_root/virtualization_containers"
(docker ps -a) > "$remote_root/virtualization_containers/docker_ps.txt" 2>&1
mkdir -p "$remote_root/virtualization_containers"
(find /srv /opt /etc -name 'docker-compose*.yml' -print 2>/dev/null) > "$remote_root/virtualization_containers/docker_compose_files_found.txt" 2>&1
echo "REMOTE_ROOT=$remote_root"
'@; $remoteRoot = $script | ssh "$user@$ip" "bash -s" | Select-String -Pattern '^REMOTE_ROOT=' | Select-Object -First 1 | ForEach-Object { $_.Line -replace '^REMOTE_ROOT=' }; scp -r "$user@$ip:$remoteRoot" .
```

## Varianta B (heslo v příkazu – méně bezpečné; vyžaduje sshpass)
```powershell
$ip="<IP_ADDRESS>"; $user="root"; $pw="<ROOT_PASSWORD>"; $script=@'
#!/usr/bin/env bash
set -o pipefail
set +e
timestamp=$(date +%Y%m%d-%H%M%S)
remote_root="/root/Diag_${timestamp}"
mkdir -p "$remote_root"
mkdir -p "$remote_root/system"
(cat /etc/os-release) > "$remote_root/system/os_release.txt" 2>&1
mkdir -p "$remote_root/system"
(uname -a) > "$remote_root/system/uname.txt" 2>&1
mkdir -p "$remote_root/system"
(uptime && who -b) > "$remote_root/system/uptime.txt" 2>&1
mkdir -p "$remote_root/system"
(locale && timedatectl) > "$remote_root/system/locale_timezone.txt" 2>&1
mkdir -p "$remote_root/system"
(hostnamectl && cat /etc/hosts && cat /etc/hostname) > "$remote_root/system/hostname_hosts.txt" 2>&1
mkdir -p "$remote_root/system"
(sysctl -a) > "$remote_root/system/sysctl_all.txt" 2>&1
mkdir -p "$remote_root/system"
(ulimit -a && ls /etc/security/limits.conf /etc/security/limits.d 2>/dev/null) > "$remote_root/system/limits_summary.txt" 2>&1
mkdir -p "$remote_root/system"
(systemctl --failed) > "$remote_root/system/systemd_failed_units.txt" 2>&1
mkdir -p "$remote_root/system"
(systemctl list-units --type=service --state=running) > "$remote_root/system/systemd_running_units.txt" 2>&1
mkdir -p "$remote_root/system"
(journalctl -b -p err..alert --no-pager) > "$remote_root/system/journal_boot_errors.txt" 2>&1
mkdir -p "$remote_root/system"
(env | grep -v -E '(PASS|KEY|SECRET|TOKEN|PASSWORD)') > "$remote_root/system/env_root_sanitized.txt" 2>&1
mkdir -p "$remote_root/hardware"
(lscpu) > "$remote_root/hardware/cpu.txt" 2>&1
mkdir -p "$remote_root/hardware"
(dmidecode -t memory) > "$remote_root/hardware/memory_modules.txt" 2>&1
mkdir -p "$remote_root/hardware"
(free -h) > "$remote_root/hardware/memory_summary.txt" 2>&1
mkdir -p "$remote_root/storage"
(lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE) > "$remote_root/storage/volumes.txt" 2>&1
mkdir -p "$remote_root/storage"
(mount | column -t) > "$remote_root/storage/mount_points.txt" 2>&1
mkdir -p "$remote_root/storage"
(if command -v smartctl >/dev/null 2>&1; then for dev in /dev/sd?; do smartctl -H "$dev"; done; else echo 'smartctl missing'; fi) > "$remote_root/storage/smart_status.txt" 2>&1
mkdir -p "$remote_root/network"
(ip addr) > "$remote_root/network/ipconfig_all.txt" 2>&1
mkdir -p "$remote_root/network"
(ip link) > "$remote_root/network/adapters_details.txt" 2>&1
mkdir -p "$remote_root/network"
(resolvectl status || systemd-resolve --status || cat /etc/resolv.conf) > "$remote_root/network/dns_client_config.txt" 2>&1
mkdir -p "$remote_root/network"
(cat /etc/hosts) > "$remote_root/network/hosts_file.txt" 2>&1
mkdir -p "$remote_root/network"
(ip route) > "$remote_root/network/routes.txt" 2>&1
mkdir -p "$remote_root/network"
(ss -tunlp) > "$remote_root/network/listening_sockets.txt" 2>&1
mkdir -p "$remote_root/firewall"
(ufw status verbose) > "$remote_root/firewall/ufw_status.txt" 2>&1
mkdir -p "$remote_root/firewall"
(iptables -S && iptables -L -n -v) > "$remote_root/firewall/iptables_rules.txt" 2>&1
mkdir -p "$remote_root/firewall"
(nft list ruleset) > "$remote_root/firewall/nft_ruleset.txt" 2>&1
mkdir -p "$remote_root/users_permissions"
(getent passwd && getent group) > "$remote_root/users_permissions/users_groups.txt" 2>&1
mkdir -p "$remote_root/users_permissions"
(cat /etc/sudoers && ls /etc/sudoers.d 2>/dev/null) > "$remote_root/users_permissions/sudoers_listing.txt" 2>&1
mkdir -p "$remote_root/users_permissions"
(umask) > "$remote_root/users_permissions/umask.txt" 2>&1
mkdir -p "$remote_root/processes_services"
(ps -ef) > "$remote_root/processes_services/process_list.txt" 2>&1
mkdir -p "$remote_root/processes_services"
(systemctl list-units --type=service --all) > "$remote_root/processes_services/services_state.txt" 2>&1
mkdir -p "$remote_root/processes_services"
(systemctl list-unit-files --state=enabled) > "$remote_root/processes_services/startup_items.txt" 2>&1
mkdir -p "$remote_root/packages"
(dpkg -l) > "$remote_root/packages/dpkg_list.txt" 2>&1
mkdir -p "$remote_root/packages"
(apt-cache policy nginx openssl python3 certbot postgresql redis) > "$remote_root/packages/apt_policy_key_pkgs.txt" 2>&1
mkdir -p "$remote_root/packages"
(snap list) > "$remote_root/packages/snap_list.txt" 2>&1
mkdir -p "$remote_root/web"
(find /var/www /srv/www -maxdepth 3 -type d -print 2>/dev/null) > "$remote_root/web/web_root_overview.txt" 2>&1
mkdir -p "$remote_root/web"
(du -h --max-depth=2 /var/www /srv/www 2>/dev/null | sort -hr) > "$remote_root/web/static_assets_sizes.csv" 2>&1
mkdir -p "$remote_root/web"
(curl -I http://127.0.0.1 2>&1 || true) > "$remote_root/web/web_server_headers_hint.txt" 2>&1
mkdir -p "$remote_root/nginx"
(nginx -V) > "$remote_root/nginx/nginx_version.txt" 2>&1
mkdir -p "$remote_root/nginx"
(nginx -t) > "$remote_root/nginx/nginx_test.txt" 2>&1
mkdir -p "$remote_root/nginx"
(find /etc/nginx -maxdepth 4 -print 2>/dev/null) > "$remote_root/nginx/nginx_conf_tree.txt" 2>&1
mkdir -p "$remote_root/app"
(find /srv /opt /var/www ~/apps -maxdepth 2 -type d -print 2>/dev/null) > "$remote_root/app/app_dirs_overview.txt" 2>&1
mkdir -p "$remote_root/app"
(systemctl list-unit-files | grep -E 'gunicorn|uvicorn|celery|worker' || true) > "$remote_root/app/systemd_units_related.txt" 2>&1
mkdir -p "$remote_root/app"
(find /srv /opt /var/www ~/apps -type f \( -name '*.env' -o -name 'config*.yml' -o -name 'settings.py' \) -print -exec ls -l {} \; 2>/dev/null) > "$remote_root/app/app_env_files_found.txt" 2>&1
mkdir -p "$remote_root/python"
(which python && which python3) > "$remote_root/python/where_python.txt" 2>&1
mkdir -p "$remote_root/python"
(python3 -m pip --version && pip3 --version) > "$remote_root/python/py_launcher_list.txt" 2>&1
mkdir -p "$remote_root/python"
(python3 -c \"import json,sys; print(json.dumps({'python': sys.executable, 'paths': sys.path}))\") > "$remote_root/python/interpreters_inventory.csv" 2>&1
mkdir -p "$remote_root/database"
(psql --version) > "$remote_root/database/postgres_version.txt" 2>&1
mkdir -p "$remote_root/database"
(systemctl status postgresql --no-pager) > "$remote_root/database/postgres_service_status.txt" 2>&1
mkdir -p "$remote_root/database"
(find /etc/postgresql -name 'postgresql.conf' -o -name 'pg_hba.conf' -print 2>/dev/null) > "$remote_root/database/postgres_conf_locations.txt" 2>&1
mkdir -p "$remote_root/certs"
(find /etc/letsencrypt /etc/ssl /etc/pki -maxdepth 3 -type f \( -name '*.pem' -o -name '*.crt' \) -print 2>/dev/null) > "$remote_root/certs/cert_locations.txt" 2>&1
mkdir -p "$remote_root/certs"
(certbot certificates || echo 'certbot missing') > "$remote_root/certs/certbot_status.txt" 2>&1
mkdir -p "$remote_root/certs"
(for cert in /etc/letsencrypt/live/*/cert.pem; do echo CERT: $cert; openssl x509 -enddate -noout -in \"$cert\"; done 2>/dev/null) > "$remote_root/certs/cert_expiry_report.txt" 2>&1
mkdir -p "$remote_root/cron_webhooks"
(crontab -l) > "$remote_root/cron_webhooks/crontab_root.txt" 2>&1
mkdir -p "$remote_root/cron_webhooks"
(ls /var/spool/cron/crontabs 2>/dev/null) > "$remote_root/cron_webhooks/crontab_users_listing.txt" 2>&1
mkdir -p "$remote_root/cron_webhooks"
(ls /etc/cron.* 2>/dev/null) > "$remote_root/cron_webhooks/system_cron_dirs_tree.txt" 2>&1
mkdir -p "$remote_root/logs"
(journalctl -u nginx -n 500 --no-pager) > "$remote_root/logs/journal_nginx_last500.txt" 2>&1
mkdir -p "$remote_root/logs"
(journalctl -n 500 --no-pager) > "$remote_root/logs/journal_app_last500.txt" 2>&1
mkdir -p "$remote_root/logs"
(journalctl -u postgresql -n 500 --no-pager) > "$remote_root/logs/journal_db_last500.txt" 2>&1
mkdir -p "$remote_root/logs"
(tail -n 200 /var/log/syslog) > "$remote_root/logs/syslog_tail.txt" 2>&1
mkdir -p "$remote_root/logs"
(tail -n 200 /var/log/auth.log) > "$remote_root/logs/auth_log_tail.txt" 2>&1
mkdir -p "$remote_root/logs"
(journalctl -k -n 400 --no-pager) > "$remote_root/logs/kernel_log_tail.txt" 2>&1
mkdir -p "$remote_root/virtualization_containers"
(docker info) > "$remote_root/virtualization_containers/docker_info.txt" 2>&1
mkdir -p "$remote_root/virtualization_containers"
(docker ps -a) > "$remote_root/virtualization_containers/docker_ps.txt" 2>&1
mkdir -p "$remote_root/virtualization_containers"
(find /srv /opt /etc -name 'docker-compose*.yml' -print 2>/dev/null) > "$remote_root/virtualization_containers/docker_compose_files_found.txt" 2>&1
echo "REMOTE_ROOT=$remote_root"
'@; $remoteRoot = $script | sshpass -p $pw ssh -o StrictHostKeyChecking=no "$user@$ip" "bash -s" | Select-String -Pattern '^REMOTE_ROOT=' | Select-Object -First 1 | ForEach-Object { $_.Line -replace '^REMOTE_ROOT=' }; sshpass -p $pw scp -o StrictHostKeyChecking=no -r "$user@$ip:$remoteRoot" .
```

> Pozn?mka: Snippet pos?l? inline bash skript identick? s t?m, kter? generuje aplikace; stdout obsahuje jen `REMOTE_ROOT=...`, kter? se pou?ije pro n?sledn? `scp`.

---

# MANIFEST.md (poslední kapitola; šablona)

```markdown
# Diagnostic Manifest

Generated at: {{timestamp_local}}
Host: {{hostname}}
User: {{collector_user}}
Run as root: {{is_root}}
OS: {{os_pretty_name}}
Kernel: {{kernel}}
Uptime: {{uptime}}
Output root: {{output_root}}

## Purpose
This folder contains a full Ubuntu web server diagnostic snapshot for troubleshooting issues in nginx/app/database/certs/network.

## Folder Overview
- system/ – OS/kernel/timezone/sysctl/limits/systemd health
- hardware/ – CPU/RAM/load/dmesg hints
- storage/ – mounts/df/inodes/top sizes
- network/ – IP/routes/DNS/ports
- firewall/ – ufw/iptables/nft rules
- users_permissions/ – users/groups/sudoers listing/permissions summary
- processes_services/ – ps/systemctl statuses/open ports correlation
- packages/ – dpkg/apt versions of key packages
- web/ – web roots overview + size triage
- nginx/ – nginx -V/-t/-T, config tree, log tails
- app/ – app dirs, systemd units, env/config discovery (metadata)
- python/ – interpreter inventory, pip config, venv discovery + per-venv reports
- database/ – postgres/mysql/redis status + config metadata + log tails
- certs/ – certbot inventory + expiry report (no private keys)
- cron_webhooks/ – crons + webhook inventory (metadata)
- logs/ – journal/syslog/auth/kernel tails
- virtualization_containers/ – docker inventory + compose metadata

## File Index
| Path | Description |
|------|-------------|
| README_problem.md | repro steps + timeline |
| system/journal_boot_errors.txt | boot errors from journal |
| network/ss_listen.txt | listening sockets |
| nginx/nginx_test.txt | nginx -t output |
| python/venv_candidates_found.txt | detected venv roots |
| python/venv_reports/venv_*__report.json | per-venv sys/pip snapshot |
| certs/cert_expiry_report.txt | certificate expiry |
| logs/journal_nginx_last500.txt | nginx journal tail |
| logs/journal_app_last500.txt | app journal tail |

## Notes
- Secrets must be redacted before sharing.
- Missing subsystems are recorded as NOT PRESENT.

## Integrity
Total files: {{file_count}}
Total size: {{total_size_human}}
Optional checksums: checksums/sha256.txt
```


# PŘÍLOHA FULL Windows Diagnostics

Tento dokument definuje **konečný návrh FULL diagnostiky pro Windows**, zaměřený na:
- úplnou rekonstrukci systému bez ZIP archivace
- jednoznačné určení výchozích vs. runtime hodnot
- detailní rozbor **více instalací Pythonu a všech venv**
- transparentní analýzu PATH, registry, aliasů a asociací

Výstupem je **adresář se soubory**, nikoli archiv.

---

## Struktura kořenového adresáře
```
Diag_YYYYMMDD-HHMMSS/
│
├─ MANIFEST.md
├─ README_problem.md
├─ CHANGELOG_last_actions.txt
│
├─ system/
├─ registry/
├─ filesystem/
├─ hardware/
├─ storage/
├─ drivers/
├─ processes_services/
├─ network/
├─ security/
├─ python/
├─ devtools/
├─ virtualization/
├─ wsl/
└─ logs/
```

---

# MANIFEST.md (automaticky generovaný)

Slouží jako **index a kontrola úplnosti**.

```markdown
# Diagnostic Manifest

Generated at: YYYY-MM-DD HH:MM:SS
Machine: <COMPUTERNAME>
User: <USERNAME>
PowerShell: 5.1 / 7.x
Run as Administrator: YES / NO

## Folder Overview
system/      – OS, build, PATH, environment
registry/    – authoritative Windows configuration
filesystem/  – actual files, Python installs, venvs
python/      – runtime Python diagnostics
network/     – adapters, DNS, proxy, firewall
logs/        – crashes and event logs
...

## Files
| File | Description | Size |
|------|-------------|------|
| system/systeminfo.txt | OS + HW summary | 45 KB |
| registry/env_machine.reg | System PATH and env | 3 KB |
| python/venv_reports/venv_projA.json | Full venv report | 18 KB |

## Notes
- ACCESS DENIED = requires Administrator
- Missing subsystems are explicitly noted
```

---

# system/
**Jak Windows má fungovat po přihlášení**

- systeminfo.txt – OS, build, hotfixy, HW
- os_build.txt – edice, build, UBR
- windows_updates_hotfixes.txt
- timezone_locale.txt- uptime_boot.txt
- power_settings.txt
- group_policy_summary.html
- run_context.txt

### Environment & PATH
- env_machine.txt – HKLM environment (rozparsované)
- env_user.txt – HKCU environment
- path_effective_process.txt – PATH skutečně viděný během běhu
- path_diff_analysis.txt – diff: Machine vs User vs Runtime

---

# registry/
**Zdroj pravdy – proč se spouští právě toto**

### Environment / PATH
- env_machine.reg – HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment
- env_user.reg – HKCU\\Environment

### Python – instalace & launcher
- python_core_hklm.reg
- python_core_hklm_wow6432.reg
- python_core_hkcu.reg
- pylauncher_hklm.reg
- pylauncher_hkcu.reg

### App Execution
- app_paths_python_hklm.reg
- app_paths_python_hkcu.reg
- windowsapps_execution_aliases.txt

### Asociace
- file_associations_python.reg

### Instalovaný software
- uninstall_inventory.txt – Python, Conda, VC++ runtimes

---

# filesystem/
**Co na disku reálně existuje (včetně přehledu uživatelských dat)**

> Cíl: poskytnout *přehled* souborové struktury mimo systémové složky Windows, zejména uživatelská data a AppData. Nejde o kopii obsahu – pouze strom a souhrny.

## Python & interpreters
- python_executables_found.txt
- python_install_dirs_tree.txt

## Virtual environments
- venv_candidates_found.txt
- venv_tree_summaries/
  - venv_<name>.txt

## Projekty
- project_requirements_found.txt

## User data & AppData overview (přehled)
- userprofile_tree_depth3.txt – strom `%USERPROFILE%` do hloubky 3 (bez binárního obsahu)
- userprofile_top_sizes.csv – top složky v `%USERPROFILE%` podle velikosti (rychlá orientace)
- appdata_roaming_tree_depth4.txt – strom `%APPDATA%` do hloubky 4
- appdata_local_tree_depth4.txt – strom `%LOCALAPPDATA%` do hloubky 4
- appdata_locallow_tree_depth4.txt – strom `%USERPROFILE%\AppData\LocalLow` do hloubky 4 (pokud existuje)
- appdata_top_sizes.csv – top složky v `AppData` podle velikosti
- known_folders_locations.txt – skutečné cesty na Documents/Downloads/Desktop atd. (redirects/OneDrive)
- onedrive_status_hint.txt – indikace OneDrive přesměrování (pokud existuje)

---

# python/
**Jak Python skutečně běží**

### Interpreters
- where_python.txt
- py_launcher_list.txt
- interpreters_inventory.csv

### Default runtime
- python_version_default.txt
- pip_version_default.txt
- pip_list_default.txt
- pip_freeze_default.txt
- pip_debug_default.txt
- pip_config_all.txt

### Runtime internals
- python_sys_path.json
- python_site_packages.txt
- python_platform.json

### Virtual env reports
python/venv_reports/
- venv_<name>__report.json

---

# processes_services/
- process_list.txt
- services_state.txt
- startup_items.txt
- scheduled_tasks_summary.txt

---

# network/
- ipconfig_all.txt
- adapters_details.txt
- dns_client_config.txt
- hosts_file.txt
- routes.txt
- netstat_ano.txt
- firewall_profiles.txt
- firewall_rules_export.wfw
- winhttp_proxy.txt
- internet_proxy_user.txt
- wifi_profiles.txt

---

# security/
- defender_status.txt
- applocker_effective.txt
- uac_settings.txt
- certificates_machine_summary.txt

---

# hardware/
- cpu.txt
- memory_modules.txt
- memory_summary.txt
- motherboard_bios.txt
- gpu_adapters.txt
- monitors_displays.txt

---

# storage/
- volumes.txt
- mount_points.txt
- smart_status.txt
- disk_performance_counters.txt

---

# drivers/
- driverquery_verbose.txt
- pnp_devices.txt
- problem_devices.txt
- signed_drivers.txt

---

# devtools/
- git_version.txt
- node_version.txt
- dotnet_info.txt
- vcpp_runtimes.txt

---

# virtualization/
- hyperv_state.txt
- virtual_machine_platform.txt
- windows_features.txt

---

# wsl/
- wsl_status.txt
- wsl_list_verbose.txt
- wsl_versions.txt

---

# logs/
- eventlog_system_last200.txt
- eventlog_application_last200.txt
- eventlog_security_last50.txt
- wer_crash_list.txt
- reliability_monitor_summary.txt
- windows_setup_logs_hint.txt

---

## Shrnutí
Tento balík umožňuje:
- kompletní rekonstrukci PATH (registry × runtime)
- rozlišení více Python instalací
- přesné určení aktivního interpreteru, pipu a venv
- vysvětlení chování Windows při spouštění python.exe
- analýzu pádů, blokací, politik, firewallu a proxy')
    print('Režim: GENERATE')
    print('Toto je simulovaný obsah souboru vyrobený pipeline.')

if __name__ == '__main__':
    run()