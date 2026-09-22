import csv
import json
from collections import defaultdict


DATA_FILE = "data.json"
ROSTER_FILE = "roster.csv"
C3PO_FILE = "c3po.json"
LOCALIZATION_FILE = "localization.json"
TARGETS_FILE = "targets.json"
REPORT_FILE = "account_farming_report.md"

IGNORE_GEAR_IDS = {"9999"}

RELIC_RECIPE_IDS = [
    f"relic_promotion_recipe_{i:02d}"
    for i in range(1, 11)
]


# ============================================================
# BASIC HELPERS
# ============================================================

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def as_int(value, default=0):
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_id(value):
    if value is None:
        return ""
    return str(value).strip()


# ============================================================
# LOCALIZATION
# ============================================================

def build_localization(localization_data):
    result = {}

    if isinstance(localization_data, dict):
        for key, value in localization_data.items():
            if isinstance(value, str):
                result[str(key)] = value

    return result


def localize(localization, key):
    if not key:
        return ""

    key = str(key)

    if key in localization:
        return localization[key]

    return key


# ============================================================
# UNIT DATABASE
# ============================================================

def build_unit_database(data):
    units = {}

    raw_units = data.get("units", [])

    if isinstance(raw_units, dict):
        raw_units = list(raw_units.values())

    for unit in raw_units:
        if not isinstance(unit, dict):
            continue

        base_id = (
            unit.get("baseId")
            or unit.get("baseID")
            or unit.get("id")
        )

        if not base_id:
            continue

        units[base_id] = unit

    return units


# ============================================================
# RECIPE DATABASE
# ============================================================

def build_recipe_database(data):
    recipes = {}

    raw_recipes = (
        data.get("recipes")
        or data.get("recipe")
        or []
    )

    if isinstance(raw_recipes, dict):
        raw_recipes = list(raw_recipes.values())

    for recipe in raw_recipes:
        if not isinstance(recipe, dict):
            continue

        recipe_id = (
            recipe.get("id")
            or recipe.get("recipeId")
            or recipe.get("recipe_id")
        )

        if recipe_id:
            recipes[recipe_id] = recipe

    return recipes


def build_relic_recipe_database(data):
    recipes = {}

    raw_recipes = data.get("recipes", [])

    if isinstance(raw_recipes, dict):
        raw_recipes = list(raw_recipes.values())

    for recipe in raw_recipes:
        if not isinstance(recipe, dict):
            continue

        recipe_id = str(
            recipe.get("id")
            or recipe.get("recipeId")
            or ""
        )

        if recipe_id.startswith("relic_promotion_recipe_"):
            recipes[recipe_id] = recipe

    return recipes


# ============================================================
# ROSTER CSV
# ============================================================

def build_roster_from_csv(path):
    roster = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            base_id = normalize_id(row.get("baseId"))

            if not base_id:
                base_id = normalize_id(row.get("definitionId"))

                if ":" in base_id:
                    base_id = base_id.split(":", 1)[0]

            if not base_id:
                continue

            gear_tier = as_int(
                row.get("gearTier"),
                as_int(row.get("gear"), 0)
            )

            relic_tier = as_int(
                row.get("relicTier"),
                as_int(row.get("relic"), 0)
            )

            rarity = as_int(
                row.get("rarity"),
                as_int(row.get("stars"), 0)
            )

            level = as_int(row.get("level"), 0)

            roster[base_id] = {
                "baseId": base_id,
                "definitionId": row.get("definitionId", ""),
                "currentTier": gear_tier,
                "gearTier": gear_tier,
                "relic": {
                    "currentTier": relic_tier
                },
                "relicTier": relic_tier,
                "currentRarity": rarity,
                "currentLevel": level,
                "name": row.get("name", base_id),
            }

    return roster


# ============================================================
# CURRENT GEAR / RELIC
# ============================================================

def get_current_gear(unit):
    if not unit:
        return 0

    for key in (
        "currentTier",
        "gearTier",
        "tier",
    ):
        if key in unit:
            return as_int(unit.get(key), 0)

    return 0


def get_current_relic(unit):
    if not unit:
        return 0

    relic = unit.get("relic")

    if isinstance(relic, dict):
        for key in (
            "currentTier",
            "tier",
            "relicTier",
        ):
            if key in relic:
                return as_int(relic.get(key), 0)

    for key in (
        "relicTier",
        "currentRelicTier",
    ):
        if key in unit:
            return as_int(unit.get(key), 0)

    return 0


# ============================================================
# C3PO INVENTORY
# ============================================================

def read_c3po_inventory(c3po_data):
    """
    Reads both:
      inventory.equipment
      inventory.material

    C3PO may represent these collections either as lists
    or dictionaries, depending on the export/version.
    """

    inventory = defaultdict(int)

    raw_inventory = c3po_data.get("inventory", {})

    if not isinstance(raw_inventory, dict):
        return inventory

    # --------------------------------------------------------
    # EQUIPMENT
    # --------------------------------------------------------

    equipment = raw_inventory.get("equipment", [])

    if isinstance(equipment, dict):
        for item_id, item_data in equipment.items():

            if isinstance(item_data, dict):
                quantity = (
                    item_data.get("quantity")
                    or item_data.get("amount")
                    or item_data.get("count")
                    or 0
                )
            else:
                quantity = item_data

            inventory[normalize_id(item_id)] += as_int(quantity)

    elif isinstance(equipment, list):
        for item in equipment:
            if not isinstance(item, dict):
                continue

            item_id = (
                item.get("id")
                or item.get("equipmentId")
                or item.get("itemId")
            )

            quantity = (
                item.get("quantity")
                or item.get("amount")
                or item.get("count")
                or 0
            )

            if item_id:
                inventory[normalize_id(item_id)] += as_int(quantity)

    # --------------------------------------------------------
    # MATERIAL
    # --------------------------------------------------------

    materials = raw_inventory.get("material", [])

    if isinstance(materials, dict):
        for item_id, item_data in materials.items():

            if isinstance(item_data, dict):
                quantity = (
                    item_data.get("quantity")
                    or item_data.get("amount")
                    or item_data.get("count")
                    or 0
                )
            else:
                quantity = item_data

            inventory[normalize_id(item_id)] += as_int(quantity)

    elif isinstance(materials, list):
        for item in materials:
            if not isinstance(item, dict):
                continue

            item_id = (
                item.get("id")
                or item.get("materialId")
                or item.get("itemId")
            )

            quantity = (
                item.get("quantity")
                or item.get("amount")
                or item.get("count")
                or 0
            )

            if item_id:
                inventory[normalize_id(item_id)] += as_int(quantity)

    return inventory


# ============================================================
# RECIPE PARSING
# ============================================================

def extract_recipe_components(recipe):
    """
    Attempts to extract recipe ingredients from several common
    SWGOH data structures.
    """

    if not isinstance(recipe, dict):
        return []

    possible_keys = (
        "ingredients",
        "components",
        "recipeIngredients",
        "items",
        "requirements",
    )

    raw = None

    for key in possible_keys:
        if key in recipe:
            raw = recipe[key]
            break

    if raw is None:
        return []

    if isinstance(raw, dict):
        raw = list(raw.values())

    if not isinstance(raw, list):
        return []

    result = []

    for component in raw:
        if not isinstance(component, dict):
            continue

        item_id = (
            component.get("id")
            or component.get("itemId")
            or component.get("equipmentId")
            or component.get("materialId")
            or component.get("resourceId")
        )

        quantity = (
            component.get("quantity")
            or component.get("amount")
            or component.get("count")
            or component.get("requiredQuantity")
            or 0
        )

        if item_id:
            result.append(
                (
                    normalize_id(item_id),
                    as_int(quantity)
                )
            )

    return result


# ============================================================
# RECURSIVE RESOURCE CONSUMPTION
# ============================================================

def expand_item(
    item_id,
    quantity,
    recipes,
    inventory,
    shortages,
    stack=None,
):
    """
    Consume an item from inventory.

    If insufficient inventory exists, recursively expand the missing
    amount through its recipe.

    This is the key part that prevents double-counting resources
    already owned by the player.
    """

    item_id = normalize_id(item_id)
    quantity = as_int(quantity)

    if quantity <= 0:
        return

    if stack is None:
        stack = set()

    # Prevent circular recipes.
    if item_id in stack:
        shortages[item_id] += quantity
        return

    owned = inventory.get(item_id, 0)

    if owned >= quantity:
        inventory[item_id] -= quantity
        return

    if owned > 0:
        quantity -= owned
        inventory[item_id] = 0

    recipe = recipes.get(item_id)

    if not recipe:
        shortages[item_id] += quantity
        return

    components = extract_recipe_components(recipe)

    if not components:
        shortages[item_id] += quantity
        return

    stack.add(item_id)

    for component_id, component_quantity in components:
        required = component_quantity * quantity

        expand_item(
            component_id,
            required,
            recipes,
            inventory,
            shortages,
            stack,
        )

    stack.remove(item_id)


def consume_or_expand(
    item_id,
    quantity,
    recipes,
    inventory,
    shortages,
):
    expand_item(
        item_id,
        quantity,
        recipes,
        inventory,
        shortages,
    )


# ============================================================
# GEAR REQUIREMENTS
# ============================================================

def get_gear_requirements(unit, target_gear_tier, data):
    """
    Returns direct gear item requirements needed to move a unit
    from its current gear tier to target tier.

    Handles several common SWGOH data layouts.
    """

    current_tier = get_current_gear(unit)

    if current_tier >= target_gear_tier:
        return []

    gear_data = data.get("gear", {})

    if not gear_data:
        return []

    requirements = []

    # --------------------------------------------------------
    # Locate character's gear progression
    # --------------------------------------------------------

    progression = None

    if isinstance(gear_data, dict):

        base_id = unit.get("baseId")

        if base_id in gear_data:
            progression = gear_data[base_id]

        elif unit.get("definitionId") in gear_data:
            progression = gear_data[unit.get("definitionId")]

    elif isinstance(gear_data, list):

        base_id = unit.get("baseId")

        for entry in gear_data:
            if not isinstance(entry, dict):
                continue

            entry_base = (
                entry.get("baseId")
                or entry.get("unitBaseId")
                or entry.get("characterId")
            )

            if entry_base == base_id:
                progression = entry
                break

    if progression is None:
        return []

    # --------------------------------------------------------
    # Progression as dict
    # --------------------------------------------------------

    if isinstance(progression, dict):

        for tier in range(current_tier + 1, target_gear_tier + 1):

            tier_data = (
                progression.get(str(tier))
                or progression.get(tier)
                or progression.get(f"G{tier}")
            )

            if tier_data is None:
                continue

            if isinstance(tier_data, dict):
                components = extract_recipe_components(tier_data)

                for item_id, quantity in components:
                    requirements.append((item_id, quantity))

            elif isinstance(tier_data, list):

                for item in tier_data:
                    if not isinstance(item, dict):
                        continue

                    item_id = (
                        item.get("id")
                        or item.get("itemId")
                        or item.get("equipmentId")
                    )

                    quantity = (
                        item.get("quantity")
                        or item.get("amount")
                        or item.get("count")
                        or 0
                    )

                    if item_id:
                        requirements.append(
                            (
                                normalize_id(item_id),
                                as_int(quantity),
                            )
                        )

    # --------------------------------------------------------
    # Progression as list
    # --------------------------------------------------------

    elif isinstance(progression, list):

        for tier_data in progression:

            if not isinstance(tier_data, dict):
                continue

            tier = as_int(
                tier_data.get("tier")
                or tier_data.get("gearTier")
                or tier_data.get("level"),
                0,
            )

            if tier <= current_tier or tier > target_gear_tier:
                continue

            components = extract_recipe_components(tier_data)

            for item_id, quantity in components:
                requirements.append((item_id, quantity))

    return requirements


# ============================================================
# RELIC REQUIREMENTS
# ============================================================

def get_relic_requirements(
    current_relic,
    target_relic,
    relic_recipes,
):
    requirements = []

    if current_relic >= target_relic:
        return requirements

    for relic_tier in range(
        current_relic + 1,
        target_relic + 1
    ):

        if relic_tier <= 0:
            continue

        recipe_id = (
            f"relic_promotion_recipe_{relic_tier:02d}"
        )

        recipe = relic_recipes.get(recipe_id)

        if not recipe:
            continue

        components = extract_recipe_components(recipe)

        for item_id, quantity in components:
            requirements.append(
                (
                    item_id,
                    quantity,
                )
            )

    return requirements


# ============================================================
# TARGET CALCULATION
# ============================================================

def calculate_target(
    target,
    roster,
    units,
    data,
    recipes,
    relic_recipes,
    inventory,
):
    base_id = normalize_id(
        target.get("baseId")
    )

    if not base_id:
        return {
            "baseId": "",
            "name": "UNKNOWN",
            "error": "Target has no baseId",
            "gear": [],
            "relic": [],
            "shortages": {},
        }

    roster_unit = roster.get(base_id)

    if roster_unit is None:
        return {
            "baseId": base_id,
            "name": base_id,
            "error": "Character not found in roster.csv",
            "gear": [],
            "relic": [],
            "shortages": {},
        }

    unit_definition = units.get(base_id, {})

    name = (
        roster_unit.get("name")
        or unit_definition.get("name")
        or base_id
    )

    current_gear = get_current_gear(roster_unit)
    current_relic = get_current_relic(roster_unit)

    target_gear = as_int(
        target.get("targetGearTier"),
        current_gear,
    )

    target_relic = as_int(
        target.get("targetRelicTier"),
        current_relic,
    )

    shortages = defaultdict(int)

    gear_requirements = get_gear_requirements(
        roster_unit,
        target_gear,
        data,
    )

    for item_id, quantity in gear_requirements:
        consume_or_expand(
            item_id,
            quantity,
            recipes,
            inventory,
            shortages,
        )

    relic_requirements = get_relic_requirements(
        current_relic,
        target_relic,
        relic_recipes,
    )

    for item_id, quantity in relic_requirements:
        consume_or_expand(
            item_id,
            quantity,
            recipes,
            inventory,
            shortages,
        )

    return {
        "baseId": base_id,
        "name": name,
        "currentGear": current_gear,
        "targetGear": target_gear,
        "currentRelic": current_relic,
        "targetRelic": target_relic,
        "gear": gear_requirements,
        "relic": relic_requirements,
        "shortages": dict(shortages),
    }


# ============================================================
# REPORT
# ============================================================

def generate_report(
    results,
    localization,
    output_path,
):
    lines = []

    lines.append("# Account Farming Report")
    lines.append("")
    lines.append(
        "Automatycznie wygenerowany raport brakujących "
        "materiałów dla aktualnej kolejki farmienia."
    )
    lines.append("")

    total_shortages = defaultdict(int)

    for result in results:

        name = result.get("name", result.get("baseId"))

        lines.append(
            f"## {name}"
        )
        lines.append("")

        if result.get("error"):
            lines.append(
                f"**Błąd:** {result['error']}"
            )
            lines.append("")
            continue

        lines.append(
            f"- **Gear:** "
            f"G{result['currentGear']} → "
            f"G{result['targetGear']}"
        )

        lines.append(
            f"- **Relic:** "
            f"R{result['currentRelic']} → "
            f"R{result['targetRelic']}"
        )

        lines.append("")

        shortages = result.get("shortages", {})

        if not shortages:
            lines.append(
                "**Brak brakujących materiałów.**"
            )
            lines.append("")
            continue

        lines.append("### Braki")
        lines.append("")

        for item_id, quantity in sorted(
            shortages.items(),
            key=lambda x: (
                localize(localization, x[0]).lower(),
                x[0],
            ),
        ):
            total_shortages[item_id] += quantity

            display_name = localize(
                localization,
                item_id,
            )

            lines.append(
                f"- **{display_name}** "
                f"`{item_id}` × **{quantity}**"
            )

        lines.append("")

    lines.append("## Łączne braki")
    lines.append("")

    if not total_shortages:
        lines.append(
            "**Brak brakujących materiałów.**"
        )
    else:
        for item_id, quantity in sorted(
            total_shortages.items(),
            key=lambda x: (
                localize(localization, x[0]).lower(),
                x[0],
            ),
        ):
            display_name = localize(
                localization,
                item_id,
            )

            lines.append(
                f"- **{display_name}** "
                f"`{item_id}` × **{quantity}**"
            )

    lines.append("")

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:
        f.write("\n".join(lines))


# ============================================================
# MAIN
# ============================================================

def main():

    print("Loading data...")

    data = load_json(DATA_FILE)
    c3po_data = load_json(C3PO_FILE)
    localization_data = load_json(LOCALIZATION_FILE)
    targets_data = load_json(TARGETS_FILE)

    print("Building databases...")

    units = build_unit_database(data)
    recipes = build_recipe_database(data)
    relic_recipes = build_relic_recipe_database(data)

    localization = build_localization(
        localization_data
    )

    print("Loading roster.csv...")

    roster = build_roster_from_csv(
        ROSTER_FILE
    )

    print(
        f"Roster entries: {len(roster)}"
    )

    print("Loading C3PO inventory...")

    original_inventory = read_c3po_inventory(
        c3po_data
    )

    print(
        f"Inventory items: "
        f"{len(original_inventory)}"
    )

    working_inventory = defaultdict(
        int,
        original_inventory,
    )

    targets = targets_data.get(
        "targets",
        [],
    )

    results = []

    for target in targets:

        base_id = target.get(
            "baseId",
            "UNKNOWN",
        )

        print(
            f"Calculating: {base_id}"
        )

        result = calculate_target(
            target=target,
            roster=roster,
            units=units,
            data=data,
            recipes=recipes,
            relic_recipes=relic_recipes,
            inventory=working_inventory,
        )

        results.append(result)

    generate_report(
        results=results,
        localization=localization,
        output_path=REPORT_FILE,
    )

    print("")
    print(
        f"Report written to {REPORT_FILE}"
    )


if __name__ == "__main__":
    main()
