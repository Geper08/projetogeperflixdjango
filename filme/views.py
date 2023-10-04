from django.shortcuts import render, redirect, reverse
from .models import Filme, Usuario
from .forms import CriarContaForm, FormHomepage
from django.views.generic import TemplateView, ListView, DetailView, FormView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect

# Create your views here.
# def homepage(request):
#    return render(request, "homepage.html")

class Homepage(FormView):
    template_name = "homepage.html"
    form_class = FormHomepage
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated: #usuario esta autenticado:
            # redireciona para a homefilmes
            return redirect('filme:homefilmes')
        else:
            return super().get(request, *args, **kwargs) # redireciona para a homepage
        
    def get_success_url(self):
        email = self.request.POST.get("email")
        usuarios = Usuario.objects.filter(email=email)
        if usuarios:
            return reverse('filme:login')
        else:
            return reverse('filme:criarconta')


# url - view - html
#def homefilmes(request):
#    context = {}
#   lista_filmes = Filme.objects.all()
#   context['lista_filmes'] = lista_filmes
#  return render(request, "homefilmes.html", context)

class Homefilmes(LoginRequiredMixin, ListView):
    template_name = "homefilmes.html"
    model = Filme
    #object_list -> lista de itens do modelo
    
    
class Detalhesfilme(LoginRequiredMixin, DetailView):
    template_name = "detalhesfilme.html"
    model = Filme
    #object -> 1 item do nosso modelo
    
    def get(self, request, *args, **kwargs):
            # contabilizar uma visualização
        filme = self.get_object()
        filme.visualizacoes += 1
        filme.save()
        usuario = request.user
        usuario.filmes_vistos.add(filme)
        return super().get(request, *args, **kwargs) # redireciona o usuario para a url final

    def get_context_data(self, **kwargs):
        context = super(Detalhesfilme, self).get_context_data(**kwargs)
        # filtrar a minha tabela de filmes pegando os filmes cuja categoria é igual a categoria do filme da página (object)
        # self.get_object()
        filmes_relacionados = self.model.objects.filter(categoria=self.get_object().categoria)[0:5]
        context["filmes_relacionados"] = filmes_relacionados
        return context
    
class Pesquisafilme(LoginRequiredMixin, ListView):
    template_name = "pesquisa.html"
    model = Filme
    
    #object_list
    def get_queryset(self):
        termo_pesquisa = self.request.GET.get('query')
        if termo_pesquisa:
            object_list = self.model.objects.filter(titulo__icontains=termo_pesquisa)
            return object_list
        else:
            return None
        
class Paginaperfil(LoginRequiredMixin, UpdateView):
    template_name = "editarperfil.html"
    model = Usuario
    fields = ['first_name', 'last_name', 'email']
    
    def get_success_url(self):
        return reverse('filme:login')


class Criarconta(FormView):
    template_name = "criarconta.html"
    form_class = CriarContaForm
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('filme:login')
    
    
class EditarPerfil(LoginRequiredMixin, UpdateView):
    template_name = 'editar_perfil.html'
    model = Usuario
    fields = ['first_name', 'last_name', 'email']

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            if self.request.user.id != self.kwargs['pk']:
                return self.redirect_to_own_profile()
        else:
            return HttpResponseRedirect(reverse('filme:login'))
        return super().dispatch(request, *args, **kwargs)

    def redirect_to_own_profile(self):
        own_profile_url = reverse('filme:editar-perfil', kwargs={'pk': self.request.user.id})
        return HttpResponseRedirect(own_profile_url)
    
    def get_success_url(self):
        return reverse('filme:home_dhytpix')
 