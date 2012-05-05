from haystack.query import SearchQuerySet, EmptySearchQuerySet
from haystack.forms import ModelSearchForm
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, InvalidPage
from django.conf import settings
from erp_test.misc import *

RESULTS_PER_PAGE = getattr(settings, 'HAYSTACK_SEARCH_RESULTS_PER_PAGE', 20)

def custom_search(request, template='search/search.html', load_all=True, form_class=ModelSearchForm, searchqueryset=None, context_class=global_context, extra_context=None, results_per_page=None):
    query = ''
    results = EmptySearchQuerySet()
    
    if request.GET.get('q'):
        sqs = SearchQuerySet().autocomplete(text = request.GET['q'])
        form = form_class(request.GET, searchqueryset=sqs, load_all=load_all)
        no_of_results=SearchQuerySet().count()
        sqs_2 = SearchQuerySet().auto_query(text = request.GET['q'])
        form_2 = form_class(request.GET, searchqueryset=sqs_2, load_all=load_all)
        
        
        if form.is_valid():
            query = form.cleaned_data['q']
            results = form.search()
            
            
        if form_2.is_valid():
            query_2 = form.cleaned_data['q']
            results_2 = form.search()
           
    else:
        form = form_class(searchqueryset=searchqueryset, load_all=load_all)
    
    paginator = Paginator(results, results_per_page or RESULTS_PER_PAGE)
    
    try:
        page = paginator.page(int(request.GET.get('page', 1)))
    except InvalidPage:
        raise Http404("No such page of results!")
    
    context = {
        'form': form,
        'page': page,
        'paginator': paginator,
        'query': query,
        'suggestion': None,
    }
    
    if getattr(settings, 'HAYSTACK_INCLUDE_SPELLING', False):
        context['suggestion'] = form.get_suggestion()
    
    if extra_context:
        context.update(extra_context)
    
    return render_to_response(template, context, context_instance=context_class(request))

'''

def custom_search(request):
    all_results = None
    query = False
    form = ModelSearchForm()
    if 'q' in request.GET:
        sqs = SearchQuerySet().autocomplete(text = request.GET['q'])
        print sqs
        form = ModelSearchForm(request.GET, searchqueryset=sqs, load_all=True)
        all_results = form.search()
        print all_results
    if all_results is not None and all_results.count() != 0:
        query = True
    results = all_results
    return render_to_response('search/search.html', locals(), context_instance = global_context(request))



  query = False
  searchqueryset = None
  form = ModelSearchForm()
  if request.GET.get('q'):
    form = ModelSearchForm(request.GET, searchqueryset=None, load_all=True)
    searchqueryset = form.search()
  if searchqueryset is not None and searchqueryset.count() != 0:
    query = True
  return render_to_response('search/search.html', locals(), context_instance = global_context(request));

'''
