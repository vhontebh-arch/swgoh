import json
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
        return json.load(f)


def as_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def extract_localization_entries(localization_data):
    if isinstance(localization_data, dict):
        if "data" in localization_data:
            return extract_localization_entries(localization_data["data"])

        if "entries" in localization_data:
            return extract_localization_entries(localization_data["entries"])

        return localization_data

    if isinstance(localization_data, list):
        result = {}

        for entry in localization_data:
            if not isinstance(entry, dict):
                continue

            key = (
                entry.get("key")
                or entry.get("id")
                or entry.get("baseId")
                or entry.get("name")
            )

            value = (
                entry.get("value")
                or entry.get("text")
                or entry.get("localized")
                or entry.get("name")
            )

            if key and value:
                result[str(key)] = str(value)

        return result

    return {}


def localized_name(item_id, localization):
    if item_id in localization:
        return localization[item_id]

    return item_id


def build_unit_database(data):
    units = {}

    source = data.get("units", data.get("characters", []))

    if isinstance(source, dict):
        iterable = source.values()
    else:
        iterable = source

    for unit in iterable:
        if not isinstance(unit, dict):
            continue

        base_id = unit.get("baseId") or unit.get("id")

        if base_id:
            units[base_id] = unit

    return units


def build_recipe_database(data):
    recipes = {}

    source = data.get("recipes", [])

    if isinstance(source, dict):
        iterable = source.values()
    else:
        iterable = source

    for recipe in iterable:
        if not isinstance(recipe, dict):
            continue

        result = recipe.get("result")

        if not isinstance(result, dict):
            continue

        result_id = result.get("id")

        if not result_id:
            continue

        ingredients = recipe.get("ingredients", [])

        if not isinstance(ingredients, list):
            ingredients = []

        recipes[result_id] = ingredients

    return recipes


def build_relic_recipe_database(data):
    recipes = {}

    source = data.get("recipes", [])

    if isinstance(source, dict):
        iterable = source.values()
    else:
        iterable = source

    for recipe in iterable:
        if not isinstance(recipe, dict):
            continue

        recipe_id = recipe.get("id")

        if recipe_id not in RELIC_RECIPE_IDS:
            continue

        ingredients = recipe.get("ingredients", [])

        if not isinstance(ingredients, list):
            ingredients = []

        recipes[recipe_id] = ingredients

    return recipes


def get_unit_tier(unit):
    return as_int(
        unit.get("currentTier")
        or unit.get("tier")
        or unit.get("gearTier")
        or unit.get("level"),
        0
    )


def get_equipment_set(unit):
    equipment = unit.get("equipment", [])

    if not isinstance(equipment, list):
        return set()

    result = set()

    for item in equipment:
        if isinstance(item, dict):
            item_id = item.get("equipmentId") or item.get("id")
        else:
            item_id = item

        if item_id:
            result.add(item_id)

    return result


def get_current_gear(unit):
    """
    Returns the character's current gear tier.

    SWGOH data normally uses currentTier / tier / gearTier.
    """
    for key in ("currentTier", "tier", "gearTier"):
        if key in unit:
            return as_int(unit[key], 0)

    return 0


def get_current_relic(unit):
    """
    Returns the current relic level.

    Supports the common SWGOH formats:
      relic.currentTier
      relic.tier
      relicTier
    """
    relic = unit.get("relic")

    if isinstance(relic, dict):
        for key in ("currentTier", "tier", "relicTier"):
            if key in relic:
                return as_int(relic[key], 0)

    for key in ("relicTier", "currentRelicTier"):
        if key in unit:
            return as_int(unit[key], 0)

    return 0


def build_player_roster(player_data, units):
    roster = {}

    source = player_data.get("roster", player_data.get("characters", []))

    if isinstance(source, dict):
        iterable = source.values()
    else:
        iterable = source

    for entry in iterable:
        if not isinstance(entry, dict):
            continue

        base_id = entry.get("baseId") or entry.get("id")

        if not base_id:
            continue

        roster[base_id] = entry

    return roster


def read_c3po_inventory(c3po_data):
    """
    Reads inventory from c3po.json.

    Supported forms include:
      inventory.equipment = [{id, quantity}, ...]
      inventory.equipment = {id: quantity, ...}

    Also supports the inventory itself being represented as a dict.
    """
    inventory = defaultdict(int)

    if not isinstance(c3po_data, dict):
        return inventory

    source = c3po_data.get("inventory", c3po_data)

    if not isinstance(source, dict):
        return inventory

    equipment = source.get("equipment", source.get("items", {}))

    if isinstance(equipment, dict):
        for item_id, quantity in equipment.items():
            inventory[str(item_id)] += as_int(quantity, 0)

    elif isinstance(equipment, list):
        for item in equipment:
            if not isinstance(item, dict):
                continue

            item_id = (
                item.get("id")
                or item.get("equipmentId")
                or item.get("baseId")
            )

            if not item_id:
                continue

            quantity = (
                item.get("quantity")
                if "quantity" in item
                else item.get("amount", 0)
            )

            inventory[str(item_id)] += as_int(quantity, 0)

    return inventory


def expand_item(item_id, quantity, recipes, result=None, path=None):
    """
    Theoretical recipe expansion.

    This function does NOT consume inventory.
    It is kept for diagnostics / compatibility.

    Inventory-aware calculation is performed by consume_or_expand().
    """
    if result is None:
        result = defaultdict(int)

    if path is None:
        path = set()

    if not item_id or quantity <= 0:
        return result

    if item_id in IGNORE_GEAR_IDS:
        return result

    if item_id in path:
        result[item_id] += quantity
        return result

    ingredients = recipes.get(item_id)

    if not ingredients:
        result[item_id] += quantity
        return result

    new_path = set(path)
    new_path.add(item_id)

    for ingredient in ingredients:
        if not isinstance(ingredient, dict):
            continue

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

        expand_item(
            ingredient_id,
            quantity * amount,
            recipes,
            result,
            new_path
        )

    return result


def consume_or_expand(
    item_id,
    quantity,
    recipes,
    working_inventory,
    shortages,
    path=None
):
    """
    Correct inventory-aware resource calculation.

    Order of operations:

    1. Look for the exact required item in inventory.
    2. Consume as much as possible.
    3. Only the remaining amount is crafted.
    4. For every crafting ingredient, repeat the same process.
    5. Only items with no recipe and no inventory become real shortages.

    This is the key fix compared with the old calculator.
    """
    if not item_id or quantity <= 0:
        return

    if item_id in IGNORE_GEAR_IDS:
        return

    if path is None:
        path = set()

    # Prevent infinite recipe loops.
    if item_id in path:
        shortages[item_id] += quantity
        return

    owned = working_inventory.get(item_id, 0)

    used = min(quantity, owned)

    if used > 0:
        working_inventory[item_id] -= used

    remaining = quantity - used

    if remaining <= 0:
        return

    ingredients = recipes.get(item_id)

    # No recipe = terminal material / finished item.
    if not ingredients:
        shortages[item_id] += remaining
        return

    new_path = set(path)
    new_path.add(item_id)

    for ingredient in ingredients:
        if not isinstance(ingredient, dict):
            continue

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

        consume_or_expand(
            ingredient_id,
            remaining * amount,
            recipes,
            working_inventory,
            shortages,
            new_path
        )


def expand_equipment_requirements(
    required_gear,
    recipes
):
    """
    Returns theoretical terminal requirements without inventory.

    Kept separately from the real shortage calculation.
    """
    result = defaultdict(int)

    for item_id, quantity in required_gear.items():
        expand_item(
            item_id,
            quantity,
            recipes,
            result
        )

    return result


def get_gear_requirements(
    unit,
    target_gear_tier,
    data
):
    """
    Returns direct gear pieces required to move from the current
    gear tier to target_gear_tier.

    Gear is taken from the game's gear requirement definitions.
    """
    result = defaultdict(int)

    current_gear = get_current_gear(unit)

    if current_gear >= target_gear_tier:
        return result

    source = data.get("gear", [])

    if isinstance(source, dict):
        gear_data = source
    else:
        gear_data = {}

        for entry in source:
            if not isinstance(entry, dict):
                continue

            gear_id = (
                entry.get("id")
                or entry.get("tier")
                or entry.get("gearTier")
            )

            if gear_id:
                gear_data[str(gear_id)] = entry

    for tier in range(current_gear + 1, min(target_gear_tier, 12) + 1):
        candidates = [
            f"gear_{tier}",
            f"GEAR{tier}",
            str(tier)
        ]

        tier_data = None

        for candidate in candidates:
            if candidate in gear_data:
                tier_data = gear_data[candidate]
                break

        if tier_data is None:
            continue

        if isinstance(tier_data, dict):
            equipment = (
                tier_data.get("equipment")
                or tier_data.get("requirements")
                or tier_data.get("gear")
                or []
            )
        else:
            equipment = tier_data

        if not isinstance(equipment, list):
            continue

        for item in equipment:
            if not isinstance(item, dict):
                continue

            item_id = (
                item.get("id")
                or item.get("equipmentId")
            )

            if not item_id:
                continue

            quantity = as_int(
                item.get(
                    "quantity",
                    item.get("minQuantity", 1)
                ),
                1
            )

            result[item_id] += quantity

    return result


def get_relic_requirements(
    current_relic,
    target_relic,
    relic_recipes
):
    """
    Returns relic recipe ingredients required for each relic level
    between current_relic + 1 and target_relic.
    """
    result = defaultdict(int)

    if current_relic >= target_relic:
        return result

    for relic_level in range(
        current_relic + 1,
        target_relic + 1
    ):
        recipe_id = f"relic_promotion_recipe_{relic_level:02d}"

        ingredients = relic_recipes.get(recipe_id, [])

        for ingredient in ingredients:
            if not isinstance(ingredient, dict):
                continue

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
    target,
    roster,
    units,
    recipes,
    relic_recipes,
    working_inventory
):
    base_id = target["baseId"]

    target_gear_tier = as_int(
        target.get("targetGearTier"),
        0
    )

    target_relic_tier = as_int(
        target.get("targetRelicTier"),
        0
    )

    unit = roster.get(base_id)

    if unit is None:
        return {
            "baseId": base_id,
            "error": "Postać nie znajduje się w rosterze.",
            "currentGear": 0,
            "targetGear": target_gear_tier,
            "currentRelic": 0,
            "targetRelic": target_relic_tier,
            "directGear": defaultdict(int),
            "relicMaterials": defaultdict(int),
            "shortages": defaultdict(int)
        }

    current_gear = get_current_gear(unit)
    current_relic = get_current_relic(unit)

    direct_gear = get_gear_requirements(
        unit,
        target_gear_tier,
        units
    )

    relic_materials = get_relic_requirements(
        current_relic,
        target_relic_tier,
        relic_recipes
    )

    shortages = defaultdict(int)

    # IMPORTANT:
    # Inventory is consumed BEFORE recipe expansion.
    #
    # This means:
    #   owned finished gear -> used first
    #   owned intermediate gear -> used first
    #   only the remaining amount is crafted
    #   only the final missing materials are reported
    for item_id, quantity in direct_gear.items():
        consume_or_expand(
            item_id,
            quantity,
            recipes,
            working_inventory,
            shortages
        )

    # Relic materials use the exact same inventory-aware algorithm.
    for item_id, quantity in relic_materials.items():
        consume_or_expand(
            item_id,
            quantity,
            recipes,
            working_inventory,
            shortages
        )

    return {
        "baseId": base_id,
        "error": None,
        "currentGear": current_gear,
        "targetGear": target_gear_tier,
        "currentRelic": current_relic,
        "targetRelic": target_relic_tier,
        "directGear": direct_gear,
        "relicMaterials": relic_materials,
        "shortages": shortages
    }


def format_item_list(items, localization):
    if not items:
        return "_brak_"

    lines = []

    for item_id, quantity in items.items():
        if quantity <= 0:
            continue

        name = localized_name(item_id, localization)

        lines.append(
            f"- **{name}** ×{quantity} (`{item_id}`)"
        )

    if not lines:
        return "_brak_"

    return "\n".join(lines)


def generate_report(
    results,
    localization,
    original_inventory
):
    lines = []

    lines.append("# Account Farming Report")
    lines.append("")
    lines.append(
        "Raport uwzględnia posiadane materiały i sprzęt "
        "przed rozwinięciem recept craftingu."
    )
    lines.append("")

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    total_shortages = defaultdict(int)

    for result in results:
        for item_id, quantity in result["shortages"].items():
            total_shortages[item_id] += quantity

    lines.append("## Łączne braki")
    lines.append("")

    if total_shortages:
        lines.append(
            "| Materiał | Brakuje |"
        )
        lines.append(
            "|---|---:|"
        )

        for item_id, quantity in sorted(
            total_shortages.items(),
            key=lambda x: (
                localized_name(x[0], localization).lower(),
                x[0]
            )
        ):
            name = localized_name(item_id, localization)

            lines.append(
                f"| {name} (`{item_id}`) | {quantity} |"
            )
    else:
        lines.append(
            "Brak brakujących materiałów dla wyznaczonych celów."
        )

    lines.append("")

    # ---------------------------------------------------------
    # TARGET DETAILS
    # ---------------------------------------------------------

    for result in results:
        base_id = result["baseId"]

        lines.append("---")
        lines.append("")
        lines.append(f"## {localized_name(base_id, localization)}")
        lines.append("")

        if result.get("error"):
            lines.append(f"**Błąd:** {result['error']}")
            lines.append("")
            continue

        lines.append(
            f"- Gear: **G{result['currentGear']} → "
            f"G{result['targetGear']}**"
        )

        lines.append(
            f"- Relic: **R{result['currentRelic']} → "
            f"R{result['targetRelic']}**"
        )

        lines.append("")

        lines.append("### Bezpośrednie wymagania gear")
        lines.append("")

        if result["directGear"]:
            lines.append("| Gear | Ilość |")
            lines.append("|---|---:|")

            for item_id, quantity in result["directGear"].items():
                name = localized_name(item_id, localization)

                lines.append(
                    f"| {name} (`{item_id}`) | {quantity} |"
                )
        else:
            lines.append("_brak_")

        lines.append("")

        lines.append("### Materiały relic")
        lines.append("")

        if result["relicMaterials"]:
            lines.append("| Materiał | Ilość |")
            lines.append("|---|---:|")

            for item_id, quantity in result["relicMaterials"].items():
                name = localized_name(item_id, localization)

                lines.append(
                    f"| {name} (`{item_id}`) | {quantity} |"
                )
        else:
            lines.append("_brak_")

        lines.append("")

        lines.append("### Rzeczywiste braki")
        lines.append("")

        if result["shortages"]:
            lines.append("| Materiał | Brakuje |")
            lines.append("|---|---:|")

            for item_id, quantity in sorted(
                result["shortages"].items(),
                key=lambda x: (
                    localized_name(x[0], localization).lower(),
                    x[0]
                )
            ):
                name = localized_name(item_id, localization)

                lines.append(
                    f"| {name} (`{item_id}`) | {quantity} |"
                )
        else:
            lines.append(
                "Brak brakujących materiałów."
            )

        lines.append("")

    # ---------------------------------------------------------
    # INVENTORY NOTE
    # ---------------------------------------------------------

    lines.append("---")
    lines.append("")
    lines.append("## Sposób liczenia")
    lines.append("")
    lines.append(
        "Dla każdego wymaganego przedmiotu kalkulator najpierw "
        "zużywa posiadane egzemplarze tego przedmiotu."
    )
    lines.append("")
    lines.append(
        "Dopiero brakująca ilość jest rozwijana przez receptę. "
        "Na każdym kolejnym poziomie recepty posiadany materiał "
        "jest ponownie zużywany przed dalszym craftingiem."
    )
    lines.append("")
    lines.append(
        "Dzięki temu raport pokazuje rzeczywisty brak do farmienia, "
        "a nie pełny koszt recepty przed uwzględnieniem magazynu."
    )
    lines.append("")

    return "\n".join(lines)


def main():
    data = load_json(DATA_FILE)
    player_data = load_json(PLAYER_FILE)
    c3po_data = load_json(C3PO_FILE)
    localization_data = load_json(LOCALIZATION_FILE)
    targets_data = load_json(TARGETS_FILE)

    localization = extract_localization_entries(
        localization_data
    )

    units = build_unit_database(data)
    recipes = build_recipe_database(data)
    relic_recipes = build_relic_recipe_database(data)

    roster = build_player_roster(
        player_data,
        units
    )

    original_inventory = read_c3po_inventory(
        c3po_data
    )

    # IMPORTANT:
    # One shared mutable inventory is intentional.
    #
    # If several targets require the same material, the first target
    # consumes the inventory and the next target sees what remains.
    working_inventory = defaultdict(
        int,
        original_inventory
    )

    targets = targets_data.get("targets", [])

    results = []

    for target in targets:
        result = calculate_target(
            target,
            roster,
            units,
            recipes,
            relic_recipes,
            working_inventory
        )

        results.append(result)

    report = generate_report(
        results,
        localization,
        original_inventory
    )

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(report)

    print(report)

    print("")
    print("=" * 60)
    print("ACCOUNT FARMING REPORT GENERATED")
    print("=" * 60)

    for result in results:
        base_id = result["baseId"]

        print("")
        print(base_id)

        if result.get("error"):
            print("ERROR:", result["error"])
            continue

        shortages = result["shortages"]

        if not shortages:
            print("No shortages.")
            continue

        for item_id, quantity in sorted(shortages.items()):
            print(
                f"  {item_id}: {quantity}"
            )


if __name__ == "__main__":
    main()
