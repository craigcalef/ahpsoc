import csv
import json
import traceback
from collections import defaultdict
from pprint import pprint
from django.utils.html import strip_tags
from slugify import slugify

# CategoryID	CategoryName	CategoryHidden	Subcat1	MembersOnly	Subcat2	ApprovalRequiredFlag	BlockSubmission	Subcat3	Subcat4	Subcat5	Subcat6
subcats = [1, 3, 5, 8, 9, 10, 11]
tsvin = csv.reader(open('category.tsv', 'r'), delimiter='\t')
categories = {}
catids = {}

def recurse_tree_build(record, subs, d):
  if len(subs) == 0:
    return
  cur = record[subs[0]]
  if not cur or cur == 'NULL':
    return
  if cur in d.keys():
    recurse_tree_build(record, subs[1:], d[cur][1])
    #recurse_tree_build(record, subs[1:], d[cur])
  else:
    n = {}
    d[cur] = (record[0], n)
    #d[cur] = n
    recurse_tree_build(record, subs[1:], n)


def slug_cats_recurse(slugs, cat):
  cats = {}
  for down in cat.items():
    # unpack categoryname, category id, and a dict of subcategories
    cname, i = down
    catid, subcats = i
    slug_cname = slugify(cname)
    cur_cat_slugs = slugs + [slug_cname]
    cur_cat_slug_url = "/".join(cur_cat_slugs)
    cats[cur_cat_slug_url] = catid
    sub_cats_reified = slug_cats_recurse(cur_cat_slugs, subcats)
    cats.update(sub_cats_reified)
  return cats
     
def cats_by_id_recurse(catids, cat, parents):
  for down in cat.items():
    # unpack categoryname, category id, and a dict of subcategories
    cname, i = down
    catid, subcats = i
    catids[catid] = parents+[cname]
    cats_by_id_recurse(catids, subcats, catids[catid])

linec = 0
try:
  for c in tsvin:
    linec = linec+1
    recurse_tree_build(c, subcats, categories)
except:
  print("Error on line", linec)
  traceback.print_exc()

cats_by_id_recurse(catids, categories, [])
slugs = slug_cats_recurse([], categories)
