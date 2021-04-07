from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import UpdateView

from main.forms import ProfileForm, UserForm
from main.models import Goods, Profile, Tag, User


class GoodsList(ListView):
    model = Goods
    paginate_by = 9
    context_object_name = "goods_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag_list"] = Tag.objects.all()
        context["tag"] = self.request.GET.get("tag")
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


class ProfileUpdate(UpdateView):
    model = User
    form_class = UserForm
    template_name = "main/profile_update.html"
    context_object_name = "profile"
    ProfileFormset = inlineformset_factory(
        User,
        Profile,
        fields="__all__",
        can_delete=False,
        labels={"phone_number": "Телефон"},
    )

    def get_success_url(self):
        self.success_url = reverse("profile", kwargs={"pk": self.request.user.pk})
        return self.success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["user_form"] = UserForm(self.request.POST, instance=self.object)
            context["profile_form_set"] = self.ProfileFormset(
                self.request.POST,
                instance=self.object,
            )
        else:
            context["user_form"] = UserForm(instance=self.object)
            context["profile_form_set"] = self.ProfileFormset(instance=self.object)
        return context

    def get(self, request, *args, **kwargs):
        self.object = User.objects.get(id=request.user.pk)
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = User.objects.get(id=request.user.pk)
        user_form = UserForm(request.POST, instance=request.user)
        profile_form_set = self.ProfileFormset(
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
    return render(
        request,
        "main/index.html",
        {
            "turn_on_block": turn_on_block,
            "user": request.user,
            "text_for_filter": text_for_filter,
        },
    )
