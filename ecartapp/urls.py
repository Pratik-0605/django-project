from django.urls import path
from ecartapp import views
from ecart import settings
from django.conf.urls.static import static

urlpatterns = [
   path('home',views.home),
   path('pdetails/<pid>',views.pdetails),
   path('viewcart',views.viewcart),
   path('register',views.register),
   path('login',views.ulogin),
   path('logout',views.ulogout),
   path('cartfilter/<cv>',views.cartfilter),
   path('sort/<sv>',views.sort),
   path('range',views.range),
   path('addtocartt/<pid>',views.addtocartt),
   path('remove/<cid>',views.remove),
   path('updateqty/<qv>/<cid>',views.updateqty),
   path('placeorder',views.placeorder),
   path('makepayment',views.makepayment),
   path('sendusermail',views.sendusermail),
]

if settings.DEBUG:
   urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)