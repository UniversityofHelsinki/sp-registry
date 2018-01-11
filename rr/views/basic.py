from django.shortcuts import render
from django.views import View

class FrontPage(View):
    template_name = 'rr/front_page.html'
    
    def get(self, request):
        return render(request, self.template_name)