import json
import os
from collections import defaultdict


DATA_FILE = "data.json"
PLAYER_FILE = "swgoh_972824625.json"
C3PO_FILE = "c3po.json"
LOCALIZATION_FILE = "localization.json"
TARGETS_FILE = "targets.json"
REPORT_FILE = "account_farming_report.md"


IGNORE_GEAR_IDS = {"9999"}

RELIC_RECIPE_IDS = [
    f"relic_promotion_recipe_{i:02d}"
    for i in range(1, 11)
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f, strict=False)


def as_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def get_localized_names(localization):
    """
    Builds a localization dictionary from the localization bundle when
    possible. The calculator does not depend on localization being complete.
    """
    names = {}

    if not isinstance(localization, dict):
        return names

    bundle = localization.get("localizationBundle")
    if not bundle:
        return names

    try:
        import base64
        import io
        import zipfile

        raw = base64.b64decode(bundle)
        z = zipfile.ZipFile(io.BytesIO(raw))

        filename = "Loc_ENG_US.txt"
        if filename not in z.namelist():
            candidates = [
                x for x in z.namelist()
                if x.lower().endswith(".txt")
            ]
            if not candidates:
                return names
            filename = candidates[0]

        text = z.read(filename).decode("utf-8", "replace")

        for line in text.splitlines():
            if "|" not in line:
                continue

            key, value = line.split("|", 1)
            names[key] = value

    except Exception:
        pass

    return names


def localized_name(item_id, names):
    """
    Try several known localization key patterns.
    """
    if item_id in names:
        return names[item_id]

    candidates = [
        f"EQUIPMENT_{item_id}_NAME",
        f"UNIT_{item_id}_NAME",
        f"{item_id}_NAME",
        item_id,
    ]

    for key in candidates:
        value = names.get(key)
        if value:
            return value

    return item_id


def build_unit_database(data):
    """
    Maps baseId -> unit definition.
    """
    result = {}

    for unit in data.get("units", []):
        base_id = unit.get("baseId")
        if base_id:
            result[base_id] = unit

    return result


def build_equipment_database(data):
    """
    Maps equipment ID -> equipment object.
    """
    equipment = {}

    for item in data.get("equipment", []):
        item_id = item.get("id")
        if item_id:
            equipment[item_id] = item

    return equipment


def build_recipe_database(data):
    """
    IMPORTANT:
    Recipes are mapped by result.id, NOT recipe object's own id.
    """
    recipes = {}

    for recipe in data.get("recipes", []):
        result = recipe.get("result")

        if not isinstance(result, dict):
            continue

        result_id = result.get("id")

        if not result_id:
            continue

        recipes[result_id] = recipe.get("ingredients", [])

    return recipes


def build_relic_recipe_database(data):
    """
    Maps relic_promotion_recipe_01 ... _10 to ingredient lists.
    """
    result = {}

    for recipe in data.get("recipes", []):
        recipe_id = recipe.get("id")

        if recipe_id in RELIC_RECIPE_IDS:
            result[recipe_id] = recipe.get("ingredients", [])

    return result


def get_unit_tier(unit_definition, tier):
    """
    Returns unitTier object for the requested gear tier.
    """
    for unit_tier in unit_definition.get("unitTier", []):
        if as_int(unit_tier.get("tier"), -1) == tier:
            return unit_tier

    return None


def get_equipment_set(unit_definition, tier):
    """
    Returns equipment IDs required at a given gear tier.
    """
    unit_tier = get_unit_tier(unit_definition, tier)

    if not unit_tier:
        return []

    equipment_set = unit_tier.get("equipmentSet", [])

    result = []

    for item in equipment_set:
        if isinstance(item, str):
            item_id = item
        elif isinstance(item, dict):
            item_id = item.get("id")
        else:
            continue

        if not item_id:
            continue

        if item_id in IGNORE_GEAR_IDS:
            continue

        result.append(item_id)

    return result


def get_current_gear(unit):
    """
    Current player gear tier.
    """
    return as_int(
        unit.get("currentTier", unit.get("gearLevel", 0))
    )


def get_current_relic(unit):
    """
    Current relic tier.
    """
    relic = unit.get("relic")

    if not isinstance(relic, dict):
        return 0

    return as_int(
        relic.get("currentTier", relic.get("tier", 0))
    )


def build_player_roster(player):
    """
    Maps baseId -> player's roster unit.

    baseId is obtained from definitionId when possible and falls back
    to the basic-skill-derived base ID used by roster.csv generation.
    """
    roster = {}

    for unit in player.get("rosterUnit", []):
        base_id = None

        definition_id = unit.get("definitionId")

        if definition_id:
            base_id = definition_id.split(":")[0]

        if not base_id:
            for skill in unit.get("skill", []):
                skill_id = skill.get("id", "")

                if skill_id.startswith("basicskill_"):
                    base_id = skill_id.replace("basicskill_", "")
                    break

        if base_id:
            roster[base_id] = unit

    return roster


def read_c3po_inventory(c3po):
    """
    Reads equipment/relic material inventory from C3PO.

    Supports the common C3PO inventory layouts.
    """
    inventory = defaultdict(int)

    inv = c3po.get("inventory", c3po)

    if not isinstance(inv, dict):
        return inventory

    equipment = inv.get("equipment", [])

    if isinstance(equipment, dict):
        for item_id, value in equipment.items():
            if isinstance(value, dict):
                quantity = value.get(
                    "quantity",
                    value.get("count", value.get("amount", 0))
                )
            else:
                quantity = value

            inventory[item_id] += as_int(quantity)

    elif isinstance(equipment, list):
        for item in equipment:
            if not isinstance(item, dict):
                continue

            item_id = (
                item.get("id")
                or item.get("equipmentId")
                or item.get("itemId")
            )

            if not item_id:
                continue

            quantity = (
                item.get("quantity")
                or item.get("count")
                or item.get("amount")
                or 0
            )

            inventory[item_id] += as_int(quantity)

    return inventory


def expand_item(item_id, quantity, recipes, output):
    """
    Recursively expands crafted equipment into terminal materials.

    output receives terminal item quantities.
    """
    if not item_id or quantity <= 0:
        return

    if item_id in IGNORE_GEAR_IDS:
        return

    ingredients = recipes.get(item_id)

    if not ingredients:
        output[item_id] += quantity
        return

    for ingredient in ingredients:
        ingredient_id = ingredient.get("id")

        if not ingredient_id:
            continue

        amount = as_int(
            ingredient.get(
                "minQuantity",
                ingredient.get("quantity", 1)
            ),
            1
        )

        if amount <= 0:
            continue

        # GRIND is already a terminal resource.
        expand_item(
            ingredient_id,
            quantity * amount,
            recipes,
            output
        )


def expand_equipment_requirements(required_equipment, recipes):
    """
    Converts direct equipment requirements into terminal material
    requirements.
    """
    result = defaultdict(int)

    for item_id, quantity in required_equipment.items():
        expand_item(
            item_id,
            quantity,
            recipes,
            result
        )

    return result


def get_gear_requirements(unit_definition, current_gear, target_gear):
    """
    Collects all direct gear pieces required from current+1 through
    target gear tier.
    """
    required = defaultdict(int)

    start = max(current_gear + 1, 1)
    end = min(target_gear, 12)

    for tier in range(start, end + 1):
        for item_id in get_equipment_set(unit_definition, tier):
            required[item_id] += 1

    return required


def get_relic_requirements(current_relic, target_relic, relic_recipes):
    """
    Returns terminal relic-material requirements for current+1 through
    target relic tier.
    """
    result = defaultdict(int)

    start = max(current_relic + 1, 1)
    end = min(target_relic, 10)

    for relic_tier in range(start, end + 1):
        recipe_id = f"relic_promotion_recipe_{relic_tier:02d}"
        ingredients = relic_recipes.get(recipe_id, [])

        for ingredient in ingredients:
            item_id = ingredient.get("id")

            if not item_id:
                continue

            quantity = as_int(
                ingredient.get(
                    "minQuantity",
                    ingredient.get("quantity", 1)
                ),
                1
            )

            result[item_id] += quantity

    return result


def calculate_target(
    base_id,
    target_gear,
    target_relic,
    roster,
    units,
    recipes,
    relic_recipes,
    working_inventory,
    names
):
    """
    Calculates one target while consuming the shared working inventory.
    """
    unit = roster.get(base_id)

    if not unit:
        raise RuntimeError(
            f"Nie znaleziono {base_id} w rosterze."
        )

    unit_definition = units.get(base_id)

    if not unit_definition:
        raise RuntimeError(
            f"Nie znaleziono definicji jednostki {base_id} w data.json."
        )

    current_gear = get_current_gear(unit)
    current_relic = get_current_relic(unit)

    required_direct_gear = get_gear_requirements(
        unit_definition,
        current_gear,
        target_gear
    )

    required_gear = expand_equipment_requirements(
        required_direct_gear,
        recipes
    )

    required_relic = get_relic_requirements(
        current_relic,
        target_relic,
        relic_recipes
    )

    total_required = defaultdict(int)

    for item_id, quantity in required_gear.items():
        total_required[item_id] += quantity

    for item_id, quantity in required_relic.items():
        total_required[item_id] += quantity

    # ------------------------------------------------------------
    # IMPORTANT FIX:
    #
    # Calculate the REAL shortage after subtracting inventory.
    #
    # The previous version reported the full required quantity even
    # when C3PO inventory already contained part of that material.
    # ------------------------------------------------------------

    shortages = {}

    for item_id, required_quantity in total_required.items():
        owned_quantity = working_inventory.get(item_id, 0)

        shortage = max(
            0,
            required_quantity - owned_quantity
        )

        if shortage > 0:
            shortages[item_id] = shortage

        # Consume inventory that is actually available.
        working_inventory[item_id] = max(
            0,
            owned_quantity - required_quantity
        )

    return {
        "base_id": base_id,
        "current_gear": current_gear,
        "target_gear": target_gear,
        "current_relic": current_relic,
        "target_relic": target_relic,
        "required_direct_gear": required_direct_gear,
        "required_gear": required_gear,
        "required_relic": required_relic,
        "total_required": dict(total_required),
        "shortages": shortages,
    }


def format_number(value):
    return f"{value:,}".replace(",", " ")


def generate_report(
    results,
    total_required,
    total_shortages,
    inventory,
    names
):
    lines = []

    lines.append("# Account Farming Report")
    lines.append("")

    for result in results:
        lines.append(
            f"- **{result['base_id']}**: "
            f"G{result['current_gear']} → G{result['target_gear']}, "
            f"R{result['current_relic']} → R{result['target_relic']}"
        )

    lines.append("")
    lines.append("## Łączne braki")
    lines.append("")

    if total_shortages:
        lines.append(
            "| ID | Przedmiot | Wymagane | Posiadane | Brakuje |"
        )
        lines.append(
            "|---|---|---:|---:|---:|"
        )

        # Sort by shortage descending.
        for item_id, shortage in sorted(
            total_shortages.items(),
            key=lambda x: (-x[1], x[0])
        ):
            # Use the actual total requirement calculated from the
            # gear/relic recipes. Do not reconstruct it from shortage.
            owned = inventory.get(item_id, 0)
            required_for_report = total_required.get(item_id, 0)

            name = localized_name(item_id, names)

            lines.append(
                f"| `{item_id}` | {name} | "
                f"{format_number(required_for_report)} | "
                f"{format_number(owned)} | "
                f"**{format_number(shortage)}** |"
            )
    else:
        lines.append("Brak braków.")

    lines.append("")
    lines.append("## Szczegóły")
    lines.append("")

    for result in results:
        lines.append(f"### {result['base_id']}")
        lines.append("")

        lines.append(
            f"Gear: **G{result['current_gear']} → "
            f"G{result['target_gear']}** "
            f"Relic: **R{result['current_relic']} → "
            f"R{result['target_relic']}**"
        )

        lines.append("")
        lines.append("#### Bezpośredni wymagany gear")
        lines.append("")

        for item_id, quantity in sorted(
            result["required_direct_gear"].items()
        ):
            name = localized_name(item_id, names)

            lines.append(
                f"- `{item_id}` × {quantity} — {name}"
            )

        lines.append("")
        lines.append("#### Materiały relic")
        lines.append("")

        for item_id, quantity in result["required_relic"].items():
            name = localized_name(item_id, names)

            lines.append(
                f"- `{item_id}` × {quantity} — {name}"
            )

        lines.append("")
        lines.append("#### Braki")
        lines.append("")

        if result["shortages"]:
            lines.append(
                "| ID | Przedmiot | Brakuje |"
            )
            lines.append(
                "|---|---|---:|"
            )

            for item_id, shortage in sorted(
                result["shortages"].items(),
                key=lambda x: (-x[1], x[0])
            ):
                name = localized_name(item_id, names)

                lines.append(
                    f"| `{item_id}` | {name} | "
                    f"**{format_number(shortage)}** |"
                )
        else:
            lines.append("Brak braków.")

        lines.append("")

    lines.append("## Informacje techniczne")
    lines.append("")
    lines.append("- Inventory pochodzi z `c3po.json`.")
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

    return "\n".join(lines)


def main():
    print("Ładowanie danych...")

    data = load_json(DATA_FILE)
    player = load_json(PLAYER_FILE)
    c3po = load_json(C3PO_FILE)
    localization = load_json(LOCALIZATION_FILE)
    targets = load_json(TARGETS_FILE)

    names = get_localized_names(localization)

    units = build_unit_database(data)
    recipes = build_recipe_database(data)
    relic_recipes = build_relic_recipe_database(data)

    roster = build_player_roster(player)

    inventory = read_c3po_inventory(c3po)

    # Shared inventory for all targets.
    working_inventory = defaultdict(int)

    for item_id, quantity in inventory.items():
        working_inventory[item_id] = quantity

    target_list = targets.get("targets", [])

    results = []
    total_required = defaultdict(int)
    total_shortages = defaultdict(int)

    for target in target_list:
        base_id = target.get("baseId")

        target_gear = as_int(
            target.get("targetGearTier", 0)
        )

        target_relic = as_int(
            target.get("targetRelicTier", 0)
        )

        if not base_id:
            continue

        print(
            f"Liczenie {base_id}: "
            f"G{target_gear}, R{target_relic}"
        )

        result = calculate_target(
            base_id=base_id,
            target_gear=target_gear,
            target_relic=target_relic,
            roster=roster,
            units=units,
            recipes=recipes,
            relic_recipes=relic_recipes,
            working_inventory=working_inventory,
            names=names,
        )

        results.append(result)

        for item_id, quantity in result["total_required"].items():
            total_required[item_id] += quantity

        for item_id, quantity in result["shortages"].items():
            total_shortages[item_id] += quantity

    report = generate_report(
        results=results,
        total_required=total_required,
        total_shortages=total_shortages,
        inventory=inventory,
        names=names,
    )

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(report)

    print("")
    print("Wygenerowano account_farming_report.md")
    print("")
    print("Łączne braki:")

    for item_id, quantity in sorted(
        total_shortages.items(),
        key=lambda x: (-x[1], x[0])
    ):
        print(
            f"  {item_id}: {quantity}"
        )


if __name__ == "__main__":
    main()
