import json
from enum import IntEnum

class HeroType(IntEnum):
    # attack type
    MELEE = 0
    RANGED = 1
    # player role
    CARRY = 2
    DISABLER = 3
    INITIATOR = 4
    JUNGLER = 5
    SUPPORT = 6
    DURABLE = 7
    NUKER = 8
    PUSHER = 9
    ESCAPE = 10
    #player category
    STRENGTH = 11
    AGILITY = 12
    INTELLIGENCE = 13

attack_range = {'melee', 'ranged'}
main_categories = {'agility', 'strength', 'intelligence'}
roles = ['carry', 'disabler', 'initiator', 'jungler', 'support', 'durable', 'nuker', 'pusher', 'escape']
all_features = roles + list(attack_range) + list(main_categories)
role_to_enumerated = {
    'melee': HeroType.MELEE,
    'ranged': HeroType.RANGED,

    'carry': HeroType.CARRY,
    'disabler': HeroType.DISABLER,
    'initiator': HeroType.INITIATOR,
    'jungler': HeroType.JUNGLER,
    'support': HeroType.SUPPORT,
    'durable': HeroType.DURABLE,
    'nuker': HeroType.NUKER,
    'pusher': HeroType.PUSHER,
    'escape': HeroType.ESCAPE,

    'agility': HeroType.AGILITY,
    'strength': HeroType.STRENGTH,
    'intelligence': HeroType.INTELLIGENCE
}
role_sets = {k: set() for k in all_features}
hero_to_hero_type = {}

# pre-processing
for role in roles:
    try:
        with open(role + '.txt', 'r') as infile:
            lines = infile.readlines()
    except FileNotFoundError as e:
        print(e)
    else:
        lines = list(map(lambda s: s[:-1] if s.endswith('\n') else s, lines))
        lines = list(filter(lambda s: not s.endswith('png'), lines))
        lines = list(map(lambda s: s.lower(), lines))
        lines = list(map(lambda s: '#' + s if s in main_categories else s, lines))

        with open(role + '.txt', 'w') as outfile:
            outfile.write('\n'.join(lines))
for ar in attack_range:
    try:
        with open(ar + '.txt', 'r') as infile:
            lines = infile.readlines()
    except FileNotFoundError as e:
        print(e)
    else:
        lines = list(map(lambda s: s[:-1] if s.endswith('\n') else s, lines))
        lines = list(filter(lambda s: s != '', lines))
        lines = list(filter(lambda s: len(s) > 1, lines))
        lines = list(map(lambda s: s.strip().lower(), lines))

        with open(ar + '.txt', 'w') as outfile:
            outfile.write('\n'.join(lines))

# fill role sets
for role in roles:
    with open(role + '.txt', 'r') as infile:
        lines = list(map(lambda s: s[:-1] if s.endswith('\n') else s, infile.readlines()))

    for hero_name in lines:
        if hero_name.startswith('#'):
            category = hero_name[1:]
        else:
            role_sets[role].add(hero_name)
            role_sets[category].add(hero_name)
for ar in attack_range:
    with open(ar + '.txt', 'r') as infile:
        lines = list(map(lambda s: s[:-1] if s.endswith('\n') else s, infile.readlines()))

    for hero_name in lines:
        role_sets[ar].add(hero_name)

# get hero id, name info
with open('dota2heroes.json', 'r') as infile:
    heroes = json.load(infile)
    for hero in heroes:
        hero['name'] = hero['localized_name'].lower()
        del hero['url_small_portrait'], hero["url_large_portrait"], hero["url_full_portrait"],\
            hero['localized_name'], hero['url_vertical_portrait']

# create hero_to_hero_type
for hero in heroes:
    hero_feature_list = []
    hero_name = hero['name']

    for role in all_features:
        if hero_name in role_sets[role]:
            hero_feature_list.append(role_to_enumerated[role])

    hero_to_hero_type[hero['id']] = sorted(hero_feature_list)

# create json file
with open('hero_to_hero_type.json', 'w') as outfile:
    json.dump(hero_to_hero_type, outfile, indent=4)

key_list = []
for key, _ in hero_to_hero_type.items():
    key_list.append(key)
print(sorted(key_list))
