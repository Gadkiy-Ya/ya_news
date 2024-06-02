import pytest

from django.urls import reverse

from yanews import settings
from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count_on_home_page(news_for_main_page, client):
    response = client.get(reverse('news:home'))
    objects_list = response.context['object_list']
    assert len(objects_list) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_ordering(client):
    response = client.get(reverse('news:home'))
    objects_list = response.context['object_list']
    all_dates = [obj.date for obj in objects_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_ordering(author_client, news_pk_for_args):
    response = author_client.get(reverse('news:detail', args=news_pk_for_args))
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [obj.created for obj in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news_pk_for_args):
    response = client.get(reverse('news:detail', args=news_pk_for_args))
    assert 'form' not in response.context


@pytest.mark.django_db
def test_author_client_has_form(author_client, news_pk_for_args):
    response = author_client.get(reverse('news:detail', args=news_pk_for_args))
    assert 'form' in response.context
    assert type(response.context['form']) is CommentForm
