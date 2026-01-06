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
