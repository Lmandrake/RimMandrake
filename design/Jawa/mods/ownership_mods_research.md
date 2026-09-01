# Jawa Ownership, Theft, and Settlement Interaction in RimWorld

## Executive Summary

There are several RimWorld mods with relevant ownership, access-control, settlement-visiting, commerce, and personal-property mechanics. However, there does not appear to be one mature mod that implements a fully generalized multi-party property system such as:

> Item → personally owned by Pawn A → inside Business B → under Faction C → Guest D has permission to use it → theft only becomes known if witnessed.

Instead, the mod ecosystem contains several strong partial implementations. For a Jawa scavenging-and-theft system, the most important finding is that **Visit Settlements** already solves a substantial fraction of the core problem.

The most promising architecture would combine:

- faction-level settlement ownership,
- thing-level personal ownership,
- access permissions,
- commercial transfer,
- provenance,
- and crime perception / knowledge.

The novel part would likely be the final layer: **ownership violation does not automatically imply universal knowledge of the crime.**

---

## Relevant Existing Mods

| Mod | Ownership / Rights Model | Relevance |
|---|---|---|
| **Visit Settlements 1.6** | Host-faction property vs visiting player | **Extremely relevant** |
| **Possessions Plus** | Individual pawns own individual items | **Extremely relevant** |
| **Get Out Of My Chair!** | Public / colonist / slave / guest / private / specific-owner permissions | Very relevant architecture |
| **Security Clearance** | Hierarchical and special-purpose access rights | Useful for buildings and zones |
| **Personal Doors / Locks** | Specific pawns or groups control access | Useful supporting mechanic |
| **This Is Mine!** | Furniture assigned to particular pawns | Simple ownership precedent |
| **Hospitality + Storefront** | Guests, shopping inventories, legal commercial transfer | Economic ownership / permissions |
| **RimCities** | Friendly faction cities, exploration, in-person trading, scavenging | Excellent environment, weaker property model |

---

# 1. Visit Settlements

## Why It Matters

**Visit Settlements** is unusually close to the desired Jawa gameplay loop.

It allows the player to enter friendly faction settlements without attacking them, walk around a generated settlement map, interact with residents, rent beds, and otherwise remain on the map peacefully.

It also explicitly models penalties for:

- theft,
- opening containers,
- mining,
- encroachment,
- vandalism.

This is directly relevant to a future system where Jawas can enter towns on foot and decide whether to trade, salvage, trespass, strip equipment, or steal.

## How Its Ownership Model Works

The implementation appears to work roughly like this:

1. The settlement map is generated.
2. Existing eligible items are gathered into a persistent collection of settlement-owned items.
3. Settlement structures are also tracked.
4. These items are treated as belonging to the host settlement/faction.
5. Player actions against them trigger consequences.

Relevant actions include:

- taking a tracked item,
- minifying a tracked building,
- deconstructing settlement structures,
- mining resources,
- constructing unauthorized buildings,
- leaving the map with stolen property.

The system also performs inventory checks when the caravan leaves, which catches property that has been taken from the settlement.

## Value-Sensitive Theft

The theft penalty scales with the value and quantity of stolen goods.

Conceptually:

```text
goodwill penalty =
base penalty
+ market value scaling
+ quantity scaling
```

That is useful because stealing a steel knife should not have the same diplomatic impact as dismantling a settlement power generator.

## Major Limitation

This is **not truly granular ownership**.

Conceptually, the logic is closer to:

> This map belongs to Faction X.  
> These things existed before you arrived.  
> Therefore these things belong to Faction X.

It does not appear to represent more complex legal relationships such as:

> Blaster → owned by Pawn Bob  
> Bob → employed by Droid Repair Shop  
> Shop → operates under Hutt faction  
> Blaster → currently merchandise  
> Jawa visitor → permitted to inspect but not take it

The other major limitation is **omniscient crime knowledge**.

A theft action can immediately affect faction goodwill even if nobody plausibly observed it.

For Jawa gameplay, this is probably the biggest thing to change.

---

# 2. Possessions Plus

## Why It Matters

**Possessions Plus** demonstrates that individual pawns can have persistent ownership relationships with individual Things.

Pawns can:

- claim possessions,
- own weapons,
- own apparel,
- own personal items,
- prevent other pawns from freely using owned objects,
- gift possessions,
- inherit possessions,
- store things in personal containers,
- maintain emotional attachment to important possessions.

This establishes an important precedent:

```text
Pawn A → owns → Thing B
```

Rather than only:

```text
Faction X → owns everything on Map Y
```

For a generalized property system, this is probably the strongest precedent for durable Thing-level ownership.

---

# 3. Get Out Of My Chair!

This mod has a surprisingly useful architectural distinction:

> **Ownership and permission are not the same thing.**

Furniture can be designated for categories such as:

- Public
- Colonist
- Slave
- Private
- Guest
- Disallowed

Private furniture can additionally be associated with a particular pawn.

This is extremely relevant because a realistic property system should separate:

```text
Who owns this?
```

from:

```text
Who is allowed to use this?
```

Examples:

- A shopkeeper owns a chair, but customers may sit in it.
- A Jawa owns a gravship reactor, but maintenance droids may work on it.
- A Hutt faction owns a warehouse, but merchants have authorized access.
- A visitor may enter a public shop but not the stockroom.

This suggests a reusable **AccessPolicy** layer.

---

# 4. Security Clearance

**Security Clearance** demonstrates another useful abstraction:

```text
Identity → rights → object or area
```

Rather than storing every allowed pawn individually on every object.

Its hierarchical clearance model could inspire systems such as:

- public,
- resident,
- employee,
- military,
- restricted,
- command,
- special-purpose authorization.

This becomes especially useful for settlement maps containing:

- public streets,
- shops,
- bedrooms,
- warehouses,
- workshops,
- secure compounds,
- military installations,
- droid maintenance bays,
- faction headquarters.

---

# 5. Hospitality and Storefront

These mods provide an important economic layer.

Hospitality already distinguishes between:

- colony members,
- guests,
- visitors from other factions,
- guest areas,
- commercial interactions.

Storefront adds physical shopping where objects become merchandise and customers purchase them.

That establishes another important state transition:

```text
owned property
→ offered for sale
→ purchaser pays
→ legal ownership transfers
```

This distinction is critical for theft.

A Jawa who buys a hydrospanner and a Jawa who steals a hydrospanner may end up physically possessing the same object, but the object's **provenance** should be different.

---

# 6. RimCities

**RimCities** is relevant primarily as an environmental and settlement-generation reference.

It supports:

- large faction cities,
- peaceful visits,
- exploration,
- in-person trading,
- combat,
- scavenging,
- abandoned urban environments,
- changes in city control.

It does not appear to provide the granular property model required here, but it is highly relevant to the desired experience of physically exploring populated settlements rather than interacting only through abstract caravan trade dialogs.

---

# Proposed Generalized Property Architecture

A Jawa settlement-interaction system should probably avoid giving literally every rock and tree a complex owner record.

Instead, use a lightweight property record only where it matters.

## PropertyRecord

Conceptually:

```text
Thing
  → legal owner
  → current possessor
  → provenance
  → permissions
  → disposition
```

Possible owner types:

```text
none
pawn
faction
business/entity
player
```

Possible dispositions:

```text
abandoned
public
private
merchandise
rented
gifted
stolen
salvage-claim
restricted
```

---

# AccessPolicy

Ownership should remain separate from authorization.

Possible policies:

```text
public
faction
resident
employee
guest
clearance-based
explicit pawn
explicit group
disallowed
```

This permits much richer settlement behavior.

For example:

```text
Moisture condenser
Owner: Mos Espa Utility Cooperative
Access: Employees only
Disposition: Operational infrastructure
```

or:

```text
Droid
Owner: Merchant Tal Vex
Access: Owner + maintenance staff
Disposition: Private property
```

or:

```text
Protocol droid
Owner: Jawa Trade Clan
Current possessor: Blackstar Company
Provenance: Stolen
```

---

# Crime Knowledge

This appears to be the most important missing layer in existing mods.

Property violation and knowledge of property violation should be separate systems.

Possible states:

```text
unknown
suspected
witnessed
recorded
identified
confirmed
```

A theft event might therefore proceed as follows:

```text
Jawa removes owned component
↓
ownership violation occurs
↓
theft event is created
↓
nearby pawns / cameras / security systems evaluate perception
↓
crime may or may not be observed
↓
faction may later discover the item missing
↓
suspect may or may not be identified
```

This creates much better gameplay than:

```text
Jawa clicks Steal
↓
Faction instantly loses goodwill
```

---

# Provenance

Every meaningful stolen or transferred object could retain lightweight provenance.

Example:

```text
Thing:
Industrial Power Regulator

Legal owner:
Blackstar Company

Current possessor:
Jawa Trade Clan

Origin:
Mos Pelgo Generator Room

Acquisition:
Unlawful removal

Faction awareness:
Known missing

Suspect:
Unknown

Serial / identity confidence:
High
```

This enables later interactions.

For example, weeks after stealing it, the player might attempt to sell the regulator back to Blackstar Company.

Possible outcomes:

```text
They fail to recognize it.
→ Sale succeeds.

They recognize the model but cannot prove ownership.
→ Suspicion increases.

Serial number matches stolen equipment.
→ Confrontation.

They urgently need the part.
→ They buy it anyway, but relations suffer.

A corrupt trader knows exactly what happened.
→ Sale succeeds at reduced price.
```

This creates stories rather than merely penalties.

---

# Jawa Gameplay Implications

The resulting system supports a broader **Jawa Scavenging & Acquisition** gameplay pillar:

```text
Explore settlements
↓
Assess technology
↓
Trade
↓
Salvage
↓
Trespass
↓
Pilfer
↓
Strip machinery
↓
Disable droids
↓
Escape
↓
Refurbish
↓
Resell
```

The point is not simply to create a `STEAL` verb.

The larger goal is to make foreign settlements into real spaces containing:

- public property,
- private property,
- commercial goods,
- faction infrastructure,
- abandoned salvage,
- restricted areas,
- personally owned possessions,
- tempting droids,
- security,
- witnesses,
- opportunities.

Jawas then become specialists in navigating the ambiguous boundary between:

```text
salvage
appropriation
theft
trade
fraud
recovery
```

---

# Recommended Design Direction

The strongest implementation path appears to be:

## Borrow Conceptually From Visit Settlements

Use it as the model for:

- peaceful foreign settlement maps,
- foreign-faction property tracking,
- penalties for hostile property interactions,
- departure inventory checks,
- settlement lifecycle.

## Borrow Conceptually From Possessions Plus

Use it as precedent for:

- persistent Thing-level ownership,
- pawn-level ownership,
- gifts,
- inheritance,
- personal property.

## Borrow Conceptually From Permission Mods

Use them as precedent for:

- ownership vs authorization,
- public/private distinctions,
- role-based permissions,
- clearance systems.

## Borrow Conceptually From Hospitality / Storefront

Use them as precedent for:

- merchandise,
- customer access,
- legal purchase,
- explicit property transfer.

## Add a New Crime-Perception Layer

This is likely the most important original system:

```text
ownership violation
≠
automatic faction knowledge
```

Instead:

```text
ownership violation
+
perception
+
evidence
+
identification
=
crime consequences
```

---

# Bottom Line

The RimWorld mod ecosystem already demonstrates nearly every technical component needed for complex Jawa property gameplay.

What does **not** appear to exist as one integrated system is:

> **ownership + provenance + permissions + perception**

That combination is likely the interesting innovation.

For the Jawa scenario, this would transform stealing from a simple action into a broader systemic gameplay loop involving settlement exploration, salvage law, trespassing, droid acquisition, theft, witnesses, contraband, resale, and faction memory.

The resulting experience would be much more distinctive than simply giving Jawas a generic theft command.
