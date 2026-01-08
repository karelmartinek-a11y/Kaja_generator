---
title: "KÁJOVO UI DESIGN STANDARD"
designation: "MASTER"
version: "MASTER v1.0"
date: "2026-01-07"
status: "ZÁVAZNÉ"
audience: "OpenAI generování programů"
language: "cs-CZ"
---

# KÁJOVO UI DESIGN STANDARD (MASTER v1.0)

Tento dokument je **normativní specifikace**. Je psaný tak, aby byl použitelný přímo jako vstup pro generování UI (LLM).  
Klíčová slova: **MUSÍ / NESMÍ / MĚL BY** se vykládají striktně.

## 0. Generační kontrakt (pro OpenAI)

1) Vše, co je označeno „MUSÍ“ nebo „NESMÍ“, je závazné.  
2) Pokud se dvě pravidla dostanou do konfliktu, platí toto pořadí precedence (od nejsilnějšího):
   a) TOKENS a KONTRAKTY stavů (sekce 1 a 5)  
   b) Specifikace komponent (sekce 6)  
   c) Layout aplikace (sekce 4)  
   d) Obecná pravidla (sekce 2–3)  
3) Pokud je nějaká hodnota odvozená (vzorec), musí se použít přesně, včetně zaokrouhlení.  
4) Jednotky: všechny rozměry jsou v **logických pixelech** (px).  
5) Zaokrouhlování: `round(x)` = matematické zaokrouhlení na nejbližší celé číslo (0.5 nahoru).  
6) Nesmí vzniknout překryv prvků (výjimka: overlay vrstvy tooltip/roletka/dialog/scrollbar).

## 1. TOKENS (jediný zdroj pravdy)

### 1.1 Barvy (HEX)

- BÍLÁ: `#FFFFFF`
- ČERNÁ: `#000000`
- ČERVENÁ: `#FF0000`
- ŠEDIVÁ: `#808080`

### 1.2 Vrstvy prvku (pořadí a tloušťky)

Každý prvek je složen ze čtyř vizuálních vrstev (zvenku dovnitř):

1) **LEM**: 2 px  
2) **OKRAJ**: 1 px  
3) **POZADÍ**: vnitřní výplň  
4) **OBSAH**: text / piktogram / grafika

Pozn.: „Obsahová plocha“ = plocha **uvnitř okraje** (uvnitř lemu 2 px a okraje 1 px).

### 1.3 UI SCALE (deterministicky)

- Referenční okno: `1280 × 720` při `UI_scale = 1.0`.
- Výpočet: `UI_scale = min(W/1280, H/720)` kde `W` a `H` jsou aktuální rozměry okna.

Co se škáluje:
- typografie, paddingy, výšky řádků, rozměry ikon, rozměry modulů času/datu, tloušťky ikon čar.

Co se **neskáluje**:
- tloušťka lemu (2 px) a okraje (1 px),
- minimální mezera mezi sibling prvky (2 px).

### 1.4 Typografie (font kontrakt)

Povolený font:
- Rodina: **Montserrat**
- Řezy: **Regular**, **Bold**
- Jiné fonty/řezy jsou zakázané.

Distribuce fontu (determinismus):
- Fonty MUSÍ být součástí aplikace (bundled assets/resources).
- Aplikace NESMÍ spoléhat na systémovou instalaci fontů.
- Aplikace MUSÍ fonty načíst/registrovat při startu.
- Pokud font nelze načíst, aplikace MUSÍ zobrazit chybový dialog ve stylu Kájovo a ukončit se (fallback fonty jsou zakázány).
- Build proces MĚL BY kontrolovat hash souborů fontu (např. SHA‑256), aby se nepokoutně nezměnila verze.

Velikosti:
- Základní velikost písma při `UI_scale = 1.0`: `FS_base = 16 px`
- Výsledná velikost písma: `FS = round(FS_base × UI_scale)`
- Line-height: `LH = round(1.25 × FS)`  *(závazné – aby šlo deterministicky odvozovat rozměry)*

Použití:
- Nadpisy / názvy sekcí / hlavičky tabulek: Montserrat **Bold**, **VŠE VELKÝMI PÍSMENY**
- Běžný obsah a hodnoty: Montserrat **Regular**

### 1.5 Radius (zaoblení)

- Radius všech prvků: `R = max(1, round(0.35 × FS))`  
- Ostré rohy jsou zakázány.

### 1.6 Rozestupy a standardní rozměry (tokeny)

- Minimální mezera mezi dvěma sibling prvky (vnější hrana lemu → vnější hrana lemu): `GAP_MIN = 2 px`
- Standardní vnitřní odsazení (padding) pro prvky s textem:
  - `PAD_X = round(0.8 × FS)`
  - `PAD_Y = round(0.4 × FS)`
- Standardní výška řádku seznamů/roletek/tabulek: `ROW_H = round(1.4 × LH)`
- Výška stavového řádku: `STATUS_H = round(1.6 × LH)`

### 1.7 Ikony (obecný styl)

- Základní velikost ikony: `ICON = round(1.5 × FS)` (čtverec ICON×ICON)
- Ikony jsou **outline** (bez výplně), pokud není u komponenty výslovně řečeno jinak.
- Tloušťka čáry ikony: `STROKE = max(1, round(0.12 × FS))`
- Barva ikony je vždy jedna z token barev (nejčastěji bílá/černá dle stavu).
- Referenční tvary jsou v PŘÍLOZE A.

## 2. Obecná pravidla vzhledu

1) UI je striktně černobílé. Šedivá pouze pro neaktivní text/symboly. Červená pouze pro ukončení/kritické akce a stavy „nebezpečí/nedostupné“ podle tohoto dokumentu.  
2) Žádné stíny, gradienty, textury, průhlednosti (mimo overlay vrstvy), ani dekorativní efekty.  
3) Všechny komponenty MUSÍ používat vrstvy LEM/OKRAJ/POZADÍ/OBSAH.  
4) Překryv je zakázán (výjimky: tooltip, roletka, dialog, overlay scrollbar).  
5) Pokud se mění stav prvku, NESMÍ se změnit layout/rozměry – mění se pouze barvy (a u textu případně velikost v rámci pravidel fit/scale).

## 3. Interakce a input (globální kontrakty)

### 3.1 Hover

- Běžné prvky: **žádný hover efekt** (žádná změna barvy ani geometrie).
- Výjimky (tooltipy):
  - Tabulky: tooltip se zobrazí **jen pokud obsah buňky nepokryje celý text** (overflow) a uživatel setrvá kurzorem 2 s.
  - Dropdown/combobox roletka: tooltip se zobrazí **jen pokud text položky nepokryje celý text** a uživatel setrvá kurzorem 2 s.

### 3.2 Focus a klávesnice

- TAB přesouvá focus na další fokusovatelný prvek.
- SHIFT+TAB přesouvá focus na předchozí fokusovatelný prvek.
- ENTER nebo MEZERNÍK aktivuje fokusovaný prvek (stisk odpovídá „kliknutí“), **s výjimkou textových polí**.

Vizuální indikace focusu (závazné):
- Focus je overlay stav: **LEM = bílý (#FFFFFF) 2 px**.
- Ostatní vrstvy (okraj/pozadí/obsah) zůstávají dle aktuálního stavu prvku.
- Focus NESMÍ měnit rozměry prvku ani rozložení.

### 3.3 ESC (globální)

- ESC zavře otevřený overlay prvek v tomto pořadí:  
  (1) tooltip (pokud existuje), (2) roletka dropdown/combobox, (3) dialog.  
- ESC odpovídá akci **CLOSE** v dialogu.

## 4. Layout aplikace (záhlaví, sekce, status)

### 4.1 Záhlaví programu

Záhlaví MUSÍ obsahovat:
- Název programu a verzi.
- Ovládací prvky.
- Ukončovací prvek (EXIT/QUIT/CLOSE) vpravo.

Ukončovací prvek je vždy „kritický“ (červený kontrakt).

### 4.2 Sekce

Sekce je rámovaná oblast (LEM/OKRAJ/POZADÍ) pro logickou skupinu prvků.

Název sekce:
- je součást horního lemu (přeruší horní lem),
- typografie: Bold, VŠE VELKÝMI PÍSMENY.

(Detailní barvy sekce se řídí barvami a kontrakty stavů; sekce sama není interaktivní.)

### 4.3 Stavový řádek (STATUS)

Výška: `STATUS_H`.

Status vždy zobrazuje:
- vlevo: text aktuálního kroku (Regular) + volitelně progress „teploměr“
- vpravo: čas (PRAGOTRON) a datum (kalendářová kresba)

Čas (PRAGOTRON / flap)
- Formát: `HH:MM:SS` (8 znaků včetně dvojteček).
- Každý znak je samostatný modul (obdélník se zaoblením R).
- Modul:
  - lem: bílý 2 px
  - okraj: černý 1 px
  - pozadí: černé
  - znak: bílý, Montserrat Bold
- Uprostřed modulu je vodorovná bílá linka 1 px („spára“).
- Výška modulu: `TIME_H = round(1.2 × LH)`.

Datum (kalendářová kresba)
- Datum je modul ve stylu ikony kalendáře (zaoblení R, lem/okraj jako ostatní moduly).
- Uvnitř je horní lišta kalendáře oddělená bílou linkou 1 px.
- Uvnitř modulu je text `DD.MM.YYYY` (Bold, bílý) vycentrovaný.
- Referenční tvar a proporce jsou v PŘÍLOZE A.

Progress „teploměr“
- Teploměr je horizontální indikátor:
  - rám: lem bílý 2 px, okraj černý 1 px
  - pozadí: černé
  - výplň: bílá
- Odhadnutelný proces: výplň odpovídá 0–100 %.
- Neodhadnutelný proces: bílý segment se pohybuje tam a zpět v rámci teploměru.

## 5. Kontrakty barevných stavů (globální)

### 5.1 Nečervené interaktivní prvky (3 stavy)

Všechny nečervené interaktivní prvky MUSÍ mít stavy:

- NORMAL
  - lem: bílý
  - okraj: černý
  - pozadí: černé
  - obsah (text/ikona): bílý

- ACTIVE
  - lem: bílý
  - okraj: černý
  - pozadí: bílý
  - obsah: černý

- DISABLED
  - lem: šedivý
  - okraj: černý
  - pozadí: černé
  - obsah: šedivý

### 5.2 Červené (kritické) prvky (2 stavy)

Červený prvek MUSÍ mít jen:

- NORMAL
  - lem: červený
  - okraj: černý
  - pozadí: červené
  - obsah: černý

- ACTIVE
  - lem: červený
  - okraj: černý
  - pozadí: černé
  - obsah: červený

Pozn.: Focus overlay (sekce 3.2) mění jen lem na bílý i u červeného prvku.

## 6. Komponenty (specifikace)

### 6.1 Tlačítko (button)

Vzhled:
- používá kontrakt stavů dle sekce 5 (nečervené nebo červené).
- padding: `PAD_X`, `PAD_Y`
- radius: `R`
- text: Bold (pokud je to primární volba) nebo Regular (pokud je to sekundární; pokud není jasné, použij Bold)

Chování:
- Klik = aktivace.
- Klávesnice: focus + ENTER/MEZERNÍK = aktivace.

Šířka vs délka textu (determinismus):
- Preferovaná šířka: `W_pref = textWidth(FS) + 2×PAD_X + 2×(LEM+OKRAJ)`
- Skupina tlačítek MŮŽE být roztažená proporcionalně podle `W_pref` (např. „VOLBA1“ vs „VOLBA1VOLBA1“ → delší tlačítko).
- Pokud dostupný prostor nestačí, použije se algoritmus z 6.6 (text fit/scale).

### 6.2 Přepínač / Toggle, Radio, Checkbox, Klikatelná ikona

Všechny tyto prvky:
- používají stejné vrstvy a stejný stavový kontrakt (sekce 5),
- nesmí měnit layout mezi stavy,
- musí být fokusovatelné a ovladatelné klávesnicí.

Ikony:
- styl dle tokenů (outline, `STROKE`), barva dle stavu.

### 6.3 Tabulka / seznam

Obecně:
- sloupce mají měnitelnou šířku,
- řádky mají neměnitelnou výšku: `ROW_H`,
- výběr řádku: vždy invert barvy (ACTIVE kontrakt na celý řádek),
- kopírování: `CTRL+C` kopíruje vybraný text/buňku/řádek.

Tooltip v tabulce:
- zobrazí se po 2 s nečinnosti kurzoru **jen při overflow**,
- vzhled tooltipu:
  - lem: černý 2 px
  - okraj: bílý 1 px
  - pozadí: bílá
  - text: černý (Regular)
- tooltip je overlay a může překrývat UI.

### 6.4 Dialog

Geometrie:
- obdélník se zaoblením R, lem bílý 2 px, okraj černý 1 px, pozadí černé.

Název dialogu:
- vlevo nahoře, přeruší horní lem stejně jako sekce,
- Bold, VŠE VELKÝMI PÍSMENY.

Obsah:
- standardně 5 řádků: `5×LH` (vizuálně i výškově).
- pokud je obsahu více, použije se **vertikální overlay scrollbar** (tokeny sekce 6.7).

Akce (vždy přítomné):
- Tlačítka: **OK / CANCEL / CLOSE** (vždy).
- V dialogu je vždy vycentrovaný text (Regular) bez dalšího rámu.

Význam akcí:
- OK: potvrdit / provést
- CANCEL: zahodit změny
- CLOSE: zavřít bez akce
- Pokud dialog nemá „změny“, CANCEL a CLOSE se chovají stejně (ale zůstávají přítomné kvůli jednotnosti).

Klávesy:
- ENTER = OK (pokud focus není v zadávacím textovém poli)
- ESC = CLOSE
- TAB/SHIFT+TAB cyklují mezi fokusovatelnými prvky dialogu

### 6.5 Textové pole (v dialogu)

Typ:
- Zadávací (editable)
- Zobrazovací (read-only) – vždy umožňuje selection a kopírování

Vzhled:
- lem: bílý 2 px
- okraj: černý 1 px
- pozadí: černé
- text: bílý (Regular)
- placeholder: šedivý (Regular)

Placeholder řetězce (pevné):
- Zadávací pole: `Zde pište...`
- Zobrazovací pole: `Zde se zobrazí text...`

Caret:
- pouze u zadávacího pole s focusem,
- blikající svislá čára střídající bílou a černou.

Selection:
- vždy inverzní:
  - vybraný text: černý
  - pozadí selection: bílá

Chování:
- Zadávací pole: jako textový editor (psaní, mazání, výběr, přepsání výběru).
- Zobrazovací pole: nelze editovat, ale lze označit text a kopírovat (`CTRL+C`).

### 6.6 Text fit / scale-to-fit / fallback scroll (globální algoritmus)

Cíl: text se MUSÍ vejít; scroll je pouze fallback pro technické selhání měření/rendrování.

Definice:
- Overflow = obsah přesahuje obsahovou plochu o > 1 px.

Algoritmus:
1) Aplikuj globální škálování UI (sekce 1.3).  
2) Pokud prvek obsahuje jednoprvkový text (label/hodnota), prvek MŮŽE zvětšit šířku v hlavní ose podle `W_pref` (sekce 6.1), pokud to layout dovolí.  
3) Pokud stále overflow, zmenši obsah (text/ikony) scale-to-fit tak, aby se vešel (bez limitů).  
4) Znovu přeměř. Pokud stále overflow (framework limit, rounding), povol overlay scrollbar pouze na ose overflow.  
5) Scroll se NESMÍ aktivovat preventivně.

### 6.7 Scrollbar (posuvný válec)

Scrollbar je overlay (neubírá místo).

Vzhled:
- track: černý
- track okraj: bílý
- thumb: bílý
- šířka: `max(6, round(0.8 × FS))`

Pokud technologie overlay scrollbar nepodporuje, je povolena výjimka (standardní scrollbar), ale barvy musí odpovídat paletě.

### 6.8 Dropdown (needitovatelný)

Vzhled pole:
- pole je needitovatelný box dle nečerveného kontraktu (sekce 5),
- vpravo je šipka dolů (referenční ikona), barva dle stavu.

Roletka:
- otevře se dolů jako overlay,
- zobrazuje 5 položek; více položek = overlay scrollbar,
- pozadí: černé, okraj: bílý, oddělovače řádků: bílá linka 1 px,
- text položek: bílý (Regular).

Hover uvnitř roletky:
- při najetí na řádek se řádek invertuje (bílá plocha, černý text) – pouze uvnitř roletky.

Klávesnice:
- ŠIPKA DOLŮ otevře roletku a posouvá výběr položek.
- MEZERNÍK potvrdí položku a zavře roletku.
- ESC zavře roletku bez změny.
- Tooltip po 2 s nečinnosti na položce **jen při overflow** (zobrazí celý text u kurzoru).

### 6.9 Combobox (editovatelný)

Combobox = textové pole + roletka.

Pole:
- chová se jako zadávací textové pole (sekce 6.5), plus šipka dolů vpravo.

Filtrování:
- během psaní se roletka otevře a filtruje položky podle **case-insensitive prefix match** (deterministicky).
- diakritika se porovnává přesně (žádné „chytré“ přepisování), aby bylo chování deterministické.

Klávesnice:
- ŠIPKA DOLŮ otevře roletku a posouvá v položkách,
- ENTER vloží aktuální položku (pokud je roletka otevřená) a zavře,
- MEZERNÍK v editaci vkládá znak mezery (pokud roletka není v režimu výběru),
- ESC zavře roletku.

Tooltip na položce:
- po 2 s nečinnosti jen při overflow.

# PŘÍLOHA A – IKONY (REFERENČNÍ TVARY)

Všechny SVG:
- `viewBox="0 0 24 24"`
- `stroke-width = STROKE`
- `stroke-linecap="round"`, `stroke-linejoin="round"`
- barvu určuje komponenta (dle stavu), tvar je fixní.

## A.1 Šipka dolů (dropdown)

```svg
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M6 9 L12 15 L18 9" />
</svg>
```

## A.2 CLOSE (X)

```svg
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M7 7 L17 17" />
  <path d="M17 7 L7 17" />
</svg>
```

## A.3 Kalendář (datum ve status)

```svg
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="5" y="6" width="14" height="14" rx="2" ry="2" />
  <path d="M5 10 H19" />
  <path d="M8 4 V8" />
  <path d="M16 4 V8" />
</svg>
```

Pozn.: Text `DD.MM.YYYY` se kreslí **uvnitř** kalendáře (pod horní lištou), je to UI text, ne součást SVG.

## A.4 INFO (volitelně)

```svg
<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 10 V17" />
  <path d="M12 7 H12.01" />
</svg>
```

# PŘÍLOHA B – PÍSMO (MONTSERRAT) – DISTRIBUCE

Cíl: font je vždy stejný a je součástí programu (determinismus).

Minimální kontrakt:
1) Přibalit `Montserrat-Regular` a `Montserrat-Bold` (TTF/OTF) do aplikace.  
2) Při startu fonty zaregistrovat a použít je pro celé UI.  
3) Zakázat fallback. Pokud registrace selže → chybový dialog + ukončení.  
4) Pinovat soubory a kontrolovat hash v build pipeline.

Implementační poznámka:
- Konkrétní API závisí na technologii (web/desktop/mobile). Pro generování programu je podstatný výsledek: font je lokální asset a je aktivně použit.

# PŘÍLOHA C – KONTROLA SHODY (pro automatické testy)

Doporučené testy pro udržení identity napříč projekty:
- Golden screenshots (hlavní obrazovky + dialog + tabulka + dropdown + combobox) ve 3 velikostech okna (např. 800×600, 1280×720, 1920×1080).
- Kontrola hash font souborů v CI.
- Statická kontrola tokenů (barvy, tloušťky, radius, paddingy).
