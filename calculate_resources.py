import json
from collections import defaultdict


DATA_FILE = "data.json"
PLAYER_FILE = "swgoh_972824625.json"
C3PO_FILE = "c3po.json"
TARGETS_FILE = "targets.json"
OUTPUT_FILE = "account_farming_report.md"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f, strict=False)


def as_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_id(value):
    if value is None:
        return ""
    return str(value).strip()


def walk(obj):
    yield obj

    if isinstance(obj, dict):
        for value in obj.values():
            yield from walk(value)

    elif isinstance(obj, list):
        for value in obj:
            yield from walk(value)


# ============================================================
# PLAYER ROSTER
# ============================================================

def get_base_id(player_unit):
    for skill in player_unit.get("skill", []):
        skill_id = skill.get("id", "")

        if skill_id.startswith("basicskill_"):
            return skill_id.replace("basicskill_", "")

    definition = player_unit.get("definitionId", "")

    if definition:
        return definition.split(":")[0]

    return ""


def build_player_roster(player):
    roster = {}

    for unit in player.get("rosterUnit", []):
        base_id = get_base_id(unit)

        if base_id:
            roster[base_id] = unit

    return roster


# ============================================================
# C3PO INVENTORY
# ============================================================

def read_c3po_inventory(c3po):
    inventory = c3po.get("inventory", {})

    result = defaultdict(int)

    # Materials
    for item in inventory.get("material", []):
        item_id = normalize_id(item.get("id"))
        quantity = as_int(item.get("quantity"))

        if item_id:
            result[item_id] += quantity

    # Equipment
    equipment = inventory.get("equipment", [])

    if isinstance(equipment, list):

        for item in equipment:
            item_id = normalize_id(item.get("id"))

            quantity = as_int(
                item.get(
                    "quantity",
                    item.get(
                        "count",
                        item.get("amount", 0)
                    )
                )
            )

            if item_id:
                result[item_id] += quantity

    elif isinstance(equipment, dict):

        for item_id, value in equipment.items():

            if isinstance(value, dict):
                quantity = as_int(
                    value.get(
                        "quantity",
                        value.get(
                            "count",
                            value.get("amount", 0)
                        )
                    )
                )
            else:
                quantity = as_int(value)

            result[normalize_id(item_id)] += quantity

    return dict(result)


# ============================================================
# UNIT DEFINITIONS
# ============================================================

def find_unit_definition(data, base_id):

    for node in data.get("units", []):

        if isinstance(node, dict) and node.get("baseId") == base_id:
            return node

    return None


def get_current_gear(unit):
    return as_int(
        unit.get(
            "currentTier",
            unit.get("gearLevel", 0)
        )
    )


def get_current_relic(unit):
    relic = unit.get("relic")

    if not isinstance(relic, dict):
        return 0

    return as_int(
        relic.get(
            "currentTier",
            relic.get("tier", 0)
        )
    )


# ============================================================
# UNIT TIER / GEAR
# ============================================================

def build_unit_tier_map(unit_definition):

    result = {}

    if not unit_definition:
        return result

    unit_tiers = unit_definition.get("unitTier", [])

    if not isinstance(unit_tiers, list):
        return result

    for entry in unit_tiers:

        if not isinstance(entry, dict):
            continue

        tier = as_int(entry.get("tier"))

        if tier <= 0:
            tier = as_int(entry.get("unitTier"))

        if tier <= 0:
            continue

        result[tier] = entry

    return result


def get_gear_for_tier(unit_definition, tier):

    tier_map = build_unit_tier_map(unit_definition)

    entry = tier_map.get(tier)

    if not entry:
        return []

    equipment_set = entry.get("equipmentSet", [])

    if not isinstance(equipment_set, list):
        return []

    result = []

    for item in equipment_set:

        item_id = normalize_id(
            item.get("id") if isinstance(item, dict) else item
        )

        if not item_id:
            continue

        # 9999 is a current-game placeholder used for G13.
        if item_id == "9999":
            continue

        result.append(item_id)

    return result


def collect_direct_gear_requirements(
    unit_definition,
    current_gear,
    target_gear
):

    required = defaultdict(int)

    if target_gear <= current_gear:
        return dict(required)

    for tier in range(
        current_gear + 1,
        target_gear + 1
    ):

        for item_id in get_gear_for_tier(
            unit_definition,
            tier
        ):
            required[item_id] += 1

    return dict(required)


# ============================================================
# EQUIPMENT / CRAFT RECIPES
# ============================================================

def build_recipe_database(data):

    """
    Maps final result item ID -> recipe ingredients.

    Example:

        G12Finisher_JARJARBINKS_C
            ->
        176Ingredient x1
        170Prototype x1
        ...
    """

    recipes = {}

    for node in walk(data):

        if not isinstance(node, dict):
            continue

        ingredients = node.get("ingredients")

        if not isinstance(ingredients, list):
            continue

        result = node.get("result")

        if not isinstance(result, dict):
            continue

        result_id = normalize_id(
            result.get("id")
        )

        if not result_id:
            continue

        parsed = []

        for ingredient in ingredients:

            if not isinstance(ingredient, dict):
                continue

            ingredient_id = normalize_id(
                ingredient.get("id")
            )

            if not ingredient_id:
                continue

            quantity = as_int(
                ingredient.get(
                    "minQuantity",
                    ingredient.get("quantity", 1)
                ),
                1
            )

            if quantity <= 0:
                continue

            parsed.append(
                (
                    ingredient_id,
                    quantity
                )
            )

        if parsed:
            recipes[result_id] = parsed

    return recipes


# ============================================================
# INVENTORY-AWARE CRAFT EXPANSION
# ============================================================

def consume_item(
    item_id,
    quantity,
    inventory,
    recipes,
    gross_shortage,
    unresolved,
    stack=None
):

    if quantity <= 0:
        return

    item_id = normalize_id(item_id)

    if not item_id:
        return

    if stack is None:
        stack = set()

    # --------------------------------------------------------
    # Use owned copies first.
    # --------------------------------------------------------

    owned = inventory.get(item_id, 0)

    used = min(
        owned,
        quantity
    )

    if used:
        inventory[item_id] -= used
        quantity -= used

    if quantity <= 0:
        return

    # --------------------------------------------------------
    # No inventory left.
    # Check whether this item can be crafted.
    # --------------------------------------------------------

    ingredients = recipes.get(item_id)

    if not ingredients:

        gross_shortage[item_id] += quantity

        return

    # --------------------------------------------------------
    # Cycle protection.
    # --------------------------------------------------------

    if item_id in stack:

        unresolved.append(
            f"Recipe cycle detected: {item_id}"
        )

        gross_shortage[item_id] += quantity

        return

    next_stack = set(stack)
    next_stack.add(item_id)

    for ingredient_id, ingredient_quantity in ingredients:

        consume_item(
            ingredient_id,
            quantity * ingredient_quantity,
            inventory,
            recipes,
            gross_shortage,
            unresolved,
            next_stack
        )


# ============================================================
# RELIC RECIPES
# ============================================================

def build_relic_recipe_database(data):

    recipes = {}

    for node in walk(data):

        if not isinstance(node, dict):
            continue

        node_id = normalize_id(
            node.get("id")
        )

        if not node_id.startswith(
            "relic_promotion_recipe_"
        ):
            continue

        ingredients = node.get("ingredients")

        if not isinstance(ingredients, list):
            continue

        parsed = []

        for ingredient in ingredients:

            if not isinstance(ingredient, dict):
                continue

            ingredient_id = normalize_id(
                ingredient.get("id")
            )

            if not ingredient_id:
                continue

            quantity = as_int(
                ingredient.get(
                    "minQuantity",
                    ingredient.get("quantity", 1)
                ),
                1
            )

            if quantity <= 0:
                continue

            parsed.append(
                (
                    ingredient_id,
                    quantity
                )
            )

        if parsed:
            recipes[node_id] = parsed

    return recipes


def add_relic_requirements(
    current_relic,
    target_relic,
    relic_recipes,
    required
):

    if target_relic <= current_relic:
        return

    for relic_tier in range(
        current_relic + 1,
        target_relic + 1
    ):

        recipe_id = (
            f"relic_promotion_recipe_{relic_tier:02d}"
        )

        ingredients = relic_recipes.get(recipe_id)

        if not ingredients:
            required["_UNRESOLVED_RELIC_"] += 1
            continue

        for item_id, quantity in ingredients:
            required[item_id] += quantity


# ============================================================
# ITEM NAMES
# ============================================================

def build_item_names(data):

    names = {}

    for node in walk(data):

        if not isinstance(node, dict):
            continue

        item_id = normalize_id(
            node.get("id")
        )

        if not item_id:
            continue

        name = (
            node.get("name")
            or node.get("displayName")
            or node.get("descKey")
            or node.get("nameKey")
        )

        if name:
            names[item_id] = name

    return names


def item_name(item_id, names):

    return names.get(
        item_id,
        item_id
    )


# ============================================================
# TARGET CALCULATION
# ============================================================

def calculate_target(
    target,
    player_roster,
    data,
    recipes,
    relic_recipes,
    working_inventory,
    item_names
):

    base_id = normalize_id(
        target.get("baseId")
    )

    target_gear = as_int(
        target.get("targetGearTier")
    )

    target_relic = as_int(
        target.get("targetRelicTier")
    )

    unit = player_roster.get(base_id)

    if not unit:

        return {
            "baseId": base_id,
            "status": "NOT_OWNED",
            "currentGear": 0,
            "currentRelic": 0,
            "targetGear": target_gear,
            "targetRelic": target_relic,
            "gearRequired": {},
            "relicRequired": {},
            "shortages": {},
            "unresolved": [
                f"{base_id} not found in player roster"
            ]
        }

    current_gear = get_current_gear(unit)
    current_relic = get_current_relic(unit)

    definition = find_unit_definition(
        data,
        base_id
    )

    if not definition:

        return {
            "baseId": base_id,
            "status": "NO_UNIT_DEFINITION",
            "currentGear": current_gear,
            "currentRelic": current_relic,
            "targetGear": target_gear,
            "targetRelic": target_relic,
            "gearRequired": {},
            "relicRequired": {},
            "shortages": {},
            "unresolved": [
                f"No unit definition found for {base_id}"
            ]
        }

    direct_gear = collect_direct_gear_requirements(
        definition,
        current_gear,
        target_gear
    )

    gear_shortage = defaultdict(int)
    unresolved = []

    # --------------------------------------------------------
    # Gear.
    # Inventory is consumed globally and recursively.
    # --------------------------------------------------------

    gear_inventory_before = dict(
        working_inventory
    )

    for item_id, quantity in direct_gear.items():

        consume_item(
            item_id,
            quantity,
            working_inventory,
            recipes,
            gear_shortage,
            unresolved
        )

    # --------------------------------------------------------
    # Relic materials.
    # These are direct recipe ingredients, not craftable
    # equipment items.
    # --------------------------------------------------------

    relic_required = defaultdict(int)

    add_relic_requirements(
        current_relic,
        target_relic,
        relic_recipes,
        relic_required
    )

    relic_shortage = {}

    for item_id, quantity in relic_required.items():

        if item_id == "_UNRESOLVED_RELIC_":
            continue

        owned = working_inventory.get(
            item_id,
            0
        )

        used = min(
            owned,
            quantity
        )

        if used:
            working_inventory[item_id] -= used

        remaining = quantity - used

        if remaining > 0:
            relic_shortage[item_id] = {
                "required": quantity,
                "owned": owned,
                "shortage": remaining
            }

    # --------------------------------------------------------
    # Combine gear shortages.
    # --------------------------------------------------------

    shortages = {}

    for item_id, quantity in gear_shortage.items():

        original_owned = (
            gear_inventory_before.get(
                item_id,
                0
            )
        )

        shortages[item_id] = {
            "required": quantity,
            "owned": original_owned,
            "shortage": quantity
        }

    # Relic shortage entries override only when same item is
    # also required by gear; otherwise combine them.
    for item_id, values in relic_shortage.items():

        if item_id in shortages:

            shortages[item_id]["required"] += (
                values["required"]
            )

            shortages[item_id]["shortage"] += (
                values["shortage"]
            )

        else:

            shortages[item_id] = dict(values)

    return {
        "baseId": base_id,
        "status": "OK",
        "currentGear": current_gear,
        "currentRelic": current_relic,
        "targetGear": target_gear,
        "targetRelic": target_relic,
        "gearRequired": direct_gear,
        "relicRequired": dict(relic_required),
        "shortages": shortages,
        "unresolved": unresolved
    }


# ============================================================
# REPORT
# ============================================================

def generate_report(
    targets,
    results,
    item_names
):

    lines = []

    lines.append(
        "# Vhonte – Account Farming Report"
    )

    lines.append("")

    lines.append(
        "Automatycznie wygenerowany raport "
        "na podstawie aktualnego gamedata, rosteru "
        "oraz `c3po.json`."
    )

    lines.append("")

    # --------------------------------------------------------
    # Targets
    # --------------------------------------------------------

    lines.append("## Cele")
    lines.append("")

    for result in results:

        lines.append(
            f"- **{result['baseId']}**: "
            f"G{result['currentGear']} → "
            f"G{result['targetGear']}, "
            f"R{result['currentRelic']} → "
            f"R{result['targetRelic']}"
        )

    lines.append("")

    # --------------------------------------------------------
    # Combined shortages
    # --------------------------------------------------------

    merged = defaultdict(
        lambda: {
            "required": 0,
            "owned": 0,
            "shortage": 0
        }
    )

    for result in results:

        for item_id, values in result["shortages"].items():

            merged[item_id]["required"] += (
                values["required"]
            )

            merged[item_id]["shortage"] += (
                values["shortage"]
            )

            if not merged[item_id]["owned"]:
                merged[item_id]["owned"] = (
                    values["owned"]
                )

    lines.append("## Łączne braki")
    lines.append("")

    if not merged:

        lines.append(
            "Brak wykrytych braków."
        )

    else:

        lines.append(
            "| ID | Przedmiot | Wymagane | Posiadane | Brakuje |"
        )

        lines.append(
            "|---|---|---:|---:|---:|"
        )

        for item_id, values in sorted(
            merged.items(),
            key=lambda x: (
                -x[1]["shortage"],
                x[0]
            )
        ):

            lines.append(
                f"| `{item_id}` | "
                f"{item_name(item_id, item_names)} | "
                f"{values['required']} | "
                f"{values['owned']} | "
                f"**{values['shortage']}** |"
            )

    lines.append("")

    # --------------------------------------------------------
    # Per target
    # --------------------------------------------------------

    lines.append("## Szczegóły")
    lines.append("")

    for result in results:

        lines.append(
            f"### {result['baseId']}"
        )

        lines.append("")

        lines.append(
            f"Gear: **G{result['currentGear']} → "
            f"G{result['targetGear']}**"
        )

        lines.append(
            f"Relic: **R{result['currentRelic']} → "
            f"R{result['targetRelic']}**"
        )

        lines.append("")

        if result["gearRequired"]:

            lines.append(
                "#### Bezpośredni wymagany gear"
            )

            lines.append("")

            for item_id, quantity in sorted(
                result["gearRequired"].items()
            ):

                lines.append(
                    f"- `{item_id}` × {quantity} "
                    f"— {item_name(item_id, item_names)}"
                )

            lines.append("")

        if result["relicRequired"]:

            lines.append(
                "#### Materiały relic"
            )

            lines.append("")

            for item_id, quantity in sorted(
                result["relicRequired"].items()
            ):

                if item_id == "_UNRESOLVED_RELIC_":
                    continue

                lines.append(
                    f"- `{item_id}` × {quantity} "
                    f"— {item_name(item_id, item_names)}"
                )

            lines.append("")

        if result["shortages"]:

            lines.append(
                "#### Braki"
            )

            lines.append("")

            lines.append(
                "| ID | Przedmiot | Brakuje |"
            )

            lines.append(
                "|---|---|---:|"
            )

            for item_id, values in sorted(
                result["shortages"].items(),
                key=lambda x: (
                    -x[1]["shortage"],
                    x[0]
                )
            ):

                lines.append(
                    f"| `{item_id}` | "
                    f"{item_name(item_id, item_names)} | "
                    f"**{values['shortage']}** |"
                )

            lines.append("")

        if result["unresolved"]:

            lines.append(
                "#### Nierozwiązane"
            )

            lines.append("")

            for entry in sorted(
                set(result["unresolved"])
            ):

                lines.append(
                    f"- `{entry}`"
                )

            lines.append("")

    # --------------------------------------------------------
    # Technical information
    # --------------------------------------------------------

    lines.append(
        "## Informacje techniczne"
    )

    lines.append("")

    lines.append(
        "- Inventory pochodzi z `c3po.json`."
    )

    lines.append(
        "- Aktualny gear/relic pochodzi z rosteru."
    )

    lines.append(
        "- Wymagany gear pochodzi z `unitTier[].equipmentSet`."
    )

    lines.append(
        "- Receptury gearu są rozwijane rekurencyjnie."
    )

    lines.append(
        "- Materiały reliców pochodzą z "
        "`relic_promotion_recipe_01...10`."
    )

    lines.append(
        "- `9999` jest traktowane jako placeholder G13 "
        "i nie jest liczone jako gear."
    )

    lines.append("")

    return "\n".join(lines)


# ============================================================
# MAIN
# ============================================================

def main():

    print("Ładowanie danych...")

    data = load_json(DATA_FILE)
    player = load_json(PLAYER_FILE)
    c3po = load_json(C3PO_FILE)
    config = load_json(TARGETS_FILE)

    targets = config.get("targets", [])

    if not targets:
        raise RuntimeError(
            "targets.json nie zawiera żadnych targets."
        )

    inventory = read_c3po_inventory(
        c3po
    )

    print(
        "Pozycji inventory:",
        len(inventory)
    )

    recipes = build_recipe_database(
        data
    )

    print(
        "Receptury gear:",
        len(recipes)
    )

    relic_recipes = build_relic_recipe_database(
        data
    )

    print(
        "Receptury relic:",
        len(relic_recipes)
    )

    item_names = build_item_names(
        data
    )

    player_roster = build_player_roster(
        player
    )

    print(
        "Jednostek w rosterze:",
        len(player_roster)
    )

    # IMPORTANT:
    # One shared inventory is used for all targets.
    # This prevents the same item from being counted twice.
    working_inventory = defaultdict(
        int,
        inventory
    )

    results = []

    for target in targets:

        base_id = normalize_id(
            target.get("baseId")
        )

        if not base_id:
            continue

        print(
            "Liczenie:",
            base_id
        )

        result = calculate_target(
            target,
            player_roster,
            data,
            recipes,
            relic_recipes,
            working_inventory,
            item_names
        )

        results.append(
            result
        )

    report = generate_report(
        targets,
        results,
        item_names
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(report)

    print()
    print(
        "Wygenerowano:",
        OUTPUT_FILE
    )

    total_shortage = sum(
        values["shortage"]
        for result in results
        for values in result["shortages"].values()
    )

    print(
        "Łączna liczba brakujących jednostek materiałów:",
        total_shortage
    )


if __name__ == "__main__":
    main()
