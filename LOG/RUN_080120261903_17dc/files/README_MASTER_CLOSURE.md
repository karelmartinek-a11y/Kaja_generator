# MASTER_SPEC_COMPLETE_DOC

Konstantní textový popis v Markdown formátu, který vysvětluje, že MASTER specifikace Linux + FULL Windows Diagnostics je kompletní a tento chunk pouze signalizuje její ukončení.

---

# Linux + FULL Windows Diagnostics – MASTER zadání (ukončovací chunk)

Tento repozitářový balík reprezentuje **pouze ukončovací MASTER chunk** návrhu „Linux + FULL Windows Diagnostics“.

## Účel tohoto souboru

- Slouží jako **lidsky čitelná dokumentace** stavu `MASTER_SPEC_COMPLETE = true`.
- **Nezavádí žádné nové technické požadavky, moduly, API ani datové modely**.
- **Nesmí měnit ani rozšiřovat** žádná pravidla, kontrakty, struktury adresářů ani bezpečnostní omezení definovaná v předchozích chuncích.

Formální export tohoto souboru:

- `MASTER_SPEC_COMPLETE_DOC` – Konstantní textový popis v Markdown formátu, který vysvětluje, že MASTER specifikace Linux + FULL Windows Diagnostics je kompletní a tento chunk pouze signalizuje její ukončení.

Formální import tohoto souboru:

- `MASTER_SPEC_FULL_CONTEXT` z `external:MASTER_SPEC_PREVIOUS_CHUNKS` – konceptuální kontext celé předchozí MASTER specifikace (Linux + FULL Windows Diagnostics), bez přímých odkazů na konkrétní zdrojové soubory.

## Co bylo definováno dříve

Všechny následující oblasti byly **kompletně specifikovány v předchozích chuncích** a tento soubor je nijak nemění:

- Cíle a rozsah diagnostiky pro Linux a Windows (FULL Windows Diagnostics).
- Struktura adresářů a obsah `MANIFEST.md`.
- Pravidla pro redakci tajných údajů a citlivých informací, včetně použití stavů `ACCESS DENIED` a `NOT PRESENT`.
- Veškeré funkční a nefunkční požadavky na diagnostické skripty a nástroje.
- Bezpečnostní omezení a zásady práce s výstupy diagnostiky.
- Pravidla determinismu, opakovatelnosti a validace výstupů.
- UI a interakční pravidla podle Kájovo UI Design Standard (MASTER v1.0), pokud byla součástí předchozích chuků.

## Co tento chunk nedělá

Tento ukončovací chunk **nedělá** následující věci:

- Nepřidává žádné nové skripty, moduly, soubory ani API.
- Nemění žádné existující názvy symbolů, datové modely ani kontrakty.
- Neupřesňuje ani neaktualizuje build/run proces – ten je plně definován v předchozích chuncích.
- Nezavádí žádné nové bezpečnostní výjimky ani pravidla pro práci s citlivými daty.

## Jak tento soubor interpretovat

Při rekonstrukci nebo interpretaci celého MASTER zadání je nutné:

1. **Číst a vyhodnotit všechny předchozí chunky** jako jediný zdroj pravdy pro návrh „Linux + FULL Windows Diagnostics“.
2. Tento soubor chápat **pouze jako explicitní značku konce** – potvrzení, že návrh je uzavřený a připravený k deterministickému použití.
3. Neočekávat za tímto chunkem žádné další rozšíření, korekce nebo doplňující technické detaily.

## Stav specifikace

- MASTER specifikace: **kompletní**.
- Stav: návrh je připraven pro:
  - implementaci skriptů a nástrojů,
  - generování diagnostik,
  - validaci a automatizované testování výstupů.

## Vztah k předchozím chuncům

Tento soubor **konceptuálně importuje**:

- `MASTER_SPEC_FULL_CONTEXT` z `external:MASTER_SPEC_PREVIOUS_CHUNKS`

Tento import znamená, že:

- Veškeré detaily návrhu (Linux + FULL Windows Diagnostics) jsou již definovány jinde.
- Tento soubor na ně pouze odkazuje jako na **hotový a závazný kontext**.

## Shrnutí

- MASTER specifikace „Linux + FULL Windows Diagnostics“ je **uzavřená**.
- Tento soubor pouze **konstatuje ukončení** a poskytuje dokumentační export `MASTER_SPEC_COMPLETE_DOC`.
- Pro jakoukoliv implementaci nebo validaci je nutné vycházet z **předchozích chuků**, nikoliv z tohoto ukončovacího souboru.

Konec MASTER zadání.
