from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', default=timezone.now)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


class Voter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    voted = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'question'], name='unique_user_and_question'),
        ]
    
    def __str__(self):
        return f'{self.user.username}, "{self.question.question_text}"'


class Message(models.Model):
    heading_text = models.CharField(max_length=200)
    content_text = models.CharField(max_length=1000)
    pub_date = models.DateTimeField('date published', default=timezone.now)

    def __str__(self):
        return self.heading_text


class SecurityQuestion(models.Model):
    question_text = models.CharField(max_length=200, default='')

    def __str__(self):
        return self.question_text


class SecurityAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(SecurityQuestion, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=200)

    def __str__(self):
        return self.answer_text
