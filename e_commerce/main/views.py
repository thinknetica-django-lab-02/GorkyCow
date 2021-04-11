from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth import logout
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from main.forms import GoodsCreateUpdateForm, ProfileFormSet, UserForm
from main.models import Goods, Seller, Tag, User, Profile


class GoodsList(ListView):
    model = Goods
    paginate_by = 9
    context_object_name = "goods_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag_list"] = Tag.objects.all()
        context["tag"] = self.request.GET.get("tag")
        if self.request.user.is_authenticated:
            context["avatar"] = Profile.objects.get(user=self.request.user).avatar
        else:
            context["avatar"] = None
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.GET.get("tag"):
            self.tag = get_object_or_404(Tag, name=self.request.GET.get("tag"))
            return queryset.filter(tags=self.tag)
        else:
            return queryset


class GoodsDetail(DetailView):
    queryset = Goods.objects.all()
    context_object_name = "goods"
    # TODO: Приделать кнопку редактирования в шаблоне, которая отображается если у пользователя есть права на редактирование товара (если он продавец)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["avatar"] = Profile.objects.get(user=self.request.user).avatar
        else:
            context["avatar"] = None
        return context


class GoodsCreate(LoginRequiredMixin, CreateView):
    login_url = "accounts/login/"
    redirect_field_name = "redirect_to"
    model = Goods
    template_name = "main/goods_create.html"
    form_class = GoodsCreateUpdateForm

    def get_success_url(self):
        self.success_url = reverse("goods-detail", kwargs={"pk": self.object.pk})
        return self.success_url

    def get_context_data(self, **kwargs):
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

    def post(self, request, *args, **kwargs):
        self.object = None
        if self.get_form().is_valid():
            return self.form_valid(self.get_form())
        else:
            return self.form_invalid(self.get_form())

    def form_valid(self, form):
        temp_goods = form.save(commit=False)
        temp_goods.seller = Seller.objects.get(
            name="Bobbie's Bits"
        )  # TODO: заменить на юзера, когда будет готова авторизация для продавцов
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class GoodsUpdate(LoginRequiredMixin, UpdateView):
    login_url = "accounts/login/"
    redirect_field_name = "redirect_to"
    model = Goods
    template_name = "main/goods_update.html"
    form_class = GoodsCreateUpdateForm

    def get_success_url(self):
        self.success_url = reverse("goods-detail", kwargs={"pk": self.object.pk})
        return self.success_url

    def get_context_data(self, **kwargs):
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

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.get_form():
            return self.form_valid(self.get_form())
        else:
            return self.form_invalid(self.get_form())

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class ProfileUpdate(UpdateView):
    model = User
    form_class = UserForm
    template_name = "main/profile_update.html"
    context_object_name = "profile"

    def get_success_url(self):
        self.success_url = reverse("profile", kwargs={"pk": self.request.user.pk})
        return self.success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "user_form" not in kwargs:
            kwargs["user_form"] = UserForm(instance=self.object)
        if "profile_form_set" not in kwargs:
            kwargs["profile_form_set"] = ProfileFormSet(instance=self.object)
        context["user_form"] = kwargs.get("user_form")
        context["profile_form_set"] = kwargs.get("profile_form_set")
        context["avatar"] = Profile.objects.get(user=self.object).avatar
        return context

    def get(self, request, *args, **kwargs):
        self.object = User.objects.get(id=request.user.pk)
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = User.objects.get(id=request.user.pk)
        user_form = UserForm(request.POST, instance=request.user)
        profile_form_set = ProfileFormSet(
            request.POST, request.FILES, instance=request.user.profile
        )
        if profile_form_set.is_valid() and user_form.is_valid():
            return self.form_valid(user_form, profile_form_set)
        else:
            return self.form_invalid(user_form, profile_form_set)

    def form_valid(self, user_form, profile_form_set):
        self.object = user_form.save()
        profile_form_set.instance = self.object
        for form in profile_form_set.forms:
            temp_profile = form.save(commit=False)
            temp_profile.user = self.object
            temp_profile.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, user_form, profile_form_set):
        return self.render_to_response(
            self.get_context_data(
                user_form=user_form, profile_form_set=profile_form_set
            )
        )


def index(request):
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


def logout_user(request):
    logout(request)
    return redirect("index")
