import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_cant_create_comment(
    news_pk_for_args,
    comment_form_data,
    client
):
    url = reverse('news:detail', args=news_pk_for_args)
    response = client.post(url, data=comment_form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_create_comment(
    news_pk_for_args,
    comment_form_data,
    author_client
):
    url = reverse('news:detail', args=news_pk_for_args)
    response = author_client.post(url, data=comment_form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.first()
    assert new_comment.text == comment_form_data['text']


@pytest.mark.django_db
def test_author_cant_use_bad_words(news_pk_for_args, author_client):
    bad_words_data = {'text': f'Начало фразы {BAD_WORDS[0]} конец фразы'}
    response = author_client.post(
        reverse('news:detail', args=news_pk_for_args),
        data=bad_words_data
    )
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_delete_comment(
    news_pk_for_args,
    author_client,
    comment_pk_for_args
):
    url = reverse('news:delete', args=comment_pk_for_args)
    news_comments_url = reverse(
        'news:detail', args=news_pk_for_args) + '#comments'
    response = author_client.delete(url)
    assertRedirects(response, news_comments_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_for_other_user(
    comment_pk_for_args,
    not_author_client
):
    url = reverse('news:delete', args=comment_pk_for_args)
    response = not_author_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_author_can_edit_comment(
    news_pk_for_args,
    author_client,
    comment_pk_for_args,
    comment_form_data
):
    url = reverse('news:edit', args=comment_pk_for_args)
    news_comments_url = reverse(
        'news:detail', args=news_pk_for_args) + '#comments'
    response = author_client.post(url, data=comment_form_data)
    assertRedirects(response, news_comments_url)
    new_comment = Comment.objects.first()
    assert new_comment.text == comment_form_data['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_for_other_user(
    comment_pk_for_args,
    not_author_client,
    comment_form_data,
    comment
):
    url = reverse('news:edit', args=comment_pk_for_args)
    response = not_author_client.post(url, data=comment_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text != comment_form_data['text']
