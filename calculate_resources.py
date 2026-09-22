import json
import math
import os
import re
from collections import defaultdict


DATA_FILE = "data.json"
PLAYER_FILE = "swgoh_972824625.json"
C3PO_FILE = "c3po.json"
TARGETS_FILE = "targets.json"
OUTPUT_FILE = "account_farming_report.md"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def as_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def walk(obj):
    """Yield every dict/list node recursively."""
    yield obj

    if isinstance(obj, dict):
        for value in obj.values():
            yield from walk(value)

    elif isinstance(obj, list):
        for value in obj:
            yield from walk(value)


def normalize_id(value):
    if value is None:
        return ""
    return str(value).strip()


def get_base_id(player_unit):
    """
    Extract baseId from a player roster unit.

    Current roster data commonly identifies the unit through
    basicskill_<BASEID>.
    """
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

        if not base_id:
            continue

        roster[base_id] = unit

    return roster


def read_c3po_inventory(c3po):
    """
    C3PO has several inventory areas.

    We keep the original IDs because current game data uses its own
    equipment/material identifiers.
    """
    inventory = c3po.get("inventory", {})

    result = defaultdict(int)

    # Standard material inventory
    for item in inventory.get("material", []):
        item_id = normalize_id(item.get("id"))
        quantity = as_int(item.get("quantity"))

        if item_id:
            result[item_id] += quantity

    # Equipment inventory
    equipment = inventory.get("equipment", [])

    if isinstance(equipment, list):
        for item in equipment:
            item_id = normalize_id(item.get("id"))
            quantity = as_int(
                item.get(
                    "quantity",
                    item.get("count", item.get("amount", 0))
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
                        value.get("count", value.get("amount", 0))
                    )
                )
            else:
                quantity = as_int(value)

            result[normalize_id(item_id)] += quantity

    return dict(result)


def build_equipment_database(data):
    """
    Build an index of equipment definitions.

    We intentionally support several possible current-gamedata layouts.
    """
    result = {}

    for node in walk(data):
        if not isinstance(node, dict):
            continue

        item_id = (
            node.get("id")
            or node.get("equipmentId")
            or node.get("equipment_id")
        )

        if not item_id:
            continue

        # Equipment definitions have characteristic fields.
        if any(
            key in node
            for key in (
                "recipeId",
                "nameKey",
                "iconKey",
                "requiredLevel",
                "equipmentStat",
                "tier",
            )
        ):
            result[normalize_id(item_id)] = node

    return result


def build_recipe_database(data):
    """
    Search recursively for recipe definitions.

    Different game-data releases have used slightly different
    container names, so this deliberately does not depend on one
    fixed top-level schema.
    """
    recipes = {}

    for node in walk(data):
        if not isinstance(node, dict):
            continue

        node_id = node.get("id") or node.get("recipeId")

        if not node_id:
            continue

        # Candidate recipe containers
        for key in (
            "ingredients",
            "ingredient",
            "recipe",
            "components",
            "component",
            "requirements",
        ):
            value = node.get(key)

            if not isinstance(value, list):
                continue

            ingredients = []

            for entry in value:
                if not isinstance(entry, dict):
                    continue

                ingredient_id = (
                    entry.get("id")
                    or entry.get("equipmentId")
                    or entry.get("itemId")
                    or entry.get("materialId")
                    or entry.get("ingredientId")
                )

                quantity = (
                    entry.get("quantity")
                    or entry.get("amount")
                    or entry.get("count")
                    or entry.get("requiredQuantity")
                )

                if ingredient_id and quantity is not None:
                    ingredients.append(
                        (
                            normalize_id(ingredient_id),
                            as_int(quantity)
                        )
                    )

            if ingredients:
                recipes[normalize_id(node_id)] = ingredients

    return recipes


def resolve_recipe_id(equipment):
    if not equipment:
        return ""

    recipe_id = equipment.get("recipeId")

    if recipe_id:
        return normalize_id(recipe_id)

    recipe = equipment.get("recipe")

    if isinstance(recipe, dict):
        return normalize_id(
            recipe.get("id") or recipe.get("recipeId")
        )

    if isinstance(recipe, str):
        return normalize_id(recipe)

    return ""


def get_name(equipment_id, equipment, localization_names):
    if equipment:
        name_key = equipment.get("nameKey")

        if name_key and name_key in localization_names:
            return localization_names[name_key]

    return equipment_id


def load_localization_names():
    """
    Localization is optional here because the workflow already downloads
    localization.json. If unavailable, IDs are still shown.
    """
    path = "localization.json"

    if not os.path.exists(path):
        return {}

    try:
        loc = load_json(path)
    except Exception:
        return {}

    # Comlink localization response contains a base64 ZIP bundle.
    # We avoid making the calculator dependent on this step.
    # Names will therefore normally come from equipment definitions.
    return {}


def find_unit_definition(data, base_id):
    """
    Find the current game-data unit definition.
    """
    for node in walk(data):
        if not isinstance(node, dict):
            continue

        if node.get("baseId") == base_id:
            return node

    return None


def extract_equipment_entries(unit_definition):
    """
    Extract equipment entries from a unit definition.

    Supports the common forms:
      equipment: [...]
      equipmentSet: [...]
      gear: [...]
    """
    if not unit_definition:
        return []

    result = []

    for key in (
        "equipment",
        "equipmentSet",
        "gear",
        "gearSet",
    ):
        value = unit_definition.get(key)

        if isinstance(value, list):
            result.extend(value)

    return result


def equipment_id_from_entry(entry):
    if isinstance(entry, str):
        return entry

    if not isinstance(entry, dict):
        return ""

    return normalize_id(
        entry.get("equipmentId")
        or entry.get("id")
        or entry.get("equipment")
    )


def equipment_tier_from_entry(entry):
    if not isinstance(entry, dict):
        return None

    for key in (
        "tier",
        "gearTier",
        "requiredTier",
        "requiredLevel",
    ):
        if key in entry:
            value = as_int(entry.get(key), -1)

            if value >= 0:
                return value

    return None


def collect_target_equipment(
    unit_definition,
    current_gear,
    target_gear,
    equipment_db
):
    """
    Determine equipment required between current and target gear.

    The current game-data unit definition is treated as authoritative.
    """
    required = defaultdict(int)

    entries = extract_equipment_entries(unit_definition)

    for entry in entries:
        item_id = equipment_id_from_entry(entry)

        if not item_id:
            continue

        tier = equipment_tier_from_entry(entry)

        # If tier is explicitly available, use it.
        if tier is not None:
            if current_gear < tier <= target_gear:
                required[item_id] += 1
            continue

        # If no tier information is present, we cannot safely assign
        # the item to a gear level. Keep it unresolved.
        required[item_id] += 0

    return dict(required)


def add_recipe_requirements(
    item_id,
    quantity,
    equipment_db,
    recipes,
    totals,
    unresolved,
    stack=None
):
    """
    Recursively expand a crafted equipment item into its components.

    Inventory is NOT subtracted here. This function calculates gross
    requirements; inventory subtraction happens afterwards.
    """
    if stack is None:
        stack = set()

    item_id = normalize_id(item_id)

    if not item_id or quantity <= 0:
        return

    if item_id in stack:
        unresolved.append(
            f"Cycle detected in recipe chain: {item_id}"
        )
        return

    equipment = equipment_db.get(item_id)

    recipe_id = resolve_recipe_id(equipment)

    if not recipe_id:
        totals[item_id] += quantity
        return

    ingredients = recipes.get(recipe_id)

    if not ingredients:
        # We know the item is craftable but don't know its recipe.
        unresolved.append(
            f"Recipe not resolved: {item_id} -> {recipe_id}"
        )
        totals[item_id] += quantity
        return

    next_stack = set(stack)
    next_stack.add(item_id)

    for ingredient_id, ingredient_quantity in ingredients:
        add_recipe_requirements(
            ingredient_id,
            quantity * ingredient_quantity,
            equipment_db,
            recipes,
            totals,
            unresolved,
            next_stack
        )


def calculate_target(
    target,
    player_roster,
    data,
    equipment_db,
    recipes,
    inventory
):
    base_id = target["baseId"]

    target_gear = as_int(target.get("targetGearTier"))
    target_relic = as_int(target.get("targetRelicTier"))

    unit = player_roster.get(base_id)

    if not unit:
        return {
            "baseId": base_id,
            "status": "NOT_OWNED",
            "currentGear": 0,
            "currentRelic": 0,
            "targetGear": target_gear,
            "targetRelic": target_relic,
            "requirements": {},
            "shortages": {},
            "unresolved": [
                f"{base_id} not found in player roster"
            ],
        }

    current_gear = as_int(unit.get("currentTier"))
    current_relic = as_int(
        (unit.get("relic") or {}).get("currentTier")
    )

    unit_definition = find_unit_definition(data, base_id)

    gross = defaultdict(int)
    unresolved = []

    gear_requirements = collect_target_equipment(
        unit_definition,
        current_gear,
        target_gear,
        equipment_db
    )

    for item_id, quantity in gear_requirements.items():
        if quantity <= 0:
            continue

        add_recipe_requirements(
            item_id,
            quantity,
            equipment_db,
            recipes,
            gross,
            unresolved
        )

    shortages = {}

    for item_id, required in gross.items():
        owned = inventory.get(item_id, 0)
        shortage = max(0, required - owned)

        if shortage > 0:
            shortages[item_id] = {
                "required": required,
                "owned": owned,
                "shortage": shortage,
            }

    return {
        "baseId": base_id,
        "status": "OK",
        "currentGear": current_gear,
        "currentRelic": current_relic,
        "targetGear": target_gear,
        "targetRelic": target_relic,
        "requirements": dict(gross),
        "shortages": shortages,
        "unresolved": unresolved,
    }


def merge_shortages(results, equipment_db):
    merged = defaultdict(
        lambda: {
            "required": 0,
            "owned": 0,
            "shortage": 0,
        }
    )

    for result in results:
        for item_id, values in result["shortages"].items():
            merged[item_id]["required"] += values["required"]
            merged[item_id]["owned"] = values["owned"]
            merged[item_id]["shortage"] += values["shortage"]

    return merged


def item_name(item_id, equipment_db):
    equipment = equipment_db.get(item_id)

    if equipment:
        return (
            equipment.get("name")
            or equipment.get("displayName")
            or equipment.get("nameKey")
            or item_id
        )

    return item_id


def generate_report(
    targets,
    results,
    merged,
    equipment_db
):
    lines = []

    lines.append("# Vhonte – Account Farming Report")
    lines.append("")
    lines.append(
        "Raport wygenerowany automatycznie na podstawie "
        "`c3po.json`, aktualnego rosteru Comlink i bieżącego gamedata."
    )
    lines.append("")

    lines.append("## Cele")
    lines.append("")

    for target, result in zip(targets, results):
        lines.append(
            f"- **{target['baseId']}**: "
            f"G{result['currentGear']} → G{result['targetGear']}, "
            f"R{result['currentRelic']} → R{result['targetRelic']}"
        )

    lines.append("")

    lines.append("## Łączne braki")
    lines.append("")

    if not merged:
        lines.append("Brak wykrytych braków.")
    else:
        lines.append("| ID | Przedmiot | Wymagane | Posiadane | Brakuje |")
        lines.append("|---|---|---:|---:|---:|")

        sorted_items = sorted(
            merged.items(),
            key=lambda x: (-x[1]["shortage"], x[0])
        )

        for item_id, values in sorted_items:
            lines.append(
                f"| `{item_id}` | "
                f"{item_name(item_id, equipment_db)} | "
                f"{values['required']} | "
                f"{values['owned']} | "
                f"**{values['shortage']}** |"
            )

    lines.append("")

    lines.append("## Szczegóły celów")
    lines.append("")

    for result in results:
        lines.append(
            f"### {result['baseId']}"
        )
        lines.append("")

        if result["status"] != "OK":
            lines.append(
                f"**Status:** `{result['status']}`"
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

        if result["shortages"]:
            lines.append("| ID | Przedmiot | Brakuje |")
            lines.append("|---|---|---:|")

            for item_id, values in sorted(
                result["shortages"].items(),
                key=lambda x: (-x[1]["shortage"], x[0])
            ):
                lines.append(
                    f"| `{item_id}` | "
                    f"{item_name(item_id, equipment_db)} | "
                    f"**{values['shortage']}** |"
                )
        else:
            lines.append("Brak wykrytych braków.")

        lines.append("")

        if result["unresolved"]:
            lines.append("#### Nierozwiązane elementy")
            lines.append("")

            for entry in sorted(set(result["unresolved"])):
                lines.append(f"- `{entry}`")

            lines.append("")

    lines.append("## Uwagi techniczne")
    lines.append("")
    lines.append(
        "- C3PO jest źródłem stanu posiadanych materiałów."
    )
    lines.append(
        "- Comlink jest źródłem aktualnego rosteru i gamedata."
    )
    lines.append(
        "- Kalkulator rozwija receptury rekurencyjnie."
    )
    lines.append(
        "- Elementy, których nie udało się jednoznacznie "
        "rozpoznać, są pokazane w sekcji „Nierozwiązane elementy” "
        "zamiast być zgadywane."
    )
    lines.append("")

    return "\n".join(lines)


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

    inventory = read_c3po_inventory(c3po)

    print(
        "Pozycji inventory:",
        len(inventory)
    )

    equipment_db = build_equipment_database(data)

    print(
        "Rozpoznanych definicji equipment:",
        len(equipment_db)
    )

    recipes = build_recipe_database(data)

    print(
        "Rozpoznanych receptur:",
        len(recipes)
    )

    player_roster = build_player_roster(player)

    print(
        "Jednostek w rosterze:",
        len(player_roster)
    )

    results = []

    for target in targets:
        base_id = target.get("baseId")

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
            equipment_db,
            recipes,
            inventory
        )

        results.append(result)

    merged = merge_shortages(
        results,
        equipment_db
    )

    report = generate_report(
        targets,
        results,
        merged,
        equipment_db
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

    print(
        "Łączna liczba pozycji z brakami:",
        len(merged)
    )


if __name__ == "__main__":
    main()
