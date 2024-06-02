import pytest
from datetime import datetime, timedelta

# from django.conf import settings
from django.test.client import Client
# from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News
from yanews import settings


@pytest.fixture
def news():
    news = News.objects.create(
        title='Тестовая новость',
        text='Текст тестовой новости',
    )
    return news


@pytest.fixture
def news_pk_for_args(news):
    return (news.pk,)


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Тестовый Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Тестовый не Автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст тестового комментария',
    )
    return comment


@pytest.fixture
def comment_pk_for_args(comment):
    return (comment.pk,)


@pytest.fixture
def news_for_main_page():
    today = datetime.now()
    all_news = [
        News(
            title=f'Тестовая новость {idx}',
            text=f'Текст тестовой новости {idx}',
            date=today - timedelta(days=idx),
        )
        for idx in range((settings.NEWS_COUNT_ON_HOME_PAGE + 1))
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def comments_for_news(news, author):
    all_comments = []
    now = timezone.now()
    for idx in range(5):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст тестового комментария {idx}',
        )
        comment.created = now + timedelta(days=idx)
        comment.save()
        all_comments.append(comment)

    return all_comments


@pytest.fixture
def comment_form_data():
    return {
        'text': 'Текст нового тестового комментария',
    }
