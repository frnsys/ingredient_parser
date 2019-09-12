"""
Parse a list of USDA ingredients into
an ingredient tree
"""
import re

ANDOR = re.compile(' AND( ?\/ ?OR)? ')
PERCENT_START = re.compile('^\d+% ')
PERCENT_END = re.compile(' \d+%$')
STRAY_NUM = re.compile('\*?\d*$')

# CONTAINS 2% OR LESS OF
# 2% OR LESS OF
# LESS THAN 2% OF
# LESS THAN 1%

SPECIAL_CHARS = '†‡§'
STANDARDIZATIONS = {
    'FLAVOUR': 'FLAVOR',
    'YOGHURT': 'YOGURT',
}

def clean(ingred):
    """Clean individual ingredient"""
    ingred = ingred.strip().strip('&').strip('*').strip('#')
    for ch in SPECIAL_CHARS:
        ingred = ingred.replace(ch, '')

    # Drop qualifiers like `INGREDIENTS: Milk`
    ingred = ingred.split(':')[-1].strip()

    # Lots of stray percentages
    ingred = PERCENT_START.sub('', ingred)
    ingred = PERCENT_END.sub('', ingred)
    ingred = STRAY_NUM.sub('', ingred)

    return ingred.strip()

def parse_ingredients(inp):
    """Parse list of ingredients"""
    # Standardize to uppercase
    # inp = inp.upper()
    parsed, _ = _parse(inp)
    return parsed

def _parse(inp):
    i = 0
    buff = []
    parsed = []

    # Some standardization
    inp = inp.upper()
    inp = ANDOR.sub(',', inp)
    inp = inp.replace(';', ',')
    for f, t in STANDARDIZATIONS.items():
        inp = inp.replace(f, t)

    while i < len(inp):
        char = inp[i]
        if char == ',' or char == '.':
            if buff:
                parsed.append((clean(''.join(buff)), []))
                buff = []
        elif char == '(' or char == '[' or char == '{':
            sub, skip = _parse(inp[i+1:])
            parsed.append((clean(''.join(buff)), sub))
            buff = []
            i += skip + 1
        elif char == ')' or char == ']' or char == '}':
            if buff:
                parsed.append((clean(''.join(buff)), []))
            return parsed, i
        else:
            buff.append(char)
        i += 1

    if buff:
        parsed.append((clean(''.join(buff)), []))

    # Drop empty ingredients
    parsed = [p for p in parsed if p[0]]
    return parsed, i

def leaves(nodes):
    for node, chs in nodes:
        if not chs:
            yield node
        else:
            yield from leaves(chs)

def flatten(nodes):
    for node, chs in nodes:
        yield node
        yield from flatten(chs)

def print_tree(nodes, depth=0):
    for node, chs in nodes:
        print('{}{}'.format('  '*depth, node))
        print_tree(chs, depth+1)

if __name__ == '__main__':
    examples = [
        'MILK, SUGAR, CREAM, CHOCOLATE CHUNKS (SUGAR, COCONUT OIL, COCOA, BUTTER OIL, SOY LECITHIN, VANILLA), CORN SYRUP, NATURAL PEPPERMINT EXTRACT, TAPIOCA STARCH, WHEY PROTEIN ISOLATE, MONO- AND DI-GLYCERIDES, GUAR GUM, TARA GUM, CELLULOSE GUM, XANTHAN GUM, CARRAGEENAN, DEXTROSE, VITAMIN A PALMITATE.',
        "SUGAR, VEGETABLE SHORTENING (PALM AND SOYBEAN OILS, MONO AND DIGLYCERIDES, POLYSORBATE 60, TO PRESERVE FRESHNESS (TBHQ), ENRICHED BLEACHED WHEAT FLOUR (WHEAT FLOUR, NIACIN, REDUCED IRON, THIAMINE MONONITRATE, RIBOFLAVIN, FOLIC ACID), EGG WHITES, WATER, SOYBEAN OIL, EGGS, SKIM MILK, COCOA ALKALI PROCESSES, HIGH FRUCTOSE CORN SYRUP, CONTAINS LESS THAN 2% OF THE FOLLOWING: CORNSTARCH, PARTIALLY HYDROGENATED SOYBEAN AND COTTONSEED OILS, LEAVENING (BAKING SOFA, SODIUM ACID PYROPHOSPHATE, MONOCALCIUM PHOSPHATE), NATURAL AND ARTIFICIAL FLAVOR, PROPYLENE GLYCOL, MONO DIESTERS OF FATS AND FATTY ACIDS, WHEY (A MILK DERIVATIVE), SALT, MODIFIED TAPIOCA STARCH, CORN STARCH, WHEAT STARCH, SOY LECITHIN, GUAR GUM, CORN SYRUP SOLIDS, XANTHAN GUM, SODIUM STEAROYL LACTYLATE, ARTIFICIAL COLORS (YELLOW 5 LAKE, BLUE 1 LAKE, RED 40 LAKE), DEXTRIN, CONFECTIONER'S GLAZE, CARNAUBA WAX.",
        'WATER, EXPELLER-PRESSED CANOLA OIL*, WHITE DISTILLED VINEGAR*, DRIED GARLIC*, CANE SUGAR*, SEA SALT, LEMON JUICE CONCENTRATE*, DRIED ONION*, DRIED PARSLEY*, BLACK PEPPER*, XANTHAN GUM.*ORGANIC'
    ]

    for e in examples:
        print('--Input--')
        print(e)
        ings = parse_ingredients(e)
        print('--Parsed--')
        print(ings)
        print('--Leaves--')
        print(list(leaves(ings)))
        print('--Tree--')
        print_tree(ings)
        print('--Flattened--')
        print(list(flatten(ings)))
        print('==='*10)
