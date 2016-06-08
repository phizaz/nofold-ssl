import utils

'''
Get the families that have no bitscores
'''

all_families = set(utils.get_all_families())
available_families = set(utils.get_calculated_families())
not_having_families = all_families - available_families
print('not having families cnt:', len(not_having_families))
for each in not_having_families:
    print(each)