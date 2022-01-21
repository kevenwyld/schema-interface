# Curation
SDF v1.3 | Notes on curation fields and where to get them. Some descriptions from SDF documentation
---
- [Curation](#curation)
  - [SDF v1.3 | Notes on curation fields and where to get them. Some descriptions from SDF documentation](#sdf-v13--notes-on-curation-fields-and-where-to-get-them-some-descriptions-from-sdf-documentation)
  - [Events](#events)
  - [Participants](#participants)
  - [Children](#children)
  - [Entities](#entities)
  - [Relations](#relations)

---
Generally one event has at least 2 references in the JSON: as an event and as a child of some other event. The event reference gives more specific information about the event (node information), while the child reference simply links the event to its parent and its siblings (edge information).

## Events
⚠ denotes required fields.
- ⚠ `@id`: `prefix:Events/<unique-5-digit-number>/<anything>`, The 5-digit number is unique per event and belongs to the Events list.
    - `resin:Events/10000/resin:Events_disease-outbreak`
- ⚠ `name`: human-readable label
- `description` or `comment`: human-readable description.
  - Generally only the first event uses `description`, all other events seem to use `comment`.
  - It appears that this is where all container nodes have the comment `container node`.
- `qnode` and `qlabel`: q-node from Wikidata. `qnode` denotes the QID and `qlabel` denotes the name, eg. [disease outbreak (Q3241045)](https://www.wikidata.org/wiki/Q3241045)
- `minDuration` and `maxDuration`: minimum and maximum duration of the event. 
- `goal`: string for TA2 defining when the event achieves a goal
- (⚠) `ta1explanation`: Explanation of the event. Required for events without children.
- `privateData`:
  - `template`: ?
  - `repeatable`: whether the event can occur multiple times.
  - `importance`: [0, 1.0] represents importance. Also present in the child reference for the event.
- (⚠) `participants`: [participants](#participants) of an event. Required when there are no children.
- `children`: [children](#children) of an event.
- (⚠) `children_gate`: logical processing of node's children. Can be `and`, `or`, or `xor`. Required when there are children.

## Participants
- `@id`: `prefix:Participants/<unique-5-digit-number>/event@id_participantName`; the 5-digit number is unique per participant and belongs to the Participants list.
- `roleName`: taken from the XPO overlay. ask for the JSON.
- `entity`: @id reference to [entity](#entities)

## Children
- `child`: @id reference to event
- `comment`: human-readable description.
- `optional`: whether an event is optional.
- `importance`: [0, 1.0] represents importance of the event in the subevent.
- `outlinks`: list of @ids of other events. Generally the next event in the sequence.

## Entities
Forms coreference links between events. For example, if two different events have participants with the same `victim` entity, they are referencing the same `victim`.
- ⚠ `@id`: `prefix:Entities/<unique-5-digit-number>`; the 5-digit number is unique per entity and belongs to the Entities list.
- ⚠ `name`: human-readable label
- ⚠ `qnode` and `qlabel`: q-node from Wikidata. `qnode` denotes the QID and `qlabel` denotes the name, eg. [disease outbreak (Q3241045)](https://www.wikidata.org/wiki/Q3241045)

## Relations
Specifies event-event / entity-entity relations.
- ⚠ `relationSubject`: @id reference to event / entity
- ⚠ `relationPredicate`: Wikidata q-node or p-node
- ⚠ `relationObject`: @id reference to event / entity
- ⚠ `@id`: `prefix:Relations/<unique-5-digit-number>`; the 5-digit number is unique per entity and belongs to the Relations list.