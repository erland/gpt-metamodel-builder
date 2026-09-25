# Architecture Lite – metamodell

Liten referensmetamodell för end-to-end-test.

## Metadata

| Fält | Värde |
| --- | --- |
| ID | architecture_lite |
| Version | 1.0.0 |
| Namespace | org.example.archlite |
| Standardspråk | sv |

## Elementtyper

| ID | Namn | Typ | Beskrivning | Property sets |
| --- | --- | --- | --- | --- |
| capability | Capability | structure | En förmåga organisationen behöver ha. | lifecycle |
| application | Application | artifact | En applikation som stödjer verksamheten. | lifecycle |
| platform | Platform | structure | Teknisk plattform för applikationer. | lifecycle |
| business_process | Business Process | behavior | Verksamhetsprocess. | lifecycle |

## Relationstyper

| ID | Namn | Typ | Riktad | Källa | Mål |
| --- | --- | --- | --- | --- | --- |
| application_realizes_capability | Application realizes Capability | realization | True | application | capability |
| platform_supports_application | Platform supports Application | dependency | True | platform | application |
| process_realizes_capability | Business Process realizes Capability | realization | True | business_process | capability |

## Egenskaper

| ID | Namn | Datatyp | Kardinalitet | Obligatorisk | Default |
| --- | --- | --- | --- | --- | --- |
| status | Status | enum:lifecycle_status | 1 | True | active |
| owner | Owner | string | 0..1 | False |  |

### Enumerations

#### Lifecycle status (`lifecycle_status`)

| ID | Namn |
| --- | --- |
| planned | Planned |
| active | Active |
| retired | Retired |

## Constraints

| ID | Namn | Severity | Gäller | Regel | Meddelande |
| --- | --- | --- | --- | --- | --- |
| capability_has_owner | Capability should have owner | warning | capability | property(owner) is not empty | Capability bör ha en angiven ägare. |

## Viewpoints

### Capability Map (`capability_map`)

Visar förmågor och realiserande verksamhets-/applikationsstruktur.

| Fält | Värde |
| --- | --- |
| Syfte | Förmågeanalys |
| Intressenter | business architect, enterprise architect |
| Element | capability, application, business_process |
| Relationer | application_realizes_capability, process_realizes_capability |
| Obligatoriska element | capability |

### Application and Platform (`application_platform`)



| Fält | Värde |
| --- | --- |
| Syfte |  |
| Intressenter |  |
| Element | application, platform |
| Relationer | platform_supports_application |
| Obligatoriska element |  |

## Notation

| ID | Gäller | Form | Visar namn | Visar stereotype | Visar properties |
| --- | --- | --- | --- | --- | --- |
| capability_style | element:capability | rounded_rectangle | True | False | status |
| application_style | element:application | rectangle | True | False |  |
| platform_support_style | relationship:platform_supports_application | line | False |  |  |

## Provenance

### Källor

| ID | Namn | Typ | Notering |
| --- | --- | --- | --- |
| user_design | Metamodel Builder reference design | user_input | Intern referensmodell utan extern standardtext. |

### Mappningar

| Mål | Källa | Referens | Relation | Confidence |
| --- | --- | --- | --- | --- |
| element:capability | user_design | Capability concept | derived_from | 1.0 |

## Versionsinformation

| Fält | Värde |
| --- | --- |
| Aktuell version | 1.0.0 |
| Kompatibilitetsnivå | initial |
| Kompatibel med |  |
| Release notes | Första canonical referensversion. |

### Ändringar

| Typ | Mål | Beskrivning | Breaking |
| --- | --- | --- | --- |
| add | metamodel | Initial referensmetamodell. | False |
