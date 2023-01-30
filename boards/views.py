from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Count
from django.utils import timezone
from django.urls import reverse

from django.views.generic import View, UpdateView, ListView

from .forms import NewTopicForm, PostForm
from .models import Board, Post, Topic


class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'home.html'


class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 20

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.board = None

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset


@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)

    if request.method == 'POST':
        user = request.user
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)

            topic.board = board
            topic.starter = user
            topic.save()

            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=user,
                updated_by=user
            )
            return redirect('topic_post', pk=pk, topic_pk=topic.pk)
    else:
        form = NewTopicForm()

    return render(request, 'new_topic.html', {'board': board, 'form': form})


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_post.html'
    paginate_by = 20

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.topic = None

    def get_context_data(self, **kwargs):
        # session_key = f'viewed_topic_{self.topic.pk}'
        # if not self.request.session.get(session_key, False):
        #     self.topic.views += 1
        #     self.topic.save()
        #     self.request.session[session_key] = True

        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset


@method_decorator(login_required, name='dispatch')
class ReplyPostView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.form = None
        self.topic = None

    def get_topic(self, topic_pk, board_pk):
        self.topic = get_object_or_404(Topic, pk=topic_pk, board__pk=board_pk)

    def render(self, request):
        return render(request, 'reply_topic.html', {'form': self.form, 'topic': self.topic})

    def post(self, request, pk, topic_pk):
        self.get_topic(topic_pk, pk)
        self.form = PostForm(request.POST)
        if self.form.is_valid():
            post = self.form.save(commit=False)
            post.topic = self.topic
            post.created_by = request.user
            post.save()

            self.topic.last_updated = timezone.now()
            self.topic.save()

            topic_url = reverse('topic_post', kwargs={'pk': pk, 'topic_pk': topic_pk})
            topic_post_url = f'{topic_url}?page={self.topic.get_page_count()}#{post.pk}'
            return redirect(topic_post_url)
        return self.render(request)

    def get(self, request, pk, topic_pk):
        self.get_topic(topic_pk, pk)
        self.form = PostForm()
        return self.render(request)


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.save()
        return redirect('topic_post', pk=post.topic.board.pk, topic_pk=post.topic.pk)
