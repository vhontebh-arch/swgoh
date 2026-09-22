import json
import os
import csv
from collections import defaultdict


DATA_FILE = "data.json"
ROSTER_FILE = "roster.csv"
C3PO_FILE = "c3po.json"
LOCALIZATION_FILE = "localization.json"
TARGETS_FILE = "targets.json"
REPORT_FILE = "account_farming_report.md"

DEBUG_ITEM_ID = "G12Finisher_JARJARBINKS_C"

IGNORE_GEAR_IDS = {"9999"}

# GRIND = koszt kredytów w recepturach.
# Kredyty są celowo całkowicie pomijane w analizie braków.
IGNORE_RESOURCE_IDS = {
    "GRIND",
}

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


def debug_find_item(data, target_id):
    """
    Recursively searches the entire data.json tree for target_id.

    Prints every occurrence together with:
    - JSON path to the occurrence
    - containing object
    - useful recipe/result context
    """
    print("")
    print("=" * 80)
    print(f"DEBUG: SZUKAM {target_id} W CAŁYM data.json")
    print("=" * 80)

    matches = []

    def walk(value, path="$", parent=None, parent_path=None):

        if isinstance(value, dict):

            for key, child in value.items():

                child_path = f"{path}.{key}"

                if child == target_id:
                    matches.append({
                        "path": child_path,
                        "parent_path": path,
                        "parent": value,
                        "key": key,
                        "value": child,
                    })

                walk(
                    child,
                    child_path,
                    parent=value,
                    parent_path=path
                )

        elif isinstance(value, list):

            for index, child in enumerate(value):

                child_path = f"{path}[{index}]"

                if child == target_id:
                    matches.append({
                        "path": child_path,
                        "parent_path": path,
                        "parent": parent,
                        "key": index,
                        "value": child,
                    })

                walk(
                    child,
                    child_path,
                    parent=parent,
                    parent_path=path
                )

    walk(data)

    print("")
    print(f"Liczba wystąpień: {len(matches)}")
    print("")

    if not matches:
        print(f"!!! NIE ZNALEZIONO {target_id} !!!")
        print("=" * 80)
        print("")
        return

    for number, match in enumerate(matches, start=1):

        print("-" * 80)
        print(f"WYSTĄPIENIE #{number}")
        print("-" * 80)

        print("JSON path:")
        print(match["path"])
        print("")

        print("Rodzic:")
        try:
            print(
                json.dumps(
                    match["parent"],
                    indent=2,
                    ensure_ascii=False
                )
            )
        except Exception:
            print(repr(match["parent"]))

        print("")

        parent = match["parent"]

        if isinstance(parent, dict):

            interesting_keys = [
                "id",
                "result",
                "ingredients",
                "recipe",
                "recipeId",
                "type",
                "name",
                "quantity",
                "minQuantity",
                "maxQuantity",
            ]

            useful = {
                key: parent[key]
                for key in interesting_keys
                if key in parent
            }

            if useful:

                print("Istotne pola kontekstu:")

                print(
                    json.dumps(
                        useful,
                        indent=2,
                        ensure_ascii=False
                    )
                )

                print("")

        if isinstance(match["parent"], list):

            print("Kontekst listy:")

            try:
                print(
                    json.dumps(
                        match["parent"],
                        indent=2,
                        ensure_ascii=False
                    )
                )
            except Exception:
                print(repr(match["parent"]))

            print("")

    print("=" * 80)
    print("KONIEC DEBUG")
    print("=" * 80)
    print("")


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

        text = z.read(filename).decode(
            "utf-8",
            "replace"
        )

        for line in text.splitlines():

            if "|" not in line:
                continue

            key, value = line.split("|", 1)
            names[key] = value

    except Exception:
        pass

    return names


def localized_name(item_id, names, equipment=None):
    """
    Returns a human-readable item name.

    First tries direct localization keys.

    If no direct localization key exists, uses the authoritative
    nameKey from the equipment definition in data.json and resolves
    it through the English localization bundle.

    If that also fails, returns the technical item ID rather than
    inventing a name.
    """

    if item_id in names:
        return names[item_id]

    if equipment:

        item = equipment.get(item_id)

        if isinstance(item, dict):

            name_key = item.get("nameKey")

            if name_key:

                value = names.get(
                    name_key
                )

                if value:
                    return value

            # Defensive fallback for alternative data-dump formats.
            for key in (
                "name",
                "displayName"
            ):

                value = item.get(key)

                if isinstance(value, str) and value:
                    return value

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


def get_recipe_list(data):
    """
    Returns the recipe collection from data.json.

    Current Comlink data uses the top-level key:
        "recipe"

    Some older/alternative data dumps use:
        "recipes"

    Support both formats so the calculator remains compatible.
    """
    recipes = data.get("recipe")

    if isinstance(recipes, list):
        return recipes

    recipes = data.get("recipes")

    if isinstance(recipes, list):
        return recipes

    return []


def build_recipe_database(data):
    """
    Maps result.id -> ingredient list.

    IMPORTANT:
    Recipes are mapped by result.id, NOT recipe object's own id.
    """
    recipes = {}

    recipe_list = get_recipe_list(data)

    print(
        f"Znaleziono receptury gearu: {len(recipe_list)}"
    )

    for recipe in recipe_list:

        if not isinstance(recipe, dict):
            continue

        result = recipe.get("result")

        if not isinstance(result, dict):
            continue

        result_id = result.get("id")

        if not result_id:
            continue

        recipes[result_id] = recipe.get(
            "ingredients",
            []
        )

    print(
        f"Zbudowano bazę receptur: {len(recipes)}"
    )

    return recipes


def build_relic_recipe_database(data):
    """
    Maps relic_promotion_recipe_01 ... _10 to ingredient lists.

    Relic promotion recipes are not necessarily stored in the same
    top-level collection as ordinary gear recipes, so search the
    complete data tree recursively.
    """
    result = {}

    def walk(value):

        if isinstance(value, dict):

            recipe_id = value.get("id")

            if recipe_id in RELIC_RECIPE_IDS:

                ingredients = value.get(
                    "ingredients",
                    []
                )

                if isinstance(ingredients, list):
                    result[recipe_id] = ingredients

            for child in value.values():
                walk(child)

        elif isinstance(value, list):

            for child in value:
                walk(child)

    walk(data)

    print(
        f"Zbudowano bazę receptur relic: {len(result)}"
    )

    return result


def get_unit_tier(unit_definition, tier):

    for unit_tier in unit_definition.get(
        "unitTier",
        []
    ):

        if as_int(
            unit_tier.get("tier"),
            -1
        ) == tier:

            return unit_tier

    return None


def get_equipment_set(unit_definition, tier):

    unit_tier = get_unit_tier(
        unit_definition,
        tier
    )

    if not unit_tier:
        return []

    equipment_set = unit_tier.get(
        "equipmentSet",
        []
    )

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


def build_player_roster_from_csv(path):

    roster = {}

    with open(
        path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            base_id = row.get(
                "baseId",
                ""
            ).strip()

            if not base_id:
                continue

            roster[base_id] = {
                "currentTier": as_int(
                    row.get("gearTier"),
                    0
                ),
                "relic": {
                    "currentTier": as_int(
                        row.get("relicTier"),
                        0
                    )
                }
            }

    return roster


def read_c3po_inventory(c3po):

    inventory = defaultdict(int)

    inv = c3po.get(
        "inventory",
        c3po
    )

    if not isinstance(inv, dict):
        return inventory

    equipment = inv.get(
        "equipment",
        []
    )

    if isinstance(equipment, dict):

        for item_id, value in equipment.items():

            if isinstance(value, dict):

                quantity = value.get(
                    "quantity",
                    value.get(
                        "count",
                        value.get(
                            "amount",
                            0
                        )
                    )
                )

            else:
                quantity = value

            inventory[item_id] += as_int(
                quantity
            )

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

            inventory[item_id] += as_int(
                quantity
            )

    materials = inv.get(
        "material",
        []
    )

    if isinstance(materials, dict):

        for item_id, value in materials.items():

            if isinstance(value, dict):

                quantity = value.get(
                    "quantity",
                    value.get(
                        "count",
                        value.get(
                            "amount",
                            0
                        )
                    )
                )

            else:
                quantity = value

            inventory[item_id] += as_int(
                quantity
            )

    elif isinstance(materials, list):

        for item in materials:

            if not isinstance(item, dict):
                continue

            item_id = (
                item.get("id")
                or item.get("materialId")
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

            inventory[item_id] += as_int(
                quantity
            )

    return inventory


def expand_item(
    item_id,
    quantity,
    recipes,
    output
):

    if not item_id or quantity <= 0:
        return

    # Placeholder G13 / ignored gear.
    if item_id in IGNORE_GEAR_IDS:
        return

    # GRIND represents credit cost.
    # Credits are deliberately excluded from the farming analysis.
    if item_id in IGNORE_RESOURCE_IDS:
        return

    ingredients = recipes.get(
        item_id
    )

    if not ingredients:

        output[item_id] += quantity
        return

    for ingredient in ingredients:

        if not isinstance(ingredient, dict):
            continue

        ingredient_id = ingredient.get(
            "id"
        )

        if not ingredient_id:
            continue

        # Ignore credit cost at the ingredient level too.
        if ingredient_id in IGNORE_RESOURCE_IDS:
            continue

        amount = as_int(
            ingredient.get(
                "minQuantity",
                ingredient.get(
                    "quantity",
                    1
                )
            ),
            1
        )

        if amount <= 0:
            continue

        expand_item(
            ingredient_id,
            quantity * amount,
            recipes,
            output
        )


def expand_equipment_requirements(
    required_equipment,
    recipes
):

    result = defaultdict(int)

    for item_id, quantity in required_equipment.items():

        expand_item(
            item_id,
            quantity,
            recipes,
            result
        )

    return result


def get_gear_requirements(
    unit_definition,
    current_gear,
    target_gear
):

    required = defaultdict(int)

    start = max(
        current_gear + 1,
        1
    )

    end = min(
        target_gear,
        12
    )

    for tier in range(
        start,
        end + 1
    ):

        for item_id in get_equipment_set(
            unit_definition,
            tier
        ):

            required[item_id] += 1

    return required


def get_relic_requirements(
    current_relic,
    target_relic,
    relic_recipes
):

    result = defaultdict(int)

    start = max(
        current_relic + 1,
        1
    )

    end = min(
        target_relic,
        10
    )

    for relic_tier in range(
        start,
        end + 1
    ):

        recipe_id = (
            f"relic_promotion_recipe_{relic_tier:02d}"
        )

        ingredients = relic_recipes.get(
            recipe_id,
            []
        )

        for ingredient in ingredients:

            if not isinstance(ingredient, dict):
                continue

            item_id = ingredient.get(
                "id"
            )

            if not item_id:
                continue

            # Kredyty nie są częścią analizy reliców.
            if item_id in IGNORE_RESOURCE_IDS:
                continue

            quantity = as_int(
                ingredient.get(
                    "minQuantity",
                    ingredient.get(
                        "quantity",
                        1
                    )
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
    names,
    equipment
):

    unit = roster.get(
        base_id
    )

    if not unit:
        raise RuntimeError(
            f"Nie znaleziono {base_id} w rosterze."
        )

    unit_definition = units.get(
        base_id
    )

    if not unit_definition:
        raise RuntimeError(
            f"Nie znaleziono definicji jednostki {base_id} "
            f"w data.json."
        )

    current_gear = get_current_gear(
        unit
    )

    current_relic = get_current_relic(
        unit
    )

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

        if item_id in IGNORE_RESOURCE_IDS:
            continue

        total_required[item_id] += quantity

    for item_id, quantity in required_relic.items():

        if item_id in IGNORE_RESOURCE_IDS:
            continue

        total_required[item_id] += quantity

    shortages = {}

    for item_id, required_quantity in total_required.items():

        # Dodatkowe zabezpieczenie:
        # kredyty nigdy nie powinny wejść do raportu.
        if item_id in IGNORE_RESOURCE_IDS:
            continue

        owned_quantity = working_inventory.get(
            item_id,
            0
        )

        shortage = max(
            0,
            required_quantity - owned_quantity
        )

        if shortage > 0:
            shortages[item_id] = shortage

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

    return f"{value:,}".replace(
        ",",
        " "
    )


def generate_report(
    results,
    total_required,
    total_shortages,
    inventory,
    names,
    equipment
):

    lines = []

    lines.append(
        "# Account Farming Report"
    )

    lines.append("")

    for result in results:

        lines.append(
            f"- **{result['base_id']}**: "
            f"G{result['current_gear']} → "
            f"G{result['target_gear']}, "
            f"R{result['current_relic']} → "
            f"R{result['target_relic']}"
        )

    lines.append("")

    lines.append(
        "## Łączne braki"
    )

    lines.append("")

    if total_shortages:

        lines.append(
            "| ID | Przedmiot | Wymagane | Posiadane | Brakuje |"
        )

        lines.append(
            "|---|---|---:|---:|---:|"
        )

        for item_id, shortage in sorted(
            total_shortages.items(),
            key=lambda x: (-x[1], x[0])
        ):

            # GRIND nie powinien się tutaj znaleźć,
            # ale zostawiamy dodatkowe zabezpieczenie.
            if item_id in IGNORE_RESOURCE_IDS:
                continue

            owned = inventory.get(
                item_id,
                0
            )

            required_for_report = total_required.get(
                item_id,
                0
            )

            name = localized_name(
                item_id,
                names,
                equipment
            )

            lines.append(
                f"| `{item_id}` | {name} | "
                f"{format_number(required_for_report)} | "
                f"{format_number(owned)} | "
                f"**{format_number(shortage)}** |"
            )

    else:

        lines.append(
            "Brak braków."
        )

    lines.append("")

    lines.append(
        "## Szczegóły"
    )

    lines.append("")

    for result in results:

        lines.append(
            f"### {result['base_id']}"
        )

        lines.append("")

        lines.append(
            f"Gear: **G{result['current_gear']} → "
            f"G{result['target_gear']}** "
            f"Relic: **R{result['current_relic']} → "
            f"R{result['target_relic']}**"
        )

        lines.append("")

        lines.append(
            "#### Bezpośredni wymagany gear"
        )

        lines.append("")

        for item_id, quantity in sorted(
            result[
                "required_direct_gear"
            ].items()
        ):

            name = localized_name(
                item_id,
                names,
                equipment
            )

            lines.append(
                f"- `{item_id}` × {quantity} — {name}"
            )

        lines.append("")

        lines.append(
            "#### Materiały relic"
        )

        lines.append("")

        for item_id, quantity in result[
            "required_relic"
        ].items():

            name = localized_name(
                item_id,
                names,
                equipment
            )

            lines.append(
                f"- `{item_id}` × {quantity} — {name}"
            )

        lines.append("")

        lines.append(
            "#### Braki"
        )

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

                if item_id in IGNORE_RESOURCE_IDS:
                    continue

                name = localized_name(
                    item_id,
                    names,
                    equipment
                )

                lines.append(
                    f"| `{item_id}` | {name} | "
                    f"**{format_number(shortage)}** |"
                )

        else:

            lines.append(
                "Brak braków."
            )

        lines.append("")

    lines.append(
        "## Informacje techniczne"
    )

    lines.append("")

    lines.append(
        "- Inventory pochodzi z `c3po.json`."
    )

    lines.append(
        "- Aktualny gear/relic pochodzi z `roster.csv`."
    )

    lines.append(
        "- Wymagany gear pochodzi z "
        "`unitTier[].equipmentSet`."
    )

    lines.append(
        "- Nazwy gearu są pobierane z `nameKey` "
        "definicji equipment w `data.json` i lokalizacji ENG_US."
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

    lines.append(
        "- `GRIND` oznacza koszt kredytów i jest "
        "całkowicie pomijane w analizie."
    )

    return "\n".join(
        lines
    )


def main():

    print(
        "Ładowanie danych..."
    )

    data = load_json(
        DATA_FILE
    )

    # ------------------------------------------------------------
    # DEBUG: G12Finisher_JARJARBINKS_C
    # ------------------------------------------------------------

    debug_find_item(
        data,
        DEBUG_ITEM_ID
    )

    c3po = load_json(
        C3PO_FILE
    )

    localization = load_json(
        LOCALIZATION_FILE
    )

    targets = load_json(
        TARGETS_FILE
    )

    names = get_localized_names(
        localization
    )

    units = build_unit_database(
        data
    )

    equipment = build_equipment_database(
        data
    )

    recipes = build_recipe_database(
        data
    )

    relic_recipes = build_relic_recipe_database(
        data
    )

    roster = build_player_roster_from_csv(
        ROSTER_FILE
    )

    inventory = read_c3po_inventory(
        c3po
    )

    working_inventory = defaultdict(int)

    for item_id, quantity in inventory.items():

        # Kredyty nie są częścią inventory używanego
        # przez kalkulator farmienia.
        if item_id in IGNORE_RESOURCE_IDS:
            continue

        working_inventory[item_id] = quantity

    target_list = targets.get(
        "targets",
        []
    )

    results = []

    total_required = defaultdict(int)
    total_shortages = defaultdict(int)

    for target in target_list:

        base_id = target.get(
            "baseId"
        )

        target_gear = as_int(
            target.get(
                "targetGearTier",
                0
            )
        )

        target_relic = as_int(
            target.get(
                "targetRelicTier",
                0
            )
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
            equipment=equipment,
        )

        results.append(
            result
        )

        for item_id, quantity in result[
            "total_required"
        ].items():

            if item_id in IGNORE_RESOURCE_IDS:
                continue

            total_required[item_id] += quantity

        for item_id, quantity in result[
            "shortages"
        ].items():

            if item_id in IGNORE_RESOURCE_IDS:
                continue

            total_shortages[item_id] += quantity

    report = generate_report(
        results=results,
        total_required=total_required,
        total_shortages=total_shortages,
        inventory=inventory,
        names=names,
        equipment=equipment,
    )

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            report
        )

    print("")
    print(
        "Wygenerowano account_farming_report.md"
    )

    print("")
    print(
        "Łączne braki:"
    )

    for item_id, quantity in sorted(
        total_shortages.items(),
        key=lambda x: (-x[1], x[0])
    ):

        if item_id in IGNORE_RESOURCE_IDS:
            continue

        print(
            f"  {item_id}: {quantity}"
        )


if __name__ == "__main__":
    main()
