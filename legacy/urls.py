from django.urls import path
from . import views

urlpatterns = [
  path('', views.frontpage, name="top"),
  #path('', views.article, {'category_id':'9990448202528'}),
  #path('category/<slug:top_category>/<path:lower_category>', views.category, name="categories"),
  path('category/<slug:category_name>', views.category, name="categories"),
  path('categories', views.view_categories, name="categories"),
  path('article/<slug:category>/<int:adid>', views.article, name="article"),
  path('article/<slug:category>/<slug:headline>', views.article, name="article"),
  path('article-id/<int:pubid>/<int:adid>', views.article_byid, name="article"),
  path('search', views.search, name="search"),
  path('backchannel', views.backchannel, name="backchannel")
]
