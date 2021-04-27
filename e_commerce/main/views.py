from datetime import datetime
from typing import Any, Dict, Union

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import QuerySet
from django.forms import BaseModelForm
from django.http import HttpResponseRedirect
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView

from .forms import GoodsCreateUpdateForm, PhoneConfirmForm, ProfileFormSet, UserForm
from .models import Goods, Profile, Seller, Tag
from .tasks import send_sms_verification_code


class GoodsList(ListView):
    """This class provides a list-based view for a 'Goods' model.

    model - model of a view
    paginate_by - number of objects displayed on one page
    context_object_name - a name by which objects can be available
    in a template
    """

    model = Goods
    paginate_by = 9
    context_object_name = "goods_list"

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """This overridden method provides additional context data like
        a user's avatar and available tags to a response.
        """
        context = super().get_context_data(**kwargs)
        context["tag_list"] = Tag.objects.all()
        context["tag"] = self.request.GET.get("tag")
        if self.request.user.is_authenticated:
            context["avatar"] = Profile.objects.get(user=self.request.user).avatar
        else:
            context["avatar"] = None
        return context

    def get_queryset(self) -> QuerySet[Any]:
        """This overridden method provides a queryset filtered by tag
        if a request contains a 'tag' parameter.
        """
        queryset = super().get_queryset()
        if self.request.GET.get("tag"):
            self.tag = get_object_or_404(Tag, name=self.request.GET.get("tag"))
            return queryset.filter(tags=self.tag)
        else:
            return queryset


class GoodsDetail(DetailView):
    """This class provides a detailed view of a 'Goods' model.

    queryset - a query dict containing 'Goods' objects
    context_object_name - a name by which objects can be available
    in a template
    """

    queryset = Goods.objects.all()
    context_object_name = "goods"

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """This overridden method provides additional context data like
        a user's avatar to a response.
        """
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["avatar"] = Profile.objects.get(user=self.request.user).avatar
        else:
            context["avatar"] = None
        if "views_counter" not in context:
            views_counter_cache_name = f"views_counter_{context['goods'].id}"
            context["views_counter"] = cache.get(views_counter_cache_name)
            if not context["views_counter"]:
                context["views_counter"] = Goods.objects.get(
                    id=context["goods"].id
                ).views_counter
            context["views_counter"] += 1
            cache.set(views_counter_cache_name, context["views_counter"], 120)
        return context


class GoodsCreate(PermissionRequiredMixin, CreateView):
    """This class provides a view for creating a new 'Goods' object.

    permission_required - a name of required permission to access this page
    login_url - a redirect URL for a case when a user is not authorized
    or authenticated
    redirect_field_name - a parameter passed to URL in a case of redirection
    model - model of a view
    template_name - a template that will be used for a page rendering
    form_class - model form class
    """

    permission_required = "main.add_goods"
    login_url = reverse_lazy("account_login")
    redirect_field_name = "redirect_to"
    model = Goods
    template_name = "main/goods_create.html"
    form_class = GoodsCreateUpdateForm

    def get_success_url(self) -> str:
        """This overridden method provides URL for a detailed view of
        a newly created 'Goods' object.
        """
        self.success_url = reverse_lazy("goods-detail", kwargs={"pk": self.object.pk})
        return self.success_url

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """This overridden method provides additional context data like
        a user's avatar, a form, and information about CSS classes of form's
        fields to a response.
        """
        if "form" not in kwargs:
            kwargs["form"] = self.get_form()
        context = super().get_context_data(**kwargs)
        context["filds_for_form_control"] = (
            "name",
            "description",
            "weight",
            "manufacturer",
            "price",
            "discount",
        )
        context["filds_for_custom_select"] = ("tags", "size", "category")
        context["form"] = kwargs.get("form")
        if self.request.user.is_authenticated:
            context["avatar"] = Profile.objects.get(user=self.request.user).avatar
        else:
            context["avatar"] = None
        return context

    def post(
        self, request: HttpRequest, *args, **kwargs
    ) -> Union[HttpResponseRedirect, HttpResponse]:
        """This overridden method checks a form's data and saves it if it's
        valid or returns this form with found errors.

        :param request: post request object
        :type request: class 'django.http.request.HttpRequest'
        """
        self.object = None
        if self.get_form().is_valid():
            return self.form_valid(self.get_form())
        else:
            return self.form_invalid(self.get_form())

    def form_valid(self, form: BaseModelForm) -> HttpResponseRedirect:
        """This overridden method saves form's data to DB and returns a
        response with redirection to a detailed page of a created
        'Goods' object.

        :param form: form with user's data
        :type form: class 'main.forms.GoodsCreateUpdateForm'
        """
        temp_goods = form.save(commit=False)
        # TODO: заменить на юзера, когда будет готова проверка для продавцов
        temp_goods.seller = Seller.objects.get(name="Bobbie's Bits")
        temp_goods.creation_date = datetime.now()
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        """This overridden method returns a response with a template rendered
        with the given context. The context contains a form with found errors.

        :param form: form with user's data
        :type form: class 'main.forms.GoodsCreateUpdateForm'
        """
        return self.render_to_response(self.get_context_data(form=form))


class GoodsUpdate(PermissionRequiredMixin, UpdateView):
    """This class provides a view for updating an existing 'Goods' object.

    permission_required - a name of required permission to access this page
    login_url - a redirect URL for a case when a user is not authorized
    or authenticated
    redirect_field_name - a parameter passed to URL in a case of redirection
    model - model of a view
    template_name - a template that will be used for a page rendering
    form_class - model form class
    """

    permission_required = "main.change_goods"
    login_url = reverse_lazy("account_login")
    redirect_field_name = "redirect_to"
    model = Goods
    template_name = "main/goods_update.html"
    form_class = GoodsCreateUpdateForm

    def get_success_url(self) -> str:
        """This overridden method provides URL for a detailed view of
        a newly created 'Goods' object.
        """
        self.success_url = reverse_lazy("goods-detail", kwargs={"pk": self.object.pk})
        return self.success_url

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """This overridden method provides additional context data like
        a user's avatar, a form, and information about CSS classes of form's
        fields to a response.
        """
        if "form" not in kwargs:
            kwargs["form"] = self.get_form()
        context = super().get_context_data(**kwargs)
        context["filds_for_form_control"] = (
            "name",
            "description",
            "weight",
            "manufacturer",
            "price",
            "discount",
        )
        context["filds_for_custom_select"] = ("tags", "size", "category")
        context["form"] = kwargs.get("form")
        if self.request.user.is_authenticated:
            context["avatar"] = Profile.objects.get(user=self.request.user).avatar
        else:
            context["avatar"] = None
        return context

    def post(
        self, request: HttpRequest, *args, **kwargs
    ) -> Union[HttpResponseRedirect, HttpResponse]:
        """This overridden method checks a form's data and updates with it
        linked 'Goods' object if data is valid or returns this form with
        found errors.

        :param request: post request object
        :type request: class 'django.http.request.HttpRequest'
        """
        self.object = self.get_object()
        if self.get_form():
            return self.form_valid(self.get_form())
        else:
            return self.form_invalid(self.get_form())

    def form_valid(self, form: BaseModelForm) -> HttpResponseRedirect:
        """This overridden method saves form's data to DB and returns a
        response with redirection to a detailed page of an updated
        'Goods' object.

        :param form: form with user's data
        :type form: class 'main.forms.GoodsCreateUpdateForm'
        """
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        """This overridden method returns a response with a template rendered
        with the given context. The context contains a form with found errors.

        :param form: form with user's data
        :type form: class 'main.forms.GoodsCreateUpdateForm'
        """
        return self.render_to_response(self.get_context_data(form=form))


class ProfileUpdate(LoginRequiredMixin, UpdateView):
    """This class provides a view for updating a linked user's 'Profile'.

    login_url - a redirect URL for a case when a user is not authenticated
    redirect_field_name - a parameter passed to URL in a case of redirection
    model - model of a view
    form_class - model form class
    template_name - a template that will be used for a page rendering
    context_object_name - a name by which objects can be available
    in a template
    """

    login_url = reverse_lazy("account_login")
    redirect_field_name = "redirect_to"
    model = User
    form_class = UserForm
    template_name = "main/profile_update.html"
    context_object_name = "profile"

    def get_success_url(self) -> str:
        """This overridden method provides URL for an update view of
        a linked user's 'Profile'.
        """
        self.success_url = reverse_lazy("profile", kwargs={"pk": self.request.user.pk})
        return self.success_url

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """This overridden method provides additional context data like
        a user's avatar and forms to a response.
        """
        context = super().get_context_data(**kwargs)
        if "user_form" not in kwargs:
            kwargs["user_form"] = UserForm(instance=self.object)
        if "profile_form_set" not in kwargs:
            kwargs["profile_form_set"] = ProfileFormSet(instance=self.object)
        context["user_form"] = kwargs.get("user_form")
        context["profile_form_set"] = kwargs.get("profile_form_set")
        context["avatar"] = Profile.objects.get(user=self.object).avatar
        return context

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """This overridden method gets a 'User' object linked with 'Profile'
        and returns a rendered template of a 'Profile' update view.

        :param request: user's request object
        :type request: class 'django.http.request.HttpRequest'
        """
        self.object = User.objects.get(id=request.user.pk)
        return self.render_to_response(self.get_context_data())

    def post(
        self, request: HttpRequest, *args, **kwargs
    ) -> Union[HttpResponseRedirect, HttpResponse]:
        """This overridden method checks data in forms and updates with it
        linked 'User' and 'Profile' objects if data is valid or returns these
        forms with found errors.

        :param request: post request object
        :type request: class 'django.http.request.HttpRequest'
        """
        self.object = User.objects.get(id=request.user.pk)
        user_form = UserForm(request.POST, instance=self.object)
        profile_form_set = ProfileFormSet(
            request.POST, request.FILES, instance=self.object
        )
        if profile_form_set.is_valid() and user_form.is_valid():
            return self.form_valid(user_form, profile_form_set)
        else:
            return self.form_invalid(user_form, profile_form_set)

    def form_valid(
        self, user_form: UserForm, profile_form_set: ProfileFormSet
    ) -> HttpResponseRedirect:
        """This overridden method saves data in forms to DB and returns a
        response with redirection to a successful URL.

        :param user_form: form with user's data
        :type user_form: class 'main.forms.UserForm'
        :param profile_form_set: form with user's data
        :type profile_form_set: class 'main.forms.ProfileFormSet'
        """
        self.object = user_form.save()
        profile_form_set.instance = self.object
        for form in profile_form_set.forms:
            temp_profile = form.save(commit=False)
            temp_profile.user = self.object
            temp_profile.save()
        profile_form_set.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(
        self, user_form: UserForm, profile_form_set: ProfileFormSet
    ) -> HttpResponse:
        """This overridden method returns a response with a template rendered
        with the given context. The context contains forms with found errors.

        :param user_form: form with user's data
        :type user_form: class 'main.forms.UserForm'
        :param profile_form_set: form with user's data
        :type profile_form_set: class 'main.forms.ProfileFormSet'
        """
        return self.render_to_response(
            self.get_context_data(
                user_form=user_form, profile_form_set=profile_form_set
            )
        )


class PhoneConfirmation(LoginRequiredMixin, FormView):
    """This class provides a view for a 'phone confirmation' page.

    login_url - a redirect URL for a case when a user is not authenticated
    redirect_field_name - a parameter passed to URL in a case of redirection
    model - model of a view
    form_class - model form class
    template_name - a template that will be used for a page rendering
    success_url - a URL of a 'phone confirmed' page
    """

    login_url = reverse_lazy("account_login")
    redirect_field_name = "redirect_to"
    form_class = PhoneConfirmForm
    template_name = "main/phone_confirmation.html"
    success_url = reverse_lazy("phone-confirmed")

    def get_form_kwargs(self) -> Dict[str, Any]:
        """This overridden method provides the availability of a request's
        data to a form.
        """
        kw = super(PhoneConfirmation, self).get_form_kwargs()
        kw["request"] = self.request
        return kw

    def get(
        self, request: HttpRequest, *args, **kwargs
    ) -> Union[HttpResponseRedirect, HttpResponse]:
        """This overridden method checks if a user's phone number was
        confirmed and sends a confirmation code if it's not. Otherwise,
        it redirects to a 'phone confirmed' page.

        :param request: user's request object
        :type request: class 'django.http.request.HttpRequest'
        """
        if request.user.profile.is_phone_confirmed:
            return HttpResponseRedirect(self.get_success_url())
        else:
            send_sms_verification_code(request.user.profile.id)
            return self.render_to_response(self.get_context_data())


class PhoneConfirmed(LoginRequiredMixin, TemplateView):
    """This class provides a view for a 'phone confirmed' page.

    template_name - a template that will be used for a page rendering
    """

    template_name = "main/phone_confirmed.html"


def index(request: HttpRequest) -> HttpResponse:
    """This function returns a rendered template of the site's main page."""
    turn_on_block = True
    text_for_filter = "Братухе подари на днюху черный орфографический словарь"
    if request.user.is_authenticated:
        avatar = Profile.objects.get(user=request.user).avatar
    else:
        avatar = None
    return render(
        request,
        "main/index.html",
        {
            "turn_on_block": turn_on_block,
            "user": request.user,
            "text_for_filter": text_for_filter,
            "avatar": avatar,
        },
    )
