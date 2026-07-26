# Tascam BD-MP4K → officiële Home Assistant integratie

Wat er in dit pakket zit en wat jij nog moet doen om de PR in te dienen.

## Wat is er veranderd ten opzichte van jouw repo

De oude code had blokkerende sockets in de event loop, een kapotte `manifest.json`
(ontbrekende `{`), een verkeerd query-commando (`!7?TNM` moest `!7?STC` zijn),
een ongebruikte `connection.py`, en losse verbindingen per entity terwijl de
speler maar één TCP-client accepteert. Dit is nu opgelost door de architectuur
die HA core vereist:

- **`aiotascam/`** — zelfstandige, volledig async PyPI-library met één
  persistente verbinding, ack/nack-afhandeling, de verplichte 30 ms
  commando-interval uit de spec, en standby-detectie via timeout op `!7?PWR`.
- **`homeassistant/components/tascam/`** — de integratie zelf:
  `DataUpdateCoordinator`, config flow met verbindingstest en duplicaat-check,
  `runtime_data`, één device met een rijke `media_player` (positie, duur,
  status, stop, standby, mute) plus buttons voor menu/lade-bediening,
  `strings.json` + EN/NL-vertalingen, `quality_scale.yaml` (Bronze).
- **`tests/components/tascam/`** — config flow 100% gedekt + setup/unload-tests.

Elapsed/remain time en playback-status zijn nu attributen van de media_player
(`media_position`/`media_duration`) in plaats van losse sensors — dat is wat
core-reviewers verwachten.

## Stappenplan indiening

Doe dit in volgorde; elke stap is een voorwaarde voor de volgende.

**Stap 1 — Publiceer `aiotascam` op PyPI.**
Maak een eigen GitHub-repo van de map `aiotascam/`, controleer dat de naam op
pypi.org nog vrij is, en publiceer: `pip install build twine && python -m build
&& twine upload dist/*`. Core accepteert geen integraties zonder gepubliceerde
library (regel: *dependency-transparency*).

**Stap 2 — Fork en kopieer.**
Fork `home-assistant/core`, maak een branch, kopieer
`homeassistant/components/tascam/` en `tests/components/tascam/` op dezelfde
plek in de fork.

**Stap 3 — Draai de core-tooling in je fork.**
`python -m script.hassfest` (genereert o.a. `config_flows.py` en
`requirements_all.txt` entries), daarna `pre-commit run --all-files` (draait
**ruff** — core gebruikt geen black meer, ruff-format is compatibel) en
`pytest tests/components/tascam`.

**Stap 4 — Logo naar het brands-repo.**
Je `Tascamlogo.png` hoort niet in de integratie maar in een aparte PR naar
`home-assistant/brands`, onder `core_integrations/tascam/` als `icon.png`
(256×256 + `icon@2x.png` 512×512) en `logo.png`. Let op: check of
TEAC/Tascam-merkgebruik geen bezwaar oplevert.

**Stap 5 — Documentatie-PR.**
Nieuwe integraties vereisen een gelijktijdige PR naar
`home-assistant/home-assistant.io` met `source/_integrations/tascam.markdown`
(installatie, verwijderen, ondersteunde functies, beperkingen). Vermeld daar de
beperking: inschakelen via Ethernet kan niet (protocol ondersteunt alleen
Wake-on-LAN), en er kan maar één controller tegelijk verbonden zijn.

**Stap 6 — De PR zelf.**
Vul de PR-template volledig in, link de docs-PR en de brands-PR. Als
codeowner (`@HuisAutomatisering` staat in de manifest) wordt van je verwacht
dat je issues blijft oppakken. Reken op meerdere review-rondes; nieuwe
integraties wachten soms weken op een reviewer — dat is normaal.

## Direct zelf gebruiken (zonder op de PR te wachten)

Kopieer `homeassistant/components/tascam/` naar
`config/custom_components/tascam/` en voeg in `manifest.json` één regel toe:
`"version": "1.0.0"` (verplicht voor custom components, verboden in core).
Zolang `aiotascam` nog niet op PyPI staat, kun je tijdelijk in de manifest de
requirement vervangen door een git-URL of de library handmatig installeren.

## Nog te overwegen (Silver/Gold, mag ook na de eerste PR)

Reconfigure-flow, diagnostics, icon-translations, en `log-when-unavailable`.
De `quality_scale.yaml` markeert deze als `todo` — reviewers zien daaraan dat
je het bewust hebt opgeschoven.
