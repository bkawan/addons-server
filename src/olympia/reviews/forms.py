import re
from urllib2 import unquote

from django import forms
from django.utils.translation import ugettext as _, ugettext_lazy as _lazy

from bleach import TLDS

from olympia.amo.utils import raise_required

from .models import ReviewFlag


class ReviewReplyForm(forms.Form):
    form_id = "review-reply-edit"

    title = forms.CharField(
        required=False,
        label=_lazy(u"Title"),
        widget=forms.TextInput(
            attrs={'id': 'id_review_reply_title', },
        ),
    )
    body = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 3, 'id': 'id_review_reply_body', },
        ),
        label="Review",
    )

    def clean_body(self):
        body = self.cleaned_data.get('body', '')
        # Whitespace is not a review!
        if not body.strip():
            raise_required()
        return body


class ReviewForm(ReviewReplyForm):
    form_id = "review-edit"

    title = forms.CharField(
        required=False,
        label=_lazy(u"Title"),
        widget=forms.TextInput(
            attrs={'id': 'id_review_title', },
        ),
    )
    body = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 3, 'id': 'id_review_body', },
        ),
        label="Review",
    )
    rating = forms.ChoiceField(
        zip(range(1, 6), range(1, 6)), label=_lazy(u"Rating")
    )
    flags = re.I | re.L | re.U | re.M
    # This matches the following three types of patterns:
    # http://... or https://..., generic domain names, and IPv4
    # octets. It does not match IPv6 addresses or long strings such as
    # "example dot com".
    link_pattern = re.compile('((://)|'  # Protocols (e.g.: http://)
                              '((\d{1,3}\.){3}(\d{1,3}))|'
                              '([0-9a-z\-%%]+\.(%s)))' % '|'.join(TLDS),
                              flags)

    def _post_clean(self):
        # Unquote the body in case someone tries 'example%2ecom'.
        data = unquote(self.cleaned_data.get('body', ''))
        if '<br>' in data:
            self.cleaned_data['body'] = re.sub('<br>', '\n', data)
        if self.link_pattern.search(data) is not None:
            self.cleaned_data['flag'] = True
            self.cleaned_data['editorreview'] = True


class ReviewFlagForm(forms.ModelForm):

    class Meta:
        model = ReviewFlag
        fields = ('flag', 'note', 'review', 'user')

    def clean(self):
        data = super(ReviewFlagForm, self).clean()
        if 'note' in data and data['note'].strip():
            data['flag'] = ReviewFlag.OTHER
        elif data.get('flag') == ReviewFlag.OTHER:
            self.add_error(
                'note',
                _(u'A short explanation must be provided when selecting '
                  u'"Other" as a flag reason.'))
        return data
