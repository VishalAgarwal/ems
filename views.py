from django.http import HttpResponse, HttpResponseRedirect
from formtools.wizard.views import SessionWizardView
from django.shortcuts import render

from django.views.generic.edit import FormView
from .forms import LoginForm, ReturnSelectorFormSet
from .utils import get_latest_order, get_latest_er


def index(request):
  if request.method == "POST":
    form = LoginForm(request.POST)
    if form.is_valid():
      mobile_number = form.cleaned_data["mobile_number"]            
      latest_order = get_latest_order(mobile_number)
      latest_er = get_latest_er(mobile_number)

      # Case 1: No order and no exchange request found
      if len(latest_order) == 0 and len(latest_er) == 0:
        return render(request,"ems/order_not_found.html")

      # Case 2: Order found but no past exchange request
      if len(latest_order) != 0 and len(latest_er) == 0:
        request.session['latest_order'] = latest_order
        return render(
            request,
            "ems/customer_home.html",
            {
              "latest_order":latest_order,
              "ex_req_id":"0"
            }
          )

      return render(request,"ems/order_not_found.html")
  else:  
    form = LoginForm()
  return render(request, "ems/login.html", {"form": form})


class EmsWizard(SessionWizardView):
    def done(self, form_list, **kwargs):
        return render(self.request, 'done.html', {
            'form_data': [form.cleaned_data for form in form_list],
        })

    def get_form_kwargs(self, step):
        if step == "0":
            return {
            'max_return_counts': [2,3,4]
            }    
        elif step == "1":
            data_for_step_0 = self.get_cleaned_data_for_step('0')
            print(data_for_step_0)
            return {}

    def get_form(self, step=None, data=None, files=None):
        form = super(EmsWizard, self).get_form(step, data, files) 
        step = step or self.steps.current
        if step == "0":
            latest_order = self.request.session["latest_order"]
            form.extra = len(latest_order["products"])
        if step == "1":
            form.extra = 8
        return form

