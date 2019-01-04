# Automotive History Preservation Society - Legacy Data Views
# Author: Craig Calef <craigdcalef@gmail.com>

from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from io import StringIO

import json, os, logging, pprint

logger = logging.getLogger('ahps.views')

CATEGORIES_DATA_FILE = os.path.join(os.path.dirname(__file__), 'data/categories.json')
NZ_CATEGORIES_DATA_FILE = os.path.join(os.path.dirname(__file__), 'data/non-zero-categories.txt')
SLUGS_DATA_FILE = os.path.join(os.path.dirname(__file__), 'data/slugs.json')
CATIDPATHS_DATA_FILE = os.path.join(os.path.dirname(__file__), 'data/ids.json')
categories = json.loads(open(CATEGORIES_DATA_FILE).read()) # cat_name -> (catid, {subcats}
slugs = json.loads(open(SLUGS_DATA_FILE).read()) # slug -> catid
catids = {v:k for k,v in slugs.items()} # catid -> slug
catid_paths = json.loads(open(CATIDPATHS_DATA_FILE).read()) # catid -> [cat_names]
nz_categories = [l.strip() for l in open(NZ_CATEGORIES_DATA_FILE).readlines()]

sidebar_categories = []
for k in categories.keys():
    cat_id, subcats = categories[k]
    if cat_id in nz_categories:
        sidebar_categories.append({'slug': catids[cat_id], 'name': k})

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [ dict(zip(columns, row)) for row in cursor.fetchall() ]

def pub_counts(cursor):
    r = {}
    with connection.cursor() as cursor:
        for nz_cat in nz_categories:
            q = "select count(*) from PUB{}".format(nz_cat)
            cursor.execute(q)
            row = cursor.fetchone()
            if nz_cat in catids.keys():
                r[catids[nz_cat]] = row[0]
            else:
                r[nz_cat] = row[0]

    return HttpResponse(json.dumps(r))

def category(request, category_name):
    my_catid = slugs[category_name]
    down_cats = catid_paths[my_catid]
    sub_cats = categories
    for c in down_cats:
        sub_cats = sub_cats[c]
    return HttpResponse('')
    s = StringIO()
    render_categories_recursive(sub_cats, s, depth=1)
    pagecontext = {'sidebar_categories': sidebar_categories, 'subcategories': s.getvalue(), 'category_breadcrumbs': render_category_breadcrumbs(my_catid), 'category_name': '' }
    return render(request, 'category.html', context=pagecontext)

def render_category_breadcrumbs(bread_catid):
    down_cats = catid_paths[bread_catid]
    r = '<ol class="breadcrumb" id="category-breadcrumb">'
    levels = []
    depth_cat = categories
    for c in down_cats:
        next_down = depth_cat[c]
        slab_down = catids[next_down[0]]
        depth_cat = next_down[1]
        levels.append((slab_down, c))
    for level_slab, level_catname in levels:
        r += '<li id="category-level"><a href="/category/{}">{}</a></li>'.format(level_slab, level_catname)
    r += "</ol>"
    return r

def backchannel(request):
    #return HttpResponse(render_category_breadcrumbs("9990474216027"))
    return HttpResponse(render_category_breadcrumbs("9990448202528"))

def view_categories(request):
    s = StringIO()
    render_categories_recursive(categories, s, depth=-1)
    return HttpResponse(s.getvalue())

def render_categories_recursive(my_cats, s, depth=0):
    s.write("<ul>")
    for category in my_cats.keys():
        c = my_cats[category]
        s.write('<li><a href="/category/{}">{}</a></li>'.format(catids[c[0]], category))
        if depth != 0:
            render_categories_recursive(c[1], s, depth-1)
    s.write("</ul>")

def article(request, category, adid):
    article_catid = slugs[category]
    with connection.cursor() as cursor:
        cursor.execute('select * from PUB{} where AdID=%s'.format(article_catid), [adid])
        articles = dictfetchall(cursor)
    pagecontext = {'sidebar_categories': sidebar_categories, 'articles': articles, 'category_breadcrumbs': render_category_breadcrumbs(article_catid) }
    return HttpResponse(pprint.pformat(pagecontext))
    #return render(request, 'article.html', context=pagecontext)

def article_byid(request, pubid, adid):
    with connection.cursor() as cursor:
        cursor.execute('select * from PUB{} where AdID=%s'.format(pubid), [adid])
        articles = dictfetchall(cursor)
    #pagecontext = {'sidebar_categories': sidebar_categories, 'articles': articles, 'category_breadcrumbs': render_category_breadcrumbs(article_catid) }
    return HttpResponse(pprint.pformat(articles))

def search(request):
    return HttpResponse("Search results")

def frontpage(request):
    return article(request, 'ahps-pages', 9990448214379)
